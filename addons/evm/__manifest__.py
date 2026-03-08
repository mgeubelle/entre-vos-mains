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
    "depends": ["base"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/rules.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
}
