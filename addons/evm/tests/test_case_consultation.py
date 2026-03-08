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
        self.assertEqual(case.patient_display_name, self.patient_user.partner_id.display_name)

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
