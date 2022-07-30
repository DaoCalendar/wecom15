# -*- coding: utf-8 -*-
{
    "name": "WeCom Contacts",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 607,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.1",
    "summary": """
        WeCom Contacts
        """,
    "description": """


        """,
    "depends": [
        "contacts",
        'hr',
        'wecom_base',
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/wecom_apps_data.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
        "views/wecom_user_view.xml",
        "views/menu_view.xml",
        "views/assets_templates.xml",
    ],
    "external_dependencies": {
        "python": [],
    },
    "qweb": [
        "static/src/xml/*.xml",
    ],
}
