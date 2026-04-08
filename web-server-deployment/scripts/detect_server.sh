#!/bin/bash
# 检测系统中已安装的WEB服务器

echo "正在检测系统中已安装的WEB服务器..."

# 检测Nginx
if command -v nginx &> /dev/null; then
    echo "✓ Nginx 已安装"
    nginx -v 2>&1
    echo "  配置文件: /etc/nginx/nginx.conf"
    echo "  状态: $(systemctl is-active nginx 2>/dev/null || echo '未知')"
    NGINX_INSTALLED=true
else
    echo "✗ Nginx 未安装"
    NGINX_INSTALLED=false
fi

echo ""

# 检测Apache
if command -v apache2 &> /dev/null || command -v httpd &> /dev/null; then
    echo "✓ Apache 已安装"
    if command -v apache2 &> /dev/null; then
        apache2 -v 2>&1
        echo "  配置文件: /etc/apache2/apache2.conf"
        echo "  状态: $(systemctl is-active apache2 2>/dev/null || echo '未知')"
    else
        httpd -v 2>&1
        echo "  配置文件: /etc/httpd/conf/httpd.conf"
        echo "  状态: $(systemctl is-active httpd 2>/dev/null || echo '未知')"
    fi
    APACHE_INSTALLED=true
else
    echo "✗ Apache 未安装"
    APACHE_INSTALLED=false
fi

echo ""

# 检测Lighttpd
if command -v lighttpd &> /dev/null; then
    echo "✓ Lighttpd 已安装"
    lighttpd -v 2>&1
    echo "  配置文件: /etc/lighttpd/lighttpd.conf"
    echo "  状态: $(systemctl is-active lighttpd 2>/dev/null || echo '未知')"
    LIGHTTPD_INSTALLED=true
else
    echo "✗ Lighttpd 未安装"
    LIGHTTPD_INSTALLED=false
fi

echo ""

# 检测OpenResty
if command -v openresty &> /dev/null; then
    echo "✓ OpenResty 已安装"
    openresty -v 2>&1
    echo "  配置文件: /usr/local/openresty/nginx/conf/nginx.conf"
    echo "  状态: $(systemctl is-active openresty 2>/dev/null || echo '未知')"
    OPENRESTY_INSTALLED=true
else
    echo "✗ OpenResty 未安装"
    OPENRESTY_INSTALLED=false
fi

echo ""
echo "检测完成!"
