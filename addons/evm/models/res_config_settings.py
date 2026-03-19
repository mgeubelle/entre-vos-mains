from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    evm_annual_session_cap = fields.Integer(
        string="Plafond annuel de seances",
        config_parameter="evm.annual_session_cap",
        default=0,
        help="Nombre maximum de seances que la fondation peut autoriser sur une annee civile. 0 desactive le controle.",
    )
    evm_case_closure_delay_days = fields.Integer(
        string="Delai de cloture automatique des dossiers",
        config_parameter="evm.case_closure_delay_days",
        default=90,
        help=(
            "Nombre de jours apres la decision fondation a partir duquel un dossier accepte devient eligible "
            "a la cloture automatique. 0 desactive le critere de delai."
        ),
    )
