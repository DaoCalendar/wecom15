# -*- coding: utf-8 -*-
{
    "name": "WeCom Contacts Synchronized",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 603,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "WeCom/CRM",
    "version": "14.0.0.1",
    "summary": """
        
        """,
    "description": """


        """,
    "depends": [
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
        "views/assets_templates.xml",

        "views/res_config_settings_views.xml",
        "views/res_users_views.xml",
        "views/wecom_apps_views.xml",
        "views/hr_department_view.xml",
        "views/hr_employee_view.xml",
        "views/hr_employee_category_views.xml",
        "views/ir_cron_views.xml",
        "wizard/employee_bind_wecom_views.xml",
        "wizard/user_bind_wecom_views.xml",
        "wizard/wecom_contacts_sync_wizard_views.xml",
        "wizard/wecom_users_sync_wizard_views.xml",
        "views/wecom_contacts_block_views.xml",
        "views/menu_views.xml",
    ],
    # "assets": {
    #     "web._assets_common_styles": [
    #         "wecom_contacts_sync/static/src/scss/sync_result_dialog.scss",
    #     ],
    #     "web.assets_backend": [
    #         # SCSSS
    #         # JS
    #         "wecom_contacts_sync/static/src/js/download_deps.js",
    #         "wecom_contacts_sync/static/src/js/download_staffs.js",
    #         "wecom_contacts_sync/static/src/js/download_tags.js",
    #     ],
    #     "web.assets_qweb": ["wecom_contacts_sync/static/src/xml/*.xml",],
    # },
    "qweb": ["static/src/xml/*.xml", ],
    "license": "LGPL-3",
}
