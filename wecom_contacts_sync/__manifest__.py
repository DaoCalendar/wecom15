# -*- coding: utf-8 -*-
{
    "name": "WeCom Contacts Synchronized",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 603,
    "category": "WeCom/CRM",
    "version": "14.0.0.4",
    "summary": """
        
        """,
    "description": """


        """,
    "depends": [
        "hr",
        "wecom_contacts",
        "hrms_base",
    ],
    "external_dependencies": {"python": ["pandas"],},
    "data": [
        # "security/ir.model.access.csv",
        "security/ir.model.access.csv",
        "data/wecom_app_config_data.xml",
        "data/wecom_app_event_type_data.xml",
        "data/ir_cron_data.xml",
        "data/hr_data.xml",

        "wizard/employee_bind_wecom_views.xml",
        "wizard/user_bind_wecom_views.xml",
        "wizard/wecom_contacts_sync_wizard_views.xml",
        "wizard/wecom_users_sync_wizard_views.xml",
        "views/wecom_department_views.xml",
        "views/wecom_tag_views.xml",
        "views/wecom_contacts_block_views.xml",
        "views/assets_templates.xml",
        "views/res_config_settings_views.xml",

        "views/res_users_views.xml",
        "views/wecom_apps_views.xml",
        "views/hr_department_view.xml",
        "views/hr_employee_category_views.xml",
        "views/ir_cron_views.xml",
        "views/hr_employee_view.xml",
        "views/menu_views.xml",
        "views/wecom_user_views.xml",
    ],
    "qweb": ["static/src/xml/*.xml", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "LGPL-3",
}
