from decimal import Decimal, InvalidOperation
from math import isfinite
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
    case_authorized_session_count = fields.Integer(
        related="case_id.authorized_session_count",
        string="Seances autorisees dossier",
        readonly=True,
    )
    case_sessions_consumed = fields.Integer(
        related="case_id.sessions_consumed",
        string="Seances consommees dossier",
        readonly=True,
    )
    case_remaining_session_count = fields.Integer(
        related="case_id.remaining_session_count",
        string="Seances restantes dossier",
        readonly=True,
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
    attachment_ids = fields.Many2many(
        "ir.attachment",
        compute="_compute_attachment_data",
        string="Justificatifs",
        compute_sudo=True,
    )
    attachment_count = fields.Integer(
        compute="_compute_attachment_data",
        string="Nombre de justificatifs",
        compute_sudo=True,
    )
    submitted_on = fields.Datetime(
        string="Date de soumission",
        tracking=True,
        readonly=True,
        copy=False,
    )
    completion_request_reason = fields.Text(
        string="Motif de retour",
        tracking=True,
        copy=False,
    )
    refusal_reason = fields.Text(
        string="Motif du refus",
        tracking=True,
        copy=False,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id.id,
        required=True,
        string="Devise",
    )

    _workflow_only_write_fields = {"state", "submitted_on"}
    _immutable_write_fields = {"case_id", "patient_user_id", "currency_id"}
    _patient_editable_fields = {"name", "sessions_count", "amount_total"}
    _foundation_validation_editable_fields = {"sessions_count", "amount_total"}
    _final_state_locked_write_fields = {"name", "sessions_count", "amount_total"}
    _session_balance_counted_states = {"validated", "paid", "closed"}
    _portal_allowed_attachment_extensions = {
        "pdf": "application/pdf",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
    }
    _portal_max_attachment_size = 10 * 1024 * 1024
    _portal_resumable_states = {"draft", "to_complete"}
    _portal_uploadable_states = _portal_resumable_states
    _portal_submittable_states = _portal_resumable_states

    def _is_internal_manual_management_context(self):
        return (
            not self.env.su
            and not self._is_portal_patient_context()
            and (self.env.user.has_group("evm.group_evm_fondation") or self.env.user.has_group("evm.group_evm_admin"))
        )

    def _ensure_foundation_can_process(self):
        if not (
            self.env.user.has_group("evm.group_evm_fondation") or self.env.user.has_group("evm.group_evm_admin")
        ):
            raise AccessError(_("Seul un membre de la fondation peut traiter cette demande."))

    def _ensure_submitted_requests(self, error_message=None):
        if any(record.state != "submitted" for record in self):
            raise ValidationError(error_message or _("Seule une demande soumise peut etre traitee par cette action."))

    @api.model
    def _sanitize_completion_request_reason(self, reason):
        sanitized_reason = (reason or "").strip()
        if not sanitized_reason:
            raise ValidationError(_("Veuillez renseigner un motif de retour exploitable pour le patient."))
        return sanitized_reason

    @api.model
    def _sanitize_refusal_reason(self, reason):
        sanitized_reason = (reason or "").strip()
        if not sanitized_reason:
            raise ValidationError(_("Veuillez renseigner un motif de refus exploitable."))
        return sanitized_reason

    def _get_consumed_sessions_excluding_self(self):
        self.ensure_one()
        return sum(
            self.case_id.payment_request_ids.filtered(
                lambda payment_request: payment_request.id != self.id
                and payment_request.state in self._session_balance_counted_states
            ).mapped("sessions_count")
        )

    def _check_authorized_session_quota(self):
        tracked_records = self.filtered(
            lambda record: record.case_id and record.state in self._session_balance_counted_states
        )
        for record in tracked_records:
            if record.case_id.state != "accepted":
                raise ValidationError(
                    _("Seule une demande rattachee a un dossier accepte peut consommer des seances.")
                )

            authorized = max(record.case_id.authorized_session_count or 0, 0)
            consumed_without_record = record._get_consumed_sessions_excluding_self()
            remaining = max(authorized - consumed_without_record, 0)
            if record.sessions_count > remaining:
                raise ValidationError(
                    _(
                        "La validation depasse les seances autorisees du dossier. "
                        "Il reste %(remaining)s seance(s) validables sur %(authorized)s.",
                        remaining=remaining,
                        authorized=authorized,
                    )
                )

    def _get_attachment_domain(self):
        self.ensure_one()
        return [
            ("res_model", "=", self._name),
            ("res_id", "=", self.id),
            ("res_field", "=", False),
            ("type", "=", "binary"),
        ]

    def _compute_attachment_data(self):
        attachment_model = self.env["ir.attachment"]
        attachments_by_request = {}
        if self.ids:
            attachments = attachment_model.sudo().search(
                [
                    ("res_model", "=", self._name),
                    ("res_id", "in", self.ids),
                    ("res_field", "=", False),
                    ("type", "=", "binary"),
                ],
                order="create_date desc, id desc",
            )
            for attachment in attachments:
                attachments_by_request.setdefault(attachment.res_id, attachment_model.browse())
                attachments_by_request[attachment.res_id] |= attachment

        for record in self:
            record_attachments = attachments_by_request.get(record.id, attachment_model.browse())
            record.attachment_ids = record_attachments
            record.attachment_count = len(record_attachments)

    @api.constrains("sessions_count", "amount_total")
    def _check_patient_payload(self):
        for record in self:
            if record.sessions_count <= 0:
                raise ValidationError(_("Veuillez renseigner un nombre de seances strictement positif."))
            if record.amount_total is not False and record.amount_total < 0:
                raise ValidationError(_("Veuillez renseigner un montant positif ou nul."))

    @api.constrains("state", "sessions_count", "case_id")
    def _check_validated_session_quota(self):
        self._check_authorized_session_quota()

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
            decimal_amount = Decimal(normalized_amount)
        except (InvalidOperation, TypeError, ValueError):
            cleaned_values["amount_total"] = False
            errors["amount_total"] = _("Veuillez renseigner un montant positif ou nul.")
            return cleaned_values, errors

        if not decimal_amount.is_finite():
            cleaned_values["amount_total"] = False
            errors["amount_total"] = _("Veuillez renseigner un montant positif ou nul.")
            return cleaned_values, errors

        cleaned_values["amount_total"] = float(decimal_amount)
        if not isfinite(cleaned_values["amount_total"]):
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
            raise AccessError(_("Seule une demande en brouillon ou a completer peut recevoir des justificatifs."))

    def _check_portal_submission_access(self):
        self.ensure_one()
        if not self._is_portal_patient_context():
            raise AccessError(_("Seul le portail patient peut soumettre une demande de paiement."))
        if self.patient_user_id != self.env.user or self.case_id.state != "accepted":
            raise AccessError(_("Cette demande de paiement n'est pas accessible depuis votre portail."))

    def _get_submission_attachment_domain(self):
        return [*self._get_attachment_domain(), ("evm_patient_visible", "=", True)]

    def _get_submission_attachment_count(self):
        self.ensure_one()
        return self.env["ir.attachment"].sudo().search_count(self._get_submission_attachment_domain())

    def get_submission_errors(self):
        self.ensure_one()
        errors = []

        if self.state not in self._portal_submittable_states:
            errors.append(_("Seule une demande en brouillon ou a completer peut etre soumise."))
        if self.sessions_count <= 0:
            errors.append(_("Veuillez renseigner un nombre de seances strictement positif."))
        if not self._get_submission_attachment_count():
            errors.append(_("Ajoutez au moins un justificatif avant de soumettre la demande."))
        return errors

    def is_complete_for_submission(self):
        self.ensure_one()
        return not self.get_submission_errors()

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

    def action_submit(self):
        for record in self:
            record._check_portal_submission_access()
            errors = record.get_submission_errors()
            if errors:
                raise ValidationError("\n".join(errors))

        submitted_on = fields.Datetime.now()
        for record in self:
            previous_state = record.state
            attachment_count = record._get_submission_attachment_count()
            values = {
                "state": "submitted",
                "submitted_on": submitted_on,
                "refusal_reason": False,
            }
            if previous_state == "to_complete":
                values["completion_request_reason"] = False
            record.with_context(evm_allow_payment_request_workflow_write=True).write(values)
            record.message_post(
                body=_(
                    "Demande de paiement completee puis soumise a nouveau par le patient avec %(count)s justificatif(s).",
                    count=attachment_count,
                )
                if previous_state == "to_complete"
                else _(
                    "Demande de paiement soumise par le patient avec %(count)s justificatif(s).",
                    count=attachment_count,
                ),
                subtype_xmlid="mail.mt_comment",
            )
        return True

    def action_return_to_complete(self, reason=None):
        self._ensure_foundation_can_process()
        self._ensure_submitted_requests(_("Seule une demande soumise peut etre retournee a completer."))

        for record in self:
            sanitized_reason = self._sanitize_completion_request_reason(
                reason if reason is not None else record.completion_request_reason
            )
            record.with_context(evm_allow_payment_request_workflow_write=True).write(
                {
                    "state": "to_complete",
                    "completion_request_reason": sanitized_reason,
                    "refusal_reason": False,
                }
            )
            record.message_post(
                body=_(
                    "Demande retournee au patient pour complementation. Motif: %(reason)s",
                    reason=sanitized_reason,
                ),
                subtype_xmlid="mail.mt_comment",
            )
        return True

    def action_refuse(self, reason=None):
        self._ensure_foundation_can_process()
        self._ensure_submitted_requests(_("Seule une demande soumise peut etre refusee."))

        for record in self:
            sanitized_reason = self._sanitize_refusal_reason(reason if reason is not None else record.refusal_reason)
            record.with_context(evm_allow_payment_request_workflow_write=True).write(
                {
                    "state": "refused",
                    "completion_request_reason": False,
                    "refusal_reason": sanitized_reason,
                }
            )
            record.message_post(
                body=_(
                    "Demande refusee par la fondation. Motif: %(reason)s",
                    reason=sanitized_reason,
                ),
                subtype_xmlid="mail.mt_comment",
            )
        return True

    def action_validate(self):
        self._ensure_foundation_can_process()
        self._ensure_submitted_requests(_("Seule une demande soumise peut etre validee."))

        with self.env.cr.savepoint():
            for record in self:
                record.with_context(evm_allow_payment_request_workflow_write=True).write(
                    {
                        "state": "validated",
                        "completion_request_reason": False,
                        "refusal_reason": False,
                    }
                )
                record.message_post(
                    body=_(
                        "Demande de paiement validee par la fondation avec %(count)s seance(s) retenue(s). "
                        "Solde restant sur le dossier: %(remaining)s.",
                        count=record.sessions_count,
                        remaining=record.case_remaining_session_count,
                    ),
                    subtype_xmlid="mail.mt_comment",
                )
        return True

    def action_open_attachments(self):
        self.ensure_one()
        return {
            "name": _("Justificatifs"),
            "type": "ir.actions.act_window",
            "res_model": "ir.attachment",
            "view_mode": "list,form",
            "domain": self._get_attachment_domain(),
            "context": {
                "create": False,
                "default_res_model": self._name,
                "default_res_id": self.id,
            },
        }

    @api.model_create_multi
    def create(self, vals_list):
        if self._is_internal_manual_management_context():
            raise AccessError(_("La creation manuelle d'une demande de paiement n'est pas autorisee."))
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
            record.message_post(
                body=_("Demande de paiement creee avec le statut %(state)s.", state=state_label),
                subtype_xmlid="mail.mt_comment",
            )
        return records

    def write(self, vals):
        allow_workflow_write = self.env.context.get("evm_allow_payment_request_workflow_write")
        if set(vals) & self._workflow_only_write_fields and not allow_workflow_write:
            raise AccessError(_("Le statut de la demande ne peut etre modifie que via une action metier."))
        if set(vals) & self._immutable_write_fields:
            raise AccessError(_("Le dossier et les metadonnees systeme de la demande ne peuvent pas etre modifies."))
        if (
            set(vals) & self._final_state_locked_write_fields
            and not allow_workflow_write
            and self._is_internal_manual_management_context()
            and any(record.state == "refused" for record in self)
        ):
            raise AccessError(_("Une demande refusee est cloturee et ne peut plus etre modifiee."))
        if (
            set(vals) & self._foundation_validation_editable_fields
            and not allow_workflow_write
            and self._is_internal_manual_management_context()
            and any(record.state != "submitted" for record in self)
        ):
            raise AccessError(_("Les donnees de validation ne peuvent etre ajustees que sur une demande soumise."))
        if "name" in vals:
            vals["name"] = self._sanitize_name(vals["name"])
        if "completion_request_reason" in vals and not allow_workflow_write:
            self._ensure_foundation_can_process()
            if any(record.state != "submitted" for record in self):
                raise AccessError(_("Le motif de retour ne peut etre prepare que sur une demande soumise."))
            vals["completion_request_reason"] = self._sanitize_completion_request_reason(vals["completion_request_reason"])
        if "refusal_reason" in vals and not allow_workflow_write:
            self._ensure_foundation_can_process()
            if any(record.state != "submitted" for record in self):
                raise AccessError(_("Le motif de refus ne peut etre prepare que sur une demande soumise."))
            vals["refusal_reason"] = self._sanitize_refusal_reason(vals["refusal_reason"])
        if self._is_portal_patient_context():
            if set(vals) - self._patient_editable_fields and not allow_workflow_write:
                raise AccessError(_("Le patient ne peut modifier que les informations de saisie de sa demande."))
            if any(record.state not in self._portal_resumable_states for record in self):
                raise AccessError(_("Seule une demande en brouillon ou a completer peut etre modifiee depuis le portail patient."))
        return super().write(vals)

    def unlink(self):
        if self._is_internal_manual_management_context():
            raise AccessError(_("La suppression manuelle d'une demande de paiement n'est pas autorisee."))
        if self._is_portal_patient_context() and any(record.state != "draft" for record in self):
            raise AccessError(_("Seule une demande en brouillon peut etre supprimee depuis le portail patient."))
        return super().unlink()
