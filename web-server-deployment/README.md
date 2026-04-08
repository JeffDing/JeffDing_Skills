# WEB服务器安装部署技能

## 简介

本技能帮助用户快速搭建和部署WEB服务器环境,提供完整的交互式安装流程。

## 功能特性

- ✅ 支持多种WEB服务器软件(Nginx、Apache、Lighttpd、OpenResty)
- ✅ 自动检测已安装的服务器和数据库
- ✅ 支持多种编程语言(PHP、Python、Node.js、Java等)
- ✅ 支持多种数据库(MySQL、PostgreSQL、MongoDB、Redis等)
- ✅ 自动创建测试页面验证部署
- ✅ 提供配置文件修改指导
- ✅ 完整的中文提示界面

## 目录结构

```
web-server-deployment/
├── SKILL.md                          # 技能主文件
├── scripts/                          # 辅助脚本
│   ├── detect_server.sh             # 检测WEB服务器
│   ├── detect_database.sh           # 检测数据库
│   ├── create_test_files.sh         # 创建测试文件
│   └── cleanup_test_files.sh        # 清理测试文件
├── references/                       # 参考文档
│   ├── server_configs.md            # 服务器配置参考
│   └── installation_guides.md       # 安装指南
├── assets/                           # 资源文件
└── evals/                            # 测试用例
    └── evals.json
```

## 使用方法

### 触发方式

当用户提到以下关键词时,技能会自动触发:
- "安装WEB服务器"
- "部署WEB服务器"
- "搭建网站服务器"
- "配置Apache"
- "配置Nginx"
- "安装Nginx"
- "安装Apache"

### 工作流程

1. **检测现有环境** - 检查系统中已安装的服务器和数据库
2. **服务器选择** - 让用户选择要安装的WEB服务器软件
3. **语言配置** - 询问网站使用的编程语言
4. **数据库配置** - 询问是否需要数据库支持
5. **目录配置** - 设置网站文件存放目录
6. **配置修改** - 协助修改配置文件
7. **安装部署** - 执行安装和配置
8. **测试验证** - 创建测试页面验证部署
9. **清理文件** - 清理测试生成的文件

## 脚本使用

### 检测WEB服务器
```bash
bash scripts/detect_server.sh
```

### 检测数据库
```bash
bash scripts/detect_database.sh
```

### 创建测试文件
```bash
bash scripts/create_test_files.sh <web_root> [db_type] [db_host] [db_name] [db_user] [db_pass]
```

### 清理测试文件
```bash
bash scripts/cleanup_test_files.sh <web_root>
```

## 示例场景

### 场景1: 安装Nginx + PHP + MySQL
```
用户: 帮我安装一个Nginx WEB服务器,用于托管PHP网站,需要连接MySQL数据库
技能: 
  1. 检测现有环境
  2. 引导选择Nginx
  3. 配置PHP支持
  4. 安装和配置MySQL
  5. 创建测试页面
  6. 验证部署成功
```

### 场景2: 搭建Apache + Python环境
```
用户: 我想搭建一个Apache服务器来运行我的Python Flask应用
技能:
  1. 检测现有环境
  2. 引导选择Apache
  3. 配置Python/WSGI支持
  4. 设置虚拟主机
  5. 创建测试应用
```

## 配置参考

详细的配置参考请查看:
- `references/server_configs.md` - 服务器配置示例
- `references/installation_guides.md` - 安装指南

## 注意事项

1. 所有提示信息均使用中文
2. 重要操作前会确认用户意图
3. 提供配置文件路径供用户参考
4. 测试完成后可选择清理测试文件
5. 支持自动和手动两种配置修改方式

## 许可证

本技能遵循MIT许可证。
