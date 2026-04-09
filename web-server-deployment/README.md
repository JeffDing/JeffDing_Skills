# WEB服务器安装部署 Skill

## 简介

这个skill帮助用户快速、交互式地搭建和部署WEB服务器,提供从服务器选择到测试验证的完整流程。

## 功能特性

- ✅ 支持多种WEB服务器(Apache、Nginx、Tomcat等)
- ✅ 支持多种开发语言(PHP、Java、Python、Node.js、Go等)
- ✅ 智能检测已安装服务
- ✅ 数据库服务器集成(MySQL、MariaDB、PostgreSQL、Oracle、OpenGauss等)
- ✅ 自动/手动配置文件管理
- ✅ 测试代码生成和验证
- ✅ 全程中文交互

## 目录结构

```
web-server-deployment/
├── SKILL.md                          # Skill主文件
├── scripts/                          # 辅助脚本
│   ├── detect_server.sh             # 服务器检测脚本
│   └── generate_test_files.sh       # 测试文件生成脚本
├── references/                       # 参考文档
│   ├── server_configs.md            # 服务器配置参考
│   └── installation_guides.md       # 安装指南
├── assets/                          # 资源文件
└── evals/                           # 测试用例
    └── evals.json                   # 测试定义
```

## 使用方法

### 1. 安装Skill

将此skill目录复制到你的skills目录:

```bash
cp -r /root/web-server-deployment ~/.codeartsdoer/skills/
```

### 2. 使用示例

**部署PHP网站:**
```
用户: 我想部署一个PHP网站
助手会引导你完成:
1. 选择WEB服务器(Apache/Nginx)
2. 设置网页目录
3. 配置数据库(可选)
4. 安装和配置服务器
5. 生成测试文件验证
```

**部署Java应用:**
```
用户: 帮我部署一个Java Web应用
助手会引导你完成:
1. 选择Tomcat服务器
2. 设置应用目录
3. 配置数据库(可选)
4. 安装Java和Tomcat
5. 部署应用并测试
```

**检测已安装服务:**
```
用户: 检测系统中已安装的WEB服务器
助手会运行检测脚本并显示结果
```

## 核心工作流程

```
开始
  ↓
收集需求(语言、服务器、目录)
  ↓
检测已安装服务 → 已安装 → 询问卸载/保留
  ↓
安装服务器软件
  ↓
配置服务器(自动/手动)
  ↓
数据库集成(可选)
  ↓
启动服务
  ↓
生成测试代码
  ↓
验证部署
  ↓
清理测试文件(可选)
  ↓
完成
```

## 支持的服务器

### WEB服务器
- Apache HTTP Server
- Nginx
- Apache Tomcat
- Jetty
- JBoss

### 数据库服务器
- MySQL (Oracle官方维护的关系型数据库)
- MariaDB (MySQL的开源分支,完全兼容MySQL)
- PostgreSQL
- Oracle
- OpenGauss
- MongoDB

**注意:** MySQL和MariaDB是两个不同的数据库系统,用户需要明确选择安装其中一个:
- **MySQL**: Oracle官方维护,适合需要商业支持的场景
- **MariaDB**: 开源免费,性能优化,完全兼容MySQL,社区活跃

## 配置文件位置

| 服务器 | 主配置文件 |
|--------|-----------|
| Apache (Debian/Ubuntu) | /etc/apache2/apache2.conf |
| Apache (RHEL/CentOS) | /etc/httpd/conf/httpd.conf |
| Nginx | /etc/nginx/nginx.conf |
| Tomcat | /opt/tomcat/conf/server.xml |

## 测试

运行测试用例:

```bash
# 检测服务器
bash scripts/detect_server.sh

# 生成测试文件
bash scripts/generate_test_files.sh /var/www/html none
```

## 注意事项

1. 需要root或sudo权限
2. 支持主流Linux发行版(Ubuntu、Debian、CentOS、RHEL、Fedora)
3. 所有交互均使用中文
4. 建议在生产环境使用前先在测试环境验证

## 许可证

MIT License

## 作者

Created by skill-creator
