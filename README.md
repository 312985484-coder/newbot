# TeleGreat - Telegram 防骗举报机器人

一个专为 Telegram 用户打造的防骗举报与查询平台，通过社区力量共同抵制诈骗行为，保护用户财产安全。

## 功能特性

- 🔍 **信息查询**：查询用户是否有诈骗历史
- 🚨 **不良举报**：提交骗子信息，建立骗子数据库（需API Key验证）
- 🛡️ **用户申诉**：申诉被恶意举报的账号
- 👥 **群管理**：自动检测新入群用户、自动禁言风险用户、自动欢迎
- 📢 **广告系统**：置顶广告 + 随机广告，多元化收入
- 🔑 **批量 API Key**：后台批量生成和管理 API Keys

## 组件架构

本项目包含两个主要组件：

| 组件 | 端口 | 说明 |
|------|------|------|
| Telegram Bot | - | 机器人主程序，处理用户交互 |
| Web Admin | 5000 | 管理后台，独立部署 |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# Telegram Bot Token (必需)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# 管理员 Telegram ID
ADMIN_USER_IDS=123456789

# Web 管理后台 (重要! 请修改默认密码!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me-in-production
```

### 3. 运行

**运行 Telegram 机器人：**
```bash
python -m bot.main
```

**运行管理后台（另一个终端）：**
```bash
python -m admin.app
```

### 4. Docker 部署

```bash
docker-compose up -d
```

## 项目结构

```
telegreat/
├── bot/                        # Telegram 机器人
│   ├── main.py                 # 入口
│   ├── config.py               # 配置
│   ├── database/               # 数据库
│   ├── handlers/               # 命令处理器
│   ├── keyboards/             # 按钮
│   ├── services/               # 业务逻辑
│   │   ├── batch_key_service.py  # 批量 API Key
│   │   └── ...
│   └── locales/                # 多语言
├── admin/                      # Web 管理后台
│   ├── app.py                  # Flask 入口
│   ├── auth.py                 # JWT 认证
│   ├── routes/                 # API 路由
│   ├── static/                 # CSS/JS
│   └── templates/              # HTML
├── docker/
├── config/
└── tests/
```

## 管理后台

访问地址：`http://your-domain.com:5000`

**功能模块：**
- 📊 仪表盘 - 数据统计概览
- 👥 用户管理 - 查看/编辑用户
- 🚨 举报管理 - 审核举报
- 🛡️ 申诉管理 - 处理申诉
- 🔑 API Keys - **批量生成 Keys**
- 📢 广告管理 - 添加/管理广告
- 📨 广播 - 群发通知

**安全特性：**
- JWT Token 认证
- Token 吊销机制
- 独立部署，不暴露在公网
- 登录失败锁定（可选）

## 命令列表

### 用户命令
| 命令 | 功能 |
|------|------|
| /start | 启动机器人 |
| /help | 帮助信息 |
| /search @用户 | 查询用户 |
| /report | 举报骗子（需Key） |
| /appeal | 申诉通道 |

### 管理员命令
| 命令 | 功能 |
|------|------|
| /admin | 机器人内管理面板 |
| /group | 群组设置 |

## 数据库

使用 SQLite（可升级至 PostgreSQL）

**主要表：**
- `users` - 用户表
- `reports` - 举报表
- `reported_users` - 被举报用户汇总
- `appeals` - 申诉表
- `advertisements` - 广告表
- `api_keys` - API Keys 表
- `group_settings` - 群组设置

## 许可证

MIT License