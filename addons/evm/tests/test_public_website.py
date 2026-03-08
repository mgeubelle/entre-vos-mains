from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged("post_install", "-at_install")
class TestEvmPublicWebsite(HttpCase):
    def test_public_homepage_renders_evm_content_and_portal_links(self):
        response = self.url_open("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Entre Vos Mains", response.text)
        self.assertIn("soutenir les soins de kinesitherapie", response.text)
        self.assertIn('href="/#parcours"', response.text)
        self.assertIn('href="/my"', response.text)
        self.assertIn('href="/web/login?redirect=/my"', response.text)
