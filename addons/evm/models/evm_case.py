from odoo import fields, models


class EvmCase(models.Model):
    _name = "evm.case"
    _description = "EVM Case"

    name = fields.Char(required=True, string="Nom")
    kine_user_id = fields.Many2one(
        "res.users",
        index=True,
        required=True,
        string="Kinesitherapeute",
    )
    patient_user_id = fields.Many2one(
        "res.users",
        index=True,
        string="Patient",
    )
