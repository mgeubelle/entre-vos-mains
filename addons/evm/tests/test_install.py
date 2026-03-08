from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestEvmInstall(TransactionCase):
    def test_module_is_installed(self):
        module = self.env["ir.module.module"].search([("name", "=", "evm")], limit=1)

        self.assertTrue(module, "The evm module should be discoverable.")
        self.assertEqual(module.state, "installed")
