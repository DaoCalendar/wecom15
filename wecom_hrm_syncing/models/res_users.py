# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

class ResUsers(models.Model):
    _inherit = "res.users"

    employee_id = fields.Many2one(
        "hr.employee",
        string="Company employee",
        compute="_compute_company_employee",
        search="_search_company_employee",
        store=True,
    )  # 变更用户类型时，需要绑定用户，避免出现“创建员工”的按钮，故 store=True


    @api.model_create_multi
    def create(self, vals_list):
        """
        重写以自动邀请用户注册
        send_mail: true 表示发送邀请邮件, false 表示不发送邀请邮件
        批量创建用户时，建议 send_mail=False
        """
        users = super(ResUsers, self).create(vals_list)
        send_mail = self.env.context.get('send_mail')
        # print(send_mail)
        if not self.env.context.get('no_reset_password') and send_mail:
            users_with_email = users.filtered('email')
            if users_with_email:
                try:
                    users_with_email.with_context(create_user=True).action_reset_password()
                except MailDeliveryException:
                    users_with_email.partner_id.with_context(create_user=True).signup_cancel()
        
        return users

    def set_wecom_user(self):
        """
        设置企业微信用户，当该用户已经关联employee时，将该employee的企业微信id信息写入到user中
        """
        if (
            self.employee_ids
            and self.employee_ids[0].is_wecom_user
            and self.employee_ids[0].wecom_userid
        ):
            self.write(
                {
                    "is_wecom_user": True,
                    # "is_wecom_notice": True,
                    "wecom_userid": self.employee_ids[0].wecom_userid,
                }
            )
        else:
            raise UserError(_("Please set wxwork employee for this user!"))


# ----------------------------------------------------------
# 变更用户类型向导
# ----------------------------------------------------------


class ChangeTypeWizard(models.TransientModel):
    _name = "change.type.wizard"
    _description = "Wizard to change user type(WeCom)"

    def _default_user_ids(self):
        user_ids = (
            self._context.get("active_model") == "res.users"
            and self._context.get("active_ids")
            or []
        )
        return [
            (
                0,
                0,
                {"user_id": user.id, "user_login": user.login, "user_name": user.name,},
            )
            for user in self.env["res.users"].browse(user_ids)
        ]

    user_ids = fields.One2many(
        "change.type.user", "wizard_id", string="Users", default=_default_user_ids
    )

    def change_type_button(self):
        self.ensure_one()
        self.user_ids.change_type_button()
        if self.env.user in self.mapped("user_ids.user_id"):
            return {"type": "ir.actions.client", "tag": "reload"}
        return {"type": "ir.actions.act_window_close"}


class ChangeTypeUser(models.TransientModel):
    _name = "change.type.user"
    _description = "User, Change Type Wizard"

    wizard_id = fields.Many2one(
        "change.type.wizard", string="Wizard", required=True, ondelete="cascade"
    )

    user_id = fields.Many2one(
        "res.users", string="User", required=True, ondelete="cascade"
    )
    user_login = fields.Char(string="Login account", readonly=True,)
    user_name = fields.Char(string="Login name", readonly=True)
    # 用户类型参见res_group
    new_type = fields.Selection(
        [("1", _("Internal User")), ("9", _("Portal")), ("10", _("Public")),],
        string="User Type",
        default="1",
    )

    def change_type_button(self):
        for line in self:
            if not line.new_type:
                raise UserError(
                    _(
                        "Before clicking the 'Change User Type' button, you must modify the new user type"
                    )
                )
            if (
                # 排除初始系统自带的用户
                line.user_id.id == 1
                or line.user_id.id == 2
                or line.user_id.id == 3
                or line.user_id.id == 4
                or line.user_id.id == 5
            ):
                pass
            else:
                if line.new_type == "1":
                    try:
                        line.user_id.employee_id = (
                            self.env["hr.employee"].search(
                                [
                                    ("id", "in", line.user_id.employee_ids.ids),
                                    ("company_id", "=", line.user_id.company_id.id),
                                ],
                                limit=1,
                            ),
                        )
                    except Exception as e:
                        print("用户 %s 类型变更错误,错误:%s" % (line.user_id.name, repr(e)))

                line.user_id.write({"groups_id": [(6, 0, line.new_type)]})
        self.write({"new_type": False})
