import base64
import html
import re
from io import BytesIO

from odoo.tests import tagged
from odoo.tests.common import HttpCase, new_test_user

MINIMAL_PDF = base64.b64decode(
    "JVBERi0xLjEKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCAxMDAgMTAwXSA+PgplbmRvYmoKdHJhaWxlcgo8PCAvUm9vdCAxIDAgUiA+PgolJUVPRgo="
)
MINIMAL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aF9sAAAAASUVORK5CYII="
)


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
        cls.accepted_case_payment_requests = cls.env["evm.payment_request"].create(
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
        cls.accepted_case_draft_request = cls.accepted_case_payment_requests[0]
        cls.accepted_case_validated_request = cls.accepted_case_payment_requests[1]
        cls.accepted_case_paid_request = cls.accepted_case_payment_requests[2]
        cls.case_document_attachments = cls.env["ir.attachment"].create(
            [
                {
                    "name": "facture-portail.pdf",
                    "datas": base64.b64encode(b"pdf portail"),
                    "mimetype": "application/pdf",
                    "res_model": "evm.payment_request",
                    "res_id": cls.accepted_case_validated_request.id,
                    "evm_patient_visible": True,
                },
                {
                    "name": "justificatif-portail.png",
                    "datas": base64.b64encode(b"png portail"),
                    "mimetype": "image/png",
                    "res_model": "evm.payment_request",
                    "res_id": cls.accepted_case_paid_request.id,
                    "evm_patient_visible": True,
                },
            ]
        )
        cls.internal_case_attachment = cls.env["ir.attachment"].create(
            {
                "name": "note-interne.pdf",
                "datas": base64.b64encode(b"pdf interne"),
                "mimetype": "application/pdf",
                "res_model": "evm.payment_request",
                "res_id": cls.accepted_case_validated_request.id,
                "evm_patient_visible": False,
            }
        )
        cls.other_case_payment_request = cls.env["evm.payment_request"].create(
            {
                "name": "Demande autre patient portail",
                "case_id": cls.other_case.id,
                "sessions_count": 3,
                "state": "submitted",
                "amount_total": 90.0,
            }
        )
        cls.other_case_attachment = cls.env["ir.attachment"].create(
            {
                "name": "facture-autre-patient.pdf",
                "datas": base64.b64encode(b"pdf autre"),
                "mimetype": "application/pdf",
                "res_model": "evm.payment_request",
                "res_id": cls.other_case_payment_request.id,
                "evm_patient_visible": True,
            }
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

    def test_patient_portal_case_detail_shows_aggregated_document_space_for_own_case(self):
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")

        self.assertEqual(detail_response.status_code, 200)
        self.assertIn("Documents du dossier", detail_response.text)
        self.assertIn("Historique documentaire", detail_response.text)
        self.assertIn("facture-portail.pdf", detail_response.text)
        self.assertIn("justificatif-portail.png", detail_response.text)
        self.assertIn("Demande validee portail", detail_response.text)
        self.assertIn("Demande payee portail", detail_response.text)
        self.assertIn(f'/web/content/{self.case_document_attachments[0].id}?download=true', detail_response.text)
        self.assertIn(f'/web/content/{self.case_document_attachments[1].id}?download=true', detail_response.text)
        self.assertNotIn("facture-autre-patient.pdf", detail_response.text)
        self.assertNotIn("note-interne.pdf", detail_response.text)
        self.assertIn('aria-label="Telecharger facture-portail.pdf pour Demande validee portail"', detail_response.text)
        self.assertIn(">PDF<", detail_response.text)
        self.assertIn(">Image PNG<", detail_response.text)

    def test_patient_portal_case_detail_shows_completion_reason_for_request_to_complete(self):
        payment_request = self.env["evm.payment_request"].create(
            {
                "name": "Demande a completer portail",
                "case_id": self.accepted_case.id,
                "sessions_count": 3,
                "state": "to_complete",
                "completion_request_reason": "Merci d'ajouter une facture lisible et les dates de seances.",
            }
        )
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        response_text = html.unescape(detail_response.text)

        self.assertEqual(detail_response.status_code, 200)
        self.assertIn("Demande a completer portail", response_text)
        self.assertIn("Motif de retour", response_text)
        self.assertIn("Merci d'ajouter une facture lisible et les dates de seances.", response_text)
        self.assertIn(
            f'/my/evm/payment-requests/{payment_request.id}/attachments/upload',
            detail_response.text,
        )
        self.assertIn(
            f'/my/evm/payment-requests/{payment_request.id}/submit',
            detail_response.text,
        )

    def test_patient_portal_case_detail_can_resubmit_request_to_complete(self):
        payment_request = self.env["evm.payment_request"].create(
            {
                "name": "Demande resoumission portail",
                "case_id": self.accepted_case.id,
                "sessions_count": 3,
                "state": "to_complete",
                "completion_request_reason": "Merci d'ajouter le justificatif complementaire.",
            }
        )
        self.env["ir.attachment"].create(
            {
                "name": "facture-resoumission.pdf",
                "datas": base64.b64encode(MINIMAL_PDF),
                "mimetype": "application/pdf",
                "res_model": "evm.payment_request",
                "res_id": payment_request.id,
                "evm_patient_visible": True,
            }
        )
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        submit_response = self.url_open(
            f"/my/evm/payment-requests/{payment_request.id}/submit",
            data={
                "csrf_token": self._extract_csrf_token(detail_response.text),
                "submission_token": self._extract_submission_token(detail_response.text),
                "payment_request_page": "1",
                "document_page": "1",
            },
            allow_redirects=False,
        )

        self.assertEqual(submit_response.status_code, 303)
        self.assertRegex(submit_response.headers["Location"], rf"/my/evm/cases/{self.accepted_case.id}$")
        self.assertEqual(payment_request.state, "submitted")
        self.assertFalse(payment_request.completion_request_reason)

        success_response = self.url_open(submit_response.headers["Location"])
        response_text = html.unescape(success_response.text)
        self.assertIn("La demande de paiement a ete soumise a la fondation.", response_text)
        self.assertNotIn("Motif de retour", response_text)

    def test_patient_portal_document_download_refuses_unrelated_case_attachment(self):
        self.authenticate(self.patient_login, self.patient_password)

        allowed_response = self.url_open(f"/web/content/{self.case_document_attachments[0].id}?download=true")
        internal_response = self.url_open(f"/web/content/{self.internal_case_attachment.id}?download=true")
        forbidden_response = self.url_open(f"/web/content/{self.other_case_attachment.id}?download=true")

        self.assertEqual(allowed_response.status_code, 200)
        self.assertEqual(internal_response.status_code, 404)
        self.assertEqual(forbidden_response.status_code, 404)

    def test_patient_portal_case_detail_paginates_documents_independently(self):
        self.authenticate(self.patient_login, self.patient_password)
        for index in range(25):
            self.env["ir.attachment"].create(
                {
                    "name": f"facture-pagination-{index:02d}.pdf",
                    "datas": base64.b64encode(f"pdf-{index:02d}".encode()),
                    "mimetype": "application/pdf",
                    "res_model": "evm.payment_request",
                    "res_id": self.accepted_case_validated_request.id,
                    "evm_patient_visible": True,
                }
            )

        first_page_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        second_page_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}?document_page=2")

        self.assertEqual(first_page_response.status_code, 200)
        self.assertEqual(second_page_response.status_code, 200)
        self.assertIn("facture-pagination-24.pdf", first_page_response.text)
        self.assertNotIn("facture-pagination-00.pdf", first_page_response.text)
        self.assertIn("facture-pagination-00.pdf", second_page_response.text)

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

    def test_patient_portal_case_detail_uploads_multiple_documents_for_own_draft_request(self):
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")

        self.assertEqual(detail_response.status_code, 200)
        self.assertIn("Ajouter des justificatifs", detail_response.text)

        upload_response = self.url_open(
            f"/my/evm/payment-requests/{self.accepted_case_draft_request.id}/attachments/upload",
            data={"csrf_token": self._extract_csrf_token(detail_response.text)},
            files=[
                ("documents", ("facture-brouillon.pdf", BytesIO(MINIMAL_PDF), "application/pdf")),
                ("documents", ("justificatif-brouillon.png", BytesIO(MINIMAL_PNG), "image/png")),
            ],
            allow_redirects=False,
        )

        self.assertEqual(upload_response.status_code, 303)
        self.assertRegex(upload_response.headers["Location"], rf"/my/evm/cases/{self.accepted_case.id}$")

        uploaded_attachments = self.env["ir.attachment"].sudo().search(
            [
                ("res_model", "=", "evm.payment_request"),
                ("res_id", "=", self.accepted_case_draft_request.id),
                ("name", "in", ["facture-brouillon.pdf", "justificatif-brouillon.png"]),
            ]
        )
        self.assertEqual(len(uploaded_attachments), 2)
        self.assertTrue(all(uploaded_attachments.mapped("evm_patient_visible")))

        success_response = self.url_open(upload_response.headers["Location"])
        self.assertIn("2 document(s) ont ete ajoutes a la demande.", success_response.text)
        self.assertIn("facture-brouillon.pdf", success_response.text)
        self.assertIn("justificatif-brouillon.png", success_response.text)

    def test_patient_portal_case_detail_rejects_invalid_uploaded_documents_in_french(self):
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        response = self.url_open(
            f"/my/evm/payment-requests/{self.accepted_case_draft_request.id}/attachments/upload",
            data={"csrf_token": self._extract_csrf_token(detail_response.text)},
            files=[("documents", ("piece.exe", BytesIO(b"exe"), "application/octet-stream"))],
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Veuillez corriger les erreurs ci-dessous.", html.unescape(response.text))
        self.assertIn("Formats autorises", html.unescape(response.text))
        self.assertFalse(
            self.env["ir.attachment"].sudo().search(
                [
                    ("res_model", "=", "evm.payment_request"),
                    ("res_id", "=", self.accepted_case_draft_request.id),
                    ("name", "=", "piece.exe"),
                ]
            )
        )

    def test_patient_portal_case_detail_rejects_mismatched_file_content_in_french(self):
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        response = self.url_open(
            f"/my/evm/payment-requests/{self.accepted_case_draft_request.id}/attachments/upload",
            data={
                "csrf_token": self._extract_csrf_token(detail_response.text),
                "payment_request_page": "1",
                "document_page": "1",
            },
            files=[("documents", ("piece.pdf", BytesIO(b"pas un vrai pdf"), "application/pdf"))],
        )

        self.assertEqual(response.status_code, 200)
        response_text = html.unescape(response.text)
        self.assertIn("Veuillez corriger les erreurs ci-dessous.", response_text)
        self.assertIn("Le contenu du fichier ne correspond pas a son format autorise.", response_text)

    def test_patient_portal_case_detail_refuses_upload_on_unrelated_request_with_french_message(self):
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        response = self.url_open(
            f"/my/evm/payment-requests/{self.other_case_payment_request.id}/attachments/upload",
            data={
                "csrf_token": self._extract_csrf_token(detail_response.text),
                "payment_request_page": "1",
                "document_page": "1",
            },
            files=[("documents", ("facture.pdf", BytesIO(b"pdf"), "application/pdf"))],
            allow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["Location"].endswith("/my/evm/cases"))

        redirected_response = self.url_open(response.headers["Location"])
        self.assertEqual(redirected_response.status_code, 200)
        self.assertIn(
            "Cette demande de paiement n'est pas accessible depuis votre portail.",
            html.unescape(redirected_response.text),
        )

    def test_patient_portal_case_detail_keeps_pagination_context_after_upload(self):
        self.authenticate(self.patient_login, self.patient_password)
        for index in range(35):
            self.env["evm.payment_request"].create(
                {
                    "name": f"Demande upload pagination {index:02d}",
                    "case_id": self.accepted_case.id,
                    "sessions_count": 1,
                    "state": "draft",
                }
            )

        second_page_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}/page/2?document_page=2")
        self.assertEqual(second_page_response.status_code, 200)

        upload_response = self.url_open(
            f"/my/evm/payment-requests/{self.accepted_case_draft_request.id}/attachments/upload",
            data={
                "csrf_token": self._extract_csrf_token(second_page_response.text),
                "payment_request_page": "2",
                "document_page": "2",
            },
            files=[("documents", ("facture-pagination.pdf", BytesIO(MINIMAL_PDF), "application/pdf"))],
            allow_redirects=False,
        )

        self.assertEqual(upload_response.status_code, 303)
        self.assertRegex(upload_response.headers["Location"], rf"/my/evm/cases/{self.accepted_case.id}/page/2\?document_page=2$")

    def test_patient_portal_case_detail_submits_complete_request(self):
        self.authenticate(self.patient_login, self.patient_password)
        self.env["ir.attachment"].create(
            {
                "name": "facture-a-soumettre.pdf",
                "datas": base64.b64encode(MINIMAL_PDF),
                "mimetype": "application/pdf",
                "res_model": "evm.payment_request",
                "res_id": self.accepted_case_draft_request.id,
                "evm_patient_visible": True,
            }
        )

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        submit_response = self.url_open(
            f"/my/evm/payment-requests/{self.accepted_case_draft_request.id}/submit",
            data={
                "csrf_token": self._extract_csrf_token(detail_response.text),
                "submission_token": self._extract_submission_token(detail_response.text),
                "payment_request_page": "1",
                "document_page": "1",
            },
            allow_redirects=False,
        )

        self.assertEqual(submit_response.status_code, 303)
        self.assertRegex(submit_response.headers["Location"], rf"/my/evm/cases/{self.accepted_case.id}$")
        self.assertEqual(self.accepted_case_draft_request.state, "submitted")

        success_response = self.url_open(submit_response.headers["Location"])
        self.assertIn("La demande de paiement a ete soumise a la fondation.", html.unescape(success_response.text))
        self.assertNotIn("Ajouter des justificatifs", success_response.text)

    def test_patient_portal_case_detail_submission_replay_keeps_success_feedback(self):
        self.authenticate(self.patient_login, self.patient_password)
        self.env["ir.attachment"].create(
            {
                "name": "facture-replay.pdf",
                "datas": base64.b64encode(MINIMAL_PDF),
                "mimetype": "application/pdf",
                "res_model": "evm.payment_request",
                "res_id": self.accepted_case_draft_request.id,
                "evm_patient_visible": True,
            }
        )

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        submit_payload = {
            "csrf_token": self._extract_csrf_token(detail_response.text),
            "submission_token": self._extract_submission_token(detail_response.text),
            "payment_request_page": "1",
            "document_page": "1",
        }

        first_submit = self.url_open(
            f"/my/evm/payment-requests/{self.accepted_case_draft_request.id}/submit",
            data=submit_payload,
            allow_redirects=False,
        )
        replay_submit = self.url_open(
            f"/my/evm/payment-requests/{self.accepted_case_draft_request.id}/submit",
            data=submit_payload,
            allow_redirects=False,
        )

        self.assertEqual(first_submit.status_code, 303)
        self.assertEqual(replay_submit.status_code, 303)
        self.assertRegex(replay_submit.headers["Location"], rf"/my/evm/cases/{self.accepted_case.id}$")

        replay_response = self.url_open(replay_submit.headers["Location"])
        self.assertIn("La demande de paiement a deja ete soumise a la fondation.", html.unescape(replay_response.text))
        self.assertEqual(self.accepted_case_draft_request.state, "submitted")

    def test_patient_portal_case_detail_rejects_incomplete_submission_in_french(self):
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        response = self.url_open(
            f"/my/evm/payment-requests/{self.accepted_case_draft_request.id}/submit",
            data={
                "csrf_token": self._extract_csrf_token(detail_response.text),
                "submission_token": self._extract_submission_token(detail_response.text),
                "payment_request_page": "1",
                "document_page": "1",
            },
        )

        self.assertEqual(response.status_code, 200)
        response_text = html.unescape(response.text)
        self.assertIn("Veuillez corriger les erreurs ci-dessous.", response_text)
        self.assertIn("Ajoutez au moins un justificatif avant de soumettre la demande.", response_text)
        self.assertEqual(self.accepted_case_draft_request.state, "draft")

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
