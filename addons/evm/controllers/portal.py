from uuid import uuid4

from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.http import request


class EvmCustomerPortal(CustomerPortal):
    _patient_payment_request_items_per_page = 20

    def _get_kine_case_domain(self):
        return [("kine_user_id", "=", request.env.user.id)]

    def _get_patient_case_domain(self):
        return [("patient_user_id", "=", request.env.user.id), ("state", "=", "accepted")]

    def _is_kine_user(self):
        return request.env.user.has_group("evm.group_evm_kine")

    def _is_patient_user(self):
        return request.env.user.has_group("evm.group_evm_patient")

    def _get_portal_case_domain(self):
        if self._is_kine_user():
            return self._get_kine_case_domain()
        if self._is_patient_user():
            return self._get_patient_case_domain()
        return []

    def _issue_payment_request_submission_token(self, case_id):
        token = uuid4().hex
        submission_store = request.session.get("evm_payment_request_submission_store", {})
        submission_store[token] = {"case_id": case_id, "request_id": False}
        request.session["evm_payment_request_submission_store"] = dict(list(submission_store.items())[-20:])
        return token

    def _begin_payment_request_submission(self, case_id, token):
        submission_store = request.session.get("evm_payment_request_submission_store", {})
        submission_state = submission_store.get(token)
        if not token or not submission_state or submission_state.get("case_id") != case_id:
            return "invalid", False
        if submission_state.get("request_id"):
            return "replay", submission_state["request_id"]
        submission_state["in_progress"] = True
        submission_store[token] = submission_state
        request.session["evm_payment_request_submission_store"] = submission_store
        return "fresh", False

    def _finish_payment_request_submission(self, token, request_id=None):
        submission_store = request.session.get("evm_payment_request_submission_store", {})
        submission_state = submission_store.get(token)
        if not submission_state:
            return
        submission_state.pop("in_progress", None)
        if request_id:
            submission_state["request_id"] = request_id
            submission_store[token] = submission_state
        else:
            submission_store.pop(token, None)
        request.session["evm_payment_request_submission_store"] = submission_store

    def _set_created_payment_request_flash(self, case_id, request_id):
        request.session["evm_payment_request_created_flash"] = {"case_id": case_id, "request_id": request_id}

    def _pop_created_payment_request_flash(self, case_id):
        flash_payload = request.session.pop("evm_payment_request_created_flash", None)
        if not flash_payload or flash_payload.get("case_id") != case_id or not flash_payload.get("request_id"):
            return request.env["evm.payment_request"]
        try:
            return self._document_check_access("evm.payment_request", flash_payload["request_id"])
        except (AccessError, MissingError):
            return request.env["evm.payment_request"]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        case_model = request.env["evm.case"]
        if "evm_case_count" in counters:
            domain = self._get_portal_case_domain()
            values["evm_case_count"] = case_model.search_count(domain) if domain and case_model.has_access("read") else 0
        return values

    def _get_allowed_history_messages(self, case_sudo):
        return case_sudo.message_ids.filtered(
            lambda message: message.body and (not message.subtype_id or not message.subtype_id.internal)
        ).sorted(lambda message: message.date or message.create_date, reverse=True)

    def _prepare_case_creation_values(self, form_values=None, errors=None):
        values = self._prepare_portal_layout_values()
        values.update(
            {
                "page_name": "evm_case_create",
                "form_values": form_values or {},
                "errors": errors or {},
                "page_error": "Veuillez corriger les erreurs ci-dessous." if errors else False,
            }
        )
        return values

    def _prepare_payment_request_creation_values(
        self,
        case,
        form_values=None,
        errors=None,
        created_request=None,
        submission_token=None,
    ):
        values = self._prepare_portal_layout_values()
        values.update(
            {
                "case": case,
                "created_request": created_request,
                "page_name": "evm_payment_request_create",
                "form_values": form_values or {},
                "errors": errors or {},
                "page_error": "Veuillez corriger les erreurs ci-dessous." if errors else False,
                "submission_token": submission_token or self._issue_payment_request_submission_token(case.id),
            }
        )
        return values

    def _get_patient_case_or_redirect(self, case_id):
        if not self._is_patient_user():
            return None
        try:
            case_sudo = self._document_check_access("evm.case", case_id)
        except (AccessError, MissingError):
            return None
        if case_sudo.patient_user_id != request.env.user or case_sudo.state != "accepted":
            return None
        return case_sudo

    def _get_portal_case_or_redirect(self, case_id):
        if not request.env["evm.case"].has_access("read"):
            return None
        try:
            return self._document_check_access("evm.case", case_id)
        except (AccessError, MissingError):
            return None

    @http.route(
        ["/my/evm/cases", "/my/evm/cases/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_cases(self, page=1, **kwargs):
        case_model = request.env["evm.case"]
        domain = self._get_portal_case_domain()
        if not domain or not case_model.has_access("read"):
            return request.redirect("/my")

        case_count = case_model.search_count(domain)
        pager = portal_pager(
            url="/my/evm/cases",
            total=case_count,
            page=page,
            step=self._items_per_page,
            url_args=kwargs,
        )
        cases = case_model.search(domain, order="create_date desc, id desc", limit=self._items_per_page, offset=pager["offset"])

        values = self._prepare_portal_layout_values()
        values.update(
            {
                "cases": cases,
                "page_name": "evm_patient_cases" if self._is_patient_user() else "evm_cases",
                "pager": pager,
                "default_url": "/my/evm/cases",
            }
        )
        request.session["my_evm_cases_history"] = cases.ids[:100]
        template = "evm.evm_portal_my_patient_cases" if self._is_patient_user() else "evm.evm_portal_my_cases"
        return request.render(template, values)

    @http.route("/my/evm/cases/new", type="http", auth="user", methods=["GET"], website=True)
    def portal_my_case_new(self, **kwargs):
        case_model = request.env["evm.case"]
        if not self._is_kine_user() or not case_model.has_access("create"):
            return request.redirect("/my")

        return request.render("evm.evm_portal_my_case_create", self._prepare_case_creation_values())

    @http.route("/my/evm/cases/create", type="http", auth="user", methods=["POST"], website=True)
    def portal_my_case_create(self, **post):
        case_model = request.env["evm.case"]
        if not self._is_kine_user() or not case_model.has_access("create"):
            return request.redirect("/my")

        form_values = {
            "patient_name": (post.get("patient_name") or "").strip(),
            "patient_email": (post.get("patient_email") or "").strip(),
            "requested_session_count": post.get("requested_session_count") or "",
        }
        cleaned_values, errors = case_model.validate_submission_data(form_values)
        if errors:
            return request.render("evm.evm_portal_my_case_create", self._prepare_case_creation_values(form_values, errors))

        case = case_model.create(
            {
                "kine_user_id": request.env.user.id,
                **cleaned_values,
            }
        )
        try:
            case.action_submit_to_pending()
        except ValidationError as exc:
            errors = {"form": exc.args[0]}
            return request.render("evm.evm_portal_my_case_create", self._prepare_case_creation_values(form_values, errors))
        return request.redirect(f"/my/evm/cases/{case.id}")

    @http.route(
        ["/my/evm/cases/<int:case_id>", "/my/evm/cases/<int:case_id>/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_case(self, case_id, page=1, **kwargs):
        if not self._is_kine_user() and not self._is_patient_user():
            return request.redirect("/my")

        case_sudo = (
            self._get_patient_case_or_redirect(case_id)
            if self._is_patient_user()
            else self._get_portal_case_or_redirect(case_id)
        )
        if not case_sudo:
            return request.redirect("/my/evm/cases")

        if self._is_patient_user():
            payment_request_model = request.env["evm.payment_request"]
            payment_request_domain = [("case_id", "=", case_sudo.id)]
            payment_request_count = payment_request_model.search_count(payment_request_domain)
            page_size = min(self._items_per_page, self._patient_payment_request_items_per_page)
            pager = portal_pager(
                url=f"/my/evm/cases/{case_sudo.id}",
                total=payment_request_count,
                page=page,
                step=page_size,
                url_args=kwargs,
            )
            payment_requests = request.env["evm.payment_request"].search(
                payment_request_domain,
                order="create_date desc, id desc",
                limit=page_size,
                offset=pager["offset"],
            )
            values = self._prepare_portal_layout_values()
            values.update(
                {
                    "case": case_sudo,
                    "payment_requests": payment_requests,
                    "pager": pager,
                    "default_url": f"/my/evm/cases/{case_sudo.id}",
                    "page_name": "evm_patient_case",
                }
            )
            return request.render("evm.evm_portal_my_patient_case", values)

        values = self._prepare_portal_layout_values()
        values.update(
            {
                "case": case_sudo,
                "history_messages": self._get_allowed_history_messages(case_sudo),
                "page_name": "evm_case",
            }
        )
        return request.render("evm.evm_portal_my_case", values)

    @http.route(
        "/my/evm/cases/<int:case_id>/payment-requests/new",
        type="http",
        auth="user",
        methods=["GET"],
        website=True,
    )
    def portal_my_payment_request_new(self, case_id, created_request_id=None, **kwargs):
        case_sudo = self._get_patient_case_or_redirect(case_id)
        if not case_sudo:
            return request.redirect("/my")

        created_request = self._pop_created_payment_request_flash(case_sudo.id)
        if created_request and created_request.case_id != case_sudo:
            created_request = request.env["evm.payment_request"]

        return request.render(
            "evm.evm_portal_my_payment_request_create",
            self._prepare_payment_request_creation_values(case_sudo, created_request=created_request),
        )

    @http.route(
        "/my/evm/cases/<int:case_id>/payment-requests/create",
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def portal_my_payment_request_create(self, case_id, **post):
        case_sudo = self._get_patient_case_or_redirect(case_id)
        if not case_sudo:
            return request.redirect("/my")

        submission_status, replay_request_id = self._begin_payment_request_submission(case_sudo.id, post.get("submission_token"))
        if submission_status == "replay":
            self._set_created_payment_request_flash(case_sudo.id, replay_request_id)
            return request.redirect(f"/my/evm/cases/{case_sudo.id}/payment-requests/new")
        if submission_status == "invalid":
            errors = {"form": "Le formulaire n'est plus valide. Veuillez reessayer."}
            return request.render(
                "evm.evm_portal_my_payment_request_create",
                self._prepare_payment_request_creation_values(case_sudo, errors=errors),
            )

        payment_request_model = request.env["evm.payment_request"]
        form_values = {
            "sessions_count": (post.get("sessions_count") or "").strip(),
            "amount_total": (post.get("amount_total") or "").strip(),
        }
        cleaned_values, errors = payment_request_model.validate_portal_creation_data(form_values)
        if errors:
            self._finish_payment_request_submission(post.get("submission_token"))
            return request.render(
                "evm.evm_portal_my_payment_request_create",
                self._prepare_payment_request_creation_values(case_sudo, form_values=form_values, errors=errors),
            )

        try:
            payment_request = payment_request_model.create(
                {
                    "case_id": case_sudo.id,
                    **cleaned_values,
                }
            )
        except (AccessError, ValidationError) as exc:
            self._finish_payment_request_submission(post.get("submission_token"))
            errors = {"form": exc.args[0]}
            return request.render(
                "evm.evm_portal_my_payment_request_create",
                self._prepare_payment_request_creation_values(case_sudo, form_values=form_values, errors=errors),
            )
        self._finish_payment_request_submission(post.get("submission_token"), payment_request.id)
        self._set_created_payment_request_flash(case_sudo.id, payment_request.id)
        return request.redirect(f"/my/evm/cases/{case_sudo.id}/payment-requests/new")
