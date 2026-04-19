from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    evm_default_service_provider_id = fields.Many2one(
        "res.partner",
        string="Prestataire EVM par defaut",
        domain=[("evm_is_service_provider", "=", True)],
        help="Prestataire propose par defaut lors de la creation d'un dossier EVM par ce kinesitherapeute.",
    )

    @api.constrains("evm_default_service_provider_id")
    def _check_default_service_provider_is_flagged(self):
        for user in self:
            if user.evm_default_service_provider_id and not user.evm_default_service_provider_id.evm_is_service_provider:
                raise ValidationError(_("Le prestataire par defaut du kinesitherapeute doit etre marque comme prestataire EVM."))
