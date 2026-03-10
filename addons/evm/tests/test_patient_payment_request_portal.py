import html
import re

from odoo.tests import tagged
from odoo.tests.common import HttpCase, new_test_user


@tagged("post_install", "-at_install")
class TestEvmPatientPaymentRequestPortal(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kine_user = new_test_user(
            cls.env,
            login="kine_payment_portal",
            groups="evm.group_evm_kine",
            name="Kine Paiement",
        )
        cls.patient_login = "patient_payment_portal"
        cls.patient_password = cls.patient_login
        cls.patient_user = new_test_user(
            cls.env,
            login=cls.patient_login,
            groups="evm.group_evm_patient",
            name="Patient Paiement",
        )
        cls.other_patient_user = new_test_user(
            cls.env,
            login="patient_payment_portal_other",
            groups="evm.group_evm_patient",
            name="Autre Patient",
        )
        cls.accepted_case = cls.env["evm.case"].create(
            {
                "name": "Dossier patient portail",
                "kine_user_id": cls.kine_user.id,
                "patient_user_id": cls.patient_user.id,
                "state": "accepted",
                "requested_session_count": 20,
                "authorized_session_count": 12,
            }
        )
        cls.other_case = cls.env["evm.case"].create(
            {
                "name": "Dossier autre patient portail",
                "kine_user_id": cls.kine_user.id,
                "patient_user_id": cls.other_patient_user.id,
                "state": "accepted",
                "requested_session_count": 20,
                "authorized_session_count": 10,
            }
        )
        cls.pending_case = cls.env["evm.case"].create(
            {
                "name": "Dossier patient en attente",
                "kine_user_id": cls.kine_user.id,
                "patient_user_id": cls.patient_user.id,
                "state": "pending",
                "requested_session_count": 8,
                "authorized_session_count": 0,
            }
        )
        cls.env["evm.payment_request"].create(
            [
                {
                    "name": "Demande brouillon portail",
                    "case_id": cls.accepted_case.id,
                    "sessions_count": 2,
                    "state": "draft",
                    "amount_total": 80.0,
                },
                {
                    "name": "Demande validee portail",
                    "case_id": cls.accepted_case.id,
                    "sessions_count": 4,
                    "state": "validated",
                    "amount_total": 160.0,
                },
                {
                    "name": "Demande payee portail",
                    "case_id": cls.accepted_case.id,
                    "sessions_count": 1,
                    "state": "paid",
                    "amount_total": 40.0,
                },
            ]
        )
        cls.over_consumed_case = cls.env["evm.case"].create(
            {
                "name": "Dossier patient depassement",
                "kine_user_id": cls.kine_user.id,
                "patient_user_id": cls.patient_user.id,
                "state": "accepted",
                "requested_session_count": 12,
                "authorized_session_count": 3,
            }
        )
        cls.env["evm.payment_request"].create(
            {
                "name": "Demande depassement portail",
                "case_id": cls.over_consumed_case.id,
                "sessions_count": 5,
                "state": "validated",
                "amount_total": 200.0,
            }
        )

    def test_patient_portal_pages_show_case_access_and_payment_request_entrypoints(self):
        self.authenticate(self.patient_login, self.patient_password)

        home_response = self.url_open("/my")
        list_response = self.url_open("/my/evm/cases")
        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")

        self.assertEqual(home_response.status_code, 200)
        self.assertIn("Mes dossiers", home_response.text)
        self.assertEqual(list_response.status_code, 200)
        self.assertIn(self.accepted_case.name, list_response.text)
        self.assertNotIn(self.other_case.name, list_response.text)
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn("Demandes de paiement", detail_response.text)
        self.assertIn("Nouvelle demande de paiement", detail_response.text)
        self.assertIn("Seances consommees", detail_response.text)
        self.assertIn("Seances restantes", detail_response.text)
        self.assertIn("Demande validee portail", detail_response.text)
        self.assertIn("Demande payee portail", detail_response.text)
        self.assertRegex(detail_response.text, r"160(?:[.,]00)")
        self.assertRegex(detail_response.text, r"40(?:[.,]00)")

    def test_patient_portal_case_detail_shows_session_balance_from_validated_requests_only(self):
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")

        self.assertEqual(detail_response.status_code, 200)
        self.assertIn("Seances autorisees", detail_response.text)
        self.assertIn("Seances consommees", detail_response.text)
        self.assertIn("Seances restantes", detail_response.text)
        self.assertRegex(detail_response.text, r">\s*12\s*<")
        self.assertRegex(detail_response.text, r">\s*5\s*<")
        self.assertRegex(detail_response.text, r">\s*7\s*<")

    def test_patient_portal_case_detail_surfaces_quota_overrun_without_hiding_it(self):
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.over_consumed_case.id}")

        self.assertEqual(detail_response.status_code, 200)
        self.assertIn("depassent actuellement le quota autorise", detail_response.text)
        self.assertRegex(detail_response.text, r">\s*-2\s*<")

    def test_patient_portal_payment_request_form_creates_a_draft_request_once_per_submission_token(self):
        self.authenticate(self.patient_login, self.patient_password)

        form_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}/payment-requests/new")

        self.assertEqual(form_response.status_code, 200)
        self.assertIn("Nouvelle demande de paiement", form_response.text)
        self.assertIn(self.accepted_case.name, form_response.text)
        self.assertIn("Nombre de seances concernees", form_response.text)
        self.assertIn("Montant total a payer", form_response.text)

        submit_response = self.url_open(
            f"/my/evm/cases/{self.accepted_case.id}/payment-requests/create",
            data={
                "csrf_token": self._extract_csrf_token(form_response.text),
                "submission_token": self._extract_submission_token(form_response.text),
                "sessions_count": "4",
                "amount_total": "123.45",
            },
            allow_redirects=False,
        )

        self.assertEqual(submit_response.status_code, 303)
        self.assertRegex(
            submit_response.headers["Location"],
            rf"/my/evm/cases/{self.accepted_case.id}/payment-requests/new$",
        )

        payment_request = self.env["evm.payment_request"].sudo().search(
            [
                ("case_id", "=", self.accepted_case.id),
                ("patient_user_id", "=", self.patient_user.id),
                ("sessions_count", "=", 4),
                ("amount_total", "=", 123.45),
            ]
        )
        self.assertEqual(len(payment_request), 1)
        self.assertEqual(payment_request.state, "draft")
        self.assertEqual(payment_request.amount_total, 123.45)

        duplicate_submit_response = self.url_open(
            f"/my/evm/cases/{self.accepted_case.id}/payment-requests/create",
            data={
                "csrf_token": self._extract_csrf_token(form_response.text),
                "submission_token": self._extract_submission_token(form_response.text),
                "sessions_count": "4",
                "amount_total": "123.45",
            },
            allow_redirects=False,
        )
        self.assertEqual(duplicate_submit_response.status_code, 303)
        self.assertEqual(
            self.env["evm.payment_request"].sudo().search_count(
                [
                    ("case_id", "=", self.accepted_case.id),
                    ("patient_user_id", "=", self.patient_user.id),
                    ("sessions_count", "=", 4),
                    ("amount_total", "=", 123.45),
                ]
            ),
            1,
        )

        success_response = self.url_open(duplicate_submit_response.headers["Location"])
        self.assertIn("La demande de paiement a ete creee en brouillon.", success_response.text)

        refreshed_form_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}/payment-requests/new")
        self.assertNotIn("La demande de paiement a ete creee en brouillon.", refreshed_form_response.text)

    def test_patient_portal_payment_request_form_shows_french_errors_and_preserves_data(self):
        self.authenticate(self.patient_login, self.patient_password)

        form_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}/payment-requests/new")
        response = self.url_open(
            f"/my/evm/cases/{self.accepted_case.id}/payment-requests/create",
            data={
                "csrf_token": self._extract_csrf_token(form_response.text),
                "submission_token": self._extract_submission_token(form_response.text),
                "sessions_count": "0",
                "amount_total": "-8",
            },
        )
        response_text = html.unescape(response.text)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Veuillez corriger les erreurs ci-dessous.", response_text)
        self.assertIn("Veuillez renseigner un nombre de seances strictement positif.", response_text)
        self.assertIn("Veuillez renseigner un montant positif ou nul.", response_text)
        self.assertIn('value="0"', response_text)
        self.assertIn('value="-8"', response_text)
        self.assertFalse(
            self.env["evm.payment_request"].sudo().search(
                [
                    ("case_id", "=", self.accepted_case.id),
                    ("patient_user_id", "=", self.patient_user.id),
                    ("sessions_count", "=", 0),
                ]
            )
        )

    def test_patient_portal_payment_request_form_rejects_other_patient_case_access(self):
        self.authenticate(self.patient_login, self.patient_password)

        response = self.url_open(
            f"/my/evm/cases/{self.other_case.id}/payment-requests/new",
            allow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["Location"].endswith("/my"))

    def test_patient_portal_case_detail_rejects_unrelated_or_non_accepted_cases(self):
        self.authenticate(self.patient_login, self.patient_password)

        other_case_response = self.url_open(f"/my/evm/cases/{self.other_case.id}", allow_redirects=False)
        pending_case_response = self.url_open(f"/my/evm/cases/{self.pending_case.id}", allow_redirects=False)

        self.assertEqual(other_case_response.status_code, 303)
        self.assertTrue(other_case_response.headers["Location"].endswith("/my/evm/cases"))
        self.assertEqual(pending_case_response.status_code, 303)
        self.assertTrue(pending_case_response.headers["Location"].endswith("/my/evm/cases"))

    def test_patient_portal_case_detail_paginates_payment_requests(self):
        self.authenticate(self.patient_login, self.patient_password)
        for index in range(35):
            self.env["evm.payment_request"].create(
                {
                    "name": f"Demande pagination {index:02d}",
                    "case_id": self.accepted_case.id,
                    "sessions_count": 1,
                    "state": "draft",
                }
            )

        first_page_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        second_page_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}/page/2")

        self.assertEqual(first_page_response.status_code, 200)
        self.assertEqual(second_page_response.status_code, 200)
        self.assertIn("Demande pagination 24", first_page_response.text)
        self.assertNotIn("Demande pagination 00", first_page_response.text)
        self.assertIn("Demande pagination 00", second_page_response.text)

    @staticmethod
    def _extract_csrf_token(page_html):
        csrf_token_match = re.search(r'name="csrf_token" value="([^"]+)"', page_html)
        if not csrf_token_match:
            raise AssertionError("Le formulaire portail doit exposer un jeton CSRF.")
        return csrf_token_match.group(1)

    @staticmethod
    def _extract_submission_token(page_html):
        submission_token_match = re.search(r'name="submission_token" value="([^"]+)"', page_html)
        if not submission_token_match:
            raise AssertionError("Le formulaire portail doit exposer un jeton de soumission.")
        return submission_token_match.group(1)
