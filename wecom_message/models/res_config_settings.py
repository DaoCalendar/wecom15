# -*- coding: utf-8 -*-

import base64
import os
import io
from PIL import Image
from requests import request
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # 消息
    message_app_id = fields.Many2one(
        related="company_id.message_app_id", readonly=False
    )
    message_agentid = fields.Integer(string="Message App Id", related="message_app_id.agentid", readonly=False)
    message_secret = fields.Char(string="Message App Secret", related="message_app_id.secret", readonly=False)
    message_access_token = fields.Char(string="Message Auth Access App Token", related="message_app_id.access_token")

    message_domain = fields.Selection([
        ('prod', 'Production'),
        ('sand', 'Sandbox'),
    ], string='message Environment', default='sand', required=True, config_parameter='wecom_message_domain')

    message_app_callback_service_ids = fields.One2many(
        string="Message Auth Callback App Service Ids",
        related="message_app_id.app_callback_service_ids", readonly=False
    )

    message_sending_method = fields.Selection(
        [
            ("1", "Block mail and send only messages."),
            ("2", "Send mail and messages at the same time"),
        ],
        string="Sending Method",
        default="1",
        required=True,
        config_parameter="wecom_message_sending_method",
    )
    # module_gamification = fields.Boolean(readonly=False)

    # module_wecom_hr_gamification_message = fields.Boolean(
    #     related="company_id.module_wecom_hr_gamification_message", readonly=False
    # )

    module_digest = fields.Boolean("KPI Digests")
    module_wecom_message_digest = fields.Boolean(
        "Send KPI Digests periodically via WeCom",
    )

    # module_stock = fields.Boolean()
    # module_wecom_stock_message = fields.Boolean(
    #     related="company_id.module_wecom_stock_message", readonly=False
    # )

    # module_purchase = fields.Boolean()
    # module_wecom_purchase_message = fields.Boolean(
    #     "Send Purchase message via WeCom",
    # )

    # @api.onchange("wecom_message_logo")
    # def _onchange_wecom_message_logo(self):
    #     if self.wecom_message_logo:
    #         image = tools.base64_to_image(self.wecom_message_logo)
    #         w, h = image.size
    #         if w == h:
    #             self.wecom_message_logo_web = tools.image_process(
    #                 self.wecom_message_logo, size=(180, 180)
    #             )
    #         else:
    #             raise UserError(_("Please upload a picture of the square!"))

    def generate_parameters(self):
        """
        生成参数
        :return:
        """
        code = self.env.context.get("code")
        if bool(code) and code == "message":
            for record in self:
                if not record.message_app_id:
                    raise ValidationError(_("Please bind message app!"))
                else:
                    record.message_app_id.with_context(code=code).generate_parameters()
        # super(ResConfigSettings, self).generate_parameters()

    def generate_service(self):
        """
        生成服务
        :return:
        """
        code = self.env.context.get("code")
        if bool(code) and code == "message":
            for record in self:
                if not record.message_app_id:
                    raise ValidationError(_("Please bind message app!"))
                else:
                    record.message_app_id.with_context(code=code).generate_service()
        # super(ResConfigSettings, self).generate_service()

    def get_message_app_info(self):
        """
        获取应用信息
        :return:
        """
        agentid = self.message_app_id.agentid
        secret = self.message_app_id.secret
        assert agentid
        for record in self:
            if agentid == "1000002" and (
                    record.message_app_id.agentid == 0 or record.message_app_id.secret == ""
            ):
                raise UserError(_("Message application ID and secret cannot be empty!"))
            if agentid and record.message_app_id.agentid and secret:
                record.message_app_id.get_agentid_info(agentid, secret)
            else:
                raise UserError(_("Message application ID and secret cannot be empty!"))

