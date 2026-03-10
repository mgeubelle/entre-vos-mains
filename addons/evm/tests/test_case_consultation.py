from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged("post_install", "-at_install")
class TestEvmCaseConsultation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kine_user = new_test_user(cls.env, login="kine_consult", groups="evm.group_evm_kine")
        cls.patient_user = new_test_user(cls.env, login="patient_consult", groups="evm.group_evm_patient")

    def test_case_model_exposes_consultation_fields(self):
        case_model = self.env["evm.case"]

        self.assertIn("state", case_model._fields)
        self.assertIn("requested_session_count", case_model._fields)
        self.assertIn("authorized_session_count", case_model._fields)
        self.assertIn("sessions_consumed", case_model._fields)
        self.assertIn("remaining_session_count", case_model._fields)
        self.assertIn("patient_display_name", case_model._fields)
        self.assertTrue(case_model._fields["state"].tracking)
        self.assertTrue(case_model._fields["requested_session_count"].tracking)
        self.assertTrue(case_model._fields["authorized_session_count"].tracking)

        case = case_model.create(
            {
                "name": "Dossier consultation",
                "kine_user_id": self.kine_user.id,
                "patient_user_id": self.patient_user.id,
                "requested_session_count": 12,
            }
        )

        self.assertEqual(case.state, "draft")
        self.assertEqual(case.requested_session_count, 12)
        self.assertEqual(case.sessions_consumed, 0)
        self.assertEqual(case.remaining_session_count, 0)
        self.assertEqual(case.patient_display_name, self.patient_user.partner_id.display_name)

    def test_case_consumed_and_remaining_sessions_only_follow_finalized_requests(self):
        case = self.env["evm.case"].create(
            {
                "name": "Dossier compteur seances",
                "kine_user_id": self.kine_user.id,
                "patient_user_id": self.patient_user.id,
                "state": "accepted",
                "requested_session_count": 14,
                "authorized_session_count": 12,
            }
        )

        self.env["evm.payment_request"].create(
            [
                {
                    "name": "Demande brouillon",
                    "case_id": case.id,
                    "sessions_count": 2,
                    "state": "draft",
                },
                {
                    "name": "Demande soumise",
                    "case_id": case.id,
                    "sessions_count": 3,
                    "state": "submitted",
                },
                {
                    "name": "Demande validee",
                    "case_id": case.id,
                    "sessions_count": 4,
                    "state": "validated",
                },
                {
                    "name": "Demande payee",
                    "case_id": case.id,
                    "sessions_count": 1,
                    "state": "paid",
                },
                {
                    "name": "Demande cloturee",
                    "case_id": case.id,
                    "sessions_count": 2,
                    "state": "closed",
                },
            ]
        )

        self.assertEqual(case.sessions_consumed, 7)
        self.assertEqual(case.remaining_session_count, 5)

    def test_case_remaining_sessions_cannot_be_driven_negative_by_validated_requests(self):
        case = self.env["evm.case"].create(
            {
                "name": "Dossier quota bloque",
                "kine_user_id": self.kine_user.id,
                "patient_user_id": self.patient_user.id,
                "state": "accepted",
                "requested_session_count": 6,
                "authorized_session_count": 3,
            }
        )

        self.env["evm.payment_request"].create(
            {
                "name": "Demande validee quota",
                "case_id": case.id,
                "sessions_count": 3,
                "state": "validated",
            }
        )
        self.assertEqual(case.sessions_consumed, 3)
        self.assertEqual(case.remaining_session_count, 0)

        with self.assertRaisesRegex(ValidationError, "depasse les seances autorisees"):
            self.env["evm.payment_request"].create(
                {
                    "name": "Demande bloquee par quota",
                    "case_id": case.id,
                    "sessions_count": 1,
                    "state": "validated",
                }
            )

    def test_case_creation_adds_a_visible_activity_entry(self):
        case = self.env["evm.case"].create(
            {
                "name": "Dossier historise",
                "kine_user_id": self.kine_user.id,
            }
        )

        self.assertTrue(case.message_ids, "La creation du dossier doit produire une trace d'activite.")
        self.assertIn("Dossier cree", case.message_ids[0].body)
        self.assertEqual(case.patient_display_name, "Dossier historise")

    def test_case_submission_moves_record_to_pending_and_tracks_initial_request(self):
        case = self.env["evm.case"].create(
            {
                "kine_user_id": self.kine_user.id,
                "patient_name": "Patient Creation",
                "patient_email": "patient.creation@example.com",
                "requested_session_count": 14,
            }
        )

        case.action_submit_to_pending()

        self.assertEqual(case.state, "pending")
        self.assertEqual(case.name, "Patient Creation")
        self.assertEqual(case.patient_display_name, "Patient Creation")
        self.assertEqual(case.requested_session_count, 14)
        bodies = case.message_ids.mapped("body")
        self.assertTrue(
            any("Demande initiale soumise" in body for body in bodies),
            "La soumission doit laisser une trace exploitable dans l'historique.",
        )

    def test_case_submission_rejects_missing_or_invalid_required_values(self):
        missing_values_case = self.env["evm.case"].create(
            {
                "kine_user_id": self.kine_user.id,
            }
        )
        invalid_sessions_case = self.env["evm.case"].create(
            {
                "kine_user_id": self.kine_user.id,
                "patient_name": "Patient Invalide",
                "patient_email": "patient.invalide@example.com",
                "requested_session_count": 0,
            }
        )

        with self.assertRaisesRegex(ValidationError, "nom du patient"):
            missing_values_case.action_submit_to_pending()
        with self.assertRaisesRegex(ValidationError, "adresse e-mail"):
            missing_values_case.write({"patient_name": "Patient Sans Email"})
            missing_values_case.action_submit_to_pending()
        with self.assertRaisesRegex(ValidationError, "nombre de seances"):
            invalid_sessions_case.action_submit_to_pending()

    def test_case_submission_rejects_non_draft_cases(self):
        case = self.env["evm.case"].create(
            {
                "kine_user_id": self.kine_user.id,
                "patient_name": "Patient Bloque",
                "patient_email": "patient.bloque@example.com",
                "requested_session_count": 8,
                "state": "pending",
            }
        )

        with self.assertRaisesRegex(ValidationError, "brouillon"):
            case.action_submit_to_pending()
