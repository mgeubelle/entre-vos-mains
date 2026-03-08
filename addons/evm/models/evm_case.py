from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import single_email_re


class EvmCase(models.Model):
    _name = "evm.case"
    _inherit = ["mail.thread"]
    _description = "EVM Case"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, string="Nom")
    state = fields.Selection(
        selection=[
            ("draft", "Brouillon"),
            ("pending", "En attente"),
            ("accepted", "Accepte"),
            ("refused", "Refuse"),
            ("closed", "Cloture"),
        ],
        default="draft",
        required=True,
        string="Statut",
        tracking=True,
    )
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
    requested_session_count = fields.Integer(
        string="Seances demandees",
        tracking=True,
    )
    authorized_session_count = fields.Integer(
        string="Seances autorisees",
        tracking=True,
    )
    patient_display_name = fields.Char(
        compute="_compute_patient_display_name",
        compute_sudo=True,
        string="Patient visible",
    )
    patient_name = fields.Char(
        string="Nom du patient",
        tracking=True,
    )
    patient_email = fields.Char(
        string="Adresse e-mail du patient",
        tracking=True,
    )

    _kine_protected_write_fields = {"state", "authorized_session_count", "kine_user_id", "patient_user_id"}
    _kine_draft_only_fields = {"name", "patient_name", "patient_email", "requested_session_count"}

    @api.depends("patient_user_id", "patient_user_id.partner_id.display_name", "patient_name", "name")
    def _compute_patient_display_name(self):
        for record in self:
            record.patient_display_name = record.patient_user_id.partner_id.display_name or record.patient_name or record.name

    @api.model
    def validate_submission_data(self, values):
        cleaned_values = {
            "patient_name": (values.get("patient_name") or "").strip(),
            "patient_email": (values.get("patient_email") or "").strip(),
        }
        errors = {}
        requested_session_count = values.get("requested_session_count")

        if not cleaned_values["patient_name"]:
            errors["patient_name"] = _("Veuillez renseigner le nom du patient.")

        if not cleaned_values["patient_email"]:
            errors["patient_email"] = _("Veuillez renseigner l'adresse e-mail du patient.")
        elif not single_email_re.match(cleaned_values["patient_email"]):
            errors["patient_email"] = _("Veuillez renseigner une adresse e-mail valide pour le patient.")

        try:
            cleaned_values["requested_session_count"] = int(requested_session_count)
        except (TypeError, ValueError):
            cleaned_values["requested_session_count"] = 0

        if cleaned_values["requested_session_count"] <= 0:
            errors["requested_session_count"] = _("Veuillez renseigner un nombre de seances strictement positif.")

        return cleaned_values, errors

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.user.has_group("evm.group_evm_kine"):
            invalid_state_vals = [vals for vals in vals_list if vals.get("state") not in (None, False, "draft")]
            if invalid_state_vals:
                raise AccessError(_("Le kinesitherapeute ne peut creer qu'un dossier en brouillon."))
            restricted_vals = [vals for vals in vals_list if vals.get("authorized_session_count")]
            if restricted_vals:
                raise AccessError(_("Le kinesitherapeute ne peut pas definir les seances autorisees."))

        for vals in vals_list:
            vals["patient_name"] = (vals.get("patient_name") or "").strip() or False
            vals["patient_email"] = (vals.get("patient_email") or "").strip() or False
            vals["name"] = (vals.get("name") or vals.get("patient_name") or _("Nouveau dossier")).strip()
        records = super().create(vals_list)
        for record in records:
            record.message_post(body=_("Dossier cree."))
        return records

    def write(self, vals):
        if self.env.user.has_group("evm.group_evm_kine") and not self.env.context.get("evm_allow_case_workflow_write"):
            touched_fields = set(vals)
            if touched_fields & self._kine_protected_write_fields:
                raise AccessError(_("Le kinesitherapeute ne peut pas modifier ce champ directement."))
            if touched_fields & self._kine_draft_only_fields and any(record.state != "draft" for record in self):
                raise AccessError(_("Le dossier deja soumis ne peut plus etre modifie par le kinesitherapeute."))
        return super().write(vals)

    def action_submit_to_pending(self):
        for record in self:
            if record.state != "draft":
                raise ValidationError(_("Seul un dossier en brouillon peut etre soumis."))
            cleaned_values, errors = self.validate_submission_data(
                {
                    "patient_name": record.patient_name,
                    "patient_email": record.patient_email,
                    "requested_session_count": record.requested_session_count,
                }
            )
            if errors:
                raise ValidationError("\n".join(errors.values()))

            record.with_context(evm_allow_case_workflow_write=True).write(
                {
                    "name": cleaned_values["patient_name"],
                    "patient_name": cleaned_values["patient_name"],
                    "patient_email": cleaned_values["patient_email"],
                    "requested_session_count": cleaned_values["requested_session_count"],
                    "state": "pending",
                }
            )
            record.message_post(body=_("Demande initiale soumise par le kinesitherapeute."))
        return True
