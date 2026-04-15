import logging
from datetime import datetime, time, timedelta

from odoo import Command, _, api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import email_normalize, plaintext2html, single_email_re

_logger = logging.getLogger(__name__)


class EvmCase(models.Model):
    _name = "evm.case"
    _inherit = ["mail.thread", "evm.notification.mixin"]
    _description = "EVM Case"
    _order = "create_date desc, id desc"
    _session_balance_counted_states = ("validated", "paid", "closed")
    _default_closure_delay_days = 90
    _closure_blocking_payment_request_states = ("draft", "submitted", "to_complete")

    name = fields.Char(required=True, string="Nom", tracking=True)
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
        tracking=True,
    )
    patient_partner_id = fields.Many2one(
        "res.partner",
        index=True,
        string="Contact patient",
        copy=False,
    )
    requested_session_count = fields.Integer(
        string="Seances demandees",
        tracking=True,
    )
    authorized_session_count = fields.Integer(
        string="Seances autorisees",
        tracking=True,
    )
    sessions_consumed = fields.Integer(
        string="Seances consommees",
        compute="_compute_session_balance",
        compute_sudo=True,
    )
    remaining_session_count = fields.Integer(
        string="Seances restantes",
        compute="_compute_session_balance",
        compute_sudo=True,
    )
    foundation_decision_note = fields.Text(
        string="Note de decision",
        tracking=True,
        copy=False,
    )
    foundation_decision_user_id = fields.Many2one(
        "res.users",
        string="Decision prise par",
        tracking=True,
        readonly=True,
        copy=False,
    )
    foundation_decision_date = fields.Date(
        string="Date de decision",
        tracking=True,
        readonly=True,
        copy=False,
    )
    annual_session_cap = fields.Integer(
        string="Plafond annuel",
        compute="_compute_annual_session_cap_metrics",
        compute_sudo=True,
    )
    annual_session_cap_used = fields.Integer(
        string="Seances deja autorisees",
        compute="_compute_annual_session_cap_metrics",
        compute_sudo=True,
    )
    annual_session_cap_remaining = fields.Integer(
        string="Seances restantes sur le plafond",
        compute="_compute_annual_session_cap_metrics",
        compute_sudo=True,
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
    payment_request_ids = fields.One2many(
        "evm.payment_request",
        "case_id",
        string="Demandes de paiement",
    )

    _workflow_only_write_fields = {"state", "patient_user_id", "patient_partner_id"}
    _kine_protected_write_fields = {"authorized_session_count", "kine_user_id", "patient_user_id", "patient_partner_id"}
    _kine_draft_only_fields = {"name", "patient_name", "patient_email", "requested_session_count"}
    _submitted_locked_write_fields = {"name", "kine_user_id", "patient_name", "patient_email", "requested_session_count"}
    _decision_locked_write_fields = {
        "authorized_session_count",
        "foundation_decision_note",
        "foundation_decision_user_id",
        "foundation_decision_date",
    }
    @api.depends("patient_user_id", "patient_user_id.partner_id.display_name", "patient_name", "name")
    def _compute_patient_display_name(self):
        for record in self:
            record.patient_display_name = record.patient_user_id.partner_id.display_name or record.patient_name or record.name

    @api.depends("state", "authorized_session_count", "foundation_decision_date")
    def _compute_annual_session_cap_metrics(self):
        today = fields.Date.context_today(self)
        years = {(record.foundation_decision_date or today).year for record in self}
        annual_cap = self._get_annual_session_cap()
        usage_by_year = self._get_annual_session_cap_usage_by_year(years)
        for record in self:
            current_year = (record.foundation_decision_date or today).year
            used = usage_by_year.get(current_year, 0)
            record.annual_session_cap = annual_cap
            record.annual_session_cap_used = used
            record.annual_session_cap_remaining = max(annual_cap - used, 0) if annual_cap else 0

    @api.depends("authorized_session_count", "payment_request_ids.state", "payment_request_ids.sessions_count")
    def _compute_session_balance(self):
        for record in self:
            authorized = max(record.authorized_session_count or 0, 0)
            consumed = sum(
                record.payment_request_ids.filtered(
                    lambda payment_request: payment_request.state in self._session_balance_counted_states
                ).mapped("sessions_count")
            )
            record.sessions_consumed = consumed
            record.remaining_session_count = max(authorized - consumed, 0)

    @api.constrains("requested_session_count", "authorized_session_count")
    def _check_session_counts_consistency(self):
        for record in self:
            if record.authorized_session_count < 0:
                raise ValidationError(_("Le nombre de seances autorisees ne peut pas etre negatif."))
            if record.authorized_session_count and record.authorized_session_count > record.requested_session_count:
                raise ValidationError(
                    _("Le nombre de seances autorisees ne peut pas depasser le nombre de seances demandees.")
                )

    def _get_annual_session_cap(self):
        raw_value = self.env["ir.config_parameter"].sudo().get_param("evm.annual_session_cap", default="0")
        try:
            return max(int(raw_value or 0), 0)
        except (TypeError, ValueError):
            return 0

    def _get_annual_session_cap_usage_by_year(self, years=None):
        accepted_cases = self.env["evm.case"].sudo().search([("state", "=", "accepted")])
        usage_by_year = {}
        for case in accepted_cases:
            decision_date = case.foundation_decision_date or fields.Date.to_date(case.create_date)
            if not decision_date:
                continue
            if years and decision_date.year not in years:
                continue
            usage_by_year.setdefault(decision_date.year, 0)
            usage_by_year[decision_date.year] += case.authorized_session_count or 0
        return usage_by_year

    def _ensure_foundation_can_decide(self):
        if not (
            self.env.user.has_group("evm.group_evm_fondation") or self.env.user.has_group("evm.group_evm_admin")
        ):
            raise AccessError(_("Seul un membre de la fondation peut prendre cette decision."))

    def _ensure_pending_cases(self):
        if any(record.state != "pending" for record in self):
            raise ValidationError(_("Seul un dossier soumis peut etre traite par la fondation."))

    @api.model
    def _sanitize_comment_body(self, body):
        sanitized_body = (body or "").strip()
        if not sanitized_body:
            raise ValidationError(_("Veuillez saisir un commentaire avant de l'envoyer."))
        return plaintext2html(sanitized_body)

    def _check_comment_post_access(self):
        self.ensure_one()
        if self.state == "closed":
            raise AccessError(_("Ce dossier est cloture et reste consultable en lecture."))
        user = self.env.user
        if user.has_group("evm.group_evm_admin") or user.has_group("evm.group_evm_fondation"):
            return
        if user.has_group("evm.group_evm_kine") and self.kine_user_id == user:
            return
        if user.has_group("evm.group_evm_patient") and self.patient_user_id == user:
            return
        raise AccessError(_("Vous ne pouvez pas ajouter de commentaire sur ce dossier."))

    def action_post_comment(self, body):
        self.ensure_one()
        self._check_comment_post_access()
        sanitized_body = self._sanitize_comment_body(body)
        self.sudo().message_post(
            author_id=self.env.user.partner_id.id,
            body=sanitized_body,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        return True

    @api.model
    def _format_system_message(self, body):
        return _("Systeme: %(body)s", body=body)

    def _post_system_message(self, body, subtype_xmlid="mail.mt_comment"):
        self.ensure_one()
        self.message_post(
            body=self._format_system_message(body),
            subtype_xmlid=subtype_xmlid,
        )
        return True

    def _build_decision_message(self, decision, annual_cap_remaining=None):
        self.ensure_one()
        if decision == "accepted":
            return _(
                "Dossier accepte par la fondation avec %(count)s seances autorisees.",
                count=self.authorized_session_count,
            )
        return _("Dossier refuse par la fondation.")

    def _build_decision_internal_message(self, decision, annual_cap_remaining=None):
        self.ensure_one()
        details = []
        if decision == "accepted" and annual_cap_remaining is not None:
            details.append(
                _(
                    "Plafond annuel restant: %(remaining)s seances.",
                    remaining=annual_cap_remaining,
                )
            )
        if self.foundation_decision_note:
            details.append(_("Note: %(note)s", note=self.foundation_decision_note))
        return " ".join(details)

    def _build_patient_portal_message(self):
        self.ensure_one()
        email = self.patient_partner_id.email or self.patient_email
        return _(
            "Acces portail patient active pour %(email)s. Invitation de connexion preparee via le portail Odoo standard.",
            email=email,
        )

    def _get_patient_portal_welcome_message(self):
        self.ensure_one()
        return _(
            "Votre dossier Entre Vos Mains a ete accepte. Utilisez ce lien securise pour activer ou retrouver votre acces portail."
        )

    def _get_patient_notification_partner(self, ensure_partner=False):
        self.ensure_one()
        partner = (self.patient_user_id.partner_id or self.patient_partner_id).exists()
        if partner or not ensure_partner:
            return partner
        try:
            return self._ensure_patient_partner().exists()
        except ValidationError:
            return self.env["res.partner"]

    def _get_patient_portal_case_url(self):
        self.ensure_one()
        if not self.patient_user_id:
            return False
        return f"{self.get_base_url()}/my/evm/cases/{self.id}"

    def _get_case_notification_payload(self, event_key):
        self.ensure_one()
        status_label = self._evm_get_selection_label("state", self.state)
        if event_key == "accepted":
            return {
                "subject": _("Entre Vos Mains - dossier accepte : %(case)s", case=self.name),
                "intro": _("Votre dossier %(case)s a ete accepte par la fondation.", case=self.name),
                "object_name": self.name,
                "status_label": status_label,
                "action_text": _("Acces portail actif. Vous pouvez consulter votre dossier et preparer vos demandes."),
                "url": self._get_patient_portal_case_url(),
            }
        if event_key == "refused":
            return {
                "subject": _("Entre Vos Mains - dossier refuse : %(case)s", case=self.name),
                "intro": _("Votre dossier %(case)s a ete refuse par la fondation.", case=self.name),
                "object_name": self.name,
                "status_label": status_label,
                "action_text": _("Aucune action supplementaire n'est attendue dans la plateforme."),
                "url": False,
            }
        return {}

    def _get_closure_delay_reference_date(self):
        self.ensure_one()
        return self.foundation_decision_date or fields.Date.to_date(self.create_date)

    def _get_closure_delay_days(self):
        raw_value = self.env["ir.config_parameter"].sudo().get_param(
            "evm.case_closure_delay_days",
            default=str(self._default_closure_delay_days),
        )
        try:
            return max(int(raw_value or 0), 0)
        except (TypeError, ValueError):
            return self._default_closure_delay_days

    def _get_closure_eligibility(self, today=None):
        self.ensure_one()
        today = today or fields.Date.context_today(self)
        closure_delay_days = self._get_closure_delay_days()
        delay_reference_date = self._get_closure_delay_reference_date()
        delay_cutoff_date = today - timedelta(days=closure_delay_days) if closure_delay_days else False
        active_payment_requests = self.payment_request_ids.filtered(
            lambda payment_request: payment_request.state in self._closure_blocking_payment_request_states
        )
        session_cap_reached = bool(self.authorized_session_count) and self.remaining_session_count <= 0
        delay_reached = bool(delay_cutoff_date and delay_reference_date and delay_reference_date <= delay_cutoff_date)

        if self.state != "accepted":
            return {
                "eligible": False,
                "reason_code": "state",
                "reason_message": _("Ce dossier n'est pas eligible a la cloture: seul un dossier accepte peut etre cloture."),
                "session_cap_reached": session_cap_reached,
                "delay_reached": delay_reached,
                "delay_reference_date": delay_reference_date,
                "active_payment_request_ids": active_payment_requests.ids,
            }
        if active_payment_requests:
            return {
                "eligible": False,
                "reason_code": "active_payment_request",
                "reason_message": _(
                    "Ce dossier n'est pas eligible a la cloture: une demande de paiement active doit d'abord etre finalisee."
                ),
                "session_cap_reached": session_cap_reached,
                "delay_reached": delay_reached,
                "delay_reference_date": delay_reference_date,
                "active_payment_request_ids": active_payment_requests.ids,
            }
        if session_cap_reached and delay_reached:
            reason_code = "session_cap_and_delay"
        elif session_cap_reached:
            reason_code = "session_cap"
        elif delay_reached:
            reason_code = "delay"
        else:
            return {
                "eligible": False,
                "reason_code": "conditions_not_met",
                "reason_message": _(
                    "Ce dossier n'est pas eligible a la cloture: ni le quota de seances ni le delai projet n'ont ete atteints."
                ),
                "session_cap_reached": session_cap_reached,
                "delay_reached": delay_reached,
                "delay_reference_date": delay_reference_date,
                "active_payment_request_ids": [],
            }
        return {
            "eligible": True,
            "reason_code": reason_code,
            "reason_message": False,
            "session_cap_reached": session_cap_reached,
            "delay_reached": delay_reached,
            "delay_reference_date": delay_reference_date,
            "active_payment_request_ids": [],
        }

    @api.model
    def _get_closure_reason_label(self, reason_code):
        mapping = {
            "session_cap": _("quota de seances atteint"),
            "delay": _("delai projet atteint"),
            "session_cap_and_delay": _("quota de seances et delai projet atteints"),
        }
        return mapping.get(reason_code, _("regles metier atteintes"))

    def _build_closure_message(self, eligibility, close_origin="manual"):
        self.ensure_one()
        origin_label = (
            _("par la fondation")
            if close_origin == "manual"
            else _("automatiquement par la plateforme")
        )
        return _(
            "Dossier cloture %(origin)s. Motif: %(reason)s. Une nouvelle demande doit etre introduite pour toute nouvelle prise en charge.",
            origin=origin_label,
            reason=self._get_closure_reason_label(eligibility.get("reason_code")),
        )

    @api.model
    def _get_auto_close_candidate_domain(self, today=None):
        today = today or fields.Date.context_today(self)
        counted_payment_request_domain = [("payment_request_ids.state", "in", list(self._session_balance_counted_states))]
        closure_delay_days = self._get_closure_delay_days()
        if not closure_delay_days:
            return [("state", "=", "accepted")] + counted_payment_request_domain

        delay_cutoff_date = today - timedelta(days=closure_delay_days)
        create_date_cutoff = fields.Datetime.to_string(datetime.combine(delay_cutoff_date + timedelta(days=1), time.min))
        delay_domain = [
            "|",
            ("foundation_decision_date", "<=", delay_cutoff_date),
            "&",
            ("foundation_decision_date", "=", False),
            ("create_date", "<", create_date_cutoff),
        ]
        return [("state", "=", "accepted"), "|"] + delay_domain + counted_payment_request_domain

    def _close_case(self, close_origin="manual"):
        for record in self:
            eligibility = record._get_closure_eligibility()
            if not eligibility["eligible"]:
                raise ValidationError(eligibility["reason_message"])
            record.with_context(evm_allow_case_workflow_write=True).write({"state": "closed"})
            record._post_system_message(record._build_closure_message(eligibility, close_origin=close_origin))
        return True

    @api.model
    def _cron_auto_close_cases(self):
        closed_cases = self.browse()
        today = fields.Date.context_today(self)
        for case in self.search(self._get_auto_close_candidate_domain(today=today)):
            try:
                with self.env.cr.savepoint():
                    if case._get_closure_eligibility(today=today)["eligible"]:
                        case._close_case(close_origin="automatic")
                        closed_cases |= case
            except Exception:
                _logger.exception("Le cron de cloture automatique a echoue pour le dossier %s (%s).", case.id, case.name)
        return len(closed_cases)

    def _notify_patient_case_event(self, event_key, ensure_partner=False):
        for record in self:
            payload = record._get_case_notification_payload(event_key)
            if not payload:
                continue
            patient_partner = record._get_patient_notification_partner(ensure_partner=ensure_partner)
            record._evm_send_partner_notification(
                "evm.evm_case_notification_email_template",
                subject=payload["subject"],
                intro=payload["intro"],
                object_name=payload["object_name"],
                status_label=payload["status_label"],
                action_text=payload["action_text"],
                url=payload["url"],
                partner=patient_partner,
            )
        return True

    def _get_patient_normalized_email(self):
        self.ensure_one()
        return email_normalize(self.patient_email)

    def _get_patient_identity_values(self):
        self.ensure_one()
        partner_values = {"name": self.patient_name}
        normalized_email = self._get_patient_normalized_email()
        if normalized_email:
            partner_values["email"] = normalized_email
        return partner_values

    def _ensure_reusable_patient_user(self, user):
        self.ensure_one()
        if not user:
            return
        user = user.with_context(active_test=False).sudo()
        if user._is_internal():
            raise ValidationError(
                _("L'adresse e-mail du patient est deja rattachee a un utilisateur interne et ne peut pas etre reutilisee.")
            )
        if user.has_group("evm.group_evm_kine"):
            raise ValidationError(
                _("L'adresse e-mail du patient est deja rattachee a un compte kinesitherapeute et ne peut pas etre reutilisee.")
            )

    def _ensure_partner_matches_patient_identity(self, partner, normalized_email):
        self.ensure_one()
        linked_users = partner.with_context(active_test=False).sudo().user_ids
        if len(linked_users) > 1:
            raise ValidationError(
                _("Le contact patient est rattache a plusieurs utilisateurs et ne peut pas etre active automatiquement.")
            )
        if not linked_users:
            return
        linked_user = linked_users[:1]
        self._ensure_reusable_patient_user(linked_user)
        if normalized_email and email_normalize(linked_user.login) != normalized_email:
            raise ValidationError(
                _(
                    "Le contact patient existant est rattache a un compte dont l'identifiant ne correspond pas a l'adresse e-mail du dossier."
                )
            )

    def _resolve_patient_portal_user(self, partner):
        self.ensure_one()
        normalized_email = self._get_patient_normalized_email()
        linked_users = partner.with_context(active_test=False).sudo().user_ids
        if normalized_email:
            linked_users = linked_users.filtered(lambda user: email_normalize(user.login) == normalized_email)
        if len(linked_users) > 1:
            raise ValidationError(
                _("Impossible d'identifier de maniere fiable le compte portail du patient pour ce dossier.")
            )
        if not linked_users:
            raise ValidationError(_("Aucun compte portail patient n'a ete cree ou retrouve pour ce dossier."))
        patient_user = linked_users[:1]
        self._ensure_reusable_patient_user(patient_user)
        return patient_user

    def _find_existing_patient_user(self):
        self.ensure_one()
        normalized_email = self._get_patient_normalized_email()
        if not normalized_email:
            return self.env["res.users"]
        return self.env["res.users"].with_context(active_test=False).sudo().search([("login", "=", normalized_email)], limit=1)

    def _get_existing_patient_portal_binding_values(self):
        self.ensure_one()
        existing_user = self._find_existing_patient_user()
        if not existing_user:
            return {}
        try:
            self._ensure_reusable_patient_user(existing_user)
        except ValidationError:
            return {}
        return {
            "patient_user_id": existing_user.id,
            "patient_partner_id": existing_user.partner_id.id,
        }

    def _ensure_patient_partner(self):
        self.ensure_one()
        partner_values = self._get_patient_identity_values()
        normalized_email = self._get_patient_normalized_email()
        partner = self.patient_partner_id.sudo()
        existing_user = self._find_existing_patient_user()
        if existing_user:
            self._ensure_reusable_patient_user(existing_user)
            partner = existing_user.partner_id
        elif not partner and normalized_email:
            partner = self.env["res.partner"].sudo().search([("email", "=", normalized_email)], limit=1)
        if partner:
            self._ensure_partner_matches_patient_identity(partner, normalized_email)
        if not partner:
            partner = self.env["res.partner"].sudo().create(partner_values)
        else:
            partner.sudo().write(partner_values)
        self.with_context(evm_allow_case_workflow_write=True).write({"patient_partner_id": partner.id})
        return partner

    def _activate_patient_portal_access(self):
        patient_group = self.env.ref("evm.group_evm_patient")
        for record in self:
            partner = record._ensure_patient_partner()
            wizard = (
                self.env["portal.wizard"]
                .with_context(active_test=False)
                .sudo()
                .create(
                    {
                        "partner_ids": [Command.link(partner.id)],
                        "welcome_message": record._get_patient_portal_welcome_message(),
                    }
                )
            )
            wizard_user = wizard.user_ids.filtered(lambda user: user.partner_id == partner)[:1]
            if wizard_user.is_internal:
                raise ValidationError(
                    _("Le contact patient est deja rattache a un utilisateur interne et ne peut pas recevoir un acces portail.")
                )
            if wizard_user.is_portal:
                wizard_user.action_invite_again()
            else:
                wizard_user.action_grant_access()

            patient_user = record._resolve_patient_portal_user(partner)
            patient_user.write({"group_ids": [Command.link(patient_group.id)]})
            record.with_context(evm_allow_case_workflow_write=True).write(
                {
                    "patient_partner_id": partner.id,
                    "patient_user_id": patient_user.id,
                }
            )
            record._post_system_message(record._build_patient_portal_message())
        return True

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
            record._post_system_message(_("Dossier cree."))
        return records

    def write(self, vals):
        allow_workflow_write = self.env.context.get("evm_allow_case_workflow_write")
        touched_fields = set(vals)
        if touched_fields & self._workflow_only_write_fields and not allow_workflow_write:
            raise AccessError(_("Le statut et les acces patient du dossier ne peuvent etre modifies que via une action metier."))
        if not allow_workflow_write:
            if touched_fields & self._submitted_locked_write_fields and any(record.state != "draft" for record in self):
                raise AccessError(_("Les informations soumises du dossier ne peuvent plus etre modifiees apres l'envoi."))
            if touched_fields & self._decision_locked_write_fields and any(record.state != "pending" for record in self):
                raise AccessError(_("La decision de la fondation ne peut plus etre modifiee apres traitement du dossier."))
        if self.env.user.has_group("evm.group_evm_kine") and not allow_workflow_write:
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
                    **record._get_existing_patient_portal_binding_values(),
                }
            )
            record._post_system_message(_("Demande initiale soumise par le kinesitherapeute."))
        return True

    def action_accept(self):
        self._ensure_foundation_can_decide()
        self._ensure_pending_cases()

        today = fields.Date.context_today(self)
        annual_cap = self._get_annual_session_cap()
        annual_cap_used = self._get_annual_session_cap_usage_by_year({today.year}).get(today.year, 0)

        with self.env.cr.savepoint():
            for record in self:
                if record.authorized_session_count <= 0:
                    raise ValidationError(_("Veuillez definir explicitement les seances autorisees avant l'acceptation."))
                if annual_cap and annual_cap_used + record.authorized_session_count > annual_cap:
                    remaining = max(annual_cap - annual_cap_used, 0)
                    raise ValidationError(
                        _(
                            "L'acceptation depasse le plafond annuel configure. "
                            "Il reste %(remaining)s seances disponibles sur %(cap)s.",
                            remaining=remaining,
                            cap=annual_cap,
                        )
                    )

                remaining_after_accept = (
                    max(annual_cap - annual_cap_used - record.authorized_session_count, 0) if annual_cap else None
                )
                record._activate_patient_portal_access()
                record.with_context(evm_allow_case_workflow_write=True).write(
                    {
                        "state": "accepted",
                        "foundation_decision_user_id": self.env.user.id,
                        "foundation_decision_date": today,
                    }
                )
                record._post_system_message(record._build_decision_message("accepted", remaining_after_accept))
                internal_message = record._build_decision_internal_message("accepted", remaining_after_accept)
                if internal_message:
                    record._post_system_message(internal_message, subtype_xmlid="mail.mt_note")
                record._notify_patient_case_event("accepted")
                annual_cap_used += record.authorized_session_count
        return True

    def action_refuse(self):
        self._ensure_foundation_can_decide()
        self._ensure_pending_cases()

        today = fields.Date.context_today(self)
        for record in self:
            record.with_context(evm_allow_case_workflow_write=True).write(
                {
                    "state": "refused",
                    "authorized_session_count": 0,
                    "foundation_decision_user_id": self.env.user.id,
                    "foundation_decision_date": today,
                }
            )
            record._post_system_message(record._build_decision_message("refused"))
            internal_message = record._build_decision_internal_message("refused")
            if internal_message:
                record._post_system_message(internal_message, subtype_xmlid="mail.mt_note")
            record._notify_patient_case_event("refused", ensure_partner=True)
        return True

    def action_close(self):
        self._ensure_foundation_can_decide()
        return self._close_case(close_origin="manual")
