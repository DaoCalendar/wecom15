# -*- coding: utf-8 -*-
{
    "name": "WeCom Session Content Archive",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 622,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.1",
    "summary": """

        """,
    "description": """


        """,
    "depends": ["wecom_contacts_sync", "contacts"],
    "external_dependencies": {"python": ["pycryptodome", "pandas"], },
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/wecom_apps_data.xml",
        "data/ir_cron_data.xml",
        # "data/wecom_app_config_data.xml",
        # "views/res_company_views.xml",
        "wizard/wecom_modify_external_groupchat_name.xml",
        "wizard/wecom_modify_external_sender_name.xml",
        "views/assets_templates.xml",
        "views/res_config_settings_views.xml",
        "views/wecom_msgaudit_key_views.xml",
        "views/wecom_chat_data_views.xml",
        "views/ir_cron_views.xml",
        "views/menu_views.xml",
    ],
    "qweb": ["static/src/xml/*.xml",],
    # "pre_init_hook": "pre_init_hook",
}
