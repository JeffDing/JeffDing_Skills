#!/bin/bash
# 创建测试文件

WEB_ROOT=$1
DB_TYPE=$2
DB_HOST=${3:-localhost}
DB_NAME=${4:-test_db}
DB_USER=${5:-test_user}
DB_PASS=${6:-test_password}

if [ -z "$WEB_ROOT" ]; then
    echo "错误: 请提供网站根目录"
    echo "用法: $0 <web_root> [db_type] [db_host] [db_name] [db_user] [db_pass]"
    exit 1
fi

echo "正在创建测试文件到 $WEB_ROOT ..."

# 创建基础HTML测试文件
cat > "$WEB_ROOT/test.html" << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WEB服务器测试页面</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        h1 {
            color: #28a745;
        }
    </style>
</head>
<body>
    <div class="success">
        <h1>✓ WEB服务器部署成功!</h1>
        <p>您的WEB服务器已正确安装并运行。</p>
        <p>服务器时间: <span id="time"></span></p>
    </div>

    <script>
        document.getElementById('time').textContent = new Date().toLocaleString('zh-CN');
    </script>
</body>
</html>
EOF

echo "✓ 创建 test.html"

# 创建PHP测试文件
cat > "$WEB_ROOT/info.php" << 'EOF'
<?php
header('Content-Type: text/html; charset=utf-8');
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>PHP信息页面</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        h1 {
            color: #17a2b8;
        }
    </style>
</head>
<body>
    <div class="info">
        <h1>✓ PHP已正确安装</h1>
        <p>PHP版本: <?php echo phpversion(); ?></p>
        <p>服务器时间: <?php echo date('Y-m-d H:i:s'); ?></p>
        <p>服务器软件: <?php echo $_SERVER['SERVER_SOFTWARE']; ?></p>
    </div>

    <h2>PHP配置信息</h2>
    <p><a href="?phpinfo=1">点击查看完整PHP信息</a></p>

    <?php
    if (isset($_GET['phpinfo'])) {
        phpinfo();
    }
    ?>
</body>
</html>
EOF

echo "✓ 创建 info.php"

# 如果有数据库,创建数据库测试文件
if [ -n "$DB_TYPE" ] && [ "$DB_TYPE" != "none" ]; then
    if [ "$DB_TYPE" = "mysql" ] || [ "$DB_TYPE" = "mariadb" ]; then
        cat > "$WEB_ROOT/db_test.php" << EOF
<?php
header('Content-Type: text/html; charset=utf-8');

\$host = '$DB_HOST';
\$dbname = '$DB_NAME';
\$user = '$DB_USER';
\$pass = '$DB_PASS';
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>数据库连接测试</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        h1 { margin-top: 0; }
    </style>
</head>
<body>
    <?php
    try {
        \$pdo = new PDO("mysql:host=\$host;dbname=\$dbname", \$user, \$pass);
        \$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    ?>
        <div class="success">
            <h1>✓ 数据库连接成功!</h1>
            <p>数据库类型: MySQL/MariaDB</p>
            <p>主机: <?php echo \$host; ?></p>
            <p>数据库: <?php echo \$dbname; ?></p>
            <p>用户: <?php echo \$user; ?></p>
        </div>
    <?php
    } catch(PDOException \$e) {
    ?>
        <div class="error">
            <h1>✗ 数据库连接失败</h1>
            <p>错误信息: <?php echo \$e->getMessage(); ?></p>
            <p>请检查数据库配置是否正确。</p>
        </div>
    <?php
    }
    ?>
</body>
</html>
EOF
        echo "✓ 创建 db_test.php (MySQL/MariaDB)"
    fi
fi

echo ""
echo "测试文件创建完成!"
echo "请访问以下URL测试:"
echo "  - http://localhost/test.html"
echo "  - http://localhost/info.php"
if [ -n "$DB_TYPE" ] && [ "$DB_TYPE" != "none" ]; then
    echo "  - http://localhost/db_test.php"
fi
