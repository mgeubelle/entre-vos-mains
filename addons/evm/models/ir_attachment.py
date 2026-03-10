from odoo import api, fields, models
from odoo.exceptions import AccessError


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    evm_patient_visible = fields.Boolean(
        string="Visible sur le portail patient",
        default=False,
        copy=False,
        index=True,
    )

    def _is_evm_patient_portal_context(self):
        return not self.env.su and self.env.user.has_group("evm.group_evm_patient")

    def _get_evm_patient_portal_attachment_rows(self):
        if not self:
            return {}
        rows = self.sudo().read(["res_model", "res_id", "res_field", "evm_patient_visible"])
        return {row["id"]: row for row in rows}

    def _get_evm_patient_portal_readable_ids(self, attachment_rows=None):
        attachment_rows = attachment_rows or self._get_evm_patient_portal_attachment_rows()
        candidate_request_ids = [
            row["res_id"]
            for row in attachment_rows.values()
            if row["res_model"] == "evm.payment_request"
            and row["res_id"]
            and not row["res_field"]
            and row["evm_patient_visible"]
        ]
        if not candidate_request_ids:
            return set()

        allowed_request_ids = set(self.env["evm.payment_request"].search([("id", "in", candidate_request_ids)]).ids)
        return {
            attachment_id
            for attachment_id, row in attachment_rows.items()
            if row["res_model"] == "evm.payment_request"
            and row["res_id"] in allowed_request_ids
            and not row["res_field"]
            and row["evm_patient_visible"]
        }

    @api.model_create_multi
    def create(self, vals_list):
        if self._is_evm_patient_portal_context():
            for vals in vals_list:
                if vals.get("res_model") == "evm.payment_request" and vals.get("res_field") in (None, False):
                    vals.setdefault("evm_patient_visible", True)
        return super().create(vals_list)

    def _check_access(self, operation):
        if operation == "read" and self and self._is_evm_patient_portal_context():
            attachment_rows = self._get_evm_patient_portal_attachment_rows()
            evm_attachment_ids = [
                attachment_id
                for attachment_id, row in attachment_rows.items()
                if row["res_model"] == "evm.payment_request"
            ]
            readable_ids = self._get_evm_patient_portal_readable_ids(attachment_rows)
            other_attachments = self.browse([attachment_id for attachment_id in self.ids if attachment_id not in evm_attachment_ids])
            forbidden = self.browse([attachment_id for attachment_id in evm_attachment_ids if attachment_id not in readable_ids])
            error_func = None

            if other_attachments:
                other_access = super(IrAttachment, other_attachments)._check_access(operation)
                if other_access:
                    other_forbidden, error_func = other_access
                    forbidden |= other_forbidden

            if forbidden:
                if error_func is None:
                    def error_func():
                        return AccessError(
                            self.env._(
                                "Sorry, you are not allowed to access this document. "
                                "Please contact your system administrator.\n\n"
                                "(Operation: %(operation)s)\n\n"
                                "Records: %(records)s, User: %(user)s",
                                operation=operation,
                                records=forbidden[:6],
                                user=self.env.uid,
                            )
                        )
                return forbidden, error_func
            return None
        return super()._check_access(operation)
