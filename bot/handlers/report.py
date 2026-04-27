"""
举报功能处理器
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.database.connection import SessionLocal
from bot.config import settings
from bot.database.models import User, Report, ReportedUser
from bot.keyboards.inline import get_report_keyboard, get_main_menu_keyboard
from bot.services.report_service import create_report, validate_api_key


class ReportStates:
    """举报流程状态"""
    AWAITING_TARGET = 1
    AWAITING_TIME = 2
    AWAITING_AMOUNT = 3
    AWAITING_DESCRIPTION = 4
    AWAITING_EVIDENCE = 5


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /report 命令"""
    user = update.effective_user
    chat_id = update.effective_chat.id

    # 检查用户是否有有效的 API Key
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        if not db_user or not db_user.api_key or db_user.key_status != "active":
            keyboard = [
                [InlineKeyboardButton("📢 购买/申请密钥", callback_data="buy_key")],
                [InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu")]
            ]
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"""
🔒 <b>需要密钥验证</b>

举报功能需要先验证您的密钥才能使用。

如果您还没有密钥，请联系管理员获取：
👤 {settings.admin_contact}

💡 密钥可以通过以下方式获得：
• 购买获取
• 邀请好友
• 活跃贡献奖励
                """,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # 验证密钥
        if not validate_api_key(db_user.api_key):
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ 密钥已过期，请重新获取！",
                reply_markup=get_main_menu_keyboard()
            )
            return

        # 开始举报流程
        keyboard = [
            [InlineKeyboardButton("🚨 我已知悉，开始举报", callback_data="report_start")],
            [InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu")]
        ]
        await context.bot.send_message(
            chat_id=chat_id,
            text="""
📝 <b>举报须知</b>

在提交举报前，请确保：
✅ 您是被骗的受害者
✅ 提供的信息真实有效
✅ 有相关证据支持

⚠️ 恶意举报将被追究责任！

━━━━━━━━━━━━━━━━━━━━
请提供以下信息：
1️⃣ 被骗时间
2️⃣ 骗子账号/用户名
3️⃣ 被骗金额
4️⃣ 被骗经过（最少20字）
5️⃣ 证据材料（如有）
            """,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    finally:
        db.close()


async def report_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理举报相关的回调"""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data
    chat_id = query.message.chat_id

    if data == "report_start":
        await query.edit_message_text(
            text="""
🔍 <b>请输入要举报的账号</b>

输入格式：
• @username（用户名）
• 或直接发送用户ID
• 或转发一条该用户的消息

⚠️ 请确保账号信息准确
            """,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 取消", callback_data="report_cancel")]
            ])
        )
        return ReportStates.AWAITING_TARGET

    elif data == "report_cancel":
        await query.edit_message_text(
            text="❌ 举报已取消",
            reply_markup=get_main_menu_keyboard()
        )
        return -1


async def handle_report_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理举报目标输入"""
    # 实现逻辑待完善
    pass


# 快捷举报命令
async def quick_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """快捷举报命令 /report @username"""
    if not context.args:
        await update.message.reply_text(
            "❌ 请提供要举报的用户名\n用法：/report @username"
        )
        return

    target = context.args[0].lstrip("@")
    # TODO: 实现快捷举报逻辑
    await update.message.reply_text(
        f"🔍 正在查询 @{target} 的举报信息..."
    )
