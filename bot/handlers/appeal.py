"""
申诉功能处理器
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.database.connection import SessionLocal
from bot.database.models import User, Appeal, ReportedUser
from bot.config import settings
from bot.keyboards.inline import get_main_menu_keyboard


async def appeal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /appeal 命令"""
    user = update.effective_user
    chat_id = update.effective_chat.id

    # 获取管理员列表
    admin_ids = settings.get_admin_ids()
    admin_mentions = "\n".join([f"👤 <a href='tg://user?id={aid}'>管理员</a>" for aid in admin_ids[:3]])

    keyboard = [
        [InlineKeyboardButton("📝 提交正式申诉", callback_data="appeal_submit")],
        [InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu")]
    ]

    appeal_text = f"""
🛡️ <b>申诉通道</b>

如果您认为被错误举报或恶意举报，
可以使用此通道进行申诉。

📌 <b>申诉须知</b>
• 需提供充分证据证明清白
• 申诉理由需详细（最少50字）
• 管理员审核后会告知结果

━━━━━━━━━━━━━━━━━━━━

📨 <b>联系管理员</b>
{admin_mentions}

💬 请简要说明情况，
   管理员会尽快处理

━━━━━━━━━━━━━━━━━━━━

📝 <b>或提交正式申诉表单</b>

        """

    await context.bot.send_message(
        chat_id=chat_id,
        text=appeal_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def appeal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理申诉相关的回调"""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data
    chat_id = query.message.chat_id

    if data == "appeal_submit":
        # 检查用户是否被举报
        db = SessionLocal()
        try:
            reported_user = db.query(ReportedUser).filter(
                ReportedUser.user_id == user.id
            ).first()

            if not reported_user:
                await query.edit_message_text(
                    text="""
❌ <b>无需申诉</b>

您的账号目前没有被举报记录，
无需进行申诉。

如有其他问题请联系管理员。
                    """,
                    parse_mode="HTML",
                    reply_markup=get_main_menu_keyboard()
                )
                return

            await query.edit_message_text(
                text=f"""
📝 <b>提交申诉</b>

👤 被举报账号：@{reported_user.username or user.username}
📊 当前状态：被举报 {reported_user.report_count} 次
⚠️ 风险等级：{reported_user.risk_level}

请提供以下信息：

<b>1️⃣ 申诉理由</b>
请详细说明为什么您认为举报是错误的：
（最少50字）

<b>2️⃣ 证据材料</b>
如果有证明您清白的证据，
请直接发送图片或文档。
                """,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 取消", callback_data="appeal_cancel")]
                ])
            )
            return ReportStates.AWAITING_REASON

        finally:
            db.close()

    elif data == "appeal_cancel":
        await query.edit_message_text(
            text="❌ 申诉已取消",
            reply_markup=get_main_menu_keyboard()
        )


class ReportStates:
    """状态常量（与其他模块共享）"""
    AWAITING_REASON = 10
