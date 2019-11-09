# 企业微信 For Odoo 13.0
odoo 13.0变化很大，发现不少需要改动的。

自己不是专职开发,还要负债运维和管理,往往一个功能断断续续做出来,要花不少时间.所以请见谅项目的进展速度.

欢迎提交功能需求

# 适配odoo13.0开发计划，随着自己的想法而变动
## 开源项目
1. wxwork_base （企业微信-基础模块）完成适配
2. wxwork_contacts （企业微信-通讯簿同步）基本完成，部分需要腾讯更新API     
3. wxwork_auth_oauth （企业微信-登录授权）已完成在服务器上的测试
4. wxwork_attendance (企业微信-打卡) 已完成拉取打卡数据
5. wxwork_attendance_rule (企业微信-打卡规则) 已完成拉取打卡规则
6. eis_scheduling(中国国情排班)，代码加密不开源但免费提供使用,未开展
7. wxwork_notice（企业微信-通知），未开展
8. wxwork_approval（企业微信-审批），未开展
9. wxwork_reset_password（企业微信-密码重置），未开展
10. wxwork_dial_record(企业微信-公费电话拨打记录)，未开展
11. wxwork_invoice(企业微信-电子发票)，未开展

## 计划收费项目
1. 个性化后端UI


# 帮助

## 安装
1. 下载代码
    ```bash
    git clone git@gitee.com:rainbowstudio/wxwork.git --depth 1 --branch 13.0 --single-branch wxwork 
    ```
2. 切换到 wxwork 目录,安装requirements.txt中的python包
    ```bash
    pip install -r requirements.txt -i https://pypi.doubanio.com/simple
   或
   pip3 install -r requirements.txt -i https://pypi.doubanio.com/simple
    ```

 
## 模块 介绍 

## 使用说明



如果我的作品能对您有所帮助，能力范围内，请不要介意点击下面“捐赠”按钮，或者点个⭐。