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
        cls.accepted_case.message_post(body="Commentaire dossier visible patient.", subtype_xmlid="mail.mt_comment")
        cls.accepted_case.message_post(body="Note interne dossier invisible patient.", subtype_xmlid="mail.mt_note")
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
        cls.accepted_case_payment_requests = cls.env["evm.payment_request"].with_context(
            evm_allow_payment_request_workflow_write=True
        ).create(
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
        cls.accepted_case_payment_requests = cls.env["evm.payment_request"].browse(cls.accepted_case_payment_requests.ids)
        cls.accepted_case_draft_request = cls.accepted_case_payment_requests[0]
        cls.accepted_case_validated_request = cls.accepted_case_payment_requests[1]
        cls.accepted_case_paid_request = cls.accepted_case_payment_requests[2]
        cls.accepted_case_validated_request.message_post(
            body="Commentaire demande visible patient.",
            subtype_xmlid="mail.mt_comment",
        )
        cls.accepted_case_validated_request.message_post(
            body="Note interne demande invisible patient.",
            subtype_xmlid="mail.mt_note",
        )
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
        cls.other_case_payment_request = cls.env["evm.payment_request"].with_context(
            evm_allow_payment_request_workflow_write=True
        ).create(
            {
                "name": "Demande autre patient portail",
                "case_id": cls.other_case.id,
                "sessions_count": 3,
                "state": "submitted",
                "amount_total": 90.0,
            }
        )
        cls.other_case_payment_request = cls.env["evm.payment_request"].browse(cls.other_case_payment_request.ids)
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

    def _create_workflow_payment_request(self, values):
        payment_request = self.env["evm.payment_request"].with_context(
            evm_allow_payment_request_workflow_write=True
        ).create(values)
        return self.env["evm.payment_request"].browse(payment_request.ids)
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
        self.assertIn("Echanges sur le dossier", detail_response.text)
        self.assertIn("Commentaire dossier visible patient.", detail_response.text)
        self.assertNotIn("Note interne dossier invisible patient.", detail_response.text)
        self.assertIn("Demande validee portail", detail_response.text)
        self.assertIn("Demande payee portail", detail_response.text)
        self.assertIn("Commentaire demande visible patient.", detail_response.text)
        self.assertNotIn("Note interne demande invisible patient.", detail_response.text)
        self.assertRegex(detail_response.text, r"160(?:[.,]00)")
        self.assertRegex(detail_response.text, r"40(?:[.,]00)")
        self.assertIn(f'/my/evm/cases/{self.accepted_case.id}/comments/post', detail_response.text)
        self.assertIn(
            f'/my/evm/payment-requests/{self.accepted_case_validated_request.id}/comments/post',
            detail_response.text,
        )

    def test_patient_portal_case_detail_shows_aggregated_document_space_for_own_case(self):
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")

        self.assertEqual(detail_response.status_code, 200)
        self.assertIn("Justificatifs de la demande", detail_response.text)
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
        payment_request = self._create_workflow_payment_request(
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

    def test_patient_portal_case_detail_shows_refusal_reason_for_refused_request(self):
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_portal_refusal",
            groups="evm.group_evm_fondation",
            name="Fondation Paiement",
        )
        payment_request = self._create_workflow_payment_request(
            {
                "name": "Demande refusee portail",
                "case_id": self.accepted_case.id,
                "sessions_count": 3,
                "state": "submitted",
            }
        )
        payment_request.with_user(foundation_user).action_refuse(
            "La demande ne peut pas etre prise en charge car les justificatifs sont hors perimetre."
        )
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        response_text = html.unescape(detail_response.text)

        self.assertEqual(detail_response.status_code, 200)
        self.assertIn("Demande refusee portail", response_text)
        self.assertIn("Demande refusee", response_text)
        self.assertIn("Motif du refus", response_text)
        self.assertIn(
            "La demande ne peut pas etre prise en charge car les justificatifs sont hors perimetre.",
            response_text,
        )
        self.assertIn("Historique des echanges", response_text)
        self.assertIn("Demande refusee par la fondation", response_text)
        self.assertNotIn(f'/my/evm/payment-requests/{payment_request.id}/update', detail_response.text)
        self.assertNotIn(f'/my/evm/payment-requests/{payment_request.id}/attachments/upload', detail_response.text)
        self.assertNotIn(f'/my/evm/payment-requests/{payment_request.id}/submit', detail_response.text)

    def test_patient_portal_history_hides_internal_payment_references(self):
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_portal_history",
            groups="evm.group_evm_fondation",
            name="Fondation Historique",
        )
        payment_request = self._create_workflow_payment_request(
            {
                "name": "Demande historique portail",
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "state": "submitted",
                "amount_total": 75.0,
            }
        )
        payment_request.with_user(foundation_user).action_validate()
        payment_request.with_user(foundation_user).action_confirm_external_payment()
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        response_text = html.unescape(detail_response.text)

        self.assertEqual(detail_response.status_code, 200)
        self.assertIn("Demande de paiement validee par la fondation", response_text)
        self.assertIn("Paiement confirme hors plateforme par la fondation", response_text)
        self.assertIn("Paiement hors plateforme confirme pour la demande", response_text)
        self.assertNotIn(payment_request.payment_id.display_name, response_text)

    def test_patient_portal_case_detail_can_resubmit_request_to_complete(self):
        payment_request = self._create_workflow_payment_request(
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
        self.assertIn("Historique des echanges", response_text)
        self.assertIn("Demande de paiement completee puis soumise a nouveau par le patient", response_text)

    def test_patient_portal_can_post_case_comment_on_own_case(self):
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        post_response = self.url_open(
            f"/my/evm/cases/{self.accepted_case.id}/comments/post",
            data={
                "csrf_token": self._extract_csrf_token(detail_response.text),
                "comment": "Question patient via portail sur le dossier.",
            },
            allow_redirects=False,
        )

        self.assertEqual(post_response.status_code, 303)
        self.assertRegex(post_response.headers["Location"], rf"/my/evm/cases/{self.accepted_case.id}$")

        refreshed_case = self.env["evm.case"].browse(self.accepted_case.id)
        self.assertTrue(
            any("Question patient via portail sur le dossier." in (body or "") for body in refreshed_case.message_ids.mapped("body"))
        )

        success_response = self.url_open(post_response.headers["Location"])
        response_text = html.unescape(success_response.text)
        self.assertIn("Votre commentaire a ete ajoute au dossier.", response_text)
        self.assertIn("Patient Paiement", response_text)
        self.assertIn("Question patient via portail sur le dossier.", response_text)

    def test_patient_portal_can_post_payment_request_comment_on_own_request(self):
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        post_response = self.url_open(
            f"/my/evm/payment-requests/{self.accepted_case_validated_request.id}/comments/post",
            data={
                "csrf_token": self._extract_csrf_token(detail_response.text),
                "payment_request_page": "1",
                "document_page": "1",
                "comment": "Question patient via portail sur la demande.",
            },
            allow_redirects=False,
        )

        self.assertEqual(post_response.status_code, 303)
        self.assertRegex(post_response.headers["Location"], rf"/my/evm/cases/{self.accepted_case.id}$")

        refreshed_request = self.env["evm.payment_request"].browse(self.accepted_case_validated_request.id)
        self.assertTrue(
            any("Question patient via portail sur la demande." in (body or "") for body in refreshed_request.message_ids.mapped("body"))
        )

        success_response = self.url_open(post_response.headers["Location"])
        response_text = html.unescape(success_response.text)
        self.assertIn("Votre commentaire a ete ajoute a la demande.", response_text)
        self.assertIn("Patient Paiement", response_text)
        self.assertIn("Question patient via portail sur la demande.", response_text)

    def test_patient_portal_comment_routes_reject_inaccessible_targets(self):
        self.authenticate(self.patient_login, self.patient_password)
        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        csrf_token = self._extract_csrf_token(detail_response.text)

        case_response = self.url_open(
            f"/my/evm/cases/{self.other_case.id}/comments/post",
            data={
                "csrf_token": csrf_token,
                "comment": "Commentaire interdit",
            },
            allow_redirects=False,
        )
        request_response = self.url_open(
            f"/my/evm/payment-requests/{self.other_case_payment_request.id}/comments/post",
            data={
                "csrf_token": csrf_token,
                "payment_request_page": "1",
                "document_page": "1",
                "comment": "Commentaire interdit",
            },
            allow_redirects=False,
        )

        self.assertEqual(case_response.status_code, 303)
        self.assertTrue(case_response.headers["Location"].endswith("/my/evm/cases"))
        self.assertEqual(request_response.status_code, 303)
        self.assertTrue(request_response.headers["Location"].endswith("/my/evm/cases"))

    def test_patient_portal_case_comment_keeps_pagination_context(self):
        self.authenticate(self.patient_login, self.patient_password)
        for index in range(35):
            self._create_workflow_payment_request(
                {
                    "name": f"Demande commentaire pagination {index:02d}",
                    "case_id": self.accepted_case.id,
                    "sessions_count": 1,
                    "state": "draft",
                }
            )

        second_page_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}/page/2?document_page=2")
        self.assertEqual(second_page_response.status_code, 200)

        post_response = self.url_open(
            f"/my/evm/cases/{self.accepted_case.id}/comments/post",
            data={
                "csrf_token": self._extract_csrf_token(second_page_response.text),
                "payment_request_page": "2",
                "document_page": "2",
                "comment": "Commentaire avec pagination conservee.",
            },
            allow_redirects=False,
        )

        self.assertEqual(post_response.status_code, 303)
        self.assertRegex(post_response.headers["Location"], rf"/my/evm/cases/{self.accepted_case.id}/page/2\?document_page=2$")

    def test_patient_portal_case_detail_can_update_request_to_complete_before_resubmission(self):
        payment_request = self._create_workflow_payment_request(
            {
                "name": "Demande a mettre a jour portail",
                "case_id": self.accepted_case.id,
                "sessions_count": 3,
                "state": "to_complete",
                "amount_total": 90.0,
                "completion_request_reason": "Merci de preciser le nombre de seances et d'ajouter une preuve complementaire.",
            }
        )
        existing_attachment = self.env["ir.attachment"].create(
            {
                "name": "facture-existante.pdf",
                "datas": base64.b64encode(MINIMAL_PDF),
                "mimetype": "application/pdf",
                "res_model": "evm.payment_request",
                "res_id": payment_request.id,
                "evm_patient_visible": True,
            }
        )
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        update_response = self.url_open(
            f"/my/evm/payment-requests/{payment_request.id}/update",
            data={
                "csrf_token": self._extract_csrf_token(detail_response.text),
                "payment_request_page": "1",
                "document_page": "1",
                "name": "Demande mise a jour portail",
                "sessions_count": "5",
                "amount_total": "125.50",
            },
            allow_redirects=False,
        )

        self.assertEqual(update_response.status_code, 303)
        self.assertRegex(update_response.headers["Location"], rf"/my/evm/cases/{self.accepted_case.id}$")
        self.assertEqual(payment_request.name, "Demande mise a jour portail")
        self.assertEqual(payment_request.sessions_count, 5)
        self.assertEqual(payment_request.amount_total, 125.5)
        self.assertEqual(payment_request.state, "to_complete")
        self.assertEqual(
            payment_request.completion_request_reason,
            "Merci de preciser le nombre de seances et d'ajouter une preuve complementaire.",
        )
        self.assertEqual(payment_request.attachment_ids, existing_attachment)

        success_response = self.url_open(update_response.headers["Location"])
        response_text = html.unescape(success_response.text)
        self.assertIn("Les informations de la demande ont ete mises a jour.", response_text)
        self.assertIn("Demande mise a jour portail", response_text)
        self.assertIn("facture-existante.pdf", response_text)
        self.assertIn('value="Demande mise a jour portail"', response_text)
        self.assertIn('value="5"', response_text)
        self.assertIn('value="125.50"', response_text)

    def test_patient_portal_case_detail_shows_update_errors_for_request_to_complete(self):
        payment_request = self._create_workflow_payment_request(
            {
                "name": "Demande invalide portail",
                "case_id": self.accepted_case.id,
                "sessions_count": 3,
                "state": "to_complete",
                "amount_total": 90.0,
                "completion_request_reason": "Merci d'ajouter les informations manquantes.",
            }
        )
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        response = self.url_open(
            f"/my/evm/payment-requests/{payment_request.id}/update",
            data={
                "csrf_token": self._extract_csrf_token(detail_response.text),
                "payment_request_page": "1",
                "document_page": "1",
                "name": "   ",
                "sessions_count": "0",
                "amount_total": "-1",
            },
        )
        response_text = html.unescape(response.text)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Veuillez corriger les erreurs ci-dessous.", response_text)
        self.assertIn("Le nom de la demande ne peut pas etre vide.", response_text)
        self.assertIn("Veuillez renseigner un nombre de seances strictement positif.", response_text)
        self.assertIn("Veuillez renseigner un montant positif ou nul.", response_text)
        self.assertIn("Merci d'ajouter les informations manquantes.", response_text)
        self.assertEqual(payment_request.name, "Demande invalide portail")
        self.assertEqual(payment_request.sessions_count, 3)
        self.assertEqual(payment_request.amount_total, 90.0)

    def test_patient_portal_case_detail_rejects_empty_name_on_update(self):
        payment_request = self._create_workflow_payment_request(
            {
                "name": "Demande nom vide portail",
                "case_id": self.accepted_case.id,
                "sessions_count": 3,
                "state": "to_complete",
                "amount_total": 90.0,
            }
        )
        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        response = self.url_open(
            f"/my/evm/payment-requests/{payment_request.id}/update",
            data={
                "csrf_token": self._extract_csrf_token(detail_response.text),
                "payment_request_page": "1",
                "document_page": "1",
                "name": "",
                "sessions_count": "3",
                "amount_total": "90.00",
            },
        )
        response_text = html.unescape(response.text)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Le nom de la demande ne peut pas etre vide.", response_text)
        self.assertEqual(payment_request.name, "Demande nom vide portail")

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
        self.assertIn("Justificatifs de la demande", first_page_response.text)
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

    def test_patient_portal_case_detail_shows_validated_request_adjustments_and_updated_balance(self):
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_portal_validation",
            groups="evm.group_evm_fondation",
            name="Fondation Validation",
        )
        payment_request = self._create_workflow_payment_request(
            {
                "name": "Demande validation portail",
                "case_id": self.accepted_case.id,
                "sessions_count": 3,
                "state": "submitted",
                "amount_total": 90.0,
            }
        )
        payment_request.with_user(foundation_user).write(
            {
                "sessions_count": 6,
                "amount_total": 210.0,
            }
        )
        payment_request.with_user(foundation_user).action_validate()

        self.authenticate(self.patient_login, self.patient_password)

        detail_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        response_text = html.unescape(detail_response.text)

        self.assertEqual(detail_response.status_code, 200)
        self.assertIn("Demande validation portail", response_text)
        self.assertRegex(detail_response.text, r">\s*12\s*<")
        self.assertRegex(detail_response.text, r">\s*11\s*<")
        self.assertRegex(detail_response.text, r">\s*1\s*<")
        self.assertRegex(response_text, r"210(?:[.,]00)")
        self.assertIn("Demande de paiement validee par la fondation", response_text)

    def test_patient_portal_payment_request_form_creates_a_draft_request(self):
        self.authenticate(self.patient_login, self.patient_password)

        form_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}/payment-requests/new")

        self.assertEqual(form_response.status_code, 200)
        self.assertIn("Nouvelle demande de paiement", form_response.text)
        self.assertIn(self.accepted_case.name, form_response.text)
        self.assertIn("Nombre de seances concernees", form_response.text)
        self.assertIn("Montant total a payer", form_response.text)
        self.assertIn("Justificatifs", form_response.text)
        self.assertIn("Enregistrer en brouillon", form_response.text)
        self.assertIn("Creer et soumettre", form_response.text)

        submit_response = self.url_open(
            f"/my/evm/cases/{self.accepted_case.id}/payment-requests/create",
            data={
                "csrf_token": self._extract_csrf_token(form_response.text),
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

        success_response = self.url_open(submit_response.headers["Location"])
        self.assertIn("La demande de paiement a ete creee en brouillon.", success_response.text)

        refreshed_form_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}/payment-requests/new")
        self.assertNotIn("La demande de paiement a ete creee en brouillon.", refreshed_form_response.text)

    def test_patient_portal_payment_request_form_can_create_two_distinct_draft_requests_in_sequence(self):
        self.authenticate(self.patient_login, self.patient_password)

        first_form_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}/payment-requests/new")

        first_submit_response = self.url_open(
            f"/my/evm/cases/{self.accepted_case.id}/payment-requests/create",
            data={
                "csrf_token": self._extract_csrf_token(first_form_response.text),
                "sessions_count": "4",
                "amount_total": "123.45",
            },
            allow_redirects=False,
        )

        self.assertEqual(first_submit_response.status_code, 303)

        second_form_response = self.url_open(first_submit_response.headers["Location"])
        self.assertEqual(second_form_response.status_code, 200)
        self.assertIn("La demande de paiement a ete creee en brouillon.", second_form_response.text)

        second_submit_response = self.url_open(
            f"/my/evm/cases/{self.accepted_case.id}/payment-requests/create",
            data={
                "csrf_token": self._extract_csrf_token(second_form_response.text),
                "sessions_count": "2",
                "amount_total": "98.76",
            },
            allow_redirects=False,
        )

        self.assertEqual(second_submit_response.status_code, 303)
        created_requests = self.env["evm.payment_request"].sudo().search(
            [
                ("case_id", "=", self.accepted_case.id),
                ("patient_user_id", "=", self.patient_user.id),
                ("amount_total", "in", (123.45, 98.76)),
            ]
        )
        self.assertEqual(len(created_requests), 2)
        self.assertEqual(set(created_requests.mapped("sessions_count")), {4, 2})
        self.assertEqual(set(created_requests.mapped("state")), {"draft"})

    def test_patient_portal_payment_request_form_can_create_attach_and_submit_request(self):
        self.authenticate(self.patient_login, self.patient_password)

        form_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}/payment-requests/new")

        submit_response = self.url_open(
            f"/my/evm/cases/{self.accepted_case.id}/payment-requests/create",
            data={
                "csrf_token": self._extract_csrf_token(form_response.text),
                "sessions_count": "3",
                "amount_total": "150.00",
                "submission_mode": "submit",
            },
            files=[("documents", ("facture-creation.pdf", BytesIO(MINIMAL_PDF), "application/pdf"))],
            allow_redirects=False,
        )

        self.assertEqual(submit_response.status_code, 303)
        self.assertRegex(submit_response.headers["Location"], rf"/my/evm/cases/{self.accepted_case.id}$")

        payment_request = self.env["evm.payment_request"].sudo().search(
            [
                ("case_id", "=", self.accepted_case.id),
                ("patient_user_id", "=", self.patient_user.id),
                ("sessions_count", "=", 3),
                ("amount_total", "=", 150.0),
            ],
            limit=1,
        )
        self.assertTrue(payment_request)
        self.assertEqual(payment_request.state, "submitted")
        self.assertTrue(
            self.env["ir.attachment"].sudo().search_count(
                [
                    ("res_model", "=", "evm.payment_request"),
                    ("res_id", "=", payment_request.id),
                    ("name", "=", "facture-creation.pdf"),
                ]
            )
        )

        success_response = self.url_open(submit_response.headers["Location"])
        response_text = html.unescape(success_response.text)
        self.assertIn("La demande de paiement a ete creee puis soumise a la fondation.", response_text)
        self.assertIn("facture-creation.pdf", response_text)

    def test_patient_portal_payment_request_form_rejects_direct_submission_without_documents(self):
        self.authenticate(self.patient_login, self.patient_password)

        form_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}/payment-requests/new")
        response = self.url_open(
            f"/my/evm/cases/{self.accepted_case.id}/payment-requests/create",
            data={
                "csrf_token": self._extract_csrf_token(form_response.text),
                "sessions_count": "2",
                "amount_total": "45",
                "submission_mode": "submit",
            },
        )
        response_text = html.unescape(response.text)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Ajoutez au moins un justificatif avant de soumettre la demande.", response_text)
        self.assertFalse(
            self.env["evm.payment_request"].sudo().search(
                [
                    ("case_id", "=", self.accepted_case.id),
                    ("patient_user_id", "=", self.patient_user.id),
                    ("sessions_count", "=", 2),
                    ("amount_total", "=", 45.0),
                ]
            )
        )

    def test_patient_portal_payment_request_form_shows_french_errors_and_preserves_data(self):
        self.authenticate(self.patient_login, self.patient_password)

        form_response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}/payment-requests/new")
        response = self.url_open(
            f"/my/evm/cases/{self.accepted_case.id}/payment-requests/create",
            data={
                "csrf_token": self._extract_csrf_token(form_response.text),
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
            self._create_workflow_payment_request(
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
            self._create_workflow_payment_request(
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
