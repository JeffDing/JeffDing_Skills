#!/bin/bash
# 测试文件生成脚本

WEB_ROOT="$1"
DB_TYPE="$2"
TEST_DIR="$WEB_ROOT/test_deployment"

# 创建测试目录
mkdir -p "$TEST_DIR"

# 生成HTML测试文件
generate_html_test() {
    cat > "$TEST_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>WEB服务器测试页面</title>
</head>
<body>
    <h1>WEB服务器部署成功!</h1>
    <p>如果您能看到此页面,说明WEB服务器已正常运行。</p>
    <p>测试时间: <span id="time"></span></p>
    <script>
        document.getElementById('time').innerHTML = new Date().toLocaleString('zh-CN');
    </script>
</body>
</html>
EOF
    echo "已生成: $TEST_DIR/index.html"
}

# 生成PHP测试文件(无数据库)
generate_php_test_no_db() {
    cat > "$TEST_DIR/test_php.php" << 'EOF'
<?php
header('Content-Type: text/html; charset=utf-8');
echo "<h1>PHP测试页面</h1>";
echo "<p>PHP版本: " . phpversion() . "</p>";
echo "<p>服务器软件: " . $_SERVER['SERVER_SOFTWARE'] . "</p>";
echo "<p>测试时间: " . date('Y-m-d H:i:s') . "</p>";
echo "<h2>PHP信息</h2>";
phpinfo();
?>
EOF
    echo "已生成: $TEST_DIR/test_php.php"
}

# 生成PHP测试文件(有数据库)
generate_php_test_with_db() {
    cat > "$TEST_DIR/test_db.php" << 'EOF'
<?php
header('Content-Type: text/html; charset=utf-8');
$host = 'localhost';
$user = 'test_user';
$pass = 'test_pass';
$dbname = 'test_db';

echo "<h1>数据库连接测试</h1>";

try {
    $conn = new mysqli($host, $user, $pass, $dbname);
    
    if ($conn->connect_error) {
        throw new Exception("连接失败: " . $conn->connect_error);
    }
    
    echo "<p style='color:green'>数据库连接成功!</p>";
    echo "<p>数据库: $dbname</p>";
    echo "<p>服务器版本: " . $conn->server_info . "</p>";
    
    // 测试创建表
    $sql = "CREATE TABLE IF NOT EXISTS test_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )";
    
    if ($conn->query($sql) === TRUE) {
        echo "<p>测试表创建成功</p>";
    }
    
    // 测试插入数据
    $sql = "INSERT INTO test_table (name) VALUES ('测试数据')";
    if ($conn->query($sql) === TRUE) {
        echo "<p>数据插入成功, ID: " . $conn->insert_id . "</p>";
    }
    
    // 测试查询数据
    $sql = "SELECT * FROM test_table";
    $result = $conn->query($sql);
    echo "<p>查询到 " . $result->num_rows . " 条记录</p>";
    
    // 清理测试数据
    $conn->query("DROP TABLE test_table");
    echo "<p>测试表已删除</p>";
    
    $conn->close();
    echo "<p style='color:green'>所有测试通过!</p>";
    
} catch (Exception $e) {
    echo "<p style='color:red'>错误: " . $e->getMessage() . "</p>";
}
?>
EOF
    echo "已生成: $TEST_DIR/test_db.php"
}

# 生成Python测试文件
generate_python_test() {
    cat > "$TEST_DIR/test_python.py" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import datetime

print("Content-Type: text/html; charset=utf-8\n")
print("<h1>Python测试页面</h1>")
print(f"<p>Python版本: {sys.version}</p>")
print(f"<p>测试时间: {datetime.datetime.now()}</p>")
print("<p>Python环境正常!</p>")
EOF
    echo "已生成: $TEST_DIR/test_python.py"
}

# 生成Node.js测试文件
generate_nodejs_test() {
    cat > "$TEST_DIR/test_nodejs.js" << 'EOF'
const http = require('http');
const server = http.createServer((req, res) => {
    res.writeHead(200, {'Content-Type': 'text/html; charset=utf-8'});
    res.end('<h1>Node.js测试页面</h1>' +
            '<p>Node.js版本: ' + process.version + '</p>' +
            '<p>测试时间: ' + new Date().toLocaleString('zh-CN') + '</p>');
});
server.listen(3000, () => {
    console.log('测试服务器运行在 http://localhost:3000');
});
EOF
    echo "已生成: $TEST_DIR/test_nodejs.js"
}

# 清理测试文件
cleanup_test_files() {
    if [ -d "$TEST_DIR" ]; then
        rm -rf "$TEST_DIR"
        echo "测试文件已清理: $TEST_DIR"
    else
        echo "测试目录不存在"
    fi
}

# 主逻辑
echo "=== 生成测试文件 ==="
echo "WEB根目录: $WEB_ROOT"
echo "测试目录: $TEST_DIR"
echo ""

generate_html_test

if [ "$DB_TYPE" = "none" ] || [ -z "$DB_TYPE" ]; then
    echo "生成无数据库测试文件..."
    generate_php_test_no_db
    generate_python_test
    generate_nodejs_test
else
    echo "生成包含数据库测试文件..."
    generate_php_test_with_db
    generate_python_test
    generate_nodejs_test
fi

echo ""
echo "测试文件生成完成!"
echo "访问测试页面: http://localhost/$TEST_DIR/index.html"
