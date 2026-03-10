from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged("post_install", "-at_install")
class TestEvmPaymentRequest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kine_user = new_test_user(cls.env, login="kine_payment_request", groups="evm.group_evm_kine")
        cls.patient_user = new_test_user(cls.env, login="patient_payment_request", groups="evm.group_evm_patient")
        cls.other_patient_user = new_test_user(
            cls.env,
            login="patient_payment_request_other",
            groups="evm.group_evm_patient",
        )
        cls.accepted_case = cls.env["evm.case"].create(
            {
                "name": "Dossier accepte demande paiement",
                "kine_user_id": cls.kine_user.id,
                "patient_user_id": cls.patient_user.id,
                "state": "accepted",
                "requested_session_count": 18,
                "authorized_session_count": 12,
            }
        )
        cls.pending_case = cls.env["evm.case"].create(
            {
                "name": "Dossier pending demande paiement",
                "kine_user_id": cls.kine_user.id,
                "patient_user_id": cls.patient_user.id,
                "state": "pending",
                "requested_session_count": 18,
            }
        )

    def test_payment_request_model_exposes_creation_fields_and_initial_workflow_state(self):
        payment_request_model = self.env["evm.payment_request"]
        state_selection = dict(payment_request_model._fields["state"].selection)

        self.assertIn("sessions_count", payment_request_model._fields)
        self.assertIn("amount_total", payment_request_model._fields)
        self.assertEqual(
            list(state_selection),
            ["draft", "submitted", "to_complete", "validated", "paid", "refused", "closed"],
        )

        payment_request = payment_request_model.with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 3,
            }
        )

        self.assertEqual(payment_request.state, "draft")
        self.assertEqual(payment_request.case_id, self.accepted_case)
        self.assertEqual(payment_request.patient_user_id, self.patient_user)
        self.assertFalse(payment_request.amount_total)

    def test_payment_request_creation_rejects_invalid_patient_input(self):
        with self.assertRaisesRegex(ValidationError, "seances"):
            self.env["evm.payment_request"].with_user(self.patient_user).create(
                {
                    "case_id": self.accepted_case.id,
                    "sessions_count": 0,
                }
            )

        with self.assertRaisesRegex(ValidationError, "montant"):
            self.env["evm.payment_request"].with_user(self.patient_user).create(
                {
                    "case_id": self.accepted_case.id,
                    "sessions_count": 2,
                    "amount_total": -10,
                }
            )

    def test_payment_request_creation_requires_access_to_an_accepted_case(self):
        with self.assertRaises(AccessError):
            self.env["evm.payment_request"].with_user(self.patient_user).create(
                {
                    "case_id": self.pending_case.id,
                    "sessions_count": 2,
                }
            )

        with self.assertRaises(AccessError):
            self.env["evm.payment_request"].with_user(self.other_patient_user).create(
                {
                    "case_id": self.accepted_case.id,
                    "sessions_count": 2,
                }
            )

    def test_payment_request_rejects_blank_names_and_case_reassignment(self):
        with self.assertRaisesRegex(ValidationError, "nom"):
            self.env["evm.payment_request"].create(
                {
                    "name": "   ",
                    "case_id": self.accepted_case.id,
                    "sessions_count": 2,
                }
            )

        payment_request = self.env["evm.payment_request"].create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )

        with self.assertRaises(AccessError):
            payment_request.write({"case_id": self.pending_case.id})

    def test_patient_can_only_edit_draft_requests(self):
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )

        payment_request.with_user(self.patient_user).write(
            {
                "name": "Demande patient brouillon",
                "amount_total": 45,
            }
        )
        self.assertEqual(payment_request.name, "Demande patient brouillon")
        self.assertEqual(payment_request.amount_total, 45)

        payment_request.sudo().with_context(evm_allow_payment_request_workflow_write=True).write({"state": "submitted"})

        with self.assertRaises(AccessError):
            payment_request.with_user(self.patient_user).write({"name": "Tentative interdite"})
        with self.assertRaises(AccessError):
            payment_request.with_user(self.patient_user).unlink()
