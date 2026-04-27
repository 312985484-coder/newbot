"""
开始命令处理器
"""

from telegram import Update
from telegram.ext import ContextTypes

from bot.database.connection import SessionLocal
from bot.database.models import User
from bot.keyboards.inline import get_main_menu_keyboard
from bot.locales.i18n import get_text
from bot.services.ad_service import get_ad_display


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    user = update.effective_user
    chat_id = update.effective_chat.id

    # 创建或更新用户
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        if not db_user:
            db_user = User(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            db.add(db_user)
        else:
            db_user.username = user.username
            db_user.first_name = user.first_name
            db_user.last_name = user.last_name
        db.commit()
    finally:
        db.close()

    # 构建欢迎消息
    welcome_text = f"""
👋 欢迎使用 <b>TeleGreat 防骗举报机器人</b>！

🔍 我能帮助您：
• 查询可疑账号是否有诈骗历史
• 举报骗子，保护社区安全
• 申诉被错误举报的账号

⚠️ 请勿轻信陌生人的转账要求，交易前请先查询！

━━━━━━━━━━━━━━━━━━━━
    """

    # 获取广告
    ads_text = await get_ad_display()

    # 发送欢迎消息
    await context.bot.send_message(
        chat_id=chat_id,
        text=welcome_text + ads_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    message = update.effective_message
    if not message:
        return

    help_text = """
📖 <b>使用帮助</b>

<b>基本命令：</b>
/start - 启动机器人
/help - 显示帮助
/report - 举报骗子账号
/search - 查询用户信息
/appeal - 申诉通道
/profile - 查看个人资料

<b>如何举报？</b>
1. 点击「🔍 查询用户」按钮
2. 选择「🚨 举报骗子」
3. 填写被骗信息
4. 提交证据

<b>如何查询？</b>
发送 /search 后跟用户名
例如：/search @username

━━━━━━━━━━━━━━━━━━━━
⚠️ 遇到问题请联系管理员
    """

    await message.reply_text(help_text, parse_mode="HTML")


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /profile 命令"""
    user = update.effective_user
    message = update.effective_message
    if not message:
        return

    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        if not db_user:
            await message.reply_text("❌ 用户数据不存在，请先发送 /start")
            return

        # 构建个人资料
        profile_text = f"""
👤 <b>个人资料</b>

🆔 Telegram ID: <code>{db_user.id}</code>
📛 用户名: @{db_user.username or "未设置"}
👤 名字: {db_user.first_name or ""} {db_user.last_name or ""}

🔑 API 密钥状态: {'✅ 已激活' if db_user.key_status == 'active' else '❌ 未激活'}
📊 密钥: <code>{db_user.api_key or '无'}</code>

📈 统计数据:
• 总举报次数: {db_user.total_reports}
• 成功举报: {db_user.successful_reports}
• 信誉分数: {db_user.reputation_score}

⏰ 注册时间: {db_user.created_at.strftime('%Y-%m-%d %H:%M')}
        """

        await message.reply_text(profile_text.strip(), parse_mode="HTML")
    finally:
        db.close()
