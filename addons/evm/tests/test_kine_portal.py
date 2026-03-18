import html
import re

from odoo.http import Request
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
        self.assertIn("Nouveau dossier", list_response.text)
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
        self.assertIn(f'/my/evm/cases/{self.own_case.id}/comments/post', detail_response.text)

    def test_kine_portal_redirects_when_opening_another_kine_case(self):
        self.authenticate(self.kine_login, self.kine_password)

        response = self.url_open(f"/my/evm/cases/{self.other_case.id}", allow_redirects=False)

        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["Location"].endswith("/my/evm/cases"))

    def test_kine_portal_can_post_comment_on_own_case(self):
        self.authenticate(self.kine_login, self.kine_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.own_case.id}")
        post_response = self.url_open(
            f"/my/evm/cases/{self.own_case.id}/comments/post",
            data={
                "csrf_token": self._extract_csrf_token(detail_response.text),
                "comment": "Commentaire kine via portail.",
            },
            allow_redirects=False,
        )

        self.assertEqual(post_response.status_code, 303)
        self.assertRegex(post_response.headers["Location"], rf"/my/evm/cases/{self.own_case.id}$")

        refreshed_case = self.env["evm.case"].browse(self.own_case.id)
        self.assertTrue(
            any("Commentaire kine via portail." in (body or "") for body in refreshed_case.message_ids.mapped("body"))
        )

        success_response = self.url_open(post_response.headers["Location"])
        response_text = html.unescape(success_response.text)
        self.assertIn("Votre commentaire a ete ajoute au dossier.", response_text)
        self.assertIn("Commentaire kine via portail.", response_text)

    def test_kine_portal_creation_form_creates_a_pending_case(self):
        self.authenticate(self.kine_login, self.kine_password)

        form_response = self.url_open("/my/evm/cases/new")

        self.assertEqual(form_response.status_code, 200)
        self.assertIn("Creer un dossier", form_response.text)
        self.assertIn("Nom du patient", form_response.text)
        self.assertIn("Adresse e-mail du patient", form_response.text)
        self.assertIn("Nombre maximum de seances demandees", form_response.text)

        submit_response = self.url_open(
            "/my/evm/cases/create",
            data={
                "csrf_token": self._extract_csrf_token(form_response.text),
                "patient_name": "Patient Nouveau",
                "patient_email": "patient.nouveau@example.com",
                "requested_session_count": "16",
            },
            allow_redirects=False,
        )

        self.assertEqual(submit_response.status_code, 303)
        self.assertRegex(submit_response.headers["Location"], r"/my/evm/cases/\d+$")

        case = (
            self.env["evm.case"]
            .sudo()
            .search(
                [
                    ("kine_user_id", "=", self.kine_user.id),
                    ("patient_name", "=", "Patient Nouveau"),
                ]
            )
        )
        self.assertEqual(len(case), 1)
        self.assertEqual(case.state, "pending")
        self.assertEqual(case.name, "Patient Nouveau")
        self.assertTrue(any("Demande initiale soumise" in body for body in case.message_ids.mapped("body")))
        case.unlink()

    def test_kine_portal_creation_form_shows_french_errors_and_preserves_data(self):
        self.authenticate(self.kine_login, self.kine_password)

        response = self.url_open(
            "/my/evm/cases/create",
            data={
                "csrf_token": Request.csrf_token(self),
                "patient_name": "Patient Incomplet",
                "patient_email": "",
                "requested_session_count": "0",
            },
        )
        response_text = html.unescape(response.text)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Veuillez corriger les erreurs ci-dessous.", response_text)
        self.assertIn("Veuillez renseigner l'adresse e-mail du patient.", response_text)
        self.assertIn("Veuillez renseigner un nombre de seances strictement positif.", response_text)
        self.assertIn('value="Patient Incomplet"', response_text)
        self.assertFalse(
            self.env["evm.case"]
            .sudo()
            .search(
                [
                    ("kine_user_id", "=", self.kine_user.id),
                    ("patient_name", "=", "Patient Incomplet"),
                ]
            )
        )

    @staticmethod
    def _extract_csrf_token(html):
        csrf_token_match = re.search(r'name="csrf_token" value="([^"]+)"', html)
        if not csrf_token_match:
            raise AssertionError("Le formulaire portail doit exposer un jeton CSRF.")
        return csrf_token_match.group(1)
