from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class EvmCustomerPortal(CustomerPortal):
    def _get_kine_case_domain(self):
        return [("kine_user_id", "=", request.env.user.id)]

    def _is_kine_user(self):
        return request.env.user.has_group("evm.group_evm_kine")

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        case_model = request.env["evm.case"]
        if "evm_case_count" in counters:
            values["evm_case_count"] = (
                case_model.search_count(self._get_kine_case_domain())
                if self._is_kine_user() and case_model.has_access("read")
                else 0
            )
        return values

    def _get_allowed_history_messages(self, case_sudo):
        return case_sudo.message_ids.filtered(
            lambda message: message.body and (not message.subtype_id or not message.subtype_id.internal)
        ).sorted(lambda message: message.date or message.create_date, reverse=True)

    @http.route(
        ["/my/evm/cases", "/my/evm/cases/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_cases(self, page=1, **kwargs):
        case_model = request.env["evm.case"]
        if not self._is_kine_user() or not case_model.has_access("read"):
            return request.redirect("/my")

        domain = self._get_kine_case_domain()
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
                "page_name": "evm_cases",
                "pager": pager,
                "default_url": "/my/evm/cases",
            }
        )
        request.session["my_evm_cases_history"] = cases.ids[:100]
        return request.render("evm.evm_portal_my_cases", values)

    @http.route("/my/evm/cases/<int:case_id>", type="http", auth="user", website=True)
    def portal_my_case(self, case_id, **kwargs):
        if not self._is_kine_user():
            return request.redirect("/my")

        try:
            case_sudo = self._document_check_access("evm.case", case_id)
        except (AccessError, MissingError):
            return request.redirect("/my/evm/cases")

        values = self._prepare_portal_layout_values()
        values.update(
            {
                "case": case_sudo,
                "history_messages": self._get_allowed_history_messages(case_sudo),
                "page_name": "evm_case",
            }
        )
        return request.render("evm.evm_portal_my_case", values)
