import base64

from odoo.tests import tagged
from odoo.tests.common import HttpCase, new_test_user

MINIMAL_PDF = base64.b64decode(
    "JVBERi0xLjEKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCAxMDAgMTAwXSA+PgplbmRvYmoKdHJhaWxlcgo8PCAvUm9vdCAxIDAgUiA+PgolJUVPRgo="
)


@tagged("post_install", "-at_install")
class TestEvmPaymentRequestWebTour(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kine_user = new_test_user(
            cls.env,
            login="kine_payment_request_web_tour",
            groups="evm.group_evm_kine",
            name="Kine Tour Paiement",
        )
        cls.patient_login = "patient_payment_request_web_tour"
        cls.patient_password = cls.patient_login
        cls.patient_user = new_test_user(
            cls.env,
            login=cls.patient_login,
            groups="evm.group_evm_patient",
            name="Patient Tour Paiement",
        )
        cls.foundation_login = "foundation_payment_request_web_tour"
        cls.foundation_password = cls.foundation_login
        cls.foundation_user = new_test_user(
            cls.env,
            login=cls.foundation_login,
            groups="evm.group_evm_fondation",
            name="Fondation Tour Paiement",
        )
        cls.accepted_case = cls.env["evm.case"].create(
            {
                "name": "Dossier patient tour paiement externe",
                "kine_user_id": cls.kine_user.id,
                "patient_user_id": cls.patient_user.id,
                "state": "accepted",
                "requested_session_count": 20,
                "authorized_session_count": 12,
            }
        )
        cls.payment_request = cls.env["evm.payment_request"].with_user(cls.patient_user).create(
            {
                "name": "Demande tour paiement externe",
                "case_id": cls.accepted_case.id,
                "sessions_count": 2,
                "amount_total": 75.0,
            }
        )
        cls.env["ir.attachment"].sudo().create(
            {
                "name": "facture-tour-paiement-externe.pdf",
                "datas": base64.b64encode(MINIMAL_PDF),
                "mimetype": "application/pdf",
                "res_model": "evm.payment_request",
                "res_id": cls.payment_request.id,
                "evm_patient_visible": True,
            }
        )

    def test_patient_submission_then_foundation_external_payment_confirmation(self):
        self.start_tour("/my/evm/cases", "evm_patient_submit_payment_request_tour", login=self.patient_login)

        self.payment_request.invalidate_recordset(["state"])
        self.assertEqual(self.payment_request.state, "submitted")

        self.start_tour(
            "/odoo/action-evm.evm_payment_request_action",
            "evm_foundation_confirm_external_payment_tour",
            login=self.foundation_login,
        )

        self.payment_request.invalidate_recordset(["state", "payment_id"])
        self.accepted_case.invalidate_recordset(["sessions_consumed", "remaining_session_count"])

        self.assertEqual(self.payment_request.state, "paid")
        self.assertTrue(self.payment_request.payment_id)
        self.assertEqual(self.payment_request.payment_id.state, "draft")
        self.assertEqual(self.accepted_case.sessions_consumed, 2)
        self.assertEqual(self.accepted_case.remaining_session_count, 10)
        request_messages = self.env["mail.message"].sudo().search(
            [("model", "=", "evm.payment_request"), ("res_id", "=", self.payment_request.id)]
        )
        case_messages = self.env["mail.message"].sudo().search(
            [("model", "=", "evm.case"), ("res_id", "=", self.accepted_case.id)]
        )
        self.assertTrue(any("hors plateforme" in (body or "").lower() for body in request_messages.mapped("body")))
        self.assertTrue(any("payee" in (body or "").lower() for body in request_messages.mapped("body")))
        self.assertTrue(any("hors plateforme confirme" in (body or "").lower() for body in case_messages.mapped("body")))

        self.authenticate(self.patient_login, self.patient_password)
        response = self.url_open(f"/my/evm/cases/{self.accepted_case.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Demande tour paiement externe", response.text)
        self.assertIn("Payee", response.text)
        self.assertIn("Seances consommees", response.text)
        self.assertIn("Seances restantes", response.text)
        self.assertNotIn("Soumettre la demande", response.text)
