{
    "name": "Entre Vos Mains",
    "summary": "Socle technique du module Entre Vos Mains",
    "description": """
Bootstrap minimal du module custom EVM pour Odoo 19.
Le socle de securite, les groupes et les modeles porteurs des ACL
sont introduits progressivement au fil des stories.
    """,
    "author": "Entre Vos Mains",
    "website": "https://entrevosmains.be",
    "category": "Services",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "depends": ["base", "mail", "portal", "website", "account"],
    "assets": {
        "web.assets_frontend": [
            "evm/static/src/scss/website.scss",
        ],
        "website.assets_frontend": [
            "evm/static/src/scss/website.scss",
        ],
        "web.assets_tests": [
            "evm/static/tests/**/*",
        ],
    },
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/rules.xml",
        "data/ir_sequence_data.xml",
        "data/mail_templates.xml",
        "data/scheduled_actions.xml",
        "views/evm_case_views.xml",
        "views/evm_payment_request_views.xml",
        "views/res_config_settings_views.xml",
        "views/website_templates.xml",
        "views/portal_templates.xml",
    ],
    "demo": [
        "demo/res_users.xml",
    ],
    "installable": True,
    "application": False,
}
