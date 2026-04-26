# TeleGreat 防骗举报机器人 - 服务器部署指南

## 📋 目录
1. [服务器配置推荐](#1-服务器配置推荐)
2. [系统环境要求](#2-系统环境要求)
3. [项目部署步骤](#3-项目部署步骤)
4. [服务配置](#4-服务配置)
5. [安全加固](#5-安全加固)
6. [监控与日志](#6-监控与日志)
7. [常见问题](#7-常见问题)

---

## 1. 服务器配置推荐

### 推荐配置（根据用户量）

| 规模 | CPU | 内存 | 磁盘 | 月费用(参考) |
|------|-----|------|------|-------------|
| 小型（<1000用户） | 1核 | 1GB | 20GB SSD | ¥30-50 |
| 中型（1000-10000） | 2核 | 2GB | 40GB SSD | ¥60-100 |
| 大型（>10000） | 4核 | 4GB | 80GB SSD | ¥150-300 |

### 推荐服务商
- **国内**: 阿里云、腾讯云、华为云（延迟低，备案需谨慎）
- **海外**: Vultr、DigitalOcean、Linode（无需备案，推荐新加坡节点）

### 推荐操作系统
```bash
Ubuntu 22.04 LTS  # 首选
CentOS 9 Stream   # 备选
Debian 12         # 备选
```

---

## 2. 系统环境要求

### 基础依赖
```bash
# Ubuntu 22.04 安装基础依赖
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.10+ 和相关工具
sudo apt install -y python3.10 python3.10-venv python3-pip
sudo apt install -y git curl wget htop atop nginx

# 如果使用 PostgreSQL（生产环境推荐）
sudo apt install -y postgresql postgresql-contrib
```

### Python 版本检查
```bash
python3 --version
# 输出应为: Python 3.10.x 或更高
```

---

## 3. 项目部署步骤

### 3.1 创建项目目录

```bash
# 创建项目目录
sudo mkdir -p /opt/telegreat
sudo chown -R $USER:$USER /opt/telegreat

# 进入目录
cd /opt/telegreat
```

### 3.2 上传项目

**方式一：Git 克隆（推荐）**
```bash
git clone https://your-repo-url/telegreat.git .
```

**方式二：SCP 上传**
```bash
# 本地执行
scp -r ./telegreat user@your-server:/opt/
```

### 3.3 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖（国内服务器建议使用清华源）
pip install -r requirements.txt

# 或使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3.4 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
nano .env
```

**配置示例 `.env` 文件**:
```env
# Telegram Bot Token（必填）
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ

# 管理员 ID（多个用逗号分隔）
ADMIN_USER_IDS=123456789
SUPER_ADMIN_USER_IDS=123456789

# 服务器配置
BOT_HOST=0.0.0.0
BOT_PORT=801

# 数据库（SQLite 轻量，生产可用 PostgreSQL）
DATABASE_URL=sqlite:///opt/telegreat/telegreat.db

# API Key 密钥（随机生成）
API_KEY_SECRET=a3f8b2c1d4e5f6g7h8i9j0k1l2m3n4o5p6

# Web 管理后台配置
ADMIN_SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key-change-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YourSecurePassword123!
ADMIN_HOST=0.0.0.0
ADMIN_PORT=811
```

### 3.5 初始化数据库

```bash
# 激活虚拟环境
source venv/bin/activate

# 初始化数据库
cd bot
python -c "from database.migrations import init_database; init_database()"

# 创建超级管理员用户（交互式）
python -c "from database.migrations import create_admin_user; create_admin_user()"
```

---

## 4. 服务配置

### 4.1 Systemd 服务文件

**Telegram 机器人服务**:
```bash
sudo nano /etc/systemd/system/telegreat-bot.service
```

```ini
[Unit]
Description=TeleGreat Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/telegreat
Environment=PATH=/opt/telegreat/venv/bin
ExecStart=/opt/telegreat/venv/bin/python -m bot.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Web 管理后台服务**:
```bash
sudo nano /etc/systemd/system/telegreat-admin.service
```

```ini
[Unit]
Description=TeleGreat Admin Panel
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/telegreat
Environment=PATH=/opt/telegreat/venv/bin
ExecStart=/opt/telegreat/venv/bin/python -m admin.app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 4.2 启动服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable telegreat-bot telegreat-admin

# 启动服务
sudo systemctl start telegreat-bot telegreat-admin

# 查看状态
sudo systemctl status telegreat-bot
sudo systemctl status telegreat-admin
```

### 4.3 Nginx 反向代理（可选，推荐）

```bash
# 安装 Nginx
sudo apt install -y nginx

# 创建 Nginx 配置
sudo nano /etc/nginx/sites-available/telegreat-admin
```

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    location / {
        proxy_pass http://127.0.0.1:811;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/telegreat-admin /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 4.4 SSL 证书（推荐）

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

---

## 5. 安全加固

### 5.1 防火墙配置

```bash
# 安装 UFW
sudo apt install -y ufw

# 配置规则
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 801/tcp  # Telegram Bot 端口
sudo ufw allow 811/tcp  # 管理后台端口（建议限制来源IP）

# 启用防火墙
sudo ufw enable
```

### 5.2 IP 白名单（管理后台）

编辑 `admin/config.py`:
```python
class AdminConfig:
    # 允许访问的 IP 白名单（留空则不限制）
    ALLOWED_IPS = ['123.45.67.89', '98.76.54.32']
    
    # 启用 IP 白名单检查
    ENABLE_IP_WHITELIST = False  # 正式部署建议开启
```

### 5.3 Fail2ban 防暴力破解

```bash
# 安装 fail2ban
sudo apt install -y fail2ban

# 配置
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
```

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 6. 监控与日志

### 6.1 查看日志

```bash
# Systemd 日志
sudo journalctl -u telegreat-bot -f
sudo journalctl -u telegreat-admin -f

# 应用日志
tail -f /opt/telegreat/telegreat.log
```

### 6.2 资源监控

```bash
# 实时监控脚本
watch -n 5 'echo "=== CPU & Memory ===" && top -bn1 | head -5 && echo "=== Disk ===" && df -h && echo "=== Network ===" && ss -tuln | grep LISTEN'
```

### 6.3 自动备份

```bash
# 创建备份脚本
sudo nano /opt/telegreat/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR=/opt/telegreat/backups
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据库
cp /opt/telegreat/telegreat.db $BACKUP_DIR/db_$DATE.bak

# 备份配置
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /opt/telegreat/.env

# 保留最近 30 天备份
find $BACKUP_DIR -mtime +30 -delete
```

```bash
# 添加定时任务
sudo chmod +x /opt/telegreat/backup.sh
sudo crontab -e
```

```
# 每天凌晨 3 点自动备份
0 3 * * * /opt/telegreat/backup.sh >> /var/log/backup.log 2>&1
```

---

## 7. 常见问题

### Q1: 机器人无法启动
```bash
# 检查日志
sudo journalctl -u telegreat-bot -n 50

# 常见原因
# - Bot Token 错误
# - 端口被占用
# - 数据库权限问题
```

### Q2: 管理后台无法访问
```bash
# 检查服务状态
sudo systemctl status telegreat-admin

# 检查端口
curl http://localhost:811/api/health

# 检查防火墙
sudo ufw status
```

### Q3: 数据库迁移失败
```bash
# 检查数据库文件权限
ls -la /opt/telegreat/telegreat.db

# 手动初始化
cd /opt/telegreat
source venv/bin/activate
cd bot
python -m bot.database.migrations
```

### Q4: 更新代码后重启
```bash
# 拉取最新代码
cd /opt/telegreat
git pull

# 重启服务
sudo systemctl restart telegreat-bot telegreat-admin

# 检查状态
sudo systemctl status telegreat-bot
```

---

## 快速启动命令汇总

```bash
# === 一键部署脚本 === #
# 在服务器上执行以下命令

# 1. 安装基础环境
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.10 python3-pip git curl nginx

# 2. 创建项目目录
sudo mkdir -p /opt/telegreat && cd /opt/telegreat

# 3. 上传项目（替换为你的方式）
# git clone 或 scp 上传

# 4. 配置环境
cp .env.example .env
nano .env  # 编辑配置

# 5. 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. 初始化
cd bot
python -c "from database.migrations import init_database; init_database()"

# 7. 配置服务
sudo cp /opt/telegreat/deploy/telegreat-bot.service /etc/systemd/system/
sudo cp /opt/telegreat/deploy/telegreat-admin.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegreat-bot telegreat-admin
sudo systemctl start telegreat-bot telegreat-admin

# 8. 检查状态
sudo systemctl status telegreat-bot
```

---

## 联系支持

如有问题，请检查：
1. 日志输出：`sudo journalctl -u telegreat-bot -f`
2. 服务状态：`sudo systemctl status telegreat-bot`
3. 端口监听：`ss -tuln | grep LISTEN`
