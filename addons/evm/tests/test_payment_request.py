import base64
from io import BytesIO

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user
from werkzeug.datastructures import FileStorage

MINIMAL_PDF = base64.b64decode(
    "JVBERi0xLjEKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCAxMDAgMTAwXSA+PgplbmRvYmoKdHJhaWxlcgo8PCAvUm9vdCAxIDAgUiA+PgolJUVPRgo="
)
MINIMAL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aF9sAAAAASUVORK5CYII="
)


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

    def test_portal_attachment_upload_creates_patient_visible_history_without_overwrite(self):
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )

        existing_attachment = payment_request.with_user(self.patient_user).portal_upload_attachments(
            [
                FileStorage(
                    stream=BytesIO(MINIMAL_PDF),
                    filename="facture.pdf",
                    content_type="application/pdf",
                )
            ]
        )
        uploaded_attachments = payment_request.with_user(self.patient_user).portal_upload_attachments(
            [
                FileStorage(
                    stream=BytesIO(MINIMAL_PDF),
                    filename="facture.pdf",
                    content_type="application/pdf",
                ),
                FileStorage(
                    stream=BytesIO(MINIMAL_PNG),
                    filename="justificatif.png",
                    content_type="image/png",
                ),
            ]
        )

        self.assertEqual(len(existing_attachment), 1)
        self.assertEqual(len(uploaded_attachments), 2)
        self.assertEqual(
            self.env["ir.attachment"].search_count(
                [
                    ("res_model", "=", "evm.payment_request"),
                    ("res_id", "=", payment_request.id),
                    ("name", "=", "facture.pdf"),
                ]
            ),
            2,
        )
        self.assertTrue(all(uploaded_attachments.mapped("evm_patient_visible")))

    def test_portal_attachment_upload_rejects_invalid_type_and_oversized_file(self):
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )

        with self.assertRaisesRegex(ValidationError, "Formats autorises"):
            payment_request.with_user(self.patient_user).portal_upload_attachments(
                [
                    FileStorage(
                        stream=BytesIO(b"exe"),
                        filename="piece.exe",
                        content_type="application/octet-stream",
                    )
                ]
            )

        with self.assertRaisesRegex(ValidationError, "ne correspond pas"):
            payment_request.with_user(self.patient_user).portal_upload_attachments(
                [
                    FileStorage(
                        stream=BytesIO(b"ceci n'est pas un pdf"),
                        filename="facture.pdf",
                        content_type="application/pdf",
                    )
                ]
            )

        with self.assertRaisesRegex(ValidationError, "10 Mo"):
            payment_request.with_user(self.patient_user).portal_upload_attachments(
                [
                    FileStorage(
                        stream=BytesIO(b"0" * (10 * 1024 * 1024 + 1)),
                        filename="facture.pdf",
                        content_type="application/pdf",
                    )
                ]
            )

        with self.assertRaisesRegex(ValidationError, "vides"):
            payment_request.with_user(self.patient_user).portal_upload_attachments(
                [
                    FileStorage(
                        stream=BytesIO(b""),
                        filename="facture.pdf",
                        content_type="application/pdf",
                    )
                ]
            )

    def test_portal_attachment_upload_requires_owned_draft_request(self):
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )
        other_case = self.env["evm.case"].create(
            {
                "name": "Dossier autre patient pieces",
                "kine_user_id": self.kine_user.id,
                "patient_user_id": self.other_patient_user.id,
                "state": "accepted",
                "requested_session_count": 10,
            }
        )
        other_payment_request = self.env["evm.payment_request"].create(
            {
                "case_id": other_case.id,
                "sessions_count": 1,
            }
        )

        payment_request.sudo().with_context(evm_allow_payment_request_workflow_write=True).write({"state": "submitted"})

        with self.assertRaises(AccessError):
            other_payment_request.with_user(self.patient_user).portal_upload_attachments(
                [
                    FileStorage(
                        stream=BytesIO(b"pdf"),
                        filename="facture.pdf",
                        content_type="application/pdf",
                    )
                ]
            )

        with self.assertRaises(AccessError):
            payment_request.with_user(self.patient_user).portal_upload_attachments(
                [
                    FileStorage(
                        stream=BytesIO(b"pdf"),
                        filename="facture.pdf",
                        content_type="application/pdf",
                    )
                ]
            )

    def test_payment_request_completeness_requires_patient_visible_attachment(self):
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )

        self.assertFalse(payment_request.is_complete_for_submission())
        self.assertEqual(
            payment_request.get_submission_errors(),
            ["Ajoutez au moins un justificatif avant de soumettre la demande."],
        )

        payment_request.with_user(self.patient_user).portal_upload_attachments(
            [
                FileStorage(
                    stream=BytesIO(MINIMAL_PDF),
                    filename="piece-complete.pdf",
                    content_type="application/pdf",
                )
            ]
        )

        self.assertTrue(payment_request.is_complete_for_submission())
        self.assertEqual(payment_request.get_submission_errors(), [])

    def test_patient_can_submit_complete_request_and_foundation_can_find_it(self):
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "amount_total": 45,
            }
        )
        payment_request.with_user(self.patient_user).portal_upload_attachments(
            [
                FileStorage(
                    stream=BytesIO(MINIMAL_PDF),
                    filename="facture-soumission.pdf",
                    content_type="application/pdf",
                )
            ]
        )
        foundation_user = new_test_user(self.env, login="fondation_payment_request", groups="evm.group_evm_fondation")

        payment_request.with_user(self.patient_user).action_submit()

        self.assertEqual(payment_request.state, "submitted")
        self.assertTrue(payment_request.submitted_on)
        submission_messages = self.env["mail.message"].sudo().search(
            [("model", "=", "evm.payment_request"), ("res_id", "=", payment_request.id)]
        )
        self.assertTrue(any("soumise" in (body or "").lower() for body in submission_messages.mapped("body")))
        self.assertEqual(
            self.env["evm.payment_request"].with_user(foundation_user).search([("state", "=", "submitted")]),
            payment_request,
        )

    def test_foundation_can_open_submitted_request_attachments_from_processing_flow(self):
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )
        attachment = payment_request.with_user(self.patient_user).portal_upload_attachments(
            [
                FileStorage(
                    stream=BytesIO(MINIMAL_PDF),
                    filename="piece-foundation.pdf",
                    content_type="application/pdf",
                )
            ]
        )
        foundation_user = new_test_user(self.env, login="fondation_payment_request_docs", groups="evm.group_evm_fondation")
        payment_request.with_user(self.patient_user).action_submit()

        payment_request_as_foundation = payment_request.with_user(foundation_user)
        self.assertEqual(payment_request_as_foundation.attachment_count, 1)
        self.assertEqual(payment_request_as_foundation.attachment_ids, attachment)

        action = payment_request_as_foundation.action_open_attachments()
        self.assertEqual(action["res_model"], "ir.attachment")
        self.assertEqual(action["view_mode"], "list,form")
        self.assertEqual(action["domain"], [("res_model", "=", "evm.payment_request"), ("res_id", "=", payment_request.id), ("res_field", "=", False), ("type", "=", "binary")])
        self.assertFalse(action["context"]["create"])

    def test_internal_users_cannot_manually_create_or_delete_payment_requests(self):
        foundation_user = new_test_user(self.env, login="fondation_payment_request_manual", groups="evm.group_evm_fondation")
        payment_request = self.env["evm.payment_request"].create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )

        with self.assertRaisesRegex(AccessError, "creation manuelle"):
            self.env["evm.payment_request"].with_user(foundation_user).create(
                {
                    "case_id": self.accepted_case.id,
                    "sessions_count": 3,
                }
            )
        with self.assertRaisesRegex(AccessError, "suppression manuelle"):
            payment_request.with_user(foundation_user).unlink()

    def test_submission_rejects_incomplete_request_and_state_replay(self):
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )

        with self.assertRaisesRegex(ValidationError, "justificatif"):
            payment_request.with_user(self.patient_user).action_submit()

        payment_request.with_user(self.patient_user).portal_upload_attachments(
            [
                FileStorage(
                    stream=BytesIO(MINIMAL_PDF),
                    filename="piece-submit.pdf",
                    content_type="application/pdf",
                )
            ]
        )
        payment_request.with_user(self.patient_user).action_submit()

        with self.assertRaisesRegex(ValidationError, "brouillon"):
            payment_request.with_user(self.patient_user).action_submit()

    def test_foundation_processing_action_defaults_to_submitted_queue(self):
        action = self.env.ref("evm.evm_payment_request_action")
        menu = self.env.ref("evm.evm_menu_payment_requests")
        list_view = self.env.ref("evm.evm_payment_request_view_list")
        form_view = self.env.ref("evm.evm_payment_request_view_form")

        self.assertEqual(action.res_model, "evm.payment_request")
        self.assertIn("'search_default_submitted': 1", action.context)
        self.assertEqual(menu.action.id, action.id)
        self.assertIn('create="false"', list_view.arch_db)
        self.assertIn('delete="false"', form_view.arch_db)
        self.assertIn("attachment_ids", form_view.arch_db)
