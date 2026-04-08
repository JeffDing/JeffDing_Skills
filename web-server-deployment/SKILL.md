---
name: web-server-deployment
description: 帮助用户快速搭建和部署WEB服务器。当用户提到"安装WEB服务器"、"部署WEB服务器"、"搭建网站服务器"、"配置Apache"、"配置Nginx"、"安装Nginx"、"安装Apache"或需要设置WEB服务器环境时触发此技能。该技能会引导用户选择服务器软件、配置参数、可选部署MySQL、创建测试代码,完成完整的WEB服务器部署流程。
---

# WEB服务器安装部署技能

本技能帮助用户快速搭建和部署WEB服务器环境,包括服务器软件选择、配置、数据库部署等完整流程。

## 工作流程

### 第一步:检测现有环境

1. 检测系统中是否已安装WEB服务器软件(Apache、Nginx等)
2. 如果已安装:
   - 询问用户是否需要卸载现有服务器
   - 如果需要卸载:
     - 询问是否清除配置文件
     - 根据用户选择执行卸载操作
   - 如果不需要卸载:
     - 检查现有配置是否满足需求
     - 提供配置优化建议

### 第二步:服务器软件选择

如果需要安装新服务器,提供以下选项供用户选择:

**支持的WEB服务器软件:**
- **Nginx** - 高性能HTTP和反向代理服务器
- **Apache** - 世界使用排名第一的WEB服务器
- **Lighttpd** - 轻量级WEB服务器
- **OpenResty** - 基于Nginx的WEB平台
- **其他** - 用户自定义输入

使用表单方式询问用户:
```
请选择要安装的WEB服务器软件:
[1] Nginx (推荐用于高并发场景)
[2] Apache (推荐用于传统WEB应用)
[3] Lighttpd (推荐用于资源受限环境)
[4] OpenResty (推荐用于API网关)
[5] 其他 (自定义输入)

请输入选项编号或名称:
```

### 第三步:网站语言配置

询问用户网站使用的编程语言:

**常用WEB开发语言:**
- **PHP** - 动态网站开发
- **Python** - Web应用开发(Django/Flask)
- **Node.js** - JavaScript运行时
- **Java** - 企业级应用
- **Ruby** - Ruby on Rails
- **Go** - 高性能WEB服务
- **静态HTML** - 静态网站
- **其他** - 用户自定义输入

使用表单询问:
```
请选择网站使用的编程语言:
[1] PHP
[2] Python
[3] Node.js
[4] Java
[5] Ruby
[6] Go
[7] 静态HTML
[8] 其他 (自定义输入)

请输入选项编号或名称:
```

### 第四步:数据库配置

询问用户是否需要数据库支持:

```
是否需要连接数据库服务器? (y/n):
```

如果需要,提供数据库类型选择:

**支持的数据库:**
- **MySQL/MariaDB** - 开源关系型数据库
- **PostgreSQL** - 高级开源数据库
- **MongoDB** - NoSQL数据库
- **Redis** - 内存数据库
- **Oracle** - 商业数据库(需引导安装)
- **SQL Server** - 微软商业数据库(需引导安装)
- **其他** - 用户自定义输入

使用表单询问:
```
请选择数据库类型:
[1] MySQL/MariaDB (推荐用于WEB应用)
[2] PostgreSQL (推荐用于复杂查询)
[3] MongoDB (推荐用于文档存储)
[4] Redis (推荐用于缓存)
[5] Oracle (商业数据库)
[6] SQL Server (商业数据库)
[7] 其他 (自定义输入)

请输入选项编号或名称:
```

**数据库安装检测:**
- 如果选择开源数据库(MySQL/PostgreSQL等):
  - 检测系统是否已安装
  - 如果已安装:直接进入配置阶段
  - 如果未安装:帮助用户安装
- 如果选择商业数据库(Oracle/SQL Server):
  - 引导用户进行安装(提供安装指南)

**数据库配置参数:**
询问用户以下配置信息:
- 数据库root密码
- 数据库端口(提供默认值)
- 是否创建应用数据库
- 应用数据库名称
- 应用数据库用户名和密码

### 第五步:网站目录配置

询问用户网站文件存放目录:

```
请输入网站文件存放目录 (默认: /var/www/html):
```

提供选项:
- 使用默认目录
- 自定义目录路径
- 让系统自动创建目录

配置WEB服务器指向该目录,并提供配置文件路径供用户参考。

### 第六步:配置文件修改

在安装部署过程中,对于需要修改的配置文件:

1. **告知用户配置文件路径**
   - 显示配置文件位置
   - 说明需要修改的配置项

2. **询问修改方式:**
   ```
   配置文件修改方式:
   [1] 自动修改 (推荐)
   [2] 手动修改 (显示配置文件路径和修改说明)
   
   请选择:
   ```

3. **如果选择自动修改:**
   - 使用脚本自动修改配置文件
   - 显示修改内容供用户确认

4. **如果选择手动修改:**
   - 显示配置文件完整路径
   - 提供详细的修改说明和示例
   - 等待用户手动修改完成

### 第七步:安装部署执行

根据用户选择执行安装部署:

1. **安装WEB服务器软件**
   - 使用系统包管理器安装
   - 或从源码编译安装(如需要)

2. **安装数据库软件**(如需要)
   - 使用系统包管理器安装
   - 配置数据库服务

3. **配置WEB服务器**
   - 配置虚拟主机
   - 配置PHP/Python等语言支持
   - 配置数据库连接

4. **启动服务**
   - 启动WEB服务器服务
   - 启动数据库服务(如需要)
   - 设置开机自启动

### 第八步:创建测试代码

创建测试页面验证部署是否成功:

**无数据库场景:**
创建 `test.html` 和 `info.php`(如安装PHP):
```html
<!-- test.html -->
<!DOCTYPE html>
<html>
<head>
    <title>WEB服务器测试页面</title>
</head>
<body>
    <h1>WEB服务器部署成功!</h1>
    <p>服务器时间: <?php echo date('Y-m-d H:i:s'); ?></p>
</body>
</html>
```

**有数据库场景:**
创建 `db_test.php` 测试数据库连接:
```php
<?php
// 数据库连接测试
$host = 'localhost';
$dbname = 'test_db';
$user = 'test_user';
$pass = 'test_password';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $user, $pass);
    echo "<h1>数据库连接成功!</h1>";
    echo "<p>数据库: $dbname</p>";
} catch(PDOException $e) {
    echo "<h1>数据库连接失败:</h1>";
    echo "<p>" . $e->getMessage() . "</p>";
}
?>
```

### 第九步:测试验证

1. 访问测试页面验证WEB服务器
2. 如有数据库,测试数据库连接
3. 显示测试结果给用户
4. 询问是否保留测试文件

### 第十步:清理测试文件

测试完成后,询问用户:
```
是否清除测试生成的所有文件? (y/n):
```

如果选择清除,删除以下文件:
- test.html
- info.php
- db_test.php
- 其他测试相关文件

## 配置文件参考

### Nginx配置文件路径
- 主配置: `/etc/nginx/nginx.conf`
- 站点配置: `/etc/nginx/sites-available/` 和 `/etc/nginx/sites-enabled/`
- 默认站点: `/etc/nginx/sites-available/default`

### Apache配置文件路径
- 主配置: `/etc/apache2/apache2.conf` (Debian/Ubuntu)
- 主配置: `/etc/httpd/conf/httpd.conf` (RHEL/CentOS)
- 站点配置: `/etc/apache2/sites-available/` 和 `/etc/apache2/sites-enabled/`

### MySQL配置文件路径
- 配置文件: `/etc/mysql/mysql.conf.d/mysqld.cnf` (Debian/Ubuntu)
- 配置文件: `/etc/my.cnf` (RHEL/CentOS)

## 常用命令参考

### 服务管理命令
```bash
# Nginx
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl status nginx

# Apache
sudo systemctl start apache2
sudo systemctl stop apache2
sudo systemctl restart apache2
sudo systemctl status apache2

# MySQL
sudo systemctl start mysql
sudo systemctl stop mysql
sudo systemctl restart mysql
sudo systemctl status mysql
```

### 配置测试命令
```bash
# Nginx配置测试
sudo nginx -t

# Apache配置测试
sudo apache2ctl configtest
```

## 注意事项

1. **所有提示信息使用中文**
2. **每一步都提供清晰的选项和说明**
3. **重要操作前确认用户意图**
4. **提供配置文件路径供用户参考**
5. **测试完成后清理测试文件**
6. **记录安装日志供用户查阅**

## 错误处理

如果安装过程中出现错误:
1. 显示详细错误信息
2. 提供可能的解决方案
3. 询问用户是否继续或中止
4. 记录错误日志

## 完成提示

部署完成后显示:
```
========================================
WEB服务器部署完成!
========================================
服务器类型: [Nginx/Apache/...]
网站目录: [目录路径]
配置文件: [配置文件路径]
数据库: [已安装/未安装]
测试页面: [URL]

请访问测试页面验证部署是否成功。
========================================
```
