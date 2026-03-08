from odoo.tests import tagged
from odoo.tests.common import HttpCase, new_test_user


@tagged("post_install", "-at_install")
class TestEvmKinePortal(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kine_login = "kine1401"
        cls.kine_password = cls.kine_login
        cls.kine_user = new_test_user(
            cls.env,
            login=cls.kine_login,
            groups="evm.group_evm_kine",
            name="Kine Portail",
        )
        cls.other_kine_user = new_test_user(
            cls.env,
            login="kine1402",
            groups="evm.group_evm_kine",
            name="Autre Kine",
        )
        cls.patient_user = new_test_user(
            cls.env,
            login="patient14",
            groups="evm.group_evm_patient",
            name="Patient Portail",
        )

        cls.own_case = cls.env["evm.case"].create(
            {
                "name": "Dossier portail kine",
                "kine_user_id": cls.kine_user.id,
                "patient_user_id": cls.patient_user.id,
                "state": "pending",
                "requested_session_count": 24,
                "authorized_session_count": 18,
            }
        )
        cls.own_case.message_post(body="Commentaire visible.", subtype_xmlid="mail.mt_comment")
        cls.own_case.message_post(body="Note interne.", subtype_xmlid="mail.mt_note")
        cls.other_case = cls.env["evm.case"].create(
            {
                "name": "Dossier autre kine",
                "kine_user_id": cls.other_kine_user.id,
                "state": "accepted",
                "requested_session_count": 10,
            }
        )

    def test_kine_portal_pages_show_case_list_and_detail(self):
        self.authenticate(self.kine_login, self.kine_password)

        home_response = self.url_open("/my")
        self.assertEqual(home_response.status_code, 200)
        self.assertIn("Mes dossiers", home_response.text)

        list_response = self.url_open("/my/evm/cases")
        self.assertEqual(list_response.status_code, 200)
        self.assertIn(self.own_case.name, list_response.text)
        self.assertIn("En attente", list_response.text)
        self.assertIn("Patient Portail", list_response.text)
        self.assertNotIn(self.other_case.name, list_response.text)

        detail_response = self.url_open(f"/my/evm/cases/{self.own_case.id}")
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn(self.own_case.name, detail_response.text)
        self.assertIn("Seances demandees", detail_response.text)
        self.assertIn("Seances autorisees", detail_response.text)
        self.assertIn("Commentaire visible.", detail_response.text)
        self.assertNotIn("Note interne.", detail_response.text)

    def test_kine_portal_redirects_when_opening_another_kine_case(self):
        self.authenticate(self.kine_login, self.kine_password)

        response = self.url_open(f"/my/evm/cases/{self.other_case.id}", allow_redirects=False)

        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["Location"].endswith("/my/evm/cases"))
