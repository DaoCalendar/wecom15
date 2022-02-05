# -*- coding: utf-8 -*-
{
    "name": "WeCom Contacts",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 602,
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
    "depends": ["contacts",],
    "data": [
        "data/wecom_apps_data.xml",
        "data/wecom_app_config_data.xml",
        
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
        "views/wecom_apps_views.xml",
    ],
    "external_dependencies": {"python": [],},
    "qweb": ["static/src/xml/*.xml",],
}

