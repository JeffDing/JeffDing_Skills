# 安装指南

## Apache安装

### Ubuntu/Debian

```bash
# 更新包列表
sudo apt update

# 安装Apache
sudo apt install apache2

# 安装PHP模块(如需要)
sudo apt install php libapache2-mod-php php-mysql

# 启动服务
sudo systemctl start apache2
sudo systemctl enable apache2

# 检查状态
sudo systemctl status apache2
```

### CentOS/RHEL

```bash
# 安装Apache
sudo yum install httpd

# 安装PHP模块(如需要)
sudo yum install php php-mysqlnd

# 启动服务
sudo systemctl start httpd
sudo systemctl enable httpd

# 检查状态
sudo systemctl status httpd
```

---

## Nginx安装

### Ubuntu/Debian

```bash
# 更新包列表
sudo apt update

# 安装Nginx
sudo apt install nginx

# 启动服务
sudo systemctl start nginx
sudo systemctl enable nginx

# 检查状态
sudo systemctl status nginx
```

### CentOS/RHEL

```bash
# 安装EPEL仓库
sudo yum install epel-release

# 安装Nginx
sudo yum install nginx

# 启动服务
sudo systemctl start nginx
sudo systemctl enable nginx

# 检查状态
sudo systemctl status nginx
```

---

## Tomcat安装

### 通用安装方法

```bash
# 安装Java
sudo apt install default-jdk  # Ubuntu/Debian
sudo yum install java-1.8.0-openjdk  # CentOS/RHEL

# 创建Tomcat用户
sudo useradd -m -d /opt/tomcat -s /bin/bash tomcat

# 下载Tomcat
cd /tmp
wget https://downloads.apache.org/tomcat/tomcat-9/v9.0.65/bin/apache-tomcat-9.0.65.tar.gz

# 解压到/opt/tomcat
sudo tar xzvf apache-tomcat-9.0.65.tar.gz -C /opt/tomcat --strip-components=1

# 设置权限
sudo chown -R tomcat:tomcat /opt/tomcat
sudo chmod +x /opt/tomcat/bin/*.sh

# 创建systemd服务
sudo nano /etc/systemd/system/tomcat.service
```

### Tomcat systemd服务文件

```ini
[Unit]
Description=Apache Tomcat Web Application Container
After=network.target

[Service]
Type=forking
User=tomcat
Group=tomcat
Environment="JAVA_HOME=/usr/lib/jvm/default-java"
Environment="CATALINA_PID=/opt/tomcat/temp/tomcat.pid"
Environment="CATALINA_HOME=/opt/tomcat"
Environment="CATALINA_BASE=/opt/tomcat"
Environment="CATALINA_OPTS=-Xms512M -Xmx1024M -server -XX:+UseParallelGC"
Environment="JAVA_OPTS=-Djava.awt.headless=true -Djava.security.egd=file:/dev/./urandom"
ExecStart=/opt/tomcat/bin/startup.sh
ExecStop=/opt/tomcat/bin/shutdown.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 启动Tomcat

```bash
# 重载systemd
sudo systemctl daemon-reload

# 启动Tomcat
sudo systemctl start tomcat
sudo systemctl enable tomcat

# 检查状态
sudo systemctl status tomcat
```

---

## 数据库安装

### MySQL/MariaDB (Ubuntu/Debian)

```bash
# 安装MySQL
sudo apt install mysql-server

# 安装MariaDB
sudo apt install mariadb-server

# 安全配置
sudo mysql_secure_installation

# 启动服务
sudo systemctl start mysql
sudo systemctl enable mysql
```

### MySQL/MariaDB (CentOS/RHEL)

```bash
# 安装MariaDB
sudo yum install mariadb-server

# 启动服务
sudo systemctl start mariadb
sudo systemctl enable mariadb

# 安全配置
sudo mysql_secure_installation
```

### PostgreSQL (Ubuntu/Debian)

```bash
# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 切换到postgres用户
sudo -u postgres psql
```

### PostgreSQL (CentOS/RHEL)

```bash
# 安装PostgreSQL
sudo yum install postgresql-server postgresql-contrib

# 初始化数据库
sudo postgresql-setup initdb

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

## PHP-FPM安装

### Ubuntu/Debian

```bash
# 安装PHP-FPM
sudo apt install php-fpm

# 常用PHP扩展
sudo apt install php-mysql php-curl php-gd php-mbstring php-xml php-xmlrpc php-soap php-intl php-zip

# 启动服务
sudo systemctl start php7.4-fpm
sudo systemctl enable php7.4-fpm
```

### Nginx + PHP-FPM配置

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.php index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
```

---

## 卸载指南

### Apache卸载

```bash
# Ubuntu/Debian
sudo systemctl stop apache2
sudo apt remove apache2
sudo apt purge apache2  # 删除配置文件
sudo apt autoremove

# CentOS/RHEL
sudo systemctl stop httpd
sudo yum remove httpd
```

### Nginx卸载

```bash
# Ubuntu/Debian
sudo systemctl stop nginx
sudo apt remove nginx
sudo apt purge nginx  # 删除配置文件
sudo apt autoremove

# CentOS/RHEL
sudo systemctl stop nginx
sudo yum remove nginx
```

### MySQL/MariaDB卸载

```bash
# Ubuntu/Debian
sudo systemctl stop mysql
sudo apt remove mysql-server
sudo apt purge mysql-server  # 删除配置文件
sudo apt autoremove

# 删除数据目录(谨慎操作)
sudo rm -rf /var/lib/mysql
sudo rm -rf /etc/mysql
```

### PostgreSQL卸载

```bash
# Ubuntu/Debian
sudo systemctl stop postgresql
sudo apt remove postgresql
sudo apt purge postgresql  # 删除配置文件
sudo apt autoremove

# 删除数据目录(谨慎操作)
sudo rm -rf /var/lib/postgresql
sudo rm -rf /etc/postgresql
```
