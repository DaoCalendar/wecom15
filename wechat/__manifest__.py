# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": """WeChat API""",
    "summary": """Technical module to integrate Odoo with WeChat;Need cryptography""",
    "category": "Wecom/Hidden",
    "images": [],
    "version": "14.0.1.3",
    "application": False,
    "author": "IT-Projects LLC, Ivan Yelizariev, OdooChain",
    "support": "help@itpp.dev",
    "website": "https://github.com/odoochain/pos-addons#readme",
    "license": "Other OSI approved licence",  # MIT
    "depends": [
        "product",
        "account",
        "qr_payments",
        "wecom_api",
        "wecom_contacts",
    ],
    "data": [
        "views/account_menuitem.xml",
        "views/wechat_micropay_views.xml",
        "views/wechat_order_views.xml",
        "views/wechat_refund_views.xml",
        "views/account_journal_views.xml",
        "data/ir_sequence_data.xml",
        "security/ir.model.access.csv",
    ],
    "qweb": [],
    "auto_install": False,
    "installable": True,
}
