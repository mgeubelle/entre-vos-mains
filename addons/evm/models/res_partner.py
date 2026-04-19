from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    evm_is_service_provider = fields.Boolean(
        string="Prestataire EVM",
        help="Indique si ce contact peut etre selectionne comme prestataire sur un dossier EVM.",
    )
    evm_default_service_provider_id = fields.Many2one(
        "res.partner",
        string="Prestataire EVM par defaut",
        domain=[("evm_is_service_provider", "=", True)],
        help="Prestataire propose par defaut lors de la creation d'un dossier EVM pour ce contact kine.",
    )

    def _evm_get_service_provider_setup_errors(self):
        self.ensure_one()
        errors = []
        if not (self.name or "").strip():
            errors.append(_("le nom est obligatoire"))
        if not (self.email or "").strip():
            errors.append(_("une adresse e-mail est obligatoire"))
        if not self.bank_ids:
            errors.append(_("au moins un compte bancaire est obligatoire"))
        return errors

    @api.constrains("evm_is_service_provider")
    def _check_service_provider_flag_is_not_removed_while_in_use(self):
        partner_model = self.env["res.partner"].sudo()
        case_model = self.env["evm.case"].sudo()
        for partner in self:
            if partner.evm_is_service_provider:
                errors = partner._evm_get_service_provider_setup_errors()
                if errors:
                    raise ValidationError(
                        _("Le contact ne peut pas etre marque comme prestataire EVM car %(details)s.")
                        % {"details": ", ".join(errors)}
                    )
                continue
            if partner_model.search([("evm_default_service_provider_id", "=", partner.id)], limit=1):
                raise ValidationError(
                    _("Ce contact est defini comme prestataire par defaut sur au moins une fiche contact de kinesitherapeute.")
                )
            if case_model.search([("service_provider_id", "=", partner.id)], limit=1):
                raise ValidationError(_("Ce contact est deja utilise comme prestataire sur au moins un dossier."))

    @api.constrains("evm_default_service_provider_id")
    def _check_default_service_provider_is_flagged(self):
        for partner in self:
            if partner.evm_default_service_provider_id and not partner.evm_default_service_provider_id.evm_is_service_provider:
                raise ValidationError(
                    _("Le prestataire par defaut du kinesitherapeute doit etre marque comme prestataire EVM.")
                )

    @api.constrains("email", "bank_ids")
    def _check_service_provider_mandatory_data(self):
        for partner in self.filtered("evm_is_service_provider"):
            errors = partner._evm_get_service_provider_setup_errors()
            if errors:
                raise ValidationError(
                    _("Le contact marque comme prestataire EVM est incomplet: %(details)s.")
                    % {"details": ", ".join(errors)}
                )
