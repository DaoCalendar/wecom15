# -*- coding: utf-8 -*-

from ast import Store
import logging
import base64
import time
from lxml import etree
from odoo import api, fields, models, _, tools
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)

WECOM_USER_MAPPING_ODOO_EMPLOYEE = {
    "UserID": "wecom_userid",  # 成员UserID
    "Name": "name",  # 成员名称;
    "Department": "department_ids",  # 成员部门列表，仅返回该应用有查看权限的部门id
    "MainDepartment": "department_id",  # 主部门
    "IsLeaderInDept": "",  # 表示所在部门是否为上级，0-否，1-是，顺序与Department字段的部门逐一对应
    "DirectLeader": "",  # 直属上级
    "Mobile": "mobile_phone",  # 手机号码
    "Position": "job_title",  # 职位信息
    "Gender": "gender",  # 企微性别：0表示未定义，1表示男性，2表示女性；odoo性别：male为男性，female为女性，other为其他
    "Email": "work_email",  # 邮箱;
    "Status": "active",  # 激活状态：1=已激活 2=已禁用 4=未激活 已激活代表已激活企业微信或已关注微工作台（原企业号）5=成员退出
    "Avatar": "avatar",  # 头像url。注：如果要获取小图将url最后的”/0”改成”/100”即可。
    "Alias": "alias",  # 成员别名
    "Telephone": "work_phone",  # 座机;
    "Address": "work_location",  # 地址;
    "ExtAttr": {
        "Type": "",  # 扩展属性类型: 0-本文 1-网页
        "Text": "",  # 文本属性类型，扩展属性类型为0时填写
        "Value": "",  # 文本属性内容
        "Web": "",  # 网页类型属性，扩展属性类型为1时填写
        "Title": "",  # 网页的展示标题
        "Url": "",  # 网页的url
    },  # 扩展属性;
}


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    _order = "wecom_user_order"

    # ----------------------------------------------------------------------------------
    # 开发人员注意：hr模块中
    # hr.employee.work_email = res.users.email 
    # hr.employee.private_email = res.partner.email 
    # ----------------------------------------------------------------------------------
    # base 模块中
    # res.user.email = res.partner.email 
    # res.user.private_email = res.partner.email 
    # ------------------------------------------
    # hr.employee.create() 方法中 创建hr.employee.work_email时会将 res.users.email更新到hr.employee.work_email
    # res.users.write() 方法中 更新res.users.email时会将 res.users.email更新到hr.employee.work_email
    # ------------------------------------------
    # 故重写了 将  related='address_home_id.email'去掉，并添加 store 属性
    # ----------------------------------------------------------------------------------
    # private_email = fields.Char(string="Private Email", groups="hr.group_hr_user",store=True,)

    wecom_userid = fields.Char(string="WeCom user Id", readonly=True, )
    wecom_openid = fields.Char(string="WeCom OpenID", readonly=True, )
    alias = fields.Char(string="Alias", readonly=True, )
    english_name = fields.Char(string="English Name", readonly=True, )

    department_ids = fields.Many2many(
        "hr.department", string="Multiple departments", readonly=True,
    )
    use_system_avatar = fields.Boolean(readonly=True, default=True)
    avatar = fields.Char(string="Avatar")

    qr_code = fields.Char(
        string="Personal QR code",
        help="Personal QR code, Scan can be added as external contact",
        readonly=True,
    )
    wecom_user_order = fields.Char(
        "WeCom user sort",
        default="0",
        help="The sort value within the department, the default is 0. The quantity must be the same as the "
             "department, The greater the value the more sort front.The value range is [0, 2^32)",
        readonly=True,
    )
    is_wecom_user = fields.Boolean(
        string="WeCom employees", readonly=True, default=False,
    )

    def unbind_wecom_member(self):
        """
        解除绑定企业微信成员
        """
        self.write(
            {"is_wecom_user": False, "wecom_userid": None, "qr_code": None, }
        )
        if self.user_id:
            # 关联了User
            self.user_id.write(
                {"is_wecom_user": False, "wecom_userid": None, "qr_code": None, }
            )

    def get_wecom_openid(self):
        """
        获取企微OpenID
        """
        for employee in self:
            try:
                wxapi = self.env["wecom.service_api"].InitServiceApi(
                    employee.company_id.corpid,
                    employee.company_id.contacts_app_id.secret,
                )
                response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "USERID_TO_OPENID"
                    ),
                    {"userid": employee.wecom_userid, },
                )
            except ApiException as ex:
                self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    ex, raise_exception=True
                )
            else:
                employee.wecom_openid = response["openid"]

    # ------------------------------------------------------------
    # 从员工生成用户
    # ------------------------------------------------------------
    def create_user_from_employee(self):
        """
        从员工生成用户
        :return:
        """
        send_mail = self.env.context.get("send_mail")
        send_message = self.env.context.get("send_message")
        if send_mail is None:
            send_mail = True
        if send_message is None:
            send_message = True

        for employee in self:
            params = {}
            if employee.wecom_openid is False:
                employee.get_wecom_openid()

            # partner = self.env["res.users"].browse(res_user_id).partner_id
            try:
                # partner.write(
                #     {
                #         "company_id": self.company_id.id,
                #         "lang": self.env.lang,
                #     }
                # )
                res_user_id = self.env["res.users"]._get_or_create_user_by_wecom_userid(
                    employee, send_mail, send_message
                )
            except Exception as e:
                message = _(
                    "Failed to copy employee [%s] as system user, reason:%s"
                ) % (employee.name, repr(e),)
                _logger.warning(message)
                params = {
                    "title": _("Fail"),
                    "message": message,
                    "sticky": True,  # 延时关闭
                    "className": "bg-danger",
                    "type": "danger",
                }
            else:
                message = _("Successfully copied employee [%s] as system user") % (
                    employee.name
                )
                params = {
                    "title": _("Success"),
                    "message": message,
                    "sticky": False,  # 延时关闭
                    "className": "bg-success",
                    "type": "success",
                    "next": {"type": "ir.actions.client", "tag": "reload", },  # 刷新窗体
                }
            finally:
                action = {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": params,
                }
                return action

    # ------------------------------------------------------------
    # 企微员工下载
    # ------------------------------------------------------------
    @api.model
    def download_wecom_staffs(self):
        """
        下载员工列表
        """
        start_time = time.time()
        company = self.env.context.get("company_id")
        tasks = []
        if not company:
            company = self.env.company

        if company.is_wecom_organization:
            try:
                wxapi = self.env["wecom.service_api"].InitServiceApi(
                    company.corpid, company.contacts_app_id.secret
                )
                app_config = self.env["wecom.app_config"].sudo()
                contacts_sync_hr_department_id = app_config.get_param(
                    company.contacts_app_id.id, "contacts_sync_hr_department_id"
                )  # 需要同步的企业微信部门ID
                # TODO 需要判断是否安装了 同步模块
                response = wxapi.contactshttpCall(
                    self.env["wecom.service_api_list"].get_server_api_call("USER_LIST"),
                    {
                        "department_id": contacts_sync_hr_department_id,
                        "fetch_child": "1",
                    },
                )
            except ApiException as ex:
                end_time = time.time()

                self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    str(ex), raise_exception=False
                )
                tasks = [
                    {
                        "name": "download_employee_data",
                        "state": False,
                        "time": end_time - start_time,
                        "msg": str(ex),
                    }
                ]
            except Exception as e:
                end_time = time.time()
                tasks = [
                    {
                        "name": "download_employee_data",
                        "state": False,
                        "time": end_time - start_time,
                        "msg": str(e),
                    }
                ]
            else:
                wecom_employees = response["userlist"]

                # 获取block
                blocks = (
                    self.env["wecom.contacts.block"]
                    .sudo()
                    .search([("company_id", "=", company.id), ])
                )
                block_list = []

                # 生成 block_list
                if len(blocks) > 0:
                    for obj in blocks:
                        if obj.wecom_userid != None:
                            # block_list.append({"userid": obj.wecom_userid})
                            block_list.append(obj.wecom_userid)

                # 从 wecom_employees 移除 block_list
                for b in block_list:
                    for item in wecom_employees:
                        # userid不区分大小写
                        if item["userid"].lower() == b.lower():
                            wecom_employees.remove(item)

                # 1.下载员工
                for wecom_employee in wecom_employees:
                    download_employee_result = self.download_employee(
                        company, wecom_employee
                    )
                    if download_employee_result:
                        for r in download_employee_result:
                            tasks.append(r)  # 加入设置下载员工失败结果

                # 2.设置直属上级
                set_direct_leader_results = self.set_direct_leader(
                    company, wecom_employees
                )
                if set_direct_leader_results:
                    for r in set_direct_leader_results:
                        tasks.append(r)  # 加入设置直属上级失败结果

                # 3.处理离职员工
                employees = self.search(
                    [
                        ("is_wecom_user", "=", True),
                        ("company_id", "=", company.id),
                        "|",
                        ("active", "=", True),
                        ("active", "=", False),
                    ],
                )
                if not employees:
                    pass
                else:
                    set_leave_employee_results = self.set_leave_employee(
                        company, response
                    )  # 设置离职员工
                    if set_leave_employee_results:
                        for r in set_leave_employee_results:
                            tasks.append(r)  # 加入设置离职员工失败结果

                # 4.完成同步员工
                end_time = time.time()
                task = {
                    "name": "download_employee_data",
                    "state": True,
                    "time": end_time - start_time,
                    "msg": _("Employee list downloaded successfully."),
                }
                tasks.append(task)
            # finally:
            #     results.update({"time": end_time - start_time})
            #     return results  # 返回失败结果
        else:
            end_time = time.time()
            tasks = [
                {
                    "name": "download_employee_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": _(
                        "The current company does not identify the enterprise wechat organization. Please configure "
                        "or switch the company. "
                    ),
                }
            ]

        return tasks

    def download_employee(self, company, wecom_employee):
        """
        下载员工
        """
        employee = self.sudo().search(
            [
                ("wecom_userid", "=", wecom_employee["userid"].lower()),
                ("company_id", "=", company.id),
                ("is_wecom_user", "=", True),
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ],
            limit=1,
        )
        # result = {}
        print("employee：", company, employee, wecom_employee)
        if not employee:
            result = self.create_employee(company, employee, wecom_employee)
        else:
            result = self.update_employee(company, employee, wecom_employee)
        return result

    def create_employee(self, company, employee, wecom_employee):
        """
        创建员工
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        department_ids = []  # 多部门
        if len(wecom_employee["department"]) > 0:
            department_ids = self.get_employee_parent_wecom_department(
                company, wecom_employee["department"]
            )
        try:
            app_config = self.env["wecom.app_config"].sudo()
            contacts_use_default_avatar = app_config.get_param(
                company.contacts_app_id.id,
                "contacts_use_default_avatar_when_adding_employees",
            )  # 使用系统微信默认头像的标识

            emp = employee.create(
                {
                    "wecom_userid": wecom_employee["userid"].lower(),
                    "name": wecom_employee["name"],
                    "english_name": self.env["wecom.tools"].check_dictionary_keywords(
                        wecom_employee, "english_name"
                    ),
                    "gender": self.env["wecom.tools"].sex2gender(
                        wecom_employee["gender"]
                    ),
                    "marital": None,  # 不生成婚姻状况
                    "image_1920": self.env["wecomapi.tools.file"].get_avatar_base64(
                        contacts_use_default_avatar,
                        wecom_employee["gender"],
                        wecom_employee["avatar"],
                    ),
                    "mobile_phone": wecom_employee["mobile"],
                    "work_phone": wecom_employee["telephone"],
                    "work_email": wecom_employee["biz_mail"],  # 企业邮箱
                    # "private_email": wecom_employee["email"],  # 私人邮箱
                    "active": True if wecom_employee["status"] == 1 else False,
                    "alias": wecom_employee["alias"],
                    "department_id": self.get_main_department(
                        company,
                        wecom_employee["name"],
                        wecom_employee["main_department"],
                        department_ids,
                    ),
                    "company_id": company.id,
                    "department_ids": [(6, 0, department_ids)],
                    "wecom_user_order": wecom_employee["order"],
                    "qr_code": wecom_employee["qr_code"],
                    "is_wecom_user": True,
                }
            )
            # 创建员工成功后，更新员工的私人邮箱
            # 使用create()方法，不会更新员工的私人邮箱
            emp.private_email = wecom_employee["email"]
        except Exception as e:
            result = _("Error creating company [%s] employee [%s %s], error reason: %s") % (
                company.name,
                wecom_employee["userid"].lower(),
                wecom_employee["name"],
                repr(e),
            )
            if debug:
                _logger.warning(result)
            return {
                "name": "add_employee",
                "state": False,
                "time": 0,
                "msg": result,
            }  # 返回失败结果

    def update_employee(self, company, employee, wecom_employee):
        """
        更新员工
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        department_ids = []  # 多部门

        if len(wecom_employee["department"]) > 0:
            department_ids = self.get_employee_parent_wecom_department(
                company, wecom_employee["department"]
            )
        try:
            employee.write(
                {
                    "name": wecom_employee["name"],
                    "english_name": self.env["wecom.tools"].check_dictionary_keywords(
                        wecom_employee, "english_name"
                    ),
                    "mobile_phone": wecom_employee["mobile"],
                    "work_phone": wecom_employee["telephone"],
                    # "email": wecom_employee["biz_mail"],  # 企业邮箱
                    "work_email": wecom_employee["biz_mail"],  # 企业邮箱
                    "private_email": wecom_employee["email"],  # 私人邮箱
                    "active": True if wecom_employee["status"] == 1 else False,
                    "alias": wecom_employee["alias"],
                    "department_id": self.get_main_department(
                        company,
                        wecom_employee["name"],
                        wecom_employee["main_department"],
                        department_ids,
                    ),
                    "company_id": company.id,
                    "department_ids": [(6, 0, department_ids)],
                    "wecom_user_order": wecom_employee["order"],
                    "qr_code": wecom_employee["qr_code"],
                    "is_wecom_user": True,
                }
            )
            app_config = self.env["wecom.app_config"].sudo()
            contacts_update_avatar = app_config.get_param(
                company.contacts_app_id.id,
                "contacts_update_avatar_every_time_sync_employees",
            )  # 每次同步都更新头像的标识

            if contacts_update_avatar:
                employee.write(
                    {
                        "image_1920": self.env["wecomapi.tools.file"].get_avatar_base64(
                            True, wecom_employee["gender"], wecom_employee["avatar"],
                        ),
                    }
                )
        except Exception as e:
            result = _("Error update company %s employee %s %s, error reason: %s") % (
                company.name,
                wecom_employee["userid"].lower(),
                wecom_employee["name"],
                repr(e),
            )
            if debug:
                _logger.warning(result)
            return {
                "name": "update_employee",
                "state": False,
                "time": 0,
                "msg": result,
            }  # 返回失败结果

    def get_employee_parent_wecom_department(self, company, departments):
        """
        获取员工的企微上级部门ids
        """
        department_ids = []
        for department in departments:
            if department == 1:
                pass
            else:
                odoo_department = (
                    self.env["hr.department"]
                    .sudo()
                    .search(
                        [
                            ("wecom_department_id", "=", department),
                            ("company_id", "=", company.id),
                            ("is_wecom_department", "=", True),
                        ],
                        limit=1,
                    )
                )
                if len(odoo_department) > 0:
                    department_ids.append(odoo_department.id)

        return department_ids

    def get_main_department(self, company, employee_name, main_department, departments):
        """
        获取员工的主部门
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        if main_department == 1 and len(departments) > 1:
            for index, department in enumerate(departments):
                if department == 1:
                    del departments[index]
            main_department = departments[0]
        elif main_department == 1:
            return None
        try:
            departments = (
                self.env["hr.department"]
                .sudo()
                .search(
                    [
                        ("wecom_department_id", "=", main_department),
                        ("company_id", "=", company.id),
                        ("is_wecom_department", "=", True),
                    ],
                    limit=1,
                )
            )
            if len(departments) > 0:
                return departments.id
            else:
                return None
        except BaseException as e:
            if debug:
                _logger.warning(
                    _(
                        "Get the main department error of the company %s employee %s. The wrong reason is: %s."
                    )
                    % (company.name, employee_name, repr(e))
                )
            return None

    def set_direct_leader(self, company, wecom_employees):
        """
        设置 直属上级
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        results = []
        if debug:
            _logger.info(
                _(
                    "Start setting the direct leader of the employee with the company name '%s'."
                ),
                company.name,
            )
        for wecom_employee in wecom_employees:
            try:
                if len(wecom_employee["direct_leader"]) > 0:
                    direct_leader = self.search(
                        [
                            ("wecom_userid", "=", wecom_employee["direct_leader"][0]),
                            ("company_id", "=", company.id),
                            ("is_wecom_user", "=", True),
                            "|",
                            ("active", "=", True),
                            ("active", "=", False),
                        ],
                    )
                    employee = self.search(
                        [
                            ("wecom_userid", "=", wecom_employee["userid"].lower()),
                            ("company_id", "=", company.id),
                            ("is_wecom_user", "=", True),
                            "|",
                            ("active", "=", True),
                            ("active", "=", False),
                        ],
                        limit=1,
                    )
                    employee.write({"parent_id": direct_leader.id})
                else:
                    pass
            except Exception as e:
                result = _(
                    "Error setting the direct leader of the company %s employee %s. The wrong reason is: %s."
                ) % (company.name, wecom_employee["name"], repr(e))
                if debug:
                    _logger.warning(result)
                results.append(
                    {
                        "name": "set_employee_superior",
                        "state": False,
                        "time": 0,
                        "msg": result,
                    }
                )

        if debug:
            _logger.info(
                _(
                    "End setting the direct leader of the employee with the company name '%s'."
                ),
                company.name,
            )
        return results  # 返回失败结果

    def set_leave_employee(self, company, response):
        """
        比较企业微信和odoo的员工数据,且设置离职odoo员工active状态
        激活状态: 1=已激活, 2=已禁用, 4=未激活, 5=退出企业。
        已激活代表已激活企业微信或已关注微工作台(原企业号)。未激活代表既未激活企业微信又未关注微工作台(原企业号)。
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        results = []

        wecom_employees = []
        odoo_employees = []
        for wecom_employee in response["userlist"]:
            wecom_employees.append(wecom_employee["userid"].lower())

        domain = ["|", ("active", "=", False), ("active", "=", True)]
        employees = self.search(
            domain + [("is_wecom_user", "=", True), ("company_id", "=", company.id), ]
        )

        for employee in employees:
            odoo_employees.append(employee.wecom_userid)

        leave_employees = list(
            set(odoo_employees).difference(set(wecom_employees))
        )  # 生成odoo与企微不同的员工数据列表,即离职员工

        for leave_employee in leave_employees:
            employee = self.search(
                [
                    ("wecom_userid", "=", leave_employee),
                    ("company_id", "=", company.id),
                ]
            )
            try:
                employee.write({"active": False})
            except Exception as e:
                result = _("Dismissal of employee [%s] failed, reason%s") % (
                    employee.name,
                    repr(e),
                )
                if debug:
                    _logger.warning(result)
                results.append(
                    {
                        "name": "employee_termination",
                        "state": False,
                        "time": 0,
                        "msg": result,
                    }
                )
        return results  # 返回失败结果

    # ------------------------------------------------------------
    # 企微通讯录事件
    # ------------------------------------------------------------
    def wecom_event_change_contact_user(self, cmd):
        """
        通讯录事件变更员工
        """
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        xml_tree_str = etree.fromstring(bytes.decode(xml_tree))
        dic = etree.tostring(xml_tree_str, xml_declaration=True, encoding='utf-8')
        # print("hr dic", dic)
        domain = [
            "|",
            ("active", "=", True),
            ("active", "=", False),
        ]
        employee = self.sudo().search([("company_id", "=", company_id.id)] + domain)

        callback_employee = employee.search(
            [("wecom_userid", "=", dic["UserID"].lower())] + domain, limit=1,
        )
        # print("员工CMD", cmd)
        if callback_employee:
            # 如果存在，则更新
            # 用于退出企业微信又重新加入企业微信的员工
            cmd = "update"
        else:
            # 如果不存在，停止
            return

        update_dict = {}
        department_ids = []  # 多部门
        new_parent_employee = False

        for key, value in dic.items():
            if key == "DirectLeader":
                parent_employee_wecom_id = value
                if parent_employee_wecom_id is None:
                    # 直属上级为空
                    new_parent_employee = False
                else:
                    # 处理直属上级
                    if "," in value:
                        parent_employee_wecom_id = value.split(",")[0]

                    new_parent_employee = employee.search(
                        [("wecom_userid", "=", parent_employee_wecom_id)], limit=1
                    )
            elif (
                    key == "ToUserName"
                    or key == "FromUserName"
                    or key == "CreateTime"
                    or key == "Event"
                    or key == "MsgType"
                    or key == "ChangeType"
            ):
                # 忽略掉 不需要的key
                pass
            else:
                if key in WECOM_USER_MAPPING_ODOO_EMPLOYEE.keys():
                    if WECOM_USER_MAPPING_ODOO_EMPLOYEE[key] != "":
                        if WECOM_USER_MAPPING_ODOO_EMPLOYEE[key] == "wecom_userid":
                            update_dict.update({"wecom_userid": value.lower()})
                        elif WECOM_USER_MAPPING_ODOO_EMPLOYEE[key] == "department_ids":
                            # 部门列表
                            departments = value.split(",")
                            for department in departments:
                                if department == 1:
                                    pass
                                else:
                                    odoo_department = (
                                        self.env["hr.department"]
                                        .sudo()
                                        .search(
                                            [
                                                (
                                                    "wecom_department_id",
                                                    "=",
                                                    department,
                                                ),
                                                ("company_id", "=", company_id.id),
                                                ("is_wecom_department", "=", True),
                                            ],
                                            limit=1,
                                        )
                                    )
                                    if len(odoo_department) > 0:
                                        department_ids.append(odoo_department.id)
                        elif WECOM_USER_MAPPING_ODOO_EMPLOYEE[key] == "department_id":
                            # 主部门
                            department_id = self.env["hr.department"].search(
                                [("wecom_department_id", "=", value)], limit=1
                            )
                            update_dict.update({"department_id": department_id.id})
                        elif WECOM_USER_MAPPING_ODOO_EMPLOYEE[key] == "active":
                            # 状态
                            # 激活状态: 1=已激活，2=已禁用，4=未激活，5=退出企业。
                            # 已激活代表已激活企业微信或已关注微工作台（原企业号）。未激活代表既未激活企业微信又未关注微工作台（原企业号）。
                            if value == "1":
                                update_dict.update({"active": True})
                            else:
                                update_dict.update({"active": False})
                        elif WECOM_USER_MAPPING_ODOO_EMPLOYEE[key] == "gender":
                            gender = self.env["wecom.tools"].sex2gender(value)
                            update_dict.update({"gender": gender})
                        # elif WECOM_USER_MAPPING_ODOO_EMPLOYEE[key] == "image_1920":
                        #     image_1920 = (
                        #         self.env["wecomapi.tools.file"].get_avatar_base64(
                        #             contacts_use_default_avatar,
                        #             dic["Gender"],
                        #             value,
                        #         ),
                        #     )
                        #     update_dict.update({"image_1920": image_1920})
                        else:
                            update_dict[WECOM_USER_MAPPING_ODOO_EMPLOYEE[key]] = value
                else:
                    _logger.info(
                        _(
                            "There is no mapping for field [%s], please contact the developer."
                        )
                        % key
                    )

        # 更新直属上级字典
        if new_parent_employee:
            update_dict.update({"parent_id": new_parent_employee.id})
        else:
            update_dict.update({"parent_id": False, "coach_id": False})

        if len(department_ids) > 0:
            update_dict.update({"department_ids": [(6, 0, department_ids)]})

        app_config = self.env["wecom.app_config"].sudo()
        contacts_use_default_avatar = app_config.get_param(
            company_id.contacts_app_id.id,
            "contacts_use_default_avatar_when_adding_employees",
        )  # 使用系统微信默认头像的标识
        contacts_update_avatar = app_config.get_param(
            company_id.contacts_app_id.id,
            "contacts_update_avatar_every_time_sync_employees",
        )  # 允许企微通讯录添加系统用户

        if cmd == "create":
            # print("执行创建员工")
            update_dict.update(
                {"company_id": company_id.id, "is_wecom_user": True, }
            )
            if contacts_use_default_avatar:
                update_dict.update(
                    {
                        "image_1920": self.env["wecomapi.tools.file"].get_avatar_base64(
                            True, dic["Gender"], dic["Gender"]
                        )
                    }
                )
            try:
                wecomapi = self.env["wecom.service_api"].InitServiceApi(
                    company_id.corpid, company_id.contacts_app_id.secret
                )
                response = wecomapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call("USER_GET"),
                    {"userid": update_dict["wecom_userid"]},
                )
                if response.get("errcode") == 0:
                    update_dict.update({"qr_code": response.get("qr_code")})
            except:
                pass

            callback_employee.create(update_dict)
        elif cmd == "update":
            if "wecom_userid" in update_dict:
                del update_dict["wecom_userid"]
            if contacts_update_avatar:
                update_dict.update(
                    {
                        "image_1920": self.env["wecomapi.tools.file"].get_avatar_base64(
                            True, dic["Gender"], dic["Gender"]
                        )
                    }
                )

            callback_employee.write(update_dict)
        elif cmd == "delete":
            # print("执行删除员工")
            callback_employee.write(
                {"active": False, }
            )
