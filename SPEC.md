# TeleGreat - Telegram 防骗举报机器人

## 1. 项目概述

### 项目名称
TeleGreat（电报守护者）

### 项目定位
一个专为 Telegram 用户打造的防骗举报与查询平台，通过社区力量共同抵制诈骗行为，保护用户财产安全。

### 核心价值
- 帮助用户在上当受骗前进行风险预警
- 建立公开透明的骗子账号数据库
- 为受害用户提供便捷的举报通道
- 支持多渠道变现（广告收入）

---

## 2. 功能模块详细设计

### 2.1 功能一：不良举报（Report）

**目的**：让被骗用户快速提交骗子信息，建立骗子数据库。

**用户操作流程**：
1. 用户发送 `/report` 或点击「举报骗子」按钮
2. 系统检测是否有有效的密钥（API Key）绑定
3. 无密钥者需先购买/申请密钥，有密钥者继续下一步
4. 引导用户填写举报信息表单：
   - 被骗时间（日期选择器）
   - 骗子账号（用户名或用户ID）
   - 被骗金额（USDT/其他加密货币）
   - 被骗经过（文本描述，最少20字）
   - 上传证据（图片/视频，最多5张）
5. 提交后进入审核队列
6. 审核通过后数据入库，举报者获得积分奖励

**数据库字段**：
```
reports:
  - id: UUID
  - reporter_id: 用户TelegramID
  - target_username: 目标用户名
  - target_user_id: 目标用户ID
  - scam_time: 被骗时间
  - amount: 被骗金额
  - currency: 货币类型 (USDT/ETH/BTC等)
  - description: 被骗经过
  - evidence_urls: [证据文件URL列表]
  - status: pending/approved/rejected
  - created_at: 提交时间
  - approved_at: 审核时间
  - approved_by: 审核管理员ID
```

**密钥系统**：
- 每位用户有唯一的 API Key
- 密钥用于验证举报者身份
- 可通过邀请好友、付费购买等方式获取
- 密钥状态：active/inactive/expired

---

### 2.2 功能二：信息查询（Search）

**目的**：让用户在交易/联系前查询对方是否有诈骗历史。

**查询方式**：
1. 用户发送 `/search [用户名/用户ID]`
2. 或点击「查询用户」按钮，手动输入要查询的账号

**查询结果展示**：
```
🔍 查询结果：@target_user

⚠️ 该账号已被举报 X 次

💰 累积被骗金额：XXXX USDT

📊 风险等级：[高/中/低]

━━━━━━━━━━━━━━━━━━━━
📋 历史举报记录
━━━━━━━━━━━━━━━━━━━━
1️⃣ 2026-04-01 - XXX USDT
   举报人：@xxx
   简要：XXXXX
   
[查看详情 ▼]

2️⃣ 2026-03-15 - XXX USDT
   ...

━━━━━━━━━━━━━━━━━━━━
⚠️ 警告：交易需谨慎！
🆘 如被骗请联系管理员申诉
```

**详细信息展示（点击「查看详情」后）**：
```
📌 举报详情 #1

⏰ 时间：2026年4月1日 15:30
💰 金额：500 USDT
📝 经过：
   用户通过XXX渠道联系我，
   声称XXX，以XXX为由骗取
   我500 USDT后失联。
   
📎 证据：
   [图片1] [图片2]

━━━━━━━━━━━━━━━━━━━━
```

**风险等级计算规则**：
- 高风险：举报次数 ≥ 5 或 累积金额 ≥ 5000 USDT
- 中风险：举报次数 ≥ 3 或 累积金额 ≥ 1000 USDT
- 低风险：举报次数 1-2 次
- 安全：未被举报

---

### 2.3 功能三：用户申诉（Appeal）

**目的**：让被恶意举报或错误举报的用户有机会洗清冤屈。

**申诉流程**：
1. 用户发送 `/appeal` 或点击「申诉通道」
2. 系统显示申诉说明和风险等级
3. 用户提交申诉表单：
   - 被举报账号
   - 申诉理由（文本，最少50字）
   - 证据材料（证明自己是清白的）
4. 提交后通知所有管理员
5. 管理员审核后可：
   - 同意申诉：删除该账号的所有举报记录
   - 部分接受：删除部分举报记录
   - 拒绝申诉：维持原记录，告知申诉者原因

**前端显示**：
```
🛡️ 申诉通道

📌 当前状态：
   您的账号 @your_username
   被举报 X 次，累积风险
   如认为举报有误，可申诉

━━━━━━━━━━━━━━━━━━━━

📨 联系管理员：

👤 @admin1 (主管理员)
👤 @admin2 
👤 @admin3

💬 请简要说明情况，管理员
   会尽快处理您的申诉

━━━━━━━━━━━━━━━━━━━━

📝 也可提交正式申诉表单
   [提交申诉表单]
```

**申诉记录表**：
```
appeals:
  - id: UUID
  - user_id: 申诉用户ID
  - target_user_id: 被申诉的账号
  - reason: 申诉理由
  - evidence_urls: 证据URL
  - status: pending/approved/rejected
  - admin_response: 管理员回复
  - processed_by: 处理管理员ID
  - created_at: 申诉时间
  - processed_at: 处理时间
```

---

### 2.4 功能四：群管理（Group Management）

**目的**：将机器人接入群组后，提供自动化群管理功能。

**核心功能**：

#### 4.1 新成员入群检测
- 机器人自动检测新加入成员
- 调用数据库查询该用户是否有不良记录
- 有记录 → 自动禁言（不踢出）
- 无记录 → 发送欢迎消息

**欢迎消息模板**：
```
👋 欢迎 {username} 加入本群！

📌 群规：
   • 禁止发布诈骗信息
   • 禁止广告（除非管理员许可）
   • 文明交流，友善相处

⚠️ 安全提示：
   如有人向您索要金钱或
   要求转账，请提高警惕！
   可使用 /search 查询对方
   是否被举报过。

祝您在本群愉快！🎉
```

#### 4.2 关键词自动处理
- 检测违规关键词（如：菠菜、杀猪盘等）
- 自动删除违规消息
- 警告或禁言发送者

#### 4.3 举报快捷入口
- 群内用户可快速举报群内骗子
- 命令：`/report @username`

#### 4.4 管理命令（仅管理员可用）
- `/ban @username` - 禁言用户
- `/unban @username` - 解除禁言
- `/kick @username` - 踢出用户
- `/mute @username duration` - 限时禁言
- `/delete` - 删除回复的消息
- `/pin` - 置顶消息
- `/warn @username reason` - 警告用户

**群设置命令**：
```
/group setwelcome [消息] - 设置欢迎消息
/group welcomestatus [on/off] - 开关欢迎消息
/group antispam [on/off] - 开关反垃圾
/group securitylevel [low/medium/high] - 安全等级
```

---

### 2.5 功能五：广告系统（Advertisement）

**目的**：在机器人的回复中嵌入广告，实现多元化收入。

**广告位设计**：

#### 置顶广告位（2条）
- 位置：所有回复的最底部固定显示
- 内容：长期合作的高价广告
- 更替：由管理员手动更新
- 格式：
```
━━━━━━━━━━━━━━━━━━━━
📢 广告

[广告1内容+图片]
推广链接：t.me/xxx

[广告2内容+图片]
推广链接：t.me/xxx

💰 广告投放联系：@admin_contact
```

#### 随机广告位（3条）
- 位置：置顶广告下方
- 内容：从广告库随机抽取3条
- 每次查询/举报后随机更新
- 保证广告展示的多样性

**广告数据库**：
```
advertisements:
  - id: UUID
  - title: 广告标题
  - content: 广告内容/描述
  - image_url: 广告图片URL
  - link_url: 推广链接
  - link_text: 按钮文字
  - type: pinned/random
  - priority: 优先级（1-10）
  - status: active/paused/expired
  - views: 展示次数
  - clicks: 点击次数
  - created_at: 创建时间
  - expires_at: 过期时间
  - created_by: 创建管理员ID
```

**广告展示逻辑**：
```python
def get_ad_display():
    pinned_ads = get_pinned_ads()  # 获取2条置顶广告
    random_ads = get_random_ads(3)  # 随机获取3条广告
    return pinned_ads + random_ads
```

---

## 3. 机器人命令总览

### 用户命令
| 命令 | 功能 | 权限 |
|------|------|------|
| /start | 启动机器人，显示主菜单 | 所有人 |
| /help | 显示帮助信息 | 所有人 |
| /report | 举报骗子账号 | 需密钥 |
| /search | 查询用户是否有不良记录 | 所有人 |
| /appeal | 申诉通道 | 所有人 |
| /stats | 查看自己的使用统计 | 所有人 |
| /profile | 查看个人资料和密钥 | 所有人 |
| /feedback | 提交反馈建议 | 所有人 |

### 群组命令
| 命令 | 功能 | 权限 |
|------|------|------|
| /group | 群组设置 | 管理员 |
| /ban | 禁言用户 | 管理员 |
| /unban | 解除禁言 | 管理员 |
| /kick | 踢出用户 | 管理员 |
| /mute | 限时禁言 | 管理员 |
| /warn | 警告用户 | 管理员 |
| /delete | 删除消息 | 管理员 |

### 管理员命令
| 命令 | 功能 | 权限 |
|------|------|------|
| /admin | 管理面板入口 | 超级管理员 |
| /approve | 审核举报 | 审核员 |
| /reject | 拒绝举报 | 审核员 |
| /stats | 查看全局统计 | 管理员 |
| /broadcast | 广播消息 | 超级管理员 |
| /ad | 广告管理 | 超级管理员 |
| /user | 用户管理 | 管理员 |

---

## 4. 数据库设计

### 主要数据表

#### users（用户表）
```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    api_key VARCHAR(64) UNIQUE,
    key_status VARCHAR(20) DEFAULT 'active',
    key_expires_at DATETIME,
    total_reports INT DEFAULT 0,
    successful_reports INT DEFAULT 0,
    reputation_score INT DEFAULT 100,
    is_admin BOOLEAN DEFAULT FALSE,
    is_super_admin BOOLEAN DEFAULT FALSE,
    warning_count INT DEFAULT 0,
    banned_until DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### reports（举报表）
```sql
CREATE TABLE reports (
    id VARCHAR(36) PRIMARY KEY,
    reporter_id BIGINT REFERENCES users(id),
    target_username VARCHAR(255),
    target_user_id BIGINT,
    target_first_name VARCHAR(255),
    target_last_name VARCHAR(255),
    scam_time DATETIME,
    amount DECIMAL(18, 8),
    currency VARCHAR(20) DEFAULT 'USDT',
    description TEXT,
    evidence_urls JSON,
    status VARCHAR(20) DEFAULT 'pending',
    rejection_reason TEXT,
    approved_by BIGINT,
    approved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### reported_users（被举报用户汇总表）
```sql
CREATE TABLE reported_users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    report_count INT DEFAULT 0,
    total_amount DECIMAL(18, 8) DEFAULT 0,
    risk_level VARCHAR(20) DEFAULT 'safe',
    first_reported_at DATETIME,
    last_reported_at DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### appeals（申诉表）
```sql
CREATE TABLE appeals (
    id VARCHAR(36) PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    target_user_id BIGINT,
    reason TEXT,
    evidence_urls JSON,
    status VARCHAR(20) DEFAULT 'pending',
    admin_response TEXT,
    processed_by BIGINT,
    processed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### advertisements（广告表）
```sql
CREATE TABLE advertisements (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    image_url VARCHAR(500),
    link_url VARCHAR(500),
    link_text VARCHAR(100),
    type VARCHAR(20),
    priority INT DEFAULT 5,
    status VARCHAR(20) DEFAULT 'active',
    views INT DEFAULT 0,
    clicks INT DEFAULT 0,
    created_by BIGINT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME
);
```

#### group_settings（群组设置表）
```sql
CREATE TABLE group_settings (
    chat_id BIGINT PRIMARY KEY,
    welcome_message TEXT,
    welcome_enabled BOOLEAN DEFAULT TRUE,
    antispam_enabled BOOLEAN DEFAULT TRUE,
    security_level VARCHAR(20) DEFAULT 'medium',
    auto_mute_reported_users BOOLEAN DEFAULT TRUE,
    muted_keywords JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### api_keys（API密钥表）
```sql
CREATE TABLE api_keys (
    id VARCHAR(36) PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    api_key VARCHAR(64) UNIQUE,
    status VARCHAR(20) DEFAULT 'active',
    request_count INT DEFAULT 0,
    expires_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. 技术架构

### 技术栈
- **语言**：Python 3.10+
- **框架**：python-telegram-bot v20+ (基于 Telegram Bot API)
- **数据库**：SQLite（轻量级，可扩展至 PostgreSQL）
- **ORM**：SQLAlchemy
- **异步**：asyncio + aiosqlite（可选）
- **部署**：Docker 支持

### 项目结构
```
telegreat/
├── bot/                         # Telegram 机器人
│   ├── __init__.py
│   ├── main.py                 # 机器人入口
│   ├── config.py               # 配置文件
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py       # 数据库连接
│   │   ├── models.py           # 数据模型
│   │   └── migrations.py       # 数据库迁移
│   ├── handlers/               # 命令处理器
│   │   ├── __init__.py
│   │   ├── start.py
│   │   ├── report.py
│   │   ├── search.py
│   │   ├── appeal.py
│   │   ├── admin.py
│   │   └── group.py
│   ├── keyboards/
│   │   ├── __init__.py
│   │   └── inline.py           # 内联键盘
│   ├── services/               # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── report_service.py
│   │   ├── search_service.py
│   │   ├── appeal_service.py
│   │   ├── ad_service.py
│   │   ├── batch_key_service.py # 批量 API Key 生成
│   │   └── group_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   └── decorators.py
│   └── locales/                # 多语言
│       ├── __init__.py
│       ├── zh.json
│       └── en.json
├── admin/                      # Web 管理后台
│   ├── __init__.py
│   ├── app.py                  # Flask 应用入口
│   ├── config.py               # 后台配置
│   ├── auth.py                 # JWT 认证
│   ├── routes/                 # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py            # 认证路由
│   │   ├── dashboard.py       # 仪表盘
│   │   ├── users.py           # 用户管理
│   │   ├── reports.py         # 举报管理
│   │   ├── appeals.py         # 申诉管理
│   │   ├── api_keys.py        # API Key 管理
│   │   ├── ads.py             # 广告管理
│   │   ├── broadcast.py       # 广播
│   │   └── stats.py           # 统计
│   ├── static/                # 静态资源
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/              # HTML 模板
│       ├── login.html
│       └── dashboard.html
├── tests/
│   ├── __init__.py
│   ├── test_report.py
│   ├── test_search.py
│   └── test_appeal.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── config/
│   └── settings.yaml         # 配置文件
├── requirements.txt
├── README.md
├── SPEC.md
└── .env.example
```

### 核心模块说明

#### bot/main.py
- 机器人主入口
- 注册所有命令处理器
- 设置错误处理
- 启动机器人

#### bot/handlers/
- 每个功能一个文件
- 负责处理用户交互
- 调用相应的服务层

#### bot/services/
- 业务逻辑层
- 处理数据操作
- 与数据库交互

#### bot/keyboards/
- 定义所有内联键盘按钮
- 统一管理按钮布局

#### bot/locales/
- 多语言支持
- 便于国际化

---

## 6. 安全机制

### 密钥验证
- 举报功能需要有效的 API Key
- API Key 绑定用户 ID
- 支持设置过期时间

### 权限控制
- 普通用户：基本查询
- 密钥用户：举报功能
- 审核员：审核举报/申诉
- 管理员：群管理+用户管理
- 超级管理员：全部权限

### 反滥用机制
- 举报需提供证据
- 恶意举报会被记录
- 申诉误报会追究责任
- 限制单人举报频率

---

## 6.5 管理后台（Admin Panel）

### 概述
管理后台是独立于 Telegram 机器人的 Web 管理界面，提供完整的后台管理功能。

**重要特性**：
- 独立部署，隔离于机器人
- 无需暴露在 Telegram Bot API
- JWT Token 认证，支持令牌吊销
- 防暴力破解（可配合 IP 白名单）

### 访问地址
```
http://your-domain.com:5000/
```

### 功能模块

#### 仪表盘
- 实时数据统计
- 用户总数/活跃数
- 举报总数/待审核
- 申诉总数/待处理
- 涉案金额统计
- 高风险用户数

#### 用户管理
- 查看用户列表
- 搜索用户
- 用户详情（举报次数、信誉分、密钥状态）
- 修改用户权限
- 禁用/启用用户

#### 举报管理
- 待审核举报列表
- 举报详情查看
- 通过/拒绝举报
- 批量操作

#### 申诉管理
- 待处理申诉列表
- 申诉详情查看
- 通过/拒绝申诉
- 申诉原因记录

#### API Key 管理
- **批量生成 API Keys**
- 绑定用户
- 设置有效期
- 查看 Keys 列表
- 吊销/删除 Keys
- 查看使用统计

#### 广告管理
- 添加广告
- 设置置顶/随机广告
- 切换广告状态
- 查看浏览/点击数据

#### 广播消息
- 向所有用户发送通知
- 实时状态反馈

### 认证机制

#### 登录流程
```
POST /api/auth/login
{
    "username": "admin",
    "password": "password"
}

Response:
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "username": "admin"
}
```

#### Token 验证
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

#### Token 结构
```json
{
    "admin_id": 1,
    "username": "admin",
    "exp": "2026-04-28T00:00:00",
    "iat": "2026-04-27T12:00:00",
    "jti": "random-token-id"
}
```

### API 接口列表

| 方法 | 端点 | 功能 |
|------|------|------|
| POST | /api/auth/login | 登录 |
| POST | /api/auth/logout | 登出 |
| GET | /api/auth/verify | 验证 Token |
| GET | /api/admin/dashboard | 仪表盘数据 |
| GET | /api/admin/users | 用户列表 |
| GET | /api/admin/users/{id} | 用户详情 |
| PUT | /api/admin/users/{id} | 更新用户 |
| GET | /api/admin/reports | 举报列表 |
| POST | /api/admin/reports/{id}/approve | 通过举报 |
| POST | /api/admin/reports/{id}/reject | 拒绝举报 |
| GET | /api/admin/appeals | 申诉列表 |
| POST | /api/admin/appeals/{id}/approve | 通过申诉 |
| POST | /api/admin/appeals/{id}/reject | 拒绝申诉 |
| POST | /api/admin/api-keys/generate | **批量生成 Keys** |
| GET | /api/admin/api-keys | Keys 列表 |
| POST | /api/admin/api-keys/{id}/revoke | 吊销 Key |
| DELETE | /api/admin/api-keys/{id} | 删除 Key |
| GET | /api/admin/ads | 广告列表 |
| POST | /api/admin/ads | 创建广告 |
| PUT | /api/admin/ads/{id} | 更新广告 |
| DELETE | /api/admin/ads/{id} | 删除广告 |
| POST | /api/admin/broadcast | 广播消息 |

### 环境变量配置

```bash
# 后台管理配置
ADMIN_SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=jwt-secret-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me-in-production

# 端口配置
ADMIN_PORT=5000
FLASK_DEBUG=False
```

---

## 7. 扩展功能（建议）

### 7.1 数据分析
- 举报趋势图表
- 高风险账号排行
- 月度/年度报告

### 7.2 积分系统
- 举报成功获得积分
- 积分可兑换密钥或特权
- 鼓励用户参与

### 7.3 预警推送
- 当关注的账号被举报时通知用户
- 高风险账号自动预警

### 7.4 API 接口
- 提供第三方查询接口
- 支持机器人接入
- 计费模式（可选）

### 7.5 多语言支持
- 中文（默认）
- 英文
- 可扩展其他语言

---

## 8. 运营策略

### 收入来源
1. **广告收入**：置顶广告位 + 随机广告
2. **密钥销售**：高级功能的访问密钥
3. **增值服务**：高级查询、数据导出等

### 用户激励
- 举报成功奖励积分
- 邀请好友获得密钥
- 活跃用户优先审核

---

## 9. 部署说明

### 环境要求
- Python 3.10+
- 4GB+ RAM
- 稳定网络连接

### 部署方式
1. **Docker 部署**（推荐）
   ```bash
   docker-compose up -d
   ```

2. **手动部署**
   ```bash
   pip install -r requirements.txt
   python bot/main.py
   ```

### 配置说明
1. 复制 `.env.example` 为 `.env`
2. 填写必要的配置项：
   - `TELEGRAM_BOT_TOKEN`
   - 数据库配置
   - 管理员 ID

---

## 10. 版本规划

### v1.0（基础版）
- [ ] 举报功能
- [ ] 查询功能
- [ ] 基础群管理

### v1.1（完善版）
- [ ] 申诉功能
- [ ] 智能风险评估
- [ ] 广告系统

### v2.0（高级版）
- [ ] 多语言支持
- [ ] 数据分析
- [ ] API 接口
- [ ] 积分系统

---

*文档版本：1.0*
*最后更新：2026-04-27*