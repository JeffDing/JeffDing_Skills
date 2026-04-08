#!/bin/bash
# 清理测试文件

WEB_ROOT=$1

if [ -z "$WEB_ROOT" ]; then
    echo "错误: 请提供网站根目录"
    echo "用法: $0 <web_root>"
    exit 1
fi

echo "正在清理测试文件..."

# 删除测试文件
rm -f "$WEB_ROOT/test.html"
rm -f "$WEB_ROOT/info.php"
rm -f "$WEB_ROOT/db_test.php"

echo "✓ 测试文件已清理完成"
