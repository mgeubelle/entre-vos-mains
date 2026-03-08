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
            any("Dossier accepte" in body for body in case.message_ids.mapped("body")),
            "L'acceptation doit etre tracee dans le chatter.",
        )

    def test_accept_action_requires_explicit_authorized_session_count(self):
        case = self._create_pending_case(requested=12)

        with self.assertRaisesRegex(ValidationError, "seances autorisees"):
            case.with_user(self.fondation_user).action_accept()

        with self.assertRaisesRegex(ValidationError, "ne peut pas depasser"):
            case.with_user(self.fondation_user).write({"authorized_session_count": 13})

    def test_annual_cap_blocks_acceptance_and_exposes_remaining_capacity(self):
        self.config_parameters.set_param("evm.annual_session_cap", "15")
        accepted_case = self._create_pending_case(requested=12, suffix="Accepted")
        blocked_case = self._create_pending_case(requested=8, suffix="Blocked")

        self._accept_case(accepted_case, authorized=10)
        blocked_case.with_user(self.fondation_user).write({"authorized_session_count": 6})

        self.assertEqual(blocked_case.annual_session_cap, 15)
        self.assertEqual(blocked_case.annual_session_cap_used, 10)
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
            any("Dossier refuse" in body for body in case.message_ids.mapped("body")),
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
