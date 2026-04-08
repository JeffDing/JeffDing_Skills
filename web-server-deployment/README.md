# WEB服务器安装部署 Skill

## 简介

这是一个帮助用户快速搭建和部署WEB服务器的技能。通过交互式引导,帮助用户完成从服务器选择、配置到测试验证的完整流程。

## 功能特性

- ✅ **智能环境检测** - 自动检测系统中已安装的WEB服务器,支持卸载和配置清理
- ✅ **多种服务器支持** - 支持 Nginx、Apache、Lighttpd、Caddy 等主流WEB服务器
- ✅ **多语言支持** - 支持 PHP、Python、Node.js、Java、Ruby 等编程语言
- ✅ **MySQL自动部署** - 可选自动部署和配置MySQL数据库
- ✅ **交互式配置** - 通过表单逐步收集配置信息,降低使用门槛
- ✅ **自动生成测试代码** - 创建测试页面验证部署是否成功
- ✅ **完整部署报告** - 提供详细的部署报告和后续操作建议
- ✅ **中文交互** - 所有提示和交互均使用中文

## 安装方法

### 方法一:直接安装 .skill 文件

```bash
# 将 web-server-deployment.skill 文件放置到您的技能目录
cp /root/web-server-deployment.skill ~/.codeartsdoer/skills/
```

### 方法二:从源码安装

```bash
# 将整个 web-server-deployment 目录复制到技能目录
cp -r /root/web-server-deployment ~/.codeartsdoer/skills/
```

## 使用方法

安装技能后,在对话中使用以下任意触发词:

- "安装WEB服务器"
- "部署WEB服务器"
- "搭建网站服务器"
- "配置Apache"
- "配置Nginx"
- "安装Nginx"
- "安装Apache"

### 使用示例

**示例1:部署PHP网站服务器**

```
用户: 我想在我的服务器上安装一个WEB服务器,用来托管我的PHP网站,网站需要连接MySQL数据库
```

技能将引导您:
1. 选择WEB服务器软件(Nginx/Apache等)
2. 确认使用PHP语言
3. 配置MySQL数据库
4. 设置网站目录和端口
5. 自动生成配置和测试页面

**示例2:部署Python应用服务器**

```
用户: 帮我部署Nginx服务器,我的网站是用Python写的Flask应用
```

技能将:
1. 检测现有环境
2. 配置Nginx用于Python应用
3. 询问是否需要MySQL
4. 生成相应配置

**示例3:部署静态网站**

```
用户: 我需要搭建一个静态网站服务器,只需要托管HTML文件,不需要数据库
```

技能将:
1. 引导选择轻量级服务器
2. 配置静态文件服务
3. 跳过MySQL部署
4. 创建HTML测试页面

## 工作流程

1. **检查现有环境** - 检测已安装的服务器和端口占用情况
2. **选择服务器软件** - 提供 Nginx、Apache、Lighttpd、Caddy 选项
3. **收集配置信息** - 编程语言、数据库、目录、域名、端口
4. **安装和配置** - 执行安装命令,生成配置文件
5. **创建测试代码** - 生成测试页面验证部署
6. **启动和验证** - 启动服务并验证
7. **输出部署报告** - 提供完整报告和后续建议

## 支持的操作系统

- Ubuntu 18.04/20.04/22.04
- Debian 10/11
- CentOS 7/8
- RHEL 7/8

## 文件结构

```
web-server-deployment/
├── SKILL.md              # 技能主文件
└── README.md             # 本说明文档
```

## 配置文件位置

### Nginx
- 主配置: `/etc/nginx/nginx.conf`
- 站点配置: `/etc/nginx/sites-available/`
- 启用站点: `/etc/nginx/sites-enabled/`

### Apache
- 主配置: `/etc/apache2/apache2.conf` (Debian) 或 `/etc/httpd/conf/httpd.conf` (RHEL)
- 虚拟主机: `/etc/apache2/sites-available/`

## 测试页面

部署完成后,技能会创建以下测试页面:

- `test.html` - HTML基础测试
- `test.php` - PHP运行测试
- `test_mysql.php` - MySQL连接测试(如已部署MySQL)

访问方式:
```
http://[您的域名或IP]/test.html
http://[您的域名或IP]/test.php
http://[您的域名或IP]/test_mysql.php
```

## 安全建议

⚠️ 部署完成后请注意:
1. 及时修改MySQL root密码
2. 修改应用数据库用户密码
3. 配置防火墙限制访问
4. 生产环境关闭测试页面
5. 定期备份数据库和配置文件
6. 配置SSL证书启用HTTPS

## 常见问题

### Q: 端口被占用怎么办?
A: 技能会自动检测端口占用,并提示您停止占用进程或更换端口

### Q: 已有服务器如何处理?
A: 技能会询问是否卸载,并可选择保留或清除配置文件

### Q: 支持哪些编程语言?
A: 支持 PHP、Python、Node.js、Java、Ruby、静态HTML,以及自定义输入

### Q: 是否必须安装MySQL?
A: 不是,MySQL是可选的,技能会询问您的需求

### Q: 配置文件如何修改?
A: 技能会告知配置文件路径,可选择自动配置或手动修改

## 技术支持

如有问题或建议,请查看 SKILL.md 文件获取详细说明。

## 版本信息

- 版本: 1.0.0
- 创建日期: 2026-04-08
- 作者: CodeArts Agent
