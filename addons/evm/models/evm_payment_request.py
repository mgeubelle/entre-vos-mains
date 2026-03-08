from odoo import fields, models


class EvmPaymentRequest(models.Model):
    _name = "evm.payment_request"
    _description = "EVM Payment Request"

    name = fields.Char(required=True, string="Nom")
    case_id = fields.Many2one(
        "evm.case",
        index=True,
        ondelete="cascade",
        required=True,
        string="Dossier",
    )
    patient_user_id = fields.Many2one(
        "res.users",
        index=True,
        related="case_id.patient_user_id",
        store=True,
        string="Patient",
    )
