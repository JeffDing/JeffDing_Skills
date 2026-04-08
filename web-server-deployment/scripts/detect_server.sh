#!/bin/bash
# WEB服务器检测脚本

# 检测Apache
detect_apache() {
    if command -v apache2 >/dev/null 2>&1 || command -v httpd >/dev/null 2>&1; then
        echo "Apache已安装"
        if command -v apache2 >/dev/null 2>&1; then
            apache2 -v
        else
            httpd -v
        fi
        return 0
    fi
    return 1
}

# 检测Nginx
detect_nginx() {
    if command -v nginx >/dev/null 2>&1; then
        echo "Nginx已安装"
        nginx -v
        return 0
    fi
    return 1
}

# 检测Tomcat
detect_tomcat() {
    if [ -d "/opt/tomcat" ] || [ -d "/usr/share/tomcat" ]; then
        echo "Tomcat已安装"
        if [ -f "/opt/tomcat/bin/version.sh" ]; then
            /opt/tomcat/bin/version.sh
        elif [ -f "/usr/share/tomcat/bin/version.sh" ]; then
            /usr/share/tomcat/bin/version.sh
        fi
        return 0
    fi
    return 1
}

# 检测MySQL/MariaDB
detect_mysql() {
    if command -v mysql >/dev/null 2>&1; then
        echo "MySQL/MariaDB已安装"
        mysql --version
        return 0
    fi
    return 1
}

# 检测PostgreSQL
detect_postgresql() {
    if command -v psql >/dev/null 2>&1; then
        echo "PostgreSQL已安装"
        psql --version
        return 0
    fi
    return 1
}

# 主检测函数
detect_all() {
    echo "=== WEB服务器检测 ==="
    detect_apache || echo "Apache未安装"
    echo ""
    detect_nginx || echo "Nginx未安装"
    echo ""
    detect_tomcat || echo "Tomcat未安装"
    echo ""
    echo "=== 数据库服务器检测 ==="
    detect_mysql || echo "MySQL/MariaDB未安装"
    echo ""
    detect_postgresql || echo "PostgreSQL未安装"
}

# 执行检测
detect_all
