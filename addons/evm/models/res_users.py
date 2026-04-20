from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _default_groups(self):
        if self.env.context.get("evm_default_portal_user"):
            return self.env.ref("base.group_portal")
        return super()._default_groups()
