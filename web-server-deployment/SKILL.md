---
name: web-server-deployment
description: 帮助用户快速搭建和部署WEB服务器。当用户需要安装、配置或部署WEB服务器(如Apache、Nginx、Tomcat等)时使用此skill。支持服务器软件选择、已安装服务检测、数据库集成、配置文件管理、测试验证等完整部署流程。所有交互均使用中文进行。
---

# WEB服务器安装部署助手

这个skill帮助用户快速、交互式地搭建和部署WEB服务器,提供从服务器选择到测试验证的完整流程。

## 核心工作流程

### 1. 需求收集与服务器选择

首先,通过交互式表单收集用户需求:

**询问步骤:**

1. **网站开发语言**
   - 列出常用选项:PHP、Java、Python、Node.js、Go、Ruby
   - 提供"其他"选项供用户自定义输入
   - 根据语言推荐合适的服务器软件

2. **WEB服务器软件选择**
   - 根据开发语言列出推荐的服务器软件
   - 常见选项:
     - PHP: Apache、Nginx
     - Java: Tomcat、Jetty、JBoss
     - Python: Nginx+uWSGI、Gunicorn
     - Node.js: Nginx(反向代理)、直接运行
     - Go: Nginx(反向代理)、直接运行
   - 显示每个选项的简要说明
   - 让用户选择具体安装哪一款

3. **网页文件存放目录**
   - 询问用户网页文件的存放位置
   - 提供默认路径建议(如 `/var/www/html`、`/usr/share/nginx/html`)
   - 用户可以自定义路径
   - 记录此路径用于后续配置

### 2. 已安装服务检测与处理

在安装前,检测系统中是否已存在目标服务器软件:

**检测流程:**

```bash
# 检测常见WEB服务器
- Apache: 检查 httpd/apache2 进程和包管理器
- Nginx: 检查 nginx 进程和包管理器
- Tomcat: 检查 tomcat 进程和目录
```

**如果已安装:**

1. 询问用户是否需要卸载现有服务
   - **选择卸载:**
     - 询问是否清除配置文件
     - 需要清除: 删除配置文件和安装目录
     - 不需要清除: 保留配置文件,仅卸载软件
   - **选择不卸载:**
     - 检查现有配置是否满足需求
     - 如不满足,询问是否需要升级或重新配置

### 3. 数据库服务器集成

询问用户是否需要连接数据库服务器:

**数据库选择流程:**

1. **是否需要数据库**
   - 是: 继续数据库配置
   - 否: 跳过此步骤

2. **数据库类型选择**
   - 列出常用选项:MySQL/MariaDB、PostgreSQL、Oracle、OpenGauss、MongoDB
   - 提供"其他"选项供自定义

3. **数据库安装检测**
   - 检测系统是否已安装所选数据库
   - **已安装:**
     - 显示版本信息
     - 直接进入配置阶段
   - **未安装:**
     - 询问是否需要安装
     - 帮助用户安装数据库服务器

4. **数据库连接配置**
   - 配置主机地址、端口
   - 设置用户名和密码
   - 创建应用所需数据库
   - 测试连接是否成功

### 4. 服务器安装与配置

**安装流程:**

1. **安装服务器软件**
   - 使用系统包管理器(apt/yum/dnf/pacman)或源码安装
   - 显示安装进度
   - 验证安装是否成功

2. **配置文件管理**
   - 识别配置文件路径:
     - Apache: `/etc/apache2/apache2.conf` 或 `/etc/httpd/conf/httpd.conf`
     - Nginx: `/etc/nginx/nginx.conf`
     - Tomcat: `/opt/tomcat/conf/server.xml`
   
   - **配置方式选择:**
     - **自动配置:** 根据用户需求自动修改配置文件
     - **手动配置:** 告知用户配置文件路径和修改方法,让用户自行修改
   
   - **常见配置项:**
     - 网页根目录设置
     - 端口配置
     - 虚拟主机配置
     - SSL/HTTPS配置
     - 反向代理配置
     - PHP-FPM集成(如需要)

3. **防火墙配置**
   - 开放所需端口(80、443、8080等)
   - 配置SELinux或防火墙规则

### 5. 服务启动与验证

**启动服务:**

```bash
# 启动WEB服务器
systemctl start <service-name>
systemctl enable <service-name>

# 检查服务状态
systemctl status <service-name>
```

**验证部署:**

1. 创建测试页面
2. 访问测试URL验证服务正常
3. 如配置了数据库,测试数据库连接

### 6. 测试代码生成

创建示例代码测试部署是否成功:

**测试场景:**

1. **无数据库场景**
   - 创建静态HTML测试页面
   - 根据语言创建动态测试脚本:
     - PHP: `test.php` (phpinfo)
     - Java: `test.jsp`
     - Python: `test.py` (Flask/Django)
     - Node.js: `test.js`

2. **有数据库场景**
   - 创建数据库连接测试脚本
   - 执行简单的CRUD操作
   - 验证数据读写正常

**测试代码示例:**

```php
<?php
// test.php - 无数据库
phpinfo();
?>

<?php
// test_db.php - 有数据库
$conn = new mysqli("localhost", "user", "pass", "dbname");
if ($conn->connect_error) {
    die("连接失败: " . $conn->connect_error);
}
echo "数据库连接成功!";
$conn->close();
?>
```

### 7. 清理测试文件

测试完成后,询问用户是否清除测试生成的所有文件:

- 删除测试页面和脚本
- 删除测试数据库和表
- 保留用户确认需要保留的文件

## 交互原则

1. **全程中文提示**
   - 所有询问、提示、错误信息均使用中文
   - 技术术语保留英文,但提供中文解释

2. **逐步引导**
   - 一次只询问一个问题
   - 提供清晰的选项列表
   - 允许用户返回修改之前的配置

3. **智能推荐**
   - 根据用户选择的语言推荐服务器
   - 根据系统环境推荐安装方式
   - 提供合理的默认配置

4. **错误处理**
   - 检测到错误时提供解决方案
   - 允许用户重试或跳过
   - 记录详细的错误日志

## 配置文件路径参考

常见WEB服务器配置文件位置:

| 服务器 | 主配置文件 | 虚拟主机配置 | 日志目录 |
|--------|-----------|-------------|---------|
| Apache (Debian/Ubuntu) | /etc/apache2/apache2.conf | /etc/apache2/sites-available/ | /var/log/apache2/ |
| Apache (RHEL/CentOS) | /etc/httpd/conf/httpd.conf | /etc/httpd/conf.d/ | /var/log/httpd/ |
| Nginx | /etc/nginx/nginx.conf | /etc/nginx/conf.d/ | /var/log/nginx/ |
| Tomcat | /opt/tomcat/conf/server.xml | /opt/tomcat/conf/ | /opt/tomcat/logs/ |

## 常用命令参考

**服务管理:**
```bash
# 启动服务
systemctl start <service>

# 停止服务
systemctl stop <service>

# 重启服务
systemctl restart <service>

# 查看状态
systemctl status <service>

# 开机自启
systemctl enable <service>

# 禁用自启
systemctl disable <service>
```

**包管理:**
```bash
# Debian/Ubuntu
apt update && apt install <package>
apt remove <package>
apt purge <package>  # 删除配置文件

# RHEL/CentOS/Fedora
yum install <package>  # 或 dnf
yum remove <package>
```

## 使用示例

**示例1: 部署PHP网站**
```
用户: 我想部署一个PHP网站
助手: 好的,我来帮你部署PHP网站。首先,请问你的网站使用什么WEB服务器?
      1. Apache (推荐)
      2. Nginx
      请选择: [1/2]
```

**示例2: 检测到已安装服务**
```
助手: 检测到系统中已安装Apache 2.4.41版本。
      请问你需要:
      1. 卸载现有Apache并重新安装
      2. 保留现有Apache并检查配置
      3. 取消操作
      请选择: [1/2/3]
```

**示例3: 数据库集成**
```
助手: 请问你的网站需要连接数据库吗?
      [Y/n]: y
      
助手: 请选择数据库类型:
      1. MySQL/MariaDB
      2. PostgreSQL
      3. Oracle
      4. OpenGauss
      5. 其他
      请选择: [1-5]
```

## 注意事项

1. **权限要求**
   - 需要root或sudo权限进行安装和配置
   - 提示用户使用sudo或切换到root用户

2. **系统兼容性**
   - 支持主流Linux发行版:Ubuntu、Debian、CentOS、RHEL、Fedora
   - 自动检测系统版本并选择合适的包管理器

3. **安全建议**
   - 提醒用户修改默认密码
   - 建议配置防火墙规则
   - 推荐启用HTTPS

4. **备份建议**
   - 在修改配置前备份原配置文件
   - 提供回滚机制

## 工作流程总结

```
开始
  ↓
收集需求(语言、服务器、目录)
  ↓
检测已安装服务 → 已安装 → 询问卸载/保留
  ↓
安装服务器软件
  ↓
配置服务器(自动/手动)
  ↓
数据库集成(可选)
  ↓
启动服务
  ↓
生成测试代码
  ↓
验证部署
  ↓
清理测试文件(可选)
  ↓
完成
```

---

## 实施指南

当用户请求部署WEB服务器时,按照以下步骤执行:

1. **初始化交互会话**
   - 使用中文问候用户
   - 简要说明将要进行的步骤

2. **逐步收集信息**
   - 按顺序询问:开发语言 → 服务器软件 → 网页目录 → 数据库需求
   - 每个问题提供清晰的选项
   - 记录用户的选择

3. **执行部署操作**
   - 检测系统环境
   - 处理已安装服务
   - 安装所需软件
   - 配置服务器和数据库

4. **验证和测试**
   - 启动服务
   - 生成测试代码
   - 执行测试验证
   - 清理测试文件

5. **提供后续指导**
   - 告知配置文件位置
   - 提供常用管理命令
   - 给出安全建议

始终使用中文进行所有交互,确保用户理解每一步操作。
