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
        return [("patient_user_id", "=", request.env.user.id), ("state", "in", ("pending", "accepted", "closed"))]

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

    def _get_case_tabs(self):
        if self._is_patient_user():
            return [
                {"key": "pending", "title": _("En attente"), "states": ("pending",)},
                {"key": "active", "title": _("En cours"), "states": ("accepted",)},
                {
                    "key": "archived",
                    "title": _("Archives / clotures"),
                    "states": ("closed",),
                },
            ]
        return [
            {"key": "pending", "title": _("En attente"), "states": ("pending",)},
            {
                "key": "active",
                "title": _("En cours"),
                "states": ("draft", "accepted"),
            },
            {
                "key": "archived",
                "title": _("Archives / clotures"),
                "states": ("refused", "closed"),
            },
        ]

    def _build_case_tab_domain(self, base_domain, tab_states):
        return [*base_domain, ("state", "in", list(tab_states))]

    def _get_case_tab_values(self, base_domain, active_tab_key):
        case_model = request.env["evm.case"]
        tabs = self._get_case_tabs()
        tab_values = []
        for tab in tabs:
            tab_domain = self._build_case_tab_domain(base_domain, tab["states"])
            tab_count = case_model.search_count(tab_domain)
            tab_values.append(
                {
                    "key": tab["key"],
                    "title": tab["title"],
                    "count": tab_count,
                    "domain": tab_domain,
                    "is_active": tab["key"] == active_tab_key,
                    "url": f"/my/evm/cases?tab={tab['key']}",
                }
            )
        available_keys = {tab["key"] for tab in tab_values}
        if active_tab_key not in available_keys:
            if any(tab["key"] == "active" and tab["count"] for tab in tab_values):
                active_tab_key = "active"
            else:
                active_tab_key = next((tab["key"] for tab in tab_values if tab["count"]), tab_values[0]["key"])
        for tab in tab_values:
            tab["is_active"] = tab["key"] == active_tab_key
        return tab_values, active_tab_key

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

    def _set_case_comment_flash(self, case_id, message):
        request.session["evm_case_comment_flash"] = {
            "case_id": case_id,
            "message": message,
        }

    def _pop_case_comment_flash(self, case_id):
        flash_payload = request.session.pop("evm_case_comment_flash", None)
        if not flash_payload or flash_payload.get("case_id") != case_id:
            return {}
        return flash_payload

    def _set_payment_request_comment_flash(self, case_id, request_id, message):
        request.session["evm_payment_request_comment_flash"] = {
            "case_id": case_id,
            "request_id": request_id,
            "message": message,
        }

    def _pop_payment_request_comment_flash(self, case_id):
        flash_payload = request.session.pop("evm_payment_request_comment_flash", None)
        if not flash_payload or flash_payload.get("case_id") != case_id:
            return {}
        return flash_payload

    def _set_patient_case_flash(self, message):
        request.session["evm_patient_case_flash"] = {"message": message}

    def _pop_patient_case_flash(self):
        return request.session.pop("evm_patient_case_flash", {})

    def _redirect_patient_case_list_with_flash(self, message):
        self._set_patient_case_flash(message)
        return request.redirect("/my/evm/cases")

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

    def _get_history_author_names(self, messages):
        return {message.id: message.sudo().author_id.display_name for message in messages if message.author_id}

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

    def _prepare_kine_case_values(self, case_sudo, case_comment_error=None, case_comment_value=""):
        values = self._prepare_portal_layout_values()
        values.update(
            {
                "case": case_sudo,
                "history_messages": self._get_allowed_history_messages(case_sudo),
                "case_comment_error": case_comment_error,
                "case_comment_flash": self._pop_case_comment_flash(case_sudo.id),
                "case_comment_value": case_comment_value,
                "page_name": "evm_case",
            }
        )
        return values

    def _prepare_payment_request_creation_values(
        self,
        case,
        form_values=None,
        errors=None,
        created_request=None,
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

    def _build_payment_request_document_entry(self, attachment, payment_request):
        return {
            "attachment": attachment,
            "payment_request": payment_request,
            "download_url": f"/web/content/{attachment.id}?download=true",
            "download_label": _(
                "Telecharger %(attachment)s pour %(payment_request)s",
                attachment=attachment.name,
                payment_request=payment_request.name,
            ),
            "type_label": self._get_attachment_type_label(attachment),
        }

    def _get_payment_request_document_entries_map(self, payment_requests):
        if not payment_requests:
            return {}

        payment_request_by_id = {payment_request.id: payment_request for payment_request in payment_requests}
        attachments = (
            request.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "evm.payment_request"),
                    ("res_id", "in", payment_requests.ids),
                    ("res_field", "=", False),
                    ("type", "=", "binary"),
                    ("evm_patient_visible", "=", True),
                ],
                order="create_date desc, id desc",
            )
        )
        document_entries = {payment_request_id: [] for payment_request_id in payment_request_by_id}
        for attachment in attachments:
            payment_request = payment_request_by_id.get(attachment.res_id)
            if payment_request:
                document_entries[attachment.res_id].append(
                    self._build_payment_request_document_entry(attachment, payment_request)
                )
        return document_entries

    def _collect_payment_request_expanded_ids(
        self,
        payment_requests,
        upload_errors=None,
        submission_errors=None,
        update_errors=None,
        payment_request_comment_errors=None,
        upload_flash=None,
        submission_flash=None,
        update_flash=None,
        payment_request_comment_flash=None,
    ):
        expanded_ids = set()
        for errors in (
            upload_errors or {},
            submission_errors or {},
            update_errors or {},
            payment_request_comment_errors or {},
        ):
            expanded_ids.update(errors.keys())
        for flash_payload in (
            upload_flash or {},
            submission_flash or {},
            update_flash or {},
            payment_request_comment_flash or {},
        ):
            if flash_payload.get("request_id"):
                expanded_ids.add(flash_payload["request_id"])
        if not expanded_ids and payment_requests:
            expanded_ids.add(payment_requests[:1].id)
        return expanded_ids

    def _map_payment_request_creation_error(self, error_message):
        if any(
            keyword in (error_message or "")
            for keyword in ("justificatif", "fichier", "Formats autorises", "10 Mo")
        ):
            return {"documents": error_message}
        return {"form": error_message}

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

    def _sanitize_portal_comment(self, raw_comment):
        return (raw_comment or "").strip()

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
            self._build_payment_request_document_entry(attachment, payment_request_by_id[attachment.res_id])
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
        if case_sudo.patient_user_id != request.env.user or case_sudo.state not in ("pending", "accepted", "closed"):
            return None
        return case_sudo

    def _get_patient_payment_request(self, payment_request_id):
        if not self._is_patient_user():
            return request.env["evm.payment_request"]
        payment_request = request.env["evm.payment_request"].search([("id", "=", payment_request_id)], limit=1)
        return payment_request if payment_request else request.env["evm.payment_request"]

    def _build_patient_case_redirect_url(self, case_id, payment_request_page=1, document_page=1):
        redirect_url = f"/my/evm/cases/{case_id}"
        if payment_request_page > 1:
            redirect_url = f"{redirect_url}/page/{payment_request_page}"
        if document_page > 1:
            redirect_url = f"{redirect_url}?document_page={document_page}"
        return redirect_url

    def _get_patient_payment_request_context(self, payment_request_id, post):
        payment_request = self._get_patient_payment_request(payment_request_id)
        payment_request_page = self._coerce_positive_int(post.get("payment_request_page"))
        document_page = self._coerce_positive_int(post.get("document_page"))
        return {
            "payment_request": payment_request,
            "payment_request_page": payment_request_page,
            "document_page": document_page,
            "url_args": {"document_page": document_page} if document_page > 1 else {},
            "redirect_url": self._build_patient_case_redirect_url(
                payment_request.case_id.id if payment_request else False,
                payment_request_page=payment_request_page,
                document_page=document_page,
            )
            if payment_request
            else "/my/evm/cases",
        }

    def _render_patient_case_from_payment_request_context(self, payment_request_context, **kwargs):
        payment_request = payment_request_context["payment_request"]
        return request.render(
            "evm.evm_portal_my_patient_case",
            self._prepare_patient_case_values(
                payment_request.case_id,
                page=payment_request_context["payment_request_page"],
                url_args=payment_request_context["url_args"],
                **kwargs,
            ),
        )

    def _prepare_patient_case_values(
        self,
        case_sudo,
        page=1,
        url_args=None,
        upload_errors=None,
        submission_errors=None,
        update_errors=None,
        update_form_values=None,
        case_comment_error=None,
        case_comment_value="",
        payment_request_comment_errors=None,
        payment_request_comment_values=None,
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
        payment_request_document_entries = self._get_payment_request_document_entries_map(payment_requests)
        values = self._prepare_portal_layout_values()
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
        payment_request_history_author_names = {
            payment_request.id: self._get_history_author_names(messages)
            for payment_request, messages in (
                (payment_request, payment_request_history_messages.get(payment_request.id, request.env["mail.message"]))
                for payment_request in payment_requests
            )
        }
        case_comment_flash = self._pop_case_comment_flash(case_sudo.id)
        payment_request_comment_flash = self._pop_payment_request_comment_flash(case_sudo.id)
        update_flash = self._pop_payment_request_update_flash(case_sudo.id)
        upload_flash = self._pop_payment_request_upload_flash(case_sudo.id)
        submission_flash = self._pop_payment_request_submission_flash(case_sudo.id)
        expanded_payment_request_ids = self._collect_payment_request_expanded_ids(
            payment_requests,
            upload_errors=upload_errors,
            submission_errors=submission_errors,
            update_errors=update_errors,
            payment_request_comment_errors=payment_request_comment_errors,
            upload_flash=upload_flash,
            submission_flash=submission_flash,
            update_flash=update_flash,
            payment_request_comment_flash=payment_request_comment_flash,
        )
        values.update(
            {
                "case": case_sudo,
                "case_history_messages": self._get_allowed_history_messages(case_sudo),
                "case_history_author_names": self._get_history_author_names(self._get_allowed_history_messages(case_sudo)),
                "case_comment_error": case_comment_error,
                "case_comment_flash": case_comment_flash,
                "case_comment_value": case_comment_value,
                "payment_requests": payment_requests,
                "payment_request_document_entries": payment_request_document_entries,
                "expanded_payment_request_ids": expanded_payment_request_ids,
                "payment_request_comment_errors": payment_request_comment_errors or {},
                "payment_request_comment_flash": payment_request_comment_flash,
                "payment_request_comment_values": payment_request_comment_values or {},
                "payment_request_history_messages": payment_request_history_messages,
                "payment_request_history_author_names": payment_request_history_author_names,
                "document_entries": document_entries,
                "document_pager": document_pager,
                "pager": pager,
                "default_url": f"/my/evm/cases/{case_sudo.id}",
                "page_name": "evm_patient_case",
                "payment_request_page": page,
                "document_page": document_page,
                "update_errors": update_errors or {},
                "update_flash": update_flash,
                "update_form_values": update_form_values_by_request,
                "upload_errors": upload_errors or {},
                "upload_flash": upload_flash,
                "submission_errors": submission_errors or {},
                "submission_flash": submission_flash,
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

        tab_values, active_tab_key = self._get_case_tab_values(domain, kwargs.get("tab"))
        active_tab = next(tab for tab in tab_values if tab["key"] == active_tab_key)
        case_count = active_tab["count"]
        pager = portal_pager(
            url="/my/evm/cases",
            total=case_count,
            page=page,
            step=self._items_per_page,
            url_args={"tab": active_tab_key},
        )
        cases = case_model.search(
            active_tab["domain"],
            order="create_date desc, id desc",
            limit=self._items_per_page,
            offset=pager["offset"],
        )

        values = self._prepare_portal_layout_values()
        values.update(
            {
                "cases": cases,
                "case_tabs": tab_values,
                "active_case_tab": active_tab_key,
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

        return request.render("evm.evm_portal_my_case", self._prepare_kine_case_values(case_sudo))

    @http.route(
        "/my/evm/cases/<int:case_id>/comments/post",
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def portal_my_case_comment_post(self, case_id, **post):
        if self._is_patient_user():
            case_sudo = self._get_patient_case_or_redirect(case_id)
        elif self._is_kine_user():
            case_sudo = self._get_portal_case_or_redirect(case_id)
        else:
            return request.redirect("/my")
        if not case_sudo:
            if self._is_patient_user():
                return self._redirect_patient_case_list_with_flash(_("Ce dossier n'est pas accessible depuis votre portail."))
            return request.redirect("/my/evm/cases")

        comment = self._sanitize_portal_comment(post.get("comment"))
        payment_request_page = self._coerce_positive_int(post.get("payment_request_page"))
        document_page = self._coerce_positive_int(post.get("document_page"))
        case = request.env["evm.case"].browse(case_sudo.id)
        if not comment:
            if self._is_patient_user():
                return request.render(
                    "evm.evm_portal_my_patient_case",
                    self._prepare_patient_case_values(
                        case_sudo,
                        page=payment_request_page,
                        url_args={"document_page": document_page} if document_page > 1 else {},
                        case_comment_error=_("Veuillez saisir un commentaire avant de l'envoyer."),
                        case_comment_value=post.get("comment") or "",
                    ),
                )
            return request.render(
                "evm.evm_portal_my_case",
                self._prepare_kine_case_values(
                    case_sudo,
                    case_comment_error=_("Veuillez saisir un commentaire avant de l'envoyer."),
                    case_comment_value=post.get("comment") or "",
                ),
            )
        try:
            case.action_post_comment(comment)
        except (AccessError, ValidationError) as exc:
            if self._is_patient_user():
                return request.render(
                    "evm.evm_portal_my_patient_case",
                    self._prepare_patient_case_values(
                        case_sudo,
                        page=payment_request_page,
                        url_args={"document_page": document_page} if document_page > 1 else {},
                        case_comment_error=exc.args[0],
                        case_comment_value=post.get("comment") or "",
                    ),
                )
            return request.render(
                "evm.evm_portal_my_case",
                self._prepare_kine_case_values(
                    case_sudo,
                    case_comment_error=exc.args[0],
                    case_comment_value=post.get("comment") or "",
                ),
            )

        self._set_case_comment_flash(case_sudo.id, _("Votre commentaire a ete ajoute au dossier."))
        if self._is_patient_user():
            return request.redirect(
                self._build_patient_case_redirect_url(
                    case_sudo.id,
                    payment_request_page=payment_request_page,
                    document_page=document_page,
                )
            )
        return request.redirect(f"/my/evm/cases/{case_sudo.id}")

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
        if case_sudo.state != "accepted":
            return request.redirect(f"/my/evm/cases/{case_sudo.id}")

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
        if case_sudo.state != "accepted":
            return request.redirect(f"/my/evm/cases/{case_sudo.id}")

        payment_request_model = request.env["evm.payment_request"]
        submission_mode = (post.get("submission_mode") or "draft").strip()
        submit_after_creation = submission_mode == "submit"
        form_values = {
            "sessions_count": (post.get("sessions_count") or "").strip(),
            "amount_total": (post.get("amount_total") or "").strip(),
            "submission_mode": submission_mode,
        }
        uploaded_files = request.httprequest.files.getlist("documents")
        cleaned_values, errors = payment_request_model.validate_portal_creation_data(form_values)
        if submit_after_creation and not any((getattr(uploaded_file, "filename", "") or "").strip() for uploaded_file in uploaded_files):
            errors["documents"] = _("Ajoutez au moins un justificatif avant de soumettre la demande.")
        if errors:
            return request.render(
                "evm.evm_portal_my_payment_request_create",
                self._prepare_payment_request_creation_values(case_sudo, form_values=form_values, errors=errors),
            )

        try:
            with request.env.cr.savepoint():
                payment_request = payment_request_model.create(
                    {
                        "case_id": case_sudo.id,
                        **cleaned_values,
                    }
                )
                if uploaded_files:
                    payment_request.portal_upload_attachments(uploaded_files)
                if submit_after_creation:
                    payment_request.action_submit()
        except (AccessError, ValidationError) as exc:
            errors = self._map_payment_request_creation_error(exc.args[0])
            return request.render(
                "evm.evm_portal_my_payment_request_create",
                self._prepare_payment_request_creation_values(case_sudo, form_values=form_values, errors=errors),
            )
        if submit_after_creation:
            self._set_payment_request_submission_flash(
                case_sudo.id,
                payment_request.id,
                _("La demande de paiement a ete creee puis soumise a la fondation."),
            )
            return request.redirect(f"/my/evm/cases/{case_sudo.id}")
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
        payment_request_context = self._get_patient_payment_request_context(payment_request_id, post)
        payment_request = payment_request_context["payment_request"]
        if not payment_request:
            return self._redirect_patient_case_list_with_flash(
                _("Cette demande de paiement n'est pas accessible depuis votre portail.")
            )

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
            return self._render_patient_case_from_payment_request_context(
                payment_request_context,
                update_errors={payment_request.id: errors},
                update_form_values={payment_request.id: form_values},
            )

        try:
            payment_request.write(cleaned_values)
        except (AccessError, ValidationError) as exc:
            return self._render_patient_case_from_payment_request_context(
                payment_request_context,
                update_errors={payment_request.id: {"form": exc.args[0]}},
                update_form_values={payment_request.id: form_values},
            )

        self._set_payment_request_update_flash(
            payment_request.case_id.id,
            payment_request.id,
            _("Les informations de la demande ont ete mises a jour."),
        )
        return request.redirect(payment_request_context["redirect_url"])

    @http.route(
        "/my/evm/payment-requests/<int:payment_request_id>/attachments/upload",
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def portal_my_payment_request_upload_attachments(self, payment_request_id, **post):
        payment_request_context = self._get_patient_payment_request_context(payment_request_id, post)
        payment_request = payment_request_context["payment_request"]
        if not payment_request:
            return self._redirect_patient_case_list_with_flash(
                _("Cette demande de paiement n'est pas accessible depuis votre portail.")
            )

        uploaded_files = request.httprequest.files.getlist("documents")
        try:
            attachments = payment_request.portal_upload_attachments(uploaded_files)
        except (AccessError, ValidationError) as exc:
            return self._render_patient_case_from_payment_request_context(
                payment_request_context,
                upload_errors={payment_request.id: exc.args[0]},
            )

        self._set_payment_request_upload_flash(
            payment_request.case_id.id,
            payment_request.id,
            _("%(count)s document(s) ont ete ajoutes a la demande.", count=len(attachments)),
        )
        return request.redirect(payment_request_context["redirect_url"])

    @http.route(
        "/my/evm/payment-requests/<int:payment_request_id>/submit",
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def portal_my_payment_request_submit(self, payment_request_id, **post):
        payment_request_context = self._get_patient_payment_request_context(payment_request_id, post)
        payment_request = payment_request_context["payment_request"]
        if not payment_request:
            return self._redirect_patient_case_list_with_flash(
                _("Cette demande de paiement n'est pas accessible depuis votre portail.")
            )
        if payment_request.state == "submitted":
            self._set_payment_request_submission_flash(
                payment_request.case_id.id,
                payment_request.id,
                _("La demande de paiement a deja ete soumise a la fondation."),
            )
            return request.redirect(payment_request_context["redirect_url"])

        try:
            payment_request.action_submit()
        except (AccessError, ValidationError) as exc:
            return self._render_patient_case_from_payment_request_context(
                payment_request_context,
                submission_errors={payment_request.id: exc.args[0]},
            )

        self._set_payment_request_submission_flash(
            payment_request.case_id.id,
            payment_request.id,
            _("La demande de paiement a ete soumise a la fondation."),
        )
        return request.redirect(payment_request_context["redirect_url"])

    @http.route(
        "/my/evm/payment-requests/<int:payment_request_id>/comments/post",
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def portal_my_payment_request_comment_post(self, payment_request_id, **post):
        payment_request_context = self._get_patient_payment_request_context(payment_request_id, post)
        payment_request = payment_request_context["payment_request"]
        if not payment_request:
            return self._redirect_patient_case_list_with_flash(
                _("Cette demande de paiement n'est pas accessible depuis votre portail.")
            )

        comment = self._sanitize_portal_comment(post.get("comment"))
        if not comment:
            return self._render_patient_case_from_payment_request_context(
                payment_request_context,
                payment_request_comment_errors={
                    payment_request.id: _("Veuillez saisir un commentaire avant de l'envoyer.")
                },
                payment_request_comment_values={payment_request.id: post.get("comment") or ""},
            )
        try:
            payment_request.action_post_comment(comment)
        except (AccessError, ValidationError) as exc:
            return self._render_patient_case_from_payment_request_context(
                payment_request_context,
                payment_request_comment_errors={payment_request.id: exc.args[0]},
                payment_request_comment_values={payment_request.id: post.get("comment") or ""},
            )

        self._set_payment_request_comment_flash(
            payment_request.case_id.id,
            payment_request.id,
            _("Votre commentaire a ete ajoute a la demande."),
        )
        return request.redirect(payment_request_context["redirect_url"])
