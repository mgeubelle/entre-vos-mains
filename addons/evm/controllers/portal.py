from uuid import uuid4

from odoo import _, http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.http import request


class EvmCustomerPortal(CustomerPortal):
    _patient_payment_request_items_per_page = 20
    _patient_document_items_per_page = 20

    def _coerce_positive_int(self, value, default=1):
        try:
            return max(int(value or default), 1)
        except (TypeError, ValueError):
            return default

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

    def _set_payment_request_upload_flash(self, case_id, request_id, message):
        request.session["evm_payment_request_upload_flash"] = {
            "case_id": case_id,
            "request_id": request_id,
            "message": message,
        }

    def _pop_payment_request_upload_flash(self, case_id):
        flash_payload = request.session.pop("evm_payment_request_upload_flash", None)
        if not flash_payload or flash_payload.get("case_id") != case_id:
            return {}
        return flash_payload

    def _set_payment_request_submission_flash(self, case_id, request_id, message):
        request.session["evm_payment_request_submission_flash"] = {
            "case_id": case_id,
            "request_id": request_id,
            "message": message,
        }

    def _pop_payment_request_submission_flash(self, case_id):
        flash_payload = request.session.pop("evm_payment_request_submission_flash", None)
        if not flash_payload or flash_payload.get("case_id") != case_id:
            return {}
        return flash_payload

    def _set_payment_request_update_flash(self, case_id, request_id, message):
        request.session["evm_payment_request_update_flash"] = {
            "case_id": case_id,
            "request_id": request_id,
            "message": message,
        }

    def _pop_payment_request_update_flash(self, case_id):
        flash_payload = request.session.pop("evm_payment_request_update_flash", None)
        if not flash_payload or flash_payload.get("case_id") != case_id:
            return {}
        return flash_payload

    def _issue_payment_request_submit_token(self, case_id, request_id):
        token = uuid4().hex
        submission_store = request.session.get("evm_payment_request_submit_store", {})
        submission_store[token] = {"case_id": case_id, "request_id": request_id, "submitted": False}
        request.session["evm_payment_request_submit_store"] = dict(list(submission_store.items())[-50:])
        return token

    def _begin_payment_request_submit(self, case_id, request_id, token):
        submission_store = request.session.get("evm_payment_request_submit_store", {})
        submission_state = submission_store.get(token)
        if (
            not token
            or not submission_state
            or submission_state.get("case_id") != case_id
            or submission_state.get("request_id") != request_id
        ):
            return "invalid"
        if submission_state.get("submitted"):
            return "replay"
        submission_state["in_progress"] = True
        submission_store[token] = submission_state
        request.session["evm_payment_request_submit_store"] = submission_store
        return "fresh"

    def _finish_payment_request_submit(self, token, submitted=False):
        submission_store = request.session.get("evm_payment_request_submit_store", {})
        submission_state = submission_store.get(token)
        if not submission_state:
            return
        submission_state.pop("in_progress", None)
        if submitted:
            submission_state["submitted"] = True
            submission_store[token] = submission_state
        else:
            submission_store.pop(token, None)
        request.session["evm_payment_request_submit_store"] = submission_store

    def _set_patient_case_flash(self, message):
        request.session["evm_patient_case_flash"] = {"message": message}

    def _pop_patient_case_flash(self):
        return request.session.pop("evm_patient_case_flash", {})

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

    def _get_allowed_payment_request_history_messages(self, payment_request):
        return payment_request.message_ids.filtered(
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

    def _get_attachment_type_label(self, attachment):
        mimetype = attachment.mimetype or ""
        if mimetype == "application/pdf":
            return "PDF"
        if mimetype in ("image/jpeg", "image/jpg"):
            return _("Image JPEG")
        if mimetype == "image/png":
            return _("Image PNG")
        if mimetype.startswith("image/"):
            return _("Image")
        return _("Fichier")

    def _format_payment_request_amount_total(self, amount_total):
        if amount_total in (False, None):
            return ""
        return f"{amount_total:.2f}"

    def _build_payment_request_form_values(self, payment_request, overrides=None):
        values = {
            "name": payment_request.name or "",
            "sessions_count": str(payment_request.sessions_count or ""),
            "amount_total": self._format_payment_request_amount_total(payment_request.amount_total),
        }
        if overrides:
            values.update(overrides)
        return values

    def _get_patient_case_document_entries(self, case_id, payment_requests, page=1, url_args=None):
        if not payment_requests:
            return [], False

        payment_request_by_id = {payment_request.id: payment_request for payment_request in payment_requests}
        attachment_model = request.env["ir.attachment"].sudo()
        domain = [
            ("res_model", "=", "evm.payment_request"),
            ("res_id", "in", payment_requests.ids),
            ("res_field", "=", False),
            ("type", "=", "binary"),
            ("evm_patient_visible", "=", True),
        ]
        attachment_count = attachment_model.search_count(domain)
        pager = portal_pager(
            url=f"/my/evm/cases/{case_id}",
            total=attachment_count,
            page=page,
            step=self._patient_document_items_per_page,
            url_args=url_args or {},
        )
        attachments = attachment_model.search(
            domain,
            order="create_date desc, id desc",
            limit=self._patient_document_items_per_page,
            offset=pager["offset"],
        )
        return [
            {
                "attachment": attachment,
                "payment_request": payment_request_by_id[attachment.res_id],
                "download_url": f"/web/content/{attachment.id}?download=true",
                "download_label": _(
                    "Telecharger %(attachment)s pour %(payment_request)s",
                    attachment=attachment.name,
                    payment_request=payment_request_by_id[attachment.res_id].name,
                ),
                "type_label": self._get_attachment_type_label(attachment),
            }
            for attachment in attachments
            if attachment.res_id in payment_request_by_id
        ], pager

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

    def _get_patient_payment_request_or_redirect(self, payment_request_id):
        if not self._is_patient_user():
            return request.env["evm.payment_request"]
        payment_request = request.env["evm.payment_request"].search([("id", "=", payment_request_id)], limit=1)
        return payment_request if payment_request else request.env["evm.payment_request"]

    def _prepare_patient_case_values(
        self,
        case_sudo,
        page=1,
        url_args=None,
        upload_errors=None,
        submission_errors=None,
        update_errors=None,
        update_form_values=None,
    ):
        payment_request_model = request.env["evm.payment_request"]
        payment_request_domain = [("case_id", "=", case_sudo.id)]
        payment_request_count = payment_request_model.search_count(payment_request_domain)
        case_payment_requests = payment_request_model.search(payment_request_domain)
        page = self._coerce_positive_int(page)
        document_page = self._coerce_positive_int((url_args or {}).get("document_page", 1))
        page_size = min(self._items_per_page, self._patient_payment_request_items_per_page)
        pager = portal_pager(
            url=f"/my/evm/cases/{case_sudo.id}",
            total=payment_request_count,
            page=page,
            step=page_size,
            url_args=url_args or {},
        )
        payment_requests = request.env["evm.payment_request"].search(
            payment_request_domain,
            order="create_date desc, id desc",
            limit=page_size,
            offset=pager["offset"],
        )
        document_entries, document_pager = self._get_patient_case_document_entries(
            case_sudo.id,
            case_payment_requests,
            page=document_page,
            url_args={"document_page": document_page} if document_page > 1 else {},
        )
        values = self._prepare_portal_layout_values()
        submission_tokens = {
            payment_request.id: self._issue_payment_request_submit_token(case_sudo.id, payment_request.id)
            for payment_request in payment_requests
            if payment_request.state in payment_request._portal_submittable_states
        }
        update_form_values_by_request = {
            payment_request.id: self._build_payment_request_form_values(
                payment_request,
                overrides=(update_form_values or {}).get(payment_request.id),
            )
            for payment_request in payment_requests
            if payment_request.state in payment_request._portal_resumable_states
        }
        payment_request_history_messages = {
            payment_request.id: self._get_allowed_payment_request_history_messages(payment_request)
            for payment_request in payment_requests
        }
        values.update(
            {
                "case": case_sudo,
                "payment_requests": payment_requests,
                "payment_request_history_messages": payment_request_history_messages,
                "document_entries": document_entries,
                "document_pager": document_pager,
                "pager": pager,
                "default_url": f"/my/evm/cases/{case_sudo.id}",
                "page_name": "evm_patient_case",
                "payment_request_page": page,
                "document_page": document_page,
                "update_errors": update_errors or {},
                "update_flash": self._pop_payment_request_update_flash(case_sudo.id),
                "update_form_values": update_form_values_by_request,
                "upload_errors": upload_errors or {},
                "upload_flash": self._pop_payment_request_upload_flash(case_sudo.id),
                "submission_errors": submission_errors or {},
                "submission_flash": self._pop_payment_request_submission_flash(case_sudo.id),
                "submission_tokens": submission_tokens,
            }
        )
        return values

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
                "portal_flash": self._pop_patient_case_flash() if self._is_patient_user() else {},
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
            return request.render(
                "evm.evm_portal_my_patient_case",
                self._prepare_patient_case_values(case_sudo, page=page, url_args=kwargs),
            )

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

    @http.route(
        "/my/evm/payment-requests/<int:payment_request_id>/update",
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def portal_my_payment_request_update(self, payment_request_id, **post):
        payment_request = self._get_patient_payment_request_or_redirect(payment_request_id)
        if not payment_request:
            self._set_patient_case_flash(_("Cette demande de paiement n'est pas accessible depuis votre portail."))
            return request.redirect("/my/evm/cases")

        payment_request_page = self._coerce_positive_int(post.get("payment_request_page"))
        document_page = self._coerce_positive_int(post.get("document_page"))
        redirect_url = f"/my/evm/cases/{payment_request.case_id.id}"
        if payment_request_page > 1:
            redirect_url = f"{redirect_url}/page/{payment_request_page}"
        if document_page > 1:
            redirect_url = f"{redirect_url}?document_page={document_page}"

        raw_name = post.get("name") or ""
        form_values = {
            "name": raw_name.strip(),
            "sessions_count": (post.get("sessions_count") or "").strip(),
            "amount_total": (post.get("amount_total") or "").strip(),
        }
        cleaned_values, errors = payment_request.validate_portal_creation_data(form_values)
        if not form_values["name"]:
            errors["name"] = _("Le nom de la demande ne peut pas etre vide.")
        else:
            try:
                cleaned_values["name"] = payment_request._sanitize_name(form_values["name"], case=payment_request.case_id)
            except ValidationError as exc:
                errors["name"] = exc.args[0]

        if errors:
            return request.render(
                "evm.evm_portal_my_patient_case",
                self._prepare_patient_case_values(
                    payment_request.case_id,
                    page=payment_request_page,
                    url_args={"document_page": document_page} if document_page > 1 else {},
                    update_errors={payment_request.id: errors},
                    update_form_values={payment_request.id: form_values},
                ),
            )

        try:
            payment_request.write(cleaned_values)
        except (AccessError, ValidationError) as exc:
            return request.render(
                "evm.evm_portal_my_patient_case",
                self._prepare_patient_case_values(
                    payment_request.case_id,
                    page=payment_request_page,
                    url_args={"document_page": document_page} if document_page > 1 else {},
                    update_errors={payment_request.id: {"form": exc.args[0]}},
                    update_form_values={payment_request.id: form_values},
                ),
            )

        self._set_payment_request_update_flash(
            payment_request.case_id.id,
            payment_request.id,
            _("Les informations de la demande ont ete mises a jour."),
        )
        return request.redirect(redirect_url)

    @http.route(
        "/my/evm/payment-requests/<int:payment_request_id>/attachments/upload",
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def portal_my_payment_request_upload_attachments(self, payment_request_id, **post):
        payment_request = self._get_patient_payment_request_or_redirect(payment_request_id)
        if not payment_request:
            self._set_patient_case_flash(_("Cette demande de paiement n'est pas accessible depuis votre portail."))
            return request.redirect("/my/evm/cases")

        uploaded_files = request.httprequest.files.getlist("documents")
        payment_request_page = self._coerce_positive_int(post.get("payment_request_page"))
        document_page = self._coerce_positive_int(post.get("document_page"))
        redirect_url = f"/my/evm/cases/{payment_request.case_id.id}"
        if payment_request_page > 1:
            redirect_url = f"{redirect_url}/page/{payment_request_page}"
        if document_page > 1:
            redirect_url = f"{redirect_url}?document_page={document_page}"
        try:
            attachments = payment_request.portal_upload_attachments(uploaded_files)
        except (AccessError, ValidationError) as exc:
            return request.render(
                "evm.evm_portal_my_patient_case",
                self._prepare_patient_case_values(
                    payment_request.case_id,
                    page=payment_request_page,
                    url_args={"document_page": document_page} if document_page > 1 else {},
                    upload_errors={payment_request.id: exc.args[0]},
                ),
            )

        self._set_payment_request_upload_flash(
            payment_request.case_id.id,
            payment_request.id,
            _("%(count)s document(s) ont ete ajoutes a la demande.", count=len(attachments)),
        )
        return request.redirect(redirect_url)

    @http.route(
        "/my/evm/payment-requests/<int:payment_request_id>/submit",
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def portal_my_payment_request_submit(self, payment_request_id, **post):
        payment_request = self._get_patient_payment_request_or_redirect(payment_request_id)
        if not payment_request:
            self._set_patient_case_flash(_("Cette demande de paiement n'est pas accessible depuis votre portail."))
            return request.redirect("/my/evm/cases")

        payment_request_page = self._coerce_positive_int(post.get("payment_request_page"))
        document_page = self._coerce_positive_int(post.get("document_page"))
        redirect_url = f"/my/evm/cases/{payment_request.case_id.id}"
        if payment_request_page > 1:
            redirect_url = f"{redirect_url}/page/{payment_request_page}"
        if document_page > 1:
            redirect_url = f"{redirect_url}?document_page={document_page}"

        submit_token = post.get("submission_token")
        submission_status = self._begin_payment_request_submit(payment_request.case_id.id, payment_request.id, submit_token)
        if submission_status == "replay":
            self._set_payment_request_submission_flash(
                payment_request.case_id.id,
                payment_request.id,
                _("La demande de paiement a deja ete soumise a la fondation."),
            )
            return request.redirect(redirect_url)
        if submission_status == "invalid":
            return request.render(
                "evm.evm_portal_my_patient_case",
                self._prepare_patient_case_values(
                    payment_request.case_id,
                    page=payment_request_page,
                    url_args={"document_page": document_page} if document_page > 1 else {},
                    submission_errors={payment_request.id: _("Le formulaire n'est plus valide. Veuillez reessayer.")},
                ),
            )

        try:
            payment_request.action_submit()
        except (AccessError, ValidationError) as exc:
            self._finish_payment_request_submit(submit_token)
            return request.render(
                "evm.evm_portal_my_patient_case",
                self._prepare_patient_case_values(
                    payment_request.case_id,
                    page=payment_request_page,
                    url_args={"document_page": document_page} if document_page > 1 else {},
                    submission_errors={payment_request.id: exc.args[0]},
                ),
            )

        self._finish_payment_request_submit(submit_token, submitted=True)
        self._set_payment_request_submission_flash(
            payment_request.case_id.id,
            payment_request.id,
            _("La demande de paiement a ete soumise a la fondation."),
        )
        return request.redirect(redirect_url)
