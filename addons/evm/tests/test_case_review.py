from unittest.mock import patch

from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged("post_install", "-at_install")
class TestEvmCaseReview(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kine_user = new_test_user(cls.env, login="kine_review", groups="evm.group_evm_kine")
        cls.fondation_user = new_test_user(cls.env, login="fondation_review", groups="evm.group_evm_fondation")
        cls.case_model = cls.env["evm.case"]
        cls.config_parameters = cls.env["ir.config_parameter"].sudo()

    def setUp(self):
        super().setUp()
        self.config_parameters.set_param("evm.annual_session_cap", "0")

    def _create_pending_case(self, requested=12, suffix="A"):
        case = self.case_model.create(
            {
                "kine_user_id": self.kine_user.id,
                "patient_name": f"Patient Review {suffix}",
                "patient_email": f"patient.review.{suffix.lower()}@example.com",
                "requested_session_count": requested,
            }
        )
        case.action_submit_to_pending()
        return case

    def _accept_case(self, case, authorized):
        case.with_user(self.fondation_user).write({"authorized_session_count": authorized})
        case.with_user(self.fondation_user).action_accept()
        return case

    def test_accept_action_updates_case_and_history(self):
        case = self._create_pending_case(requested=12)

        self._accept_case(case, authorized=10)

        self.assertEqual(case.state, "accepted")
        self.assertEqual(case.authorized_session_count, 10)
        self.assertEqual(case.foundation_decision_user_id, self.fondation_user)
        self.assertEqual(case.foundation_decision_date, fields.Date.context_today(case))
        self.assertTrue(
            any("Systeme:" in (body or "") and "Dossier accepte" in body for body in case.message_ids.mapped("body")),
            "L'acceptation doit etre tracee dans le chatter.",
        )

    def test_decision_sensitive_details_stay_in_internal_notes(self):
        today = fields.Date.context_today(self.case_model)
        existing_usage = self.case_model._get_annual_session_cap_usage_by_year({today.year}).get(today.year, 0)
        self.config_parameters.set_param("evm.annual_session_cap", str(existing_usage + 20))
        case = self._create_pending_case(requested=12, suffix="DecisionNote")
        case.with_user(self.fondation_user).write(
            {
                "authorized_session_count": 8,
                "foundation_decision_note": "Reserve fondation uniquement.",
            }
        )

        case.with_user(self.fondation_user).action_accept()

        public_messages = case.message_ids.filtered(lambda message: not message.subtype_id or not message.subtype_id.internal)
        internal_messages = case.message_ids.filtered(lambda message: message.subtype_id and message.subtype_id.internal)

        self.assertTrue(any("Dossier accepte" in (body or "") for body in case.message_ids.mapped("body")))
        self.assertFalse(any("Plafond annuel restant" in (body or "") for body in public_messages.mapped("body")))
        self.assertFalse(any("Reserve fondation uniquement." in (body or "") for body in public_messages.mapped("body")))
        self.assertTrue(any("Plafond annuel restant" in (body or "") for body in internal_messages.mapped("body")))
        self.assertTrue(any("Reserve fondation uniquement." in (body or "") for body in internal_messages.mapped("body")))

    def test_accept_action_creates_patient_portal_access_and_prepares_invitation(self):
        case = self._create_pending_case(requested=12, suffix="Invite")

        with patch(
            "odoo.addons.portal.wizard.portal_wizard.PortalWizardUser._send_email",
            autospec=True,
            return_value=True,
        ) as mocked_send_email:
            self._accept_case(case, authorized=10)

        self.assertEqual(case.state, "accepted")
        self.assertTrue(case.patient_partner_id)
        self.assertTrue(case.patient_user_id)
        self.assertEqual(case.patient_user_id.partner_id, case.patient_partner_id)
        self.assertEqual(case.patient_partner_id.email, "patient.review.invite@example.com")
        self.assertTrue(case.patient_user_id.active)
        self.assertTrue(case.patient_user_id.has_group("evm.group_evm_patient"))
        self.assertEqual(case.patient_partner_id.signup_type, "signup")
        self.assertEqual(mocked_send_email.call_count, 1)
        self.assertTrue(
            any("Acces portail patient" in body for body in case.message_ids.mapped("body")),
            "L'activation patient doit etre tracee dans le chatter.",
        )

    def test_accept_action_reactivates_existing_patient_portal_user(self):
        archived_user = new_test_user(
            self.env,
            login="patient.review.archived@example.com",
            groups="evm.group_evm_patient",
            name="Patient Archive",
        )
        archived_user.partner_id.write({"email": "patient.review.archived@example.com"})
        archived_user.write({"active": False})
        case = self._create_pending_case(requested=12, suffix="Archived")

        with patch(
            "odoo.addons.portal.wizard.portal_wizard.PortalWizardUser._send_email",
            autospec=True,
            return_value=True,
        ) as mocked_send_email:
            self._accept_case(case, authorized=8)

        self.assertEqual(case.patient_user_id, archived_user)
        self.assertEqual(case.patient_partner_id, archived_user.partner_id)
        self.assertTrue(archived_user.active)
        self.assertTrue(archived_user.has_group("evm.group_evm_patient"))
        self.assertEqual(mocked_send_email.call_count, 1)

    def test_accept_action_rejects_patient_email_already_used_by_kine_account(self):
        kine_conflict = new_test_user(
            self.env,
            login="patient.review.rolemix@example.com",
            groups="evm.group_evm_kine",
            name="Kine Conflict",
        )
        kine_conflict.partner_id.write({"email": "patient.review.rolemix@example.com"})
        case = self._create_pending_case(requested=12, suffix="RoleMix")

        with self.assertRaisesRegex(ValidationError, "compte kinesitherapeute"):
            self._accept_case(case, authorized=7)

        self.assertEqual(case.state, "pending")
        self.assertFalse(case.patient_user_id)
        self.assertFalse(case.patient_partner_id)

    def test_accept_action_rejects_existing_partner_with_mismatched_login(self):
        mismatched_user = new_test_user(
            self.env,
            login="existing.patient.account@example.com",
            groups="evm.group_evm_patient",
            name="Patient Mismatch",
        )
        mismatched_user.partner_id.write({"email": "patient.review.partnermismatch@example.com"})
        case = self._create_pending_case(requested=12, suffix="PartnerMismatch")

        with self.assertRaisesRegex(ValidationError, "identifiant ne correspond pas"):
            self._accept_case(case, authorized=9)

        self.assertEqual(case.state, "pending")
        self.assertFalse(case.patient_user_id)
        self.assertFalse(case.patient_partner_id)

    def test_accept_action_requires_explicit_authorized_session_count(self):
        case = self._create_pending_case(requested=12)

        with self.assertRaisesRegex(ValidationError, "seances autorisees"):
            case.with_user(self.fondation_user).action_accept()

        with self.assertRaisesRegex(ValidationError, "ne peut pas depasser"):
            case.with_user(self.fondation_user).write({"authorized_session_count": 13})

    def test_annual_cap_blocks_acceptance_and_exposes_remaining_capacity(self):
        today = fields.Date.context_today(self.case_model)
        existing_usage = self.case_model._get_annual_session_cap_usage_by_year({today.year}).get(today.year, 0)
        self.config_parameters.set_param("evm.annual_session_cap", str(existing_usage + 15))
        accepted_case = self._create_pending_case(requested=12, suffix="Accepted")
        blocked_case = self._create_pending_case(requested=8, suffix="Blocked")

        self._accept_case(accepted_case, authorized=10)
        blocked_case.with_user(self.fondation_user).write({"authorized_session_count": 6})

        self.assertEqual(blocked_case.annual_session_cap, existing_usage + 15)
        self.assertEqual(blocked_case.annual_session_cap_used, existing_usage + 10)
        self.assertEqual(blocked_case.annual_session_cap_remaining, 5)

        with self.assertRaisesRegex(ValidationError, "plafond annuel"):
            blocked_case.with_user(self.fondation_user).action_accept()

        self.assertEqual(blocked_case.state, "pending")

    def test_refuse_action_updates_case_and_history(self):
        case = self._create_pending_case(requested=12)
        case.with_user(self.fondation_user).write({"foundation_decision_note": "Pieces manquantes."})

        case.with_user(self.fondation_user).action_refuse()

        self.assertEqual(case.state, "refused")
        self.assertEqual(case.authorized_session_count, 0)
        self.assertEqual(case.foundation_decision_user_id, self.fondation_user)
        self.assertEqual(case.foundation_decision_date, fields.Date.context_today(case))
        self.assertEqual(case.foundation_decision_note, "Pieces manquantes.")
        self.assertTrue(
            any("Systeme:" in (body or "") and "Dossier refuse" in body for body in case.message_ids.mapped("body")),
            "Le refus doit etre trace dans le chatter.",
        )

    def test_decision_guards_block_direct_state_write_and_non_pending_decisions(self):
        case = self._create_pending_case(requested=12)

        with self.assertRaisesRegex(AccessError, "action metier"):
            case.with_user(self.fondation_user).write({"state": "accepted"})

        self._accept_case(case, authorized=10)

        with self.assertRaisesRegex(ValidationError, "soumis"):
            case.with_user(self.fondation_user).action_refuse()

    def test_review_flow_does_not_leave_hidden_edit_capabilities(self):
        case = self._create_pending_case(requested=12)

        with self.assertRaisesRegex(AccessError, "apres l'envoi"):
            case.with_user(self.fondation_user).write({"patient_name": "Patient Modifie"})

        case.with_user(self.fondation_user).write(
            {
                "authorized_session_count": 10,
                "foundation_decision_note": "Accord avec quota confirme.",
            }
        )
        case.with_user(self.fondation_user).action_accept()

        with self.assertRaisesRegex(AccessError, "apres traitement"):
            case.with_user(self.fondation_user).write({"authorized_session_count": 9})
        with self.assertRaisesRegex(AccessError, "apres traitement"):
            case.with_user(self.fondation_user).write({"foundation_decision_note": "Modification tardive"})

    def test_foundation_review_views_and_settings_expose_decision_controls(self):
        action = self.env.ref("evm.evm_case_action")
        search_arch = self.env.ref("evm.evm_case_view_search").arch_db
        form_arch = self.env.ref("evm.evm_case_view_form").arch_db
        settings_arch = self.env.ref("evm.evm_res_config_settings_view_form").arch_db

        self.assertIn("search_default_pending", action.context or "")
        self.assertIn('name="pending"', search_arch)
        self.assertIn('name="action_accept"', form_arch)
        self.assertIn('name="action_refuse"', form_arch)
        self.assertIn('name="patient_name" readonly="state != \'draft\'"', form_arch)
        self.assertIn('name="requested_session_count" readonly="state != \'draft\'"', form_arch)
        self.assertIn('name="annual_session_cap_remaining"', form_arch)
        self.assertIn("evm_annual_session_cap", self.env["res.config.settings"]._fields)
        self.assertIn('name="evm_annual_session_cap"', settings_arch)

    def test_case_form_exposes_payment_request_notebook_with_expected_columns(self):
        form_arch = self.env.ref("evm.evm_case_view_form").arch_db

        self.assertIn('<page string="Demandes de paiement">', form_arch)
        self.assertIn('name="payment_request_ids" readonly="1"', form_arch)
        self.assertIn('default_order="create_date desc"', form_arch)
        self.assertIn('field name="name" string="Reference"', form_arch)
        self.assertIn('field name="create_date" string="Date de creation"', form_arch)
        self.assertIn('field name="sessions_count" string="Nombre de seances"', form_arch)
        self.assertIn('field name="amount_total" string="Montant"', form_arch)
        self.assertIn('field name="state" string="Statut"', form_arch)
        self.assertNotIn('field name="patient_user_id" string="Patient"', form_arch)
