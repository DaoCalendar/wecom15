# -*- coding: utf-8 -*-
{
    "name": "WeCom API",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 600,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "WeCom Suites/Settings",
    "version": "14.0.0.2",
    "summary": """
WeCom Service-side API and Client-side API              
        """,
    "description": """
 WeCom Service-side API and Client-side API
 Reconstruction based on project "https://github.com/sbzhu/weworkapi_python"
        """,
    "depends": [],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/wecom_server_api_error_data.xml",
        "data/service_api_list_data.xml",
        # "data/ir_cron_data.xml",
        # "views/ir_cron_views.xml",
    ],
    "assets": {
        "web.assets_common": [
            # JS
            "https://res.wx.qq.com/open/js/jweixin-1.2.0.js",
            "wecom_api/static/src/js/wxconfig.js",
        ],
        "web.assets_backend": [
            # JS
        ],
    },
    "external_dependencies": {
        "python": [
            "requests_toolbelt",
            "pandas",
            "pypandoc==1.7.0",
            "pycryptodome",
            "html2text",
        ],
    },
    "license": "LGPL-3",
    # "post_init_hook": "post_init_hook",
}
