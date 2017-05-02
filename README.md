# DNSPod
使用python 获取本机ip 更新动态DNS记录到donpod

接口地址： https://dnsapi.cn/Record.Ddns

HTTP请求方式：POST

请求参数：

公共参数
domain_id 或 domain, 分别对应域名ID和域名, 提交其中一个即可
record_id 记录ID，必选
sub_domain 主机记录，如 www
record_line 记录线路，通过API记录线路获得，中文，比如：默认，必选
record_line_id 线路的ID，通过API记录线路获得，英文字符串，比如：‘10=1’ 【record_line 和 record_line_id 二者传其一即可，系统优先取 record_line_id】
value IP地址，例如：6.6.6.6，可选

响应代码：

共通返回
-15 域名已被封禁
-7 企业账号的域名需要升级才能设置
-8 代理名下用户的域名需要升级才能设置
6 域名ID错误
7 不是域名所有者或没有权限
8 记录ID错误
21 域名被锁定
22 子域名不合法
23 子域名级数超出限制，比如免费套餐域名不支持三级域名
24 泛解析子域名错误，比如免费套餐载名不支持 a*
25 轮循记录数量超出限制，比如免费套餐域名只能存在两条轮循记录
26 记录线路错误，比如免费套餐域名不支持移动、国外

注意事项：

如果1小时之内，提交了超过5次没有任何变动的记录修改请求，该记录会被系统锁定1小时，不允许再次修改，所以在开发和测试的过程中，请自行处理IP变动，仅在本地IP发生变动的情况下才调用本接口。
如何理解没有任何变动的记录修改请求？比如原记录值已经是 1.1.1.1，新的请求还要求修改为 1.1.1.1。

示例:
curl -X POST https://dnsapi.cn/Record.Ddns -d 'login_token=LOGIN_TOKEN&format=json&domain_id=2317346&record_id=16894439&record_line_id=10%3D3&sub_domain=www'

返回参考：

JSON:
{
    "status": {
        "code":"1",
        "message":"Action completed successful",
        "created_at":"2015-01-18 17:23:58"
    },
    "record": {
        "id":16909160,
        "name":"@",
        "value":"111.111.111.111"
    }
}

字段说明:

id: 记录ID, 即为 record_id
name: 子域名
value”: 记录值

注意：

record_line_id 形如 “10=3”，其中可能会包含等号，即 “=”，如果是通过类似 URL 传递参数，需要将 ‘=’ 转义成 ‘%3D’
