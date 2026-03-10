from decimal import Decimal, InvalidOperation
from os.path import basename, splitext

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.mimetypes import guess_mimetype


class EvmPaymentRequest(models.Model):
    _name = "evm.payment_request"
    _inherit = ["mail.thread"]
    _description = "EVM Payment Request"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, string="Nom", tracking=True)
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
    state = fields.Selection(
        selection=[
            ("draft", "Brouillon"),
            ("submitted", "Soumise"),
            ("to_complete", "A completer"),
            ("validated", "Validee"),
            ("paid", "Payee"),
            ("refused", "Refusee"),
            ("closed", "Cloturee"),
        ],
        default="draft",
        required=True,
        string="Statut",
        tracking=True,
    )
    sessions_count = fields.Integer(
        required=True,
        string="Nombre de seances",
        tracking=True,
    )
    amount_total = fields.Monetary(
        string="Montant total a payer",
        currency_field="currency_id",
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id.id,
        required=True,
        string="Devise",
    )

    _workflow_only_write_fields = {"state"}
    _immutable_write_fields = {"case_id", "patient_user_id", "currency_id"}
    _patient_editable_fields = {"name", "sessions_count", "amount_total"}
    _portal_allowed_attachment_extensions = {
        "pdf": "application/pdf",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
    }
    _portal_max_attachment_size = 10 * 1024 * 1024
    _portal_uploadable_states = {"draft"}

    @api.constrains("sessions_count", "amount_total")
    def _check_patient_payload(self):
        for record in self:
            if record.sessions_count <= 0:
                raise ValidationError(_("Veuillez renseigner un nombre de seances strictement positif."))
            if record.amount_total is not False and record.amount_total < 0:
                raise ValidationError(_("Veuillez renseigner un montant positif ou nul."))

    @api.model
    def validate_portal_creation_data(self, values):
        cleaned_values = {}
        errors = {}

        try:
            cleaned_values["sessions_count"] = int(values.get("sessions_count"))
        except (TypeError, ValueError):
            cleaned_values["sessions_count"] = 0
        if cleaned_values["sessions_count"] <= 0:
            errors["sessions_count"] = _("Veuillez renseigner un nombre de seances strictement positif.")

        raw_amount = (values.get("amount_total") or "").strip()
        if not raw_amount:
            cleaned_values["amount_total"] = False
            return cleaned_values, errors

        normalized_amount = raw_amount.replace(",", ".")
        try:
            cleaned_values["amount_total"] = float(Decimal(normalized_amount))
        except (InvalidOperation, TypeError, ValueError):
            cleaned_values["amount_total"] = False
            errors["amount_total"] = _("Veuillez renseigner un montant positif ou nul.")
            return cleaned_values, errors

        if cleaned_values["amount_total"] < 0:
            errors["amount_total"] = _("Veuillez renseigner un montant positif ou nul.")
        return cleaned_values, errors

    @api.model
    def _build_default_name(self, case):
        if not case:
            return _("Nouvelle demande de paiement")
        return _("Demande de paiement - %(case)s", case=case.name)

    @api.model
    def _sanitize_name(self, name, case=None):
        sanitized_name = (name or self._build_default_name(case)).strip()
        if not sanitized_name:
            raise ValidationError(_("Le nom de la demande ne peut pas etre vide."))
        return sanitized_name

    def _is_portal_patient_context(self):
        return not self.env.su and self.env.user.has_group("evm.group_evm_patient")

    def _check_portal_attachment_upload_access(self):
        self.ensure_one()
        if not self._is_portal_patient_context():
            raise AccessError(_("Seul le portail patient peut deposer des justificatifs sur une demande."))
        if self.patient_user_id != self.env.user or self.case_id.state != "accepted":
            raise AccessError(_("Cette demande de paiement n'est pas accessible depuis votre portail."))
        if self.state not in self._portal_uploadable_states:
            raise AccessError(_("Seule une demande en brouillon peut recevoir des justificatifs."))

    @api.model
    def _normalize_portal_attachment_upload(self, uploaded_file):
        filename = basename((getattr(uploaded_file, "filename", "") or "").strip())
        if not filename:
            return None

        extension = splitext(filename)[1].lower().lstrip(".")
        expected_mimetype = self._portal_allowed_attachment_extensions.get(extension)
        if not expected_mimetype:
            raise ValidationError(_("Formats autorises : PDF, JPG, JPEG, PNG."))

        content = uploaded_file.read() or b""
        if len(content) > self._portal_max_attachment_size:
            raise ValidationError(_("Chaque fichier doit peser au maximum 10 Mo."))
        if not content:
            raise ValidationError(_("Les fichiers vides ne sont pas autorises."))

        detected_mimetype = guess_mimetype(content, default="application/octet-stream")
        if detected_mimetype != expected_mimetype:
            raise ValidationError(_("Le contenu du fichier ne correspond pas a son format autorise."))

        return {
            "name": filename,
            "raw": content,
            "mimetype": detected_mimetype,
            "type": "binary",
        }

    def portal_upload_attachments(self, uploaded_files):
        self.ensure_one()
        self._check_portal_attachment_upload_access()

        attachment_values = []
        for uploaded_file in uploaded_files or []:
            normalized_values = self._normalize_portal_attachment_upload(uploaded_file)
            if normalized_values:
                attachment_values.append(normalized_values)

        if not attachment_values:
            raise ValidationError(_("Veuillez selectionner au moins un fichier."))

        return self.env["ir.attachment"].sudo().create(
            [
                {
                    **values,
                    "res_model": self._name,
                    "res_id": self.id,
                    "evm_patient_visible": True,
                }
                for values in attachment_values
            ]
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            case = self.env["evm.case"].search([("id", "=", vals.get("case_id"))], limit=1)
            if self._is_portal_patient_context():
                if vals.get("state") not in (None, False, "draft"):
                    raise AccessError(_("Le patient ne peut creer qu'une demande en brouillon."))
                if not case:
                    raise AccessError(_("Le dossier demande n'est pas accessible depuis votre portail."))
                if case.state != "accepted":
                    raise AccessError(_("Le dossier doit etre accepte avant de creer une demande de paiement."))

            vals["name"] = self._sanitize_name(vals.get("name"), case=case)
            vals["state"] = vals.get("state") or "draft"

        records = super().create(vals_list)
        for record in records:
            state_label = dict(record._fields["state"].selection).get(record.state, record.state)
            record.message_post(body=_("Demande de paiement creee avec le statut %(state)s.", state=state_label))
        return records

    def write(self, vals):
        if set(vals) & self._workflow_only_write_fields and not self.env.context.get("evm_allow_payment_request_workflow_write"):
            raise AccessError(_("Le statut de la demande ne peut etre modifie que via une action metier."))
        if set(vals) & self._immutable_write_fields:
            raise AccessError(_("Le dossier et les metadonnees systeme de la demande ne peuvent pas etre modifies."))
        if "name" in vals:
            vals["name"] = self._sanitize_name(vals["name"])
        if self._is_portal_patient_context():
            if set(vals) - self._patient_editable_fields:
                raise AccessError(_("Le patient ne peut modifier que les informations de saisie de sa demande."))
            if any(record.state != "draft" for record in self):
                raise AccessError(_("Seule une demande en brouillon peut etre modifiee depuis le portail patient."))
        return super().write(vals)

    def unlink(self):
        if self._is_portal_patient_context() and any(record.state != "draft" for record in self):
            raise AccessError(_("Seule une demande en brouillon peut etre supprimee depuis le portail patient."))
        return super().unlink()
