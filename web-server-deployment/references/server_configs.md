# WEB服务器配置参考

## Apache配置

### 基本配置文件位置
- Debian/Ubuntu: `/etc/apache2/apache2.conf`
- RHEL/CentOS: `/etc/httpd/conf/httpd.conf`

### 虚拟主机配置示例

```apache
<VirtualHost *:80>
    ServerName example.com
    ServerAlias www.example.com
    DocumentRoot /var/www/html/example
    
    <Directory /var/www/html/example>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/example_error.log
    CustomLog ${APACHE_LOG_DIR}/example_access.log combined
</VirtualHost>
```

### PHP集成配置

```apache
# 启用PHP模块
LoadModule php_module modules/mod_php.so

# PHP文件处理
<FilesMatch \.php$>
    SetHandler application/x-httpd-php
</FilesMatch>
```

### 常用命令
```bash
# 启用站点
a2ensite example.conf

# 禁用站点
a2dissite example.conf

# 启用模块
a2enmod rewrite

# 测试配置
apache2ctl configtest

# 重启服务
systemctl restart apache2
```

---

## Nginx配置

### 基本配置文件位置
- 主配置: `/etc/nginx/nginx.conf`
- 站点配置: `/etc/nginx/sites-available/` 或 `/etc/nginx/conf.d/`

### 基础站点配置

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    root /var/www/html/example;
    index index.html index.php;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # PHP处理
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
    }
    
    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

### 反向代理配置

```nginx
server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 常用命令
```bash
# 测试配置
nginx -t

# 重载配置
nginx -s reload

# 查看状态
systemctl status nginx
```

---

## Tomcat配置

### 配置文件位置
- 主配置: `/opt/tomcat/conf/server.xml`
- Web应用: `/opt/tomcat/webapps/`

### server.xml基本配置

```xml
<Server port="8005" shutdown="SHUTDOWN">
  <Service name="Catalina">
    <Connector port="8080" protocol="HTTP/1.1"
               connectionTimeout="20000"
               redirectPort="8443" />
    
    <Engine name="Catalina" defaultHost="localhost">
      <Host name="localhost"  appBase="webapps"
            unpackWARs="true" autoDeploy="true">
        
        <Context path="" docBase="myapp" reloadable="true"/>
        
        <Valve className="org.apache.catalina.valves.AccessLogValve"
               directory="logs"
               prefix="localhost_access_log"
               suffix=".txt"
               pattern="%h %l %u %t &quot;%r&quot; %s %b" />
      </Host>
    </Engine>
  </Service>
</Server>
```

### 常用命令
```bash
# 启动
/opt/tomcat/bin/startup.sh

# 停止
/opt/tomcat/bin/shutdown.sh

# 查看日志
tail -f /opt/tomcat/logs/catalina.out
```

---

## 数据库配置

### MySQL/MariaDB

```bash
# 安装后安全配置
mysql_secure_installation

# 创建数据库和用户
mysql -u root -p
CREATE DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'mypassword';
GRANT ALL PRIVILEGES ON mydb.* TO 'myuser'@'localhost';
FLUSH PRIVILEGES;
```

### PostgreSQL

```bash
# 切换到postgres用户
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE mydb;
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;
```

---

## 防火墙配置

### UFW (Ubuntu/Debian)

```bash
# 允许HTTP
sudo ufw allow 80/tcp

# 允许HTTPS
sudo ufw allow 443/tcp

# 允许特定端口
sudo ufw allow 8080/tcp

# 查看状态
sudo ufw status
```

### firewalld (RHEL/CentOS)

```bash
# 允许HTTP
sudo firewall-cmd --permanent --add-service=http

# 允许HTTPS
sudo firewall-cmd --permanent --add-service=https

# 允许特定端口
sudo firewall-cmd --permanent --add-port=8080/tcp

# 重载配置
sudo firewall-cmd --reload

# 查看规则
sudo firewall-cmd --list-all
```

---

## SSL/HTTPS配置

### Let's Encrypt (Certbot)

```bash
# 安装certbot
sudo apt install certbot python3-certbot-apache  # Apache
sudo apt install certbot python3-certbot-nginx   # Nginx

# 获取证书
sudo certbot --apache -d example.com -d www.example.com
sudo certbot --nginx -d example.com -d www.example.com

# 自动续期测试
sudo certbot renew --dry-run
```

### 自签名证书

```bash
# 生成私钥和证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/selfsigned.key \
  -out /etc/ssl/certs/selfsigned.crt

# Apache配置
<VirtualHost *:443>
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/selfsigned.crt
    SSLCertificateKeyFile /etc/ssl/private/selfsigned.key
</VirtualHost>

# Nginx配置
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/selfsigned.key;
}
```
