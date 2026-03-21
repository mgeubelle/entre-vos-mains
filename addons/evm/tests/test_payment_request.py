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
    def _get_or_create_company_account(cls, account_type, code, name):
        account = cls.env["account.account"].search(
            [
                ("account_type", "=", account_type),
                ("company_ids", "in", cls.env.company.id),
            ],
            limit=1,
        )
        if account:
            return account
        return cls.env["account.account"].create(
            {
                "name": name,
                "code": code,
                "account_type": account_type,
                "company_ids": [(4, cls.env.company.id)],
            }
        )

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
        cls.receivable_account = cls._get_or_create_company_account(
            "asset_receivable",
            "136000",
            "Compte client EVM",
        )
        cls.payable_account = cls._get_or_create_company_account(
            "liability_payable",
            "236000",
            "Compte fournisseur EVM",
        )
        for partner in (cls.patient_user.partner_id, cls.other_patient_user.partner_id):
            partner.with_company(cls.env.company).write(
                {
                    "property_account_receivable_id": cls.receivable_account.id,
                    "property_account_payable_id": cls.payable_account.id,
                }
            )
        cls.payment_journal = cls.env["account.journal"].search(
            [
                ("company_id", "=", cls.env.company.id),
                ("type", "in", ("bank", "cash", "credit")),
                ("outbound_payment_method_line_ids", "!=", False),
            ],
            limit=1,
        )
        if not cls.payment_journal:
            cash_account = cls._get_or_create_company_account(
                "asset_cash",
                "570360",
                "Tresorerie paiements EVM",
            )
            cls.payment_journal = cls.env["account.journal"].create(
                {
                    "name": "Journal paiements EVM",
                    "code": "E36JV",
                    "type": "cash",
                    "company_id": cls.env.company.id,
                    "default_account_id": cash_account.id,
                }
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
        self.assertIn("completion_request_reason", payment_request_model._fields)
        self.assertIn("refusal_reason", payment_request_model._fields)
        self.assertIn("payment_id", payment_request_model._fields)
        self.assertTrue(payment_request_model._fields["payment_id"].tracking)
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

    def _create_internal_payment_request(self, values):
        payment_request = self.env["evm.payment_request"].with_context(
            evm_allow_payment_request_workflow_write=True
        ).create(values)
        return self.env["evm.payment_request"].browse(payment_request.ids)

    def _build_payment_reference(self, payment_request_name, case_name=None):
        return f"Demande {payment_request_name} - {case_name or self.accepted_case.name}"

    def _capture_mail_ids(self):
        return set(self.env["mail.mail"].sudo().search([]).ids)

    def _capture_notification_ids(self):
        return set(self.env["mail.message"].sudo().search([("message_type", "=", "notification")]).ids)

    def _capture_mail_notification_ids(self):
        return set(self.env["mail.notification"].sudo().search([]).ids)

    def _get_new_mails(self, before_ids):
        return self.env["mail.mail"].sudo().browse(
            sorted(set(self.env["mail.mail"].sudo().search([]).ids) - before_ids)
        )

    def _get_new_notifications(self, before_ids):
        return self.env["mail.message"].sudo().browse(
            sorted(
                set(self.env["mail.message"].sudo().search([("message_type", "=", "notification")]).ids) - before_ids
            )
        )

    def _get_new_mail_notifications(self, before_ids):
        return self.env["mail.notification"].sudo().browse(
            sorted(set(self.env["mail.notification"].sudo().search([]).ids) - before_ids)
        )

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

    def test_validate_portal_creation_data_rejects_non_finite_amounts(self):
        payment_request_model = self.env["evm.payment_request"]

        for raw_amount in ("NaN", "Infinity", "-Infinity", "1e309"):
            with self.subTest(raw_amount=raw_amount):
                cleaned_values, errors = payment_request_model.validate_portal_creation_data(
                    {"sessions_count": "2", "amount_total": raw_amount}
                )
                self.assertFalse(cleaned_values["amount_total"])
                self.assertIn("amount_total", errors)

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

    def test_patient_cannot_mutate_or_comment_on_request_when_related_case_is_closed(self):
        closed_case = self.env["evm.case"].create(
            {
                "name": "Dossier cloture mutation",
                "kine_user_id": self.kine_user.id,
                "patient_user_id": self.patient_user.id,
                "state": "closed",
                "requested_session_count": 8,
                "authorized_session_count": 8,
            }
        )
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande brouillon dossier clos",
                "case_id": closed_case.id,
                "sessions_count": 2,
                "state": "draft",
            }
        )

        with self.assertRaisesRegex(AccessError, "lecture"):
            payment_request.with_user(self.patient_user).write({"name": "Tentative tardive"})
        with self.assertRaisesRegex(AccessError, "lecture"):
            payment_request.with_user(self.patient_user).action_post_comment("Commentaire tardif")

    def test_patient_cannot_inject_system_fields_when_creating_a_request(self):
        existing_payment = self.env["account.payment"].sudo().create(
            {
                "partner_id": self.patient_user.partner_id.id,
                "payment_type": "outbound",
                "partner_type": "customer",
                "amount": 75.0,
                "journal_id": self.payment_journal.id,
                "payment_method_line_id": self.payment_journal.outbound_payment_method_line_ids[:1].id,
                "currency_id": self.env.company.currency_id.id,
                "memo": "Paiement existant EVM",
            }
        )

        with self.assertRaisesRegex(AccessError, "workflow"):
            self.env["evm.payment_request"].with_user(self.patient_user).create(
                {
                    "case_id": self.accepted_case.id,
                    "sessions_count": 2,
                    "payment_id": existing_payment.id,
                }
            )

        with self.assertRaisesRegex(AccessError, "workflow"):
            self.env["evm.payment_request"].with_user(self.patient_user).create(
                {
                    "case_id": self.accepted_case.id,
                    "sessions_count": 2,
                    "refusal_reason": "Champ reserve",
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

    def test_patient_can_only_edit_resumable_requests(self):
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

        payment_request.sudo().with_context(evm_allow_payment_request_workflow_write=True).write(
            {
                "state": "to_complete",
                "completion_request_reason": "Merci d'ajouter la facture manquante.",
            }
        )

        payment_request.with_user(self.patient_user).write({"name": "Demande patient a completer"})
        self.assertEqual(payment_request.name, "Demande patient a completer")

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
        self.assertTrue(
            any("Systeme:" in (body or "") and "soumise" in (body or "").lower() for body in submission_messages.mapped("body"))
        )
        self.assertEqual(
            self.env["evm.payment_request"].with_user(foundation_user).search(
                [("state", "=", "submitted"), ("id", "=", payment_request.id)]
            ),
            payment_request,
        )

    def test_submission_notifies_foundation_only_with_internal_notification(self):
        self.patient_user.partner_id.write({"email": "patient.payment.request@example.com"})
        foundation_user = new_test_user(
            self.env,
            login="fondation.payment.request.notifications@example.com",
            groups="evm.group_evm_fondation",
        )
        foundation_user.write({"notification_type": "inbox"})
        foundation_user.partner_id.write({"email": "fondation.payment.request.notifications@example.com"})
        observer_user = new_test_user(
            self.env,
            login="observer.payment.request.notifications@example.com",
            groups="base.group_user",
        )
        observer_user.write({"notification_type": "inbox"})
        observer_user.partner_id.write({"email": "observer.payment.request.notifications@example.com"})
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "name": "Demande notification soumission",
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "amount_total": 80.0,
            }
        )
        payment_request.with_user(self.patient_user).portal_upload_attachments(
            [
                FileStorage(
                    stream=BytesIO(MINIMAL_PDF),
                    filename="facture-notification-soumission.pdf",
                    content_type="application/pdf",
                )
            ]
        )
        mail_ids_before = self._capture_mail_ids()
        notification_ids_before = self._capture_notification_ids()

        payment_request.with_user(self.patient_user).action_submit()

        notification_mails = self._get_new_mails(mail_ids_before).filtered(
            lambda mail: mail.subject == f"Entre Vos Mains - demande de paiement soumise : {payment_request.name}"
        )
        inbox_notifications = self._get_new_notifications(notification_ids_before).filtered(
            lambda message: message.subject == f"Entre Vos Mains - demande de paiement soumise : {payment_request.name}"
        )

        self.assertTrue(notification_mails or inbox_notifications)
        if notification_mails:
            self.assertFalse(notification_mails.filtered(lambda mail: self.patient_user.partner_id.email in (mail.email_to or "")))
            self.assertFalse(notification_mails.filtered(lambda mail: observer_user.partner_id.email in (mail.email_to or "")))
            self.assertIn(payment_request.name, notification_mails.body_html)
            self.assertIn("Soumise", notification_mails.body_html)
        if inbox_notifications:
            self.assertEqual(inbox_notifications.partner_ids, foundation_user.partner_id)
            self.assertNotIn(self.patient_user.partner_id, inbox_notifications.partner_ids)
            self.assertNotIn(observer_user.partner_id, inbox_notifications.partner_ids)
            self.assertIn(payment_request.name, inbox_notifications.body)
            self.assertIn("Soumise", inbox_notifications.body)

    def test_authorized_users_can_post_comments_on_case_and_request(self):
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_comment",
            groups="evm.group_evm_fondation",
        )
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "amount_total": 45,
            }
        )

        self.accepted_case.with_user(self.patient_user).action_post_comment("Question patient sur le dossier")
        payment_request.with_user(foundation_user).action_post_comment("Reponse fondation sur la demande")

        case_messages = self.env["mail.message"].sudo().search(
            [("model", "=", "evm.case"), ("res_id", "=", self.accepted_case.id)]
        )
        request_messages = self.env["mail.message"].sudo().search(
            [("model", "=", "evm.payment_request"), ("res_id", "=", payment_request.id)]
        )

        self.assertTrue(any("Question patient sur le dossier" in (body or "") for body in case_messages.mapped("body")))
        self.assertTrue(any("Reponse fondation sur la demande" in (body or "") for body in request_messages.mapped("body")))
        self.assertTrue(any(message.author_id == self.patient_user.partner_id for message in case_messages))
        self.assertTrue(any(message.author_id == foundation_user.partner_id for message in request_messages))

    def test_comment_posting_requires_authorized_actor_and_non_empty_body(self):
        other_patient_user = new_test_user(
            self.env,
            login="other_patient_request_comment",
            groups="evm.group_evm_patient",
        )
        kine_user = new_test_user(
            self.env,
            login="kine_request_comment_forbidden",
            groups="evm.group_evm_kine",
        )
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )

        with self.assertRaisesRegex(ValidationError, "commentaire"):
            self.accepted_case.with_user(self.patient_user).action_post_comment("   ")

        self.accepted_case.with_user(self.kine_user).action_post_comment("Commentaire kine autorise")
        case_messages = self.env["mail.message"].sudo().search(
            [("model", "=", "evm.case"), ("res_id", "=", self.accepted_case.id)]
        )
        self.assertTrue(any("Commentaire kine autorise" in (body or "") for body in case_messages.mapped("body")))

        with self.assertRaises(AccessError):
            self.accepted_case.with_user(kine_user).action_post_comment("Commentaire non autorise")

        with self.assertRaises(AccessError):
            payment_request.with_user(other_patient_user).action_post_comment("Commentaire non autorise")

    def test_foundation_can_return_submitted_request_to_complete_with_reason_and_history(self):
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
                    filename="facture-retour.pdf",
                    content_type="application/pdf",
                )
            ]
        )
        foundation_user = new_test_user(self.env, login="fondation_payment_request_return", groups="evm.group_evm_fondation")
        payment_request.with_user(self.patient_user).action_submit()

        result = payment_request.with_user(foundation_user).action_return_to_complete(
            "Merci d'ajouter une facture lisible et le detail des seances."
        )

        self.assertTrue(result)
        self.assertEqual(payment_request.state, "to_complete")
        self.assertEqual(
            payment_request.completion_request_reason,
            "Merci d'ajouter une facture lisible et le detail des seances.",
        )
        history_messages = self.env["mail.message"].sudo().search(
            [("model", "=", "evm.payment_request"), ("res_id", "=", payment_request.id)]
        )
        self.assertTrue(
            any("Systeme:" in (body or "") and "retournee" in (body or "").lower() for body in history_messages.mapped("body"))
        )
        self.assertTrue(any("detail des seances" in (body or "").lower() for body in history_messages.mapped("body")))

    def test_return_to_complete_notifies_patient_with_email(self):
        self.patient_user.partner_id.write({"email": "patient.payment.request@example.com"})
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande notification retour",
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "state": "submitted",
                "amount_total": 80.0,
            }
        )
        foundation_user = new_test_user(
            self.env,
            login="fondation.payment.request.return.notifications@example.com",
            groups="evm.group_evm_fondation",
        )
        foundation_user.write({"notification_type": "inbox"})
        foundation_user.partner_id.write({"email": "fondation.payment.request.return.notifications@example.com"})
        mail_ids_before = self._capture_mail_ids()

        payment_request.with_user(foundation_user).action_return_to_complete("Merci d'ajouter une facture lisible.")

        notification_mails = self._get_new_mails(mail_ids_before).filtered(
            lambda mail: mail.subject == f"Entre Vos Mains - demande a completer : {payment_request.name}"
        )

        self.assertEqual(len(notification_mails), 1)
        self.assertEqual(notification_mails.email_to, self.patient_user.partner_id.email)
        self.assertEqual(notification_mails.email_from, foundation_user.partner_id.email_formatted)
        self.assertIn(payment_request.name, notification_mails.body_html)
        self.assertIn("A completer", notification_mails.body_html)
        self.assertIn(f"/my/evm/cases/{payment_request.case_id.id}", notification_mails.body_html)
        self.assertIn("facture lisible", notification_mails.body_html)

    def test_foundation_can_refuse_submitted_request_with_reason_history_and_active_queue_exit(self):
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "amount_total": 45,
            }
        )
        foundation_user = new_test_user(self.env, login="fondation_payment_request_refusal", groups="evm.group_evm_fondation")
        payment_request.with_user(self.patient_user).portal_upload_attachments(
            [
                FileStorage(
                    stream=BytesIO(MINIMAL_PDF),
                    filename="facture-refus.pdf",
                    content_type="application/pdf",
                )
            ]
        )
        payment_request.with_user(self.patient_user).action_submit()

        result = payment_request.with_user(foundation_user).action_refuse(
            "La demande n'est pas recevable car les seances ne correspondent pas au dossier accepte."
        )

        self.assertTrue(result)
        self.assertEqual(payment_request.state, "refused")
        self.assertEqual(
            payment_request.refusal_reason,
            "La demande n'est pas recevable car les seances ne correspondent pas au dossier accepte.",
        )
        self.assertFalse(payment_request.completion_request_reason)
        history_messages = self.env["mail.message"].sudo().search(
            [("model", "=", "evm.payment_request"), ("res_id", "=", payment_request.id)]
        )
        self.assertTrue(
            any("Systeme:" in (body or "") and "refusee" in (body or "").lower() for body in history_messages.mapped("body"))
        )
        self.assertTrue(any("pas recevable" in (body or "").lower() for body in history_messages.mapped("body")))
        self.assertFalse(
            self.env["evm.payment_request"].with_user(foundation_user).search([("state", "=", "submitted"), ("id", "=", payment_request.id)])
        )
        self.assertEqual(
            self.env["evm.payment_request"].with_user(foundation_user).search([("state", "=", "refused"), ("id", "=", payment_request.id)]),
            payment_request,
        )

    def test_patient_can_complete_request_to_complete_and_resubmit_it(self):
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
                    filename="facture-resoumise.pdf",
                    content_type="application/pdf",
                )
            ]
        )
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_resubmit",
            groups="evm.group_evm_fondation",
        )
        payment_request.with_user(self.patient_user).action_submit()
        payment_request.with_user(foundation_user).action_return_to_complete("Merci d'ajouter une preuve complementaire.")

        payment_request.with_user(self.patient_user).write(
            {
                "name": "Demande patient completee",
                "amount_total": 60,
            }
        )
        added_attachments = payment_request.with_user(self.patient_user).portal_upload_attachments(
            [
                FileStorage(
                    stream=BytesIO(MINIMAL_PNG),
                    filename="preuve-complementaire.png",
                    content_type="image/png",
                )
            ]
        )
        result = payment_request.with_user(self.patient_user).action_submit()

        self.assertTrue(result)
        self.assertEqual(payment_request.state, "submitted")
        self.assertFalse(payment_request.completion_request_reason)
        self.assertEqual(payment_request.name, "Demande patient completee")
        self.assertEqual(payment_request.amount_total, 60)
        self.assertEqual(len(added_attachments), 1)
        attachment_names = set(payment_request.attachment_ids.mapped("name"))
        self.assertSetEqual(
            attachment_names,
            {"facture-resoumise.pdf", "preuve-complementaire.png"},
        )
        history_messages = self.env["mail.message"].sudo().search(
            [("model", "=", "evm.payment_request"), ("res_id", "=", payment_request.id)]
        )
        self.assertTrue(any("soumise a nouveau" in (body or "").lower() for body in history_messages.mapped("body")))

    def test_patient_can_update_request_to_complete_without_losing_history(self):
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
                    filename="facture-initiale.pdf",
                    content_type="application/pdf",
                )
            ]
        )
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_edit_followup",
            groups="evm.group_evm_fondation",
        )
        payment_request.with_user(self.patient_user).action_submit()
        payment_request.with_user(foundation_user).action_return_to_complete(
            "Merci de preciser le nombre de seances remboursees."
        )

        payment_request.with_user(self.patient_user).write(
            {
                "name": "Demande completee apres retour",
                "sessions_count": 4,
                "amount_total": 60,
            }
        )

        self.assertEqual(payment_request.state, "to_complete")
        self.assertEqual(payment_request.name, "Demande completee apres retour")
        self.assertEqual(payment_request.sessions_count, 4)
        self.assertEqual(payment_request.amount_total, 60)
        self.assertEqual(payment_request.attachment_ids.mapped("name"), ["facture-initiale.pdf"])
        history_messages = self.env["mail.message"].sudo().search(
            [("model", "=", "evm.payment_request"), ("res_id", "=", payment_request.id)]
        )
        self.assertTrue(any("retournee" in (body or "").lower() for body in history_messages.mapped("body")))

    def test_return_to_complete_requires_foundation_user_submitted_state_and_reason(self):
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_return_rules",
            groups="evm.group_evm_fondation",
        )

        with self.assertRaises(AccessError):
            payment_request.with_user(self.patient_user).action_return_to_complete("Demande incomplete.")

        with self.assertRaises(AccessError):
            payment_request.with_user(foundation_user).write({"completion_request_reason": "Merci d'ajouter la facture."})

        with self.assertRaisesRegex(ValidationError, "soumise"):
            payment_request.with_user(foundation_user).action_return_to_complete("Merci d'ajouter la facture.")

        payment_request.with_user(self.patient_user).portal_upload_attachments(
            [
                FileStorage(
                    stream=BytesIO(MINIMAL_PDF),
                    filename="facture-retour-regles.pdf",
                    content_type="application/pdf",
                )
            ]
        )
        payment_request.with_user(self.patient_user).action_submit()

        with self.assertRaisesRegex(ValidationError, "motif"):
            payment_request.with_user(foundation_user).action_return_to_complete("   ")

        payment_request.with_user(foundation_user).action_return_to_complete("Merci d'ajouter la facture.")

        with self.assertRaises(AccessError):
            payment_request.with_user(foundation_user).write({"completion_request_reason": "Nouveau motif"})

        with self.assertRaisesRegex(ValidationError, "soumise"):
            payment_request.with_user(foundation_user).action_return_to_complete("Nouveau motif")

    def test_foundation_can_prepare_reason_inline_and_return_to_complete_from_form(self):
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )
        payment_request.with_user(self.patient_user).portal_upload_attachments(
            [
                FileStorage(
                    stream=BytesIO(MINIMAL_PDF),
                    filename="facture-retour-wizard.pdf",
                    content_type="application/pdf",
                )
            ]
        )
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_return_wizard",
            groups="evm.group_evm_fondation",
        )
        payment_request.with_user(self.patient_user).action_submit()

        payment_request.with_user(foundation_user).write(
            {
                "completion_request_reason": "Merci d'ajouter le justificatif manquant.",
            }
        )
        action_result = payment_request.with_user(foundation_user).action_return_to_complete()
        form_view = self.env.ref("evm.evm_payment_request_view_form")

        self.assertTrue(action_result)
        self.assertEqual(payment_request.state, "to_complete")
        self.assertEqual(payment_request.completion_request_reason, "Merci d'ajouter le justificatif manquant.")
        self.assertIn('name="action_return_to_complete"', form_view.arch_db)
        self.assertIn('name="completion_request_reason"', form_view.arch_db)
        self.assertIn("readonly=\"state != 'submitted'\"", form_view.arch_db)
        self.assertNotIn('name="completion_request_reason" required="state == \'submitted\'"', form_view.arch_db)
        self.assertNotIn("required=\"state == 'submitted'\"", form_view.arch_db)

    def test_foundation_can_prepare_refusal_reason_inline_and_refuse_from_form(self):
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_refusal_form",
            groups="evm.group_evm_fondation",
        )
        payment_request.with_user(self.patient_user).portal_upload_attachments(
            [
                FileStorage(
                    stream=BytesIO(MINIMAL_PDF),
                    filename="facture-refus-form.pdf",
                    content_type="application/pdf",
                )
            ]
        )
        payment_request.with_user(self.patient_user).action_submit()

        payment_request.with_user(foundation_user).write(
            {
                "refusal_reason": "Refus fonde sur des seances hors perimetre.",
            }
        )
        action_result = payment_request.with_user(foundation_user).action_refuse()
        form_view = self.env.ref("evm.evm_payment_request_view_form")

        self.assertTrue(action_result)
        self.assertEqual(payment_request.state, "refused")
        self.assertEqual(payment_request.refusal_reason, "Refus fonde sur des seances hors perimetre.")
        self.assertIn('name="action_refuse"', form_view.arch_db)
        self.assertIn('name="refusal_reason"', form_view.arch_db)
        self.assertIn("readonly=\"state != 'submitted'\"", form_view.arch_db)
        self.assertNotIn('name="refusal_reason" required="state == \'submitted\'"', form_view.arch_db)
        self.assertNotIn("required=\"state == 'submitted'\"", form_view.arch_db)

    def test_refusal_requires_foundation_user_submitted_state_reason_and_blocks_later_transitions(self):
        payment_request = self.env["evm.payment_request"].with_user(self.patient_user).create(
            {
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
            }
        )
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_refusal_rules",
            groups="evm.group_evm_fondation",
        )

        with self.assertRaises(AccessError):
            payment_request.with_user(self.patient_user).action_refuse("Demande non recevable.")

        with self.assertRaises(AccessError):
            payment_request.with_user(foundation_user).write({"refusal_reason": "Motif brouillon"})

        with self.assertRaisesRegex(ValidationError, "soumise"):
            payment_request.with_user(foundation_user).action_refuse("Demande non recevable.")

        payment_request.with_user(self.patient_user).portal_upload_attachments(
            [
                FileStorage(
                    stream=BytesIO(MINIMAL_PDF),
                    filename="facture-refus-regles.pdf",
                    content_type="application/pdf",
                )
            ]
        )
        payment_request.with_user(self.patient_user).action_submit()

        with self.assertRaisesRegex(ValidationError, "motif"):
            payment_request.with_user(foundation_user).action_refuse("   ")

        payment_request.with_user(foundation_user).action_refuse("Demande non recevable.")

        with self.assertRaises(AccessError):
            payment_request.with_user(foundation_user).write({"refusal_reason": "Nouveau motif"})
        with self.assertRaisesRegex(AccessError, "cloturee"):
            payment_request.with_user(foundation_user).write({"amount_total": 99})
        with self.assertRaisesRegex(AccessError, "cloturee"):
            payment_request.with_user(foundation_user).write({"sessions_count": 5})
        with self.assertRaisesRegex(ValidationError, "soumise"):
            payment_request.with_user(foundation_user).action_return_to_complete("Merci de completer.")
        with self.assertRaisesRegex(ValidationError, "brouillon ou a completer"):
            payment_request.with_user(self.patient_user).action_submit()

    def test_foundation_can_validate_submitted_request_with_inline_adjustments_and_update_case_balance(self):
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande validation fondation",
                "case_id": self.accepted_case.id,
                "sessions_count": 3,
                "state": "submitted",
                "amount_total": 90.0,
                "completion_request_reason": "Ancien motif a purger",
                "refusal_reason": "Ancien refus a purger",
            }
        )
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_validate",
            groups="evm.group_evm_fondation",
        )

        payment_request.with_user(foundation_user).write(
            {
                "sessions_count": 4,
                "amount_total": 120.0,
            }
        )
        result = payment_request.with_user(foundation_user).action_validate()

        self.assertTrue(result)
        self.assertEqual(payment_request.state, "validated")
        self.assertEqual(payment_request.sessions_count, 4)
        self.assertEqual(payment_request.amount_total, 120.0)
        self.assertTrue(payment_request.payment_id)
        self.assertEqual(payment_request.payment_id.state, "draft")
        self.assertEqual(payment_request.payment_id.amount, 120.0)
        self.assertEqual(payment_request.payment_id.partner_id, self.patient_user.partner_id)
        self.assertEqual(payment_request.payment_id.journal_id, self.payment_journal)
        self.assertFalse(payment_request.completion_request_reason)
        self.assertFalse(payment_request.refusal_reason)
        self.assertEqual(self.accepted_case.sessions_consumed, 4)
        self.assertEqual(self.accepted_case.remaining_session_count, 8)
        history_messages = self.env["mail.message"].sudo().search(
            [("model", "=", "evm.payment_request"), ("res_id", "=", payment_request.id)]
        )
        public_messages = history_messages.filtered(lambda message: not message.subtype_id or not message.subtype_id.internal)
        internal_messages = history_messages.filtered(lambda message: message.subtype_id and message.subtype_id.internal)
        self.assertTrue(
            any("Systeme:" in (body or "") and "validee" in (body or "").lower() for body in history_messages.mapped("body"))
        )
        self.assertTrue(any("4" in (body or "") for body in history_messages.mapped("body")))
        self.assertTrue(any("paiement" in (body or "").lower() for body in history_messages.mapped("body")))
        self.assertFalse(
            any(payment_request.payment_id.display_name in (body or "") for body in public_messages.mapped("body"))
        )
        self.assertTrue(
            any(payment_request.payment_id.display_name in (body or "") for body in internal_messages.mapped("body"))
        )

    def test_validation_notifies_patient_with_email(self):
        self.patient_user.partner_id.write({"email": "patient.payment.request@example.com"})
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande notification validation",
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "state": "submitted",
                "amount_total": 75.0,
            }
        )
        foundation_user = new_test_user(
            self.env,
            login="fondation.payment.request.validate.notifications@example.com",
            groups="evm.group_evm_fondation",
        )
        foundation_user.write({"notification_type": "inbox"})
        foundation_user.partner_id.write({"email": "fondation.payment.request.validate.notifications@example.com"})
        mail_ids_before = self._capture_mail_ids()

        payment_request.with_user(foundation_user).action_validate()

        notification_mails = self._get_new_mails(mail_ids_before).filtered(
            lambda mail: mail.subject == f"Entre Vos Mains - demande validee : {payment_request.name}"
        )

        self.assertEqual(len(notification_mails), 1)
        self.assertEqual(notification_mails.email_to, self.patient_user.partner_id.email)
        self.assertEqual(notification_mails.email_from, foundation_user.partner_id.email_formatted)
        self.assertIn(payment_request.name, notification_mails.body_html)
        self.assertIn("Validee", notification_mails.body_html)
        self.assertIn("paiement", notification_mails.body_html.lower())

    def test_validation_routes_patient_notification_to_inbox_for_internal_user(self):
        internal_patient = new_test_user(
            self.env,
            login="internal.patient.payment.notifications@example.com",
            groups="base.group_user",
        )
        internal_patient.write({"notification_type": "inbox"})
        internal_patient.partner_id.write({"email": "internal.patient.payment.notifications@example.com"})
        accepted_case = self.env["evm.case"].create(
            {
                "name": "Dossier accepte patient interne",
                "kine_user_id": self.kine_user.id,
                "patient_user_id": internal_patient.id,
                "state": "accepted",
                "requested_session_count": 12,
                "authorized_session_count": 8,
            }
        )
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande notification inbox",
                "case_id": accepted_case.id,
                "sessions_count": 2,
                "state": "submitted",
                "amount_total": 60.0,
            }
        )
        foundation_user = new_test_user(
            self.env,
            login="fondation.payment.request.inbox.notifications@example.com",
            groups="evm.group_evm_fondation",
        )
        mail_ids_before = self._capture_mail_ids()
        mail_notification_ids_before = self._capture_mail_notification_ids()

        payment_request.with_user(foundation_user).action_validate()

        notification_mails = self._get_new_mails(mail_ids_before).filtered(
            lambda mail: mail.subject == f"Entre Vos Mains - demande validee : {payment_request.name}"
        )
        inbox_notifications = self._get_new_mail_notifications(mail_notification_ids_before).filtered(
            lambda notification: notification.mail_message_id.subject == f"Entre Vos Mains - demande validee : {payment_request.name}"
        )

        self.assertFalse(notification_mails)
        self.assertEqual(len(inbox_notifications), 1)
        self.assertEqual(inbox_notifications.res_partner_id, internal_patient.partner_id)
        self.assertEqual(inbox_notifications.notification_type, "inbox")
        self.assertIn(payment_request.name, inbox_notifications.mail_message_id.body)
        self.assertIn("Validee", inbox_notifications.mail_message_id.body)

    def test_validation_requires_foundation_user_submitted_state_and_available_authorized_sessions(self):
        self._create_internal_payment_request(
            {
                "name": "Demande deja validee",
                "case_id": self.accepted_case.id,
                "sessions_count": 10,
                "state": "validated",
            }
        )
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande a valider sous quota",
                "case_id": self.accepted_case.id,
                "sessions_count": 3,
                "state": "submitted",
                "amount_total": 90.0,
            }
        )
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_validate_rules",
            groups="evm.group_evm_fondation",
        )

        with self.assertRaises(AccessError):
            payment_request.with_user(self.patient_user).action_validate()

        with self.assertRaisesRegex(ValidationError, "depasse les seances autorisees"):
            payment_request.with_user(foundation_user).action_validate()

        self.assertEqual(payment_request.state, "submitted")
        self.assertEqual(self.accepted_case.sessions_consumed, 10)
        self.assertEqual(self.accepted_case.remaining_session_count, 2)

        payment_request.with_user(foundation_user).write({"sessions_count": 2})
        payment_request.with_user(foundation_user).action_validate()

        self.assertEqual(payment_request.state, "validated")
        self.assertEqual(self.accepted_case.sessions_consumed, 12)
        self.assertEqual(self.accepted_case.remaining_session_count, 0)

        with self.assertRaisesRegex(ValidationError, "soumise"):
            payment_request.with_user(foundation_user).action_validate()

        with self.assertRaisesRegex(AccessError, "donnees de validation"):
            payment_request.with_user(foundation_user).write({"sessions_count": 1})

    def test_validation_rejects_requests_on_non_accepted_cases(self):
        case = self.env["evm.case"].create(
            {
                "name": "Dossier cloture validation",
                "kine_user_id": self.kine_user.id,
                "patient_user_id": self.patient_user.id,
                "state": "closed",
                "requested_session_count": 6,
                "authorized_session_count": 4,
            }
        )
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande dossier cloture",
                "case_id": case.id,
                "sessions_count": 2,
                "state": "submitted",
                "amount_total": 60.0,
            }
        )
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_validate_closed_case",
            groups="evm.group_evm_fondation",
        )

        with self.assertRaisesRegex(ValidationError, "dossier accepte"):
            payment_request.with_user(foundation_user).action_validate()

        self.assertEqual(payment_request.state, "submitted")
        self.assertEqual(case.sessions_consumed, 0)
        self.assertEqual(case.remaining_session_count, 4)

    def test_validated_paid_or_closed_requests_cannot_exceed_authorized_case_sessions(self):
        case = self.env["evm.case"].create(
            {
                "name": "Dossier quota validation",
                "kine_user_id": self.kine_user.id,
                "patient_user_id": self.patient_user.id,
                "state": "accepted",
                "requested_session_count": 10,
                "authorized_session_count": 3,
            }
        )
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande validee initiale",
                "case_id": case.id,
                "sessions_count": 3,
                "state": "validated",
            }
        )

        with self.assertRaisesRegex(ValidationError, "depasse les seances autorisees"):
            self._create_internal_payment_request(
                {
                    "name": "Demande validee en trop",
                    "case_id": case.id,
                    "sessions_count": 1,
                    "state": "validated",
                }
            )

        with self.assertRaisesRegex(ValidationError, "depasse les seances autorisees"):
            payment_request.write({"sessions_count": 4})

        with self.assertRaisesRegex(ValidationError, "depasse les seances autorisees"):
            self._create_internal_payment_request(
                {
                    "name": "Demande cloturee en trop",
                    "case_id": case.id,
                    "sessions_count": 1,
                    "state": "closed",
                }
            )

    def test_validation_reuses_existing_linked_payment_without_creating_duplicate(self):
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_validate_idempotence",
            groups="evm.group_evm_fondation",
        )
        existing_payment = self.env["account.payment"].sudo().create(
            {
                "partner_id": self.patient_user.partner_id.id,
                "payment_type": "outbound",
                "partner_type": "customer",
                "amount": 75.0,
                "journal_id": self.payment_journal.id,
                "payment_method_line_id": (
                    self.payment_journal.outbound_payment_method_line_ids.filtered(lambda line: line.code == "manual")[:1]
                    or self.payment_journal.outbound_payment_method_line_ids[:1]
                ).id,
                "currency_id": self.env.company.currency_id.id,
                "memo": "Demande validation idempotente",
                "payment_reference": self._build_payment_reference("Demande validation idempotente"),
            }
        )
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande validation idempotente",
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "state": "submitted",
                "amount_total": 75.0,
                "payment_id": existing_payment.id,
            }
        )
        payment_count_before = self.env["account.payment"].sudo().search_count([])

        payment_request.with_user(foundation_user).action_validate()

        self.assertEqual(payment_request.payment_id, existing_payment)
        self.assertEqual(self.env["account.payment"].sudo().search_count([]), payment_count_before)

    def test_validation_rejects_inconsistent_existing_linked_payment(self):
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_validate_inconsistent_payment",
            groups="evm.group_evm_fondation",
        )
        existing_payment = self.env["account.payment"].sudo().create(
            {
                "partner_id": self.patient_user.partner_id.id,
                "payment_type": "outbound",
                "partner_type": "customer",
                "amount": 74.0,
                "journal_id": self.payment_journal.id,
                "payment_method_line_id": (
                    self.payment_journal.outbound_payment_method_line_ids.filtered(lambda line: line.code == "manual")[:1]
                    or self.payment_journal.outbound_payment_method_line_ids[:1]
                ).id,
                "currency_id": self.env.company.currency_id.id,
                "memo": "Demande validation incoherente",
                "payment_reference": self._build_payment_reference("Demande validation incoherente"),
            }
        )
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande validation incoherente",
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "state": "submitted",
                "amount_total": 75.0,
                "payment_id": existing_payment.id,
            }
        )

        with self.assertRaisesRegex(ValidationError, "n'est pas coherent"):
            payment_request.with_user(foundation_user).action_validate()

        self.assertEqual(payment_request.state, "submitted")

    def test_validation_requires_amount_before_creating_linked_payment(self):
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_validate_amount",
            groups="evm.group_evm_fondation",
        )
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande sans montant pour paiement",
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "state": "submitted",
            }
        )

        with self.assertRaisesRegex(ValidationError, "montant"):
            payment_request.with_user(foundation_user).action_validate()

        self.assertFalse(payment_request.payment_id)

    def test_open_payment_requires_foundation_access(self):
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_open_payment",
            groups="evm.group_evm_fondation",
        )
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande ouverture paiement",
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "state": "submitted",
                "amount_total": 75.0,
            }
        )
        payment_request.with_user(foundation_user).action_validate()

        with self.assertRaises(AccessError):
            payment_request.with_user(self.patient_user).action_open_payment()

        action = payment_request.with_user(foundation_user).action_open_payment()
        self.assertEqual(action["res_model"], "account.payment")
        self.assertEqual(action["res_id"], payment_request.payment_id.id)

    def test_foundation_can_confirm_external_payment_on_validated_request_with_history(self):
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_confirm_external",
            groups="evm.group_evm_fondation",
        )
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande paiement externe",
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "state": "submitted",
                "amount_total": 75.0,
            }
        )

        payment_request.with_user(foundation_user).action_validate()
        result = payment_request.with_user(foundation_user).action_confirm_external_payment()

        self.assertTrue(result)
        self.assertEqual(payment_request.state, "paid")
        self.assertTrue(payment_request.payment_id)
        self.assertEqual(payment_request.payment_id.state, "draft")
        self.assertEqual(self.accepted_case.sessions_consumed, 2)
        self.assertEqual(self.accepted_case.remaining_session_count, 10)
        history_messages = self.env["mail.message"].sudo().search(
            [("model", "=", "evm.payment_request"), ("res_id", "=", payment_request.id)]
        )
        case_history_messages = self.env["mail.message"].sudo().search(
            [("model", "=", "evm.case"), ("res_id", "=", self.accepted_case.id)]
        )
        public_request_messages = history_messages.filtered(
            lambda message: not message.subtype_id or not message.subtype_id.internal
        )
        internal_request_messages = history_messages.filtered(
            lambda message: message.subtype_id and message.subtype_id.internal
        )
        public_case_messages = case_history_messages.filtered(
            lambda message: not message.subtype_id or not message.subtype_id.internal
        )
        internal_case_messages = case_history_messages.filtered(
            lambda message: message.subtype_id and message.subtype_id.internal
        )
        self.assertTrue(
            any("Systeme:" in (body or "") and "hors plateforme" in (body or "").lower() for body in history_messages.mapped("body"))
        )
        self.assertTrue(
            any("Systeme:" in (body or "") and "payee" in (body or "").lower() for body in history_messages.mapped("body"))
        )
        self.assertTrue(
            any(
                "Systeme:" in (body or "") and "paiement hors plateforme confirme" in (body or "").lower()
                for body in case_history_messages.mapped("body")
            )
        )
        self.assertTrue(any(payment_request.name in (body or "") for body in case_history_messages.mapped("body")))
        self.assertFalse(
            any(payment_request.payment_id.display_name in (body or "") for body in public_request_messages.mapped("body"))
        )
        self.assertTrue(
            any(payment_request.payment_id.display_name in (body or "") for body in internal_request_messages.mapped("body"))
        )
        self.assertFalse(
            any(payment_request.payment_id.display_name in (body or "") for body in public_case_messages.mapped("body"))
        )
        self.assertTrue(
            any(payment_request.payment_id.display_name in (body or "") for body in internal_case_messages.mapped("body"))
        )

    def test_external_payment_confirmation_notifies_patient_with_email(self):
        self.patient_user.partner_id.write({"email": "patient.payment.request@example.com"})
        foundation_user = new_test_user(
            self.env,
            login="fondation.payment.request.paid.notifications@example.com",
            groups="evm.group_evm_fondation",
        )
        foundation_user.write({"notification_type": "inbox"})
        foundation_user.partner_id.write({"email": "fondation.payment.request.paid.notifications@example.com"})
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande notification paiement",
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "state": "submitted",
                "amount_total": 75.0,
            }
        )
        payment_request.with_user(foundation_user).action_validate()
        mail_ids_before = self._capture_mail_ids()

        payment_request.with_user(foundation_user).action_confirm_external_payment()

        notification_mails = self._get_new_mails(mail_ids_before).filtered(
            lambda mail: mail.subject == f"Entre Vos Mains - demande payee : {payment_request.name}"
        )

        self.assertEqual(len(notification_mails), 1)
        self.assertEqual(notification_mails.email_to, self.patient_user.partner_id.email)
        self.assertEqual(notification_mails.email_from, foundation_user.partner_id.email_formatted)
        self.assertIn(payment_request.name, notification_mails.body_html)
        self.assertIn("Payee", notification_mails.body_html)
        self.assertIn("paiement", notification_mails.body_html.lower())

    def test_external_payment_confirmation_requires_foundation_user_validated_state_and_linked_payment(self):
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_confirm_external_rules",
            groups="evm.group_evm_fondation",
        )
        submitted_request = self._create_internal_payment_request(
            {
                "name": "Demande soumise paiement externe",
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "state": "submitted",
                "amount_total": 50.0,
            }
        )
        validated_without_payment = self._create_internal_payment_request(
            {
                "name": "Demande validee sans paiement",
                "case_id": self.accepted_case.id,
                "sessions_count": 1,
                "state": "validated",
                "amount_total": 25.0,
            }
        )

        with self.assertRaises(AccessError):
            submitted_request.with_user(self.patient_user).action_confirm_external_payment()

        with self.assertRaisesRegex(ValidationError, "validee"):
            submitted_request.with_user(foundation_user).action_confirm_external_payment()

        with self.assertRaisesRegex(ValidationError, "paiement Odoo lie"):
            validated_without_payment.with_user(foundation_user).action_confirm_external_payment()

        self.assertEqual(submitted_request.state, "submitted")
        self.assertEqual(validated_without_payment.state, "validated")

    def test_external_payment_confirmation_rejects_stale_or_mutated_linked_payment(self):
        foundation_user = new_test_user(
            self.env,
            login="fondation_payment_request_confirm_external_stale_payment",
            groups="evm.group_evm_fondation",
        )
        payment_request = self._create_internal_payment_request(
            {
                "name": "Demande paiement externe incoherente",
                "case_id": self.accepted_case.id,
                "sessions_count": 2,
                "state": "submitted",
                "amount_total": 75.0,
            }
        )

        payment_request.with_user(foundation_user).action_validate()
        payment_request.payment_id.sudo().write({"memo": "Paiement modifie hors workflow"})

        with self.assertRaisesRegex(ValidationError, "n'est pas coherent"):
            payment_request.with_user(foundation_user).action_confirm_external_payment()

        self.assertEqual(payment_request.state, "validated")

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
        self.assertIn('name="action_validate"', form_view.arch_db)
        self.assertIn('name="action_refuse"', form_view.arch_db)
        self.assertIn('name="case_authorized_session_count"', form_view.arch_db)
        self.assertIn('name="case_sessions_consumed"', form_view.arch_db)
        self.assertIn('name="case_remaining_session_count"', form_view.arch_db)
        self.assertIn('name="payment_id"', form_view.arch_db)
        self.assertIn('name="action_open_payment"', form_view.arch_db)
        self.assertIn('name="action_confirm_external_payment"', form_view.arch_db)
        self.assertIn('name="sessions_count" readonly="state != \'submitted\'"', form_view.arch_db)
        self.assertIn('name="amount_total" readonly="state != \'submitted\'"', form_view.arch_db)
        self.assertIn('name="refusal_reason"', form_view.arch_db)
        self.assertIn('name="refused"', self.env.ref("evm.evm_payment_request_view_search").arch_db)

    def test_foundation_processing_action_is_limited_to_submitted_queue_and_allowed_groups(self):
        action = self.env.ref("evm.evm_payment_request_action")

        self.assertEqual(action.domain, "[]")
        self.assertEqual(
            set(action.group_ids),
            {
                self.env.ref("evm.group_evm_fondation"),
                self.env.ref("evm.group_evm_admin"),
            },
        )

    def test_foundation_processing_list_exposes_minimum_business_columns(self):
        list_view = self.env.ref("evm.evm_payment_request_view_list")

        self.assertIn('default_order="submitted_on desc, create_date desc"', list_view.arch_db)
        self.assertIn('field name="case_id"', list_view.arch_db)
        self.assertIn('field name="patient_user_id" string="Patient"', list_view.arch_db)
        self.assertIn('field name="submitted_on"', list_view.arch_db)
        self.assertIn('field name="state"', list_view.arch_db)
        self.assertIn('field name="amount_total"', list_view.arch_db)
        self.assertIn('field name="sessions_count"', list_view.arch_db)

    def test_foundation_processing_views_deny_non_authorized_users(self):
        list_view = self.env.ref("evm.evm_payment_request_view_list")
        search_view = self.env.ref("evm.evm_payment_request_view_search")
        form_view = self.env.ref("evm.evm_payment_request_view_form")

        with self.assertRaises(AccessError):
            list_view.with_user(self.patient_user)._check_view_access()

        with self.assertRaises(AccessError):
            search_view.with_user(self.patient_user)._check_view_access()

        with self.assertRaises(AccessError):
            form_view.with_user(self.patient_user)._check_view_access()
