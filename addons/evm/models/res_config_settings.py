from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    evm_annual_session_cap = fields.Integer(
        string="Plafond annuel de seances",
        config_parameter="evm.annual_session_cap",
        default=0,
        help="Nombre maximum de seances que la fondation peut autoriser sur une annee civile. 0 desactive le controle.",
    )
