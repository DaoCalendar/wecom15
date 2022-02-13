# -*- coding: utf-8 -*-


from odoo import api, fields, models, tools, _
from odoo.tools.translate import translate


class Company(models.Model):
    _inherit = "res.company"

    # 通讯录
    contacts_app_id = fields.Many2one(
        "wecom.apps",
        string="Contacts Application",
        # required=True,
        # default=lambda self: self.env.company,
        domain="[('company_id', '=', current_company_id)]",
    )

    