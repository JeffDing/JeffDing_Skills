#!/bin/bash
# 检测系统中已安装的数据库

echo "正在检测系统中已安装的数据库..."

# 检测MySQL/MariaDB
if command -v mysql &> /dev/null; then
    echo "✓ MySQL/MariaDB 已安装"
    mysql --version 2>&1
    echo "  配置文件: /etc/mysql/mysql.conf.d/mysqld.cnf 或 /etc/my.cnf"
    echo "  状态: $(systemctl is-active mysql 2>/dev/null || systemctl is-active mysqld 2>/dev/null || echo '未知')"
    MYSQL_INSTALLED=true
else
    echo "✗ MySQL/MariaDB 未安装"
    MYSQL_INSTALLED=false
fi

echo ""

# 检测PostgreSQL
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL 已安装"
    psql --version 2>&1
    echo "  配置文件: /etc/postgresql/*/main/postgresql.conf"
    echo "  状态: $(systemctl is-active postgresql 2>/dev/null || echo '未知')"
    POSTGRES_INSTALLED=true
else
    echo "✗ PostgreSQL 未安装"
    POSTGRES_INSTALLED=false
fi

echo ""

# 检测MongoDB
if command -v mongod &> /dev/null; then
    echo "✓ MongoDB 已安装"
    mongod --version 2>&1 | head -1
    echo "  配置文件: /etc/mongod.conf"
    echo "  状态: $(systemctl is-active mongod 2>/dev/null || echo '未知')"
    MONGODB_INSTALLED=true
else
    echo "✗ MongoDB 未安装"
    MONGODB_INSTALLED=false
fi

echo ""

# 检测Redis
if command -v redis-server &> /dev/null; then
    echo "✓ Redis 已安装"
    redis-server --version 2>&1
    echo "  配置文件: /etc/redis/redis.conf"
    echo "  状态: $(systemctl is-active redis 2>/dev/null || systemctl is-active redis-server 2>/dev/null || echo '未知')"
    REDIS_INSTALLED=true
else
    echo "✗ Redis 未安装"
    REDIS_INSTALLED=false
fi

echo ""
echo "检测完成!"
