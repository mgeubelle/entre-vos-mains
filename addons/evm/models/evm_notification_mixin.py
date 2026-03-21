from odoo import _, models
from odoo.tools import html_escape


class EvmNotificationMixin(models.AbstractModel):
    _name = "evm.notification.mixin"
    _description = "EVM Notification Mixin"

    def _evm_get_notification_email_from(self):
        self.ensure_one()
        sender_partner = self.env.user.sudo().partner_id
        company_partner = self.env.company.sudo().partner_id
        return (
            sender_partner.email_formatted
            or company_partner.email_formatted
            or sender_partner.email
            or company_partner.email
            or ""
        )

    def _evm_get_selection_label(self, field_name, value):
        self.ensure_one()
        return dict(self._fields[field_name].selection).get(value, value or "")

    def _evm_get_foundation_notification_partners(self):
        foundation_group = self.env.ref("evm.group_evm_fondation", raise_if_not_found=False).sudo()
        admin_group = self.env.ref("evm.group_evm_admin", raise_if_not_found=False).sudo()
        users = self.env["res.users"].sudo()
        if foundation_group:
            users |= foundation_group.user_ids
        if admin_group:
            users |= admin_group.user_ids
        return users.filtered(lambda user: user.active and not user.share).mapped("partner_id").exists()

    def _evm_build_notification_body(self, *, intro, object_name, status_label=False, action_text=False, url=False):
        details = [
            "<ul>",
            "<li><strong>%s</strong>: %s</li>" % (
                html_escape(_("Objet concerne")),
                html_escape(object_name),
            ),
        ]
        if status_label:
            details.append(
                "<li><strong>%s</strong>: %s</li>"
                % (
                    html_escape(_("Nouveau statut")),
                    html_escape(status_label),
                )
            )
        if action_text:
            details.append(
                "<li><strong>%s</strong>: %s</li>"
                % (
                    html_escape(_("Action attendue")),
                    html_escape(action_text),
                )
            )
        details.append("</ul>")
        if url:
            details.append(
                '<p><a href="%s">%s</a></p>'
                % (
                    html_escape(url),
                    html_escape(_("Ouvrir le dossier ou la demande")),
                )
            )
        return "".join(
            [
                "<div>",
                "<p>%s</p>" % html_escape(intro),
                *details,
                "</div>",
            ]
        )

    def _evm_get_partner_notification_channel(self, partner):
        partner = partner.exists()
        if not partner:
            return False

        linked_users = partner.with_context(active_test=False).sudo().user_ids.filtered(lambda user: user.active)
        if linked_users.filtered(lambda user: not user.share and user.notification_type == "inbox"):
            return "inbox"
        if partner.filtered("email"):
            return "email"
        return False

    def _evm_send_email_notification(
        self,
        template_xmlid,
        *,
        subject,
        intro,
        object_name,
        status_label=False,
        action_text=False,
        url=False,
        partner=False,
        email_to=False,
    ):
        self.ensure_one()
        partner = partner.exists() if partner else self.env["res.partner"]
        recipient_email = email_to or partner.filtered("email")[:1].email or False
        if not recipient_email:
            return self.env["mail.mail"]

        template = self.env.ref(template_xmlid).sudo()
        mail_id = template.with_context(
            evm_notification_subject=subject,
            evm_notification_email_from=self._evm_get_notification_email_from(),
            evm_notification_intro=intro,
            evm_notification_object_name=object_name,
            evm_notification_status_label=status_label or "",
            evm_notification_action_text=action_text or "",
            evm_notification_url=url or "",
            evm_notification_partner_to="",
            evm_notification_email_to=recipient_email or "",
        ).send_mail(
            self.id,
            force_send=False,
            raise_exception=True,
            email_layout_xmlid="mail.mail_notification_layout",
        )
        return self.env["mail.mail"].sudo().browse(mail_id)

    def _evm_send_inbox_notification(
        self,
        *,
        subject,
        intro,
        object_name,
        status_label=False,
        action_text=False,
        url=False,
        partners,
    ):
        self.ensure_one()
        partners = partners.exists()
        if not partners:
            return self.env["mail.message"]
        return self.sudo().message_notify(
            partner_ids=partners.ids,
            subject=subject,
            body=self._evm_build_notification_body(
                intro=intro,
                object_name=object_name,
                status_label=status_label,
                action_text=action_text,
                url=url,
            ),
            email_layout_xmlid="mail.mail_notification_layout",
            model_description=self.env["ir.model"]._get(self._name).display_name,
        )

    def _evm_send_partner_notification(
        self,
        template_xmlid,
        *,
        subject,
        intro,
        object_name,
        status_label=False,
        action_text=False,
        url=False,
        partner,
    ):
        partner = partner.exists()
        if not partner:
            return self.env["mail.message"]

        channel = self._evm_get_partner_notification_channel(partner)
        if channel == "inbox":
            return self._evm_send_inbox_notification(
                subject=subject,
                intro=intro,
                object_name=object_name,
                status_label=status_label,
                action_text=action_text,
                url=url,
                partners=partner,
            )
        if channel == "email":
            return self._evm_send_email_notification(
                template_xmlid,
                subject=subject,
                intro=intro,
                object_name=object_name,
                status_label=status_label,
                action_text=action_text,
                url=url,
                partner=partner,
            )
        return self.env["mail.message"]
