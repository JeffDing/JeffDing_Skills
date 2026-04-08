# 安装指南

## Nginx安装

### Ubuntu/Debian
```bash
# 更新包列表
sudo apt update

# 安装Nginx
sudo apt install nginx -y

# 启动服务
sudo systemctl start nginx
sudo systemctl enable nginx

# 验证安装
nginx -v
```

### CentOS/RHEL
```bash
# 安装EPEL仓库
sudo yum install epel-release -y

# 安装Nginx
sudo yum install nginx -y

# 启动服务
sudo systemctl start nginx
sudo systemctl enable nginx

# 验证安装
nginx -v
```

---

## Apache安装

### Ubuntu/Debian
```bash
# 更新包列表
sudo apt update

# 安装Apache
sudo apt install apache2 -y

# 启动服务
sudo systemctl start apache2
sudo systemctl enable apache2

# 验证安装
apache2 -v
```

### CentOS/RHEL
```bash
# 安装Apache
sudo yum install httpd -y

# 启动服务
sudo systemctl start httpd
sudo systemctl enable httpd

# 验证安装
httpd -v
```

---

## PHP安装

### Ubuntu/Debian
```bash
# 添加PHP仓库
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:ondrej/php -y
sudo apt update

# 安装PHP和常用扩展
sudo apt install php7.4 php7.4-fpm php7.4-mysql php7.4-curl php7.4-gd php7.4-mbstring php7.4-xml php7.4-zip -y

# 启动PHP-FPM
sudo systemctl start php7.4-fpm
sudo systemctl enable php7.4-fpm

# 验证安装
php -v
```

### CentOS/RHEL
```bash
# 安装EPEL和Remi仓库
sudo yum install epel-release -y
sudo yum install https://rpms.remirepo.net/enterprise/remi-release-7.rpm -y

# 启用PHP 7.4模块
sudo yum-config-manager --enable remi-php74

# 安装PHP和扩展
sudo yum install php php-fpm php-mysqlnd php-curl php-gd php-mbstring php-xml php-zip -y

# 启动PHP-FPM
sudo systemctl start php-fpm
sudo systemctl enable php-fpm

# 验证安装
php -v
```

---

## MySQL/MariaDB安装

### Ubuntu/Debian (MySQL)
```bash
# 更新包列表
sudo apt update

# 安装MySQL
sudo apt install mysql-server -y

# 安全配置
sudo mysql_secure_installation

# 启动服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 验证安装
mysql --version
```

### Ubuntu/Debian (MariaDB)
```bash
# 更新包列表
sudo apt update

# 安装MariaDB
sudo apt install mariadb-server -y

# 安全配置
sudo mysql_secure_installation

# 启动服务
sudo systemctl start mariadb
sudo systemctl enable mariadb

# 验证安装
mysql --version
```

### CentOS/RHEL (MariaDB)
```bash
# 安装MariaDB
sudo yum install mariadb-server -y

# 启动服务
sudo systemctl start mariadb
sudo systemctl enable mariadb

# 安全配置
sudo mysql_secure_installation

# 验证安装
mysql --version
```

---

## PostgreSQL安装

### Ubuntu/Debian
```bash
# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 验证安装
psql --version

# 切换到postgres用户
sudo -u postgres psql
```

### CentOS/RHEL
```bash
# 安装PostgreSQL仓库
sudo yum install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm -y

# 安装PostgreSQL
sudo yum install postgresql-server -y

# 初始化数据库
sudo postgresql-setup initdb

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 验证安装
psql --version
```

---

## MongoDB安装

### Ubuntu/Debian
```bash
# 导入MongoDB公钥
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -

# 添加MongoDB仓库
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list

# 更新包列表
sudo apt update

# 安装MongoDB
sudo apt install mongodb-org -y

# 启动服务
sudo systemctl start mongod
sudo systemctl enable mongod

# 验证安装
mongod --version
```

### CentOS/RHEL
```bash
# 创建MongoDB仓库文件
sudo tee /etc/yum.repos.d/mongodb-org-4.4.repo << EOF
[mongodb-org-4.4]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/\$releasever/mongodb-org/4.4/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-4.4.asc
EOF

# 安装MongoDB
sudo yum install mongodb-org -y

# 启动服务
sudo systemctl start mongod
sudo systemctl enable mongod

# 验证安装
mongod --version
```

---

## Redis安装

### Ubuntu/Debian
```bash
# 更新包列表
sudo apt update

# 安装Redis
sudo apt install redis-server -y

# 启动服务
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 验证安装
redis-server --version
```

### CentOS/RHEL
```bash
# 安装EPEL仓库
sudo yum install epel-release -y

# 安装Redis
sudo yum install redis -y

# 启动服务
sudo systemctl start redis
sudo systemctl enable redis

# 验证安装
redis-server --version
```

---

## Node.js安装

### 使用NVM (推荐)
```bash
# 安装NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash

# 重新加载shell配置
source ~/.bashrc

# 安装Node.js LTS版本
nvm install --lts

# 验证安装
node -v
npm -v
```

### Ubuntu/Debian (使用包管理器)
```bash
# 添加NodeSource仓库
curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -

# 安装Node.js
sudo apt install nodejs -y

# 验证安装
node -v
npm -v
```

---

## Python安装

### Ubuntu/Debian
```bash
# 安装Python 3
sudo apt install python3 python3-pip python3-venv -y

# 验证安装
python3 --version
pip3 --version
```

### CentOS/RHEL
```bash
# 安装Python 3
sudo yum install python3 python3-pip -y

# 验证安装
python3 --version
pip3 --version
```

---

## 卸载指南

### 卸载Nginx
```bash
# Ubuntu/Debian
sudo apt remove nginx nginx-common nginx-core -y
sudo apt purge nginx nginx-common nginx-core -y
sudo apt autoremove -y

# CentOS/RHEL
sudo yum remove nginx -y
```

### 卸载Apache
```bash
# Ubuntu/Debian
sudo apt remove apache2 apache2-utils apache2-bin -y
sudo apt purge apache2 apache2-utils apache2-bin -y
sudo apt autoremove -y

# CentOS/RHEL
sudo yum remove httpd -y
```

### 卸载MySQL
```bash
# Ubuntu/Debian
sudo apt remove mysql-server mysql-client mysql-common -y
sudo apt purge mysql-server mysql-client mysql-common -y
sudo apt autoremove -y
sudo rm -rf /etc/mysql /var/lib/mysql

# CentOS/RHEL
sudo yum remove mysql-server mysql -y
sudo rm -rf /var/lib/mysql /etc/my.cnf
```
