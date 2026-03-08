from odoo import _, api, fields, models


class EvmCase(models.Model):
    _name = "evm.case"
    _inherit = ["mail.thread"]
    _description = "EVM Case"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, string="Nom")
    state = fields.Selection(
        selection=[
            ("draft", "Brouillon"),
            ("pending", "En attente"),
            ("accepted", "Accepte"),
            ("refused", "Refuse"),
            ("closed", "Cloture"),
        ],
        default="draft",
        required=True,
        string="Statut",
        tracking=True,
    )
    kine_user_id = fields.Many2one(
        "res.users",
        index=True,
        required=True,
        string="Kinesitherapeute",
    )
    patient_user_id = fields.Many2one(
        "res.users",
        index=True,
        string="Patient",
    )
    requested_session_count = fields.Integer(
        string="Seances demandees",
        tracking=True,
    )
    authorized_session_count = fields.Integer(
        string="Seances autorisees",
        tracking=True,
    )
    patient_display_name = fields.Char(
        compute="_compute_patient_display_name",
        compute_sudo=True,
        string="Patient visible",
    )

    @api.depends("patient_user_id", "patient_user_id.partner_id.display_name", "name")
    def _compute_patient_display_name(self):
        for record in self:
            record.patient_display_name = record.patient_user_id.partner_id.display_name or record.name

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record.message_post(body=_("Dossier cree."))
        return records
