# WEB服务器配置参考

## Nginx配置

### 基础配置文件结构
```
/etc/nginx/
├── nginx.conf                 # 主配置文件
├── sites-available/           # 可用站点配置
│   └── default
├── sites-enabled/             # 启用的站点配置(软链接)
│   └── default -> ../sites-available/default
├── conf.d/                    # 额外配置
└── modules-enabled/           # 启用的模块
```

### 常用配置示例

#### 虚拟主机配置
```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    root /var/www/example.com;
    index index.html index.php;

    # 日志文件
    access_log /var/log/nginx/example.com.access.log;
    error_log /var/log/nginx/example.com.error.log;

    # PHP支持
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

#### 反向代理配置
```nginx
server {
    listen 80;
    server_name api.example.com;

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
sudo nginx -t

# 重载配置
sudo systemctl reload nginx

# 重启服务
sudo systemctl restart nginx

# 查看状态
sudo systemctl status nginx
```

---

## Apache配置

### 基础配置文件结构(Debian/Ubuntu)
```
/etc/apache2/
├── apache2.conf              # 主配置文件
├── sites-available/          # 可用站点配置
│   └── 000-default.conf
├── sites-enabled/            # 启用的站点配置(软链接)
│   └── 000-default.conf -> ../sites-available/000-default.conf
├── mods-available/           # 可用模块
└── mods-enabled/             # 启用的模块
```

### 常用配置示例

#### 虚拟主机配置
```apache
<VirtualHost *:80>
    ServerName example.com
    ServerAlias www.example.com
    DocumentRoot /var/www/example.com

    ErrorLog ${APACHE_LOG_DIR}/example.com.error.log
    CustomLog ${APACHE_LOG_DIR}/example.com.access.log combined

    <Directory /var/www/example.com>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

#### 启用模块
```bash
# 启用rewrite模块
sudo a2enmod rewrite

# 启用SSL模块
sudo a2enmod ssl

# 禁用模块
sudo a2dismod rewrite
```

#### 启用站点
```bash
# 启用站点
sudo a2ensite example.com

# 禁用站点
sudo a2dissite example.com
```

### 常用命令
```bash
# 测试配置
sudo apache2ctl configtest

# 重载配置
sudo systemctl reload apache2

# 重启服务
sudo systemctl restart apache2

# 查看状态
sudo systemctl status apache2
```

---

## PHP-FPM配置

### 配置文件路径
```
/etc/php/7.4/fpm/
├── php.ini                   # PHP配置
├── pool.d/
│   └── www.conf              # 进程池配置
```

### 常用配置项
```ini
; 内存限制
memory_limit = 256M

; 上传文件大小
upload_max_filesize = 20M
post_max_size = 20M

; 执行时间
max_execution_time = 300

; 错误显示
display_errors = Off
log_errors = On
```

### 常用命令
```bash
# 重启PHP-FPM
sudo systemctl restart php7.4-fpm

# 查看状态
sudo systemctl status php7.4-fpm
```

---

## MySQL配置

### 配置文件路径
```
/etc/mysql/
├── my.cnf                    # 主配置文件
└── mysql.conf.d/
    └── mysqld.cnf            # 服务器配置
```

### 常用配置项
```ini
[mysqld]
# 监听地址
bind-address = 127.0.0.1

# 端口
port = 3306

# 字符集
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# 存储引擎
default-storage-engine = INNODB

# 缓冲池大小
innodb_buffer_pool_size = 1G
```

### 常用命令
```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户
CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'password';

# 授权
GRANT ALL PRIVILEGES ON mydb.* TO 'myuser'@'localhost';
FLUSH PRIVILEGES;

# 重启MySQL
sudo systemctl restart mysql
```

---

## 防火墙配置

### UFW (Ubuntu)
```bash
# 允许HTTP
sudo ufw allow 80/tcp

# 允许HTTPS
sudo ufw allow 443/tcp

# 允许SSH
sudo ufw allow 22/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### firewalld (CentOS/RHEL)
```bash
# 允许HTTP
sudo firewall-cmd --permanent --add-service=http

# 允许HTTPS
sudo firewall-cmd --permanent --add-service=https

# 重载配置
sudo firewall-cmd --reload

# 查看状态
sudo firewall-cmd --list-all
```
