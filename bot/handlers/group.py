"""
群组管理功能处理器
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.database.connection import SessionLocal
from bot.database.models import GroupSettings, ReportedUser
from bot.services.search_service import calculate_risk_level


DEFAULT_WELCOME_MESSAGE = """
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

祝您在本群愉快！
"""


async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理新成员加入"""
    chat_id = update.effective_chat.id
    new_members = update.message.new_chat_members

    db = SessionLocal()
    try:
        # 获取群设置
        settings = db.query(GroupSettings).filter(
            GroupSettings.chat_id == chat_id
        ).first()

        if not settings:
            # 使用默认设置
            settings = GroupSettings(
                chat_id=chat_id,
                chat_title=update.effective_chat.title,
                welcome_message=DEFAULT_WELCOME_MESSAGE,
                welcome_enabled=True,
                auto_mute_reported_users=True
            )
            db.add(settings)
            db.commit()

        for member in new_members:
            # 跳过机器人
            if member.is_bot:
                continue

            # 查询该用户是否有不良记录
            reported_user = db.query(ReportedUser).filter(
                ReportedUser.user_id == member.id
            ).first()

            if reported_user and settings.auto_mute_reported_users:
                # 风险用户，自动禁言
                try:
                    await context.bot.restrict_chat_member(
                        chat_id=chat_id,
                        user_id=member.id,
                        permissions={
                            "can_send_messages": False,
                            "can_send_media_messages": False,
                            "can_send_other_messages": False,
                            "can_add_web_page_previews": False
                        }
                    )

                    # 发送警告
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"""
⚠️ <b>安全警告</b>

用户 <a href="tg://user?id={member.id}">{member.first_name}</a>
已被系统标记为高风险账号！

📊 举报次数：{reported_user.report_count}
💰 涉案金额：{reported_user.total_amount} USDT
⚠️ 风险等级：{reported_user.risk_level}

该用户已被自动禁言，请联系管理员处理。
                        """,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"禁言失败: {e}")

            elif settings.welcome_enabled:
                # 正常用户，发送欢迎消息
                welcome_msg = settings.welcome_message or DEFAULT_WELCOME_MESSAGE
                welcome_msg = welcome_msg.format(
                    username=f"<a href='tg://user?id={member.id}'>{member.first_name}</a>"
                )

                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=welcome_msg,
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
                except Exception as e:
                    print(f"欢迎消息发送失败: {e}")

    except Exception as e:
        print(f"新成员处理错误: {e}")
    finally:
        db.close()


async def left_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理成员离开"""
    # 可选：记录离开日志
    pass


async def group_settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """群组设置命令"""
    chat_id = update.effective_chat.id
    user = update.effective_user

    # 检查是否为群组
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ 此命令需要在群组中使用")
        return

    # 获取聊天成员身份
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        if member.status not in ["administrator", "creator"]:
            await update.message.reply_text("❌ 只有管理员才能使用此命令")
            return
    except Exception:
        await update.message.reply_text("❌ 无法获取您的权限信息")
        return

    db = SessionLocal()
    try:
        settings = db.query(GroupSettings).filter(
            GroupSettings.chat_id == chat_id
        ).first()

        if not settings:
            settings = GroupSettings(
                chat_id=chat_id,
                chat_title=update.effective_chat.title
            )
            db.add(settings)
            db.commit()

        status_emoji = {
            "on": "✅",
            "off": "❌"
        }

        welcome_status = status_emoji.get("on" if settings.welcome_enabled else "off", "❌")
        antispam_status = status_emoji.get("on" if settings.antispam_enabled else "off", "❌")
        mute_status = status_emoji.get("on" if settings.auto_mute_reported_users else "off", "❌")

        keyboard = [
            [
                InlineKeyboardButton(
                    f"欢迎消息 {welcome_status}",
                    callback_data="group_welcome_toggle"
                )
            ],
            [
                InlineKeyboardButton(
                    f"反垃圾 {antispam_status}",
                    callback_data="group_antispam_toggle"
                )
            ],
            [
                InlineKeyboardButton(
                    f"自动禁言风险用户 {mute_status}",
                    callback_data="group_mute_toggle"
                )
            ],
            [
                InlineKeyboardButton("📝 设置欢迎消息", callback_data="group_set_welcome")
            ],
            [
                InlineKeyboardButton("🔒 安全等级", callback_data="group_security")
            ]
        ]

        text = f"""
⚙️ <b>群组设置</b>

📌 群组：{update.effective_chat.title}

当前设置：

👋 欢迎消息：{welcome_status}
🛡️ 反垃圾：{antispam_status}
🔇 自动禁言风险用户：{mute_status}
🔒 安全等级：{settings.security_level}

点击下方按钮进行设置
        """

        await update.message.reply_text(
            text=text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    finally:
        db.close()


async def group_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """群组设置回调"""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data
    chat_id = query.message.chat_id

    # 验证管理员权限
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        if member.status not in ["administrator", "creator"]:
            await query.answer("❌ 无权限", show_alert=True)
            return
    except Exception:
        await query.answer("❌ 权限验证失败", show_alert=True)
        return

    db = SessionLocal()
    try:
        settings = db.query(GroupSettings).filter(
            GroupSettings.chat_id == chat_id
        ).first()

        if not settings:
            await query.answer("❌ 设置不存在", show_alert=True)
            return

        if data == "group_welcome_toggle":
            settings.welcome_enabled = not settings.welcome_enabled
            db.commit()
            await query.answer(
                f"欢迎消息已{'开启' if settings.welcome_enabled else '关闭'}",
                show_alert=True
            )

        elif data == "group_antispam_toggle":
            settings.antispam_enabled = not settings.antispam_enabled
            db.commit()
            await query.answer(
                f"反垃圾已{'开启' if settings.antispam_enabled else '关闭'}",
                show_alert=True
            )

        elif data == "group_mute_toggle":
            settings.auto_mute_reported_users = not settings.auto_mute_reported_users
            db.commit()
            await query.answer(
                f"自动禁言已{'开启' if settings.auto_mute_reported_users else '关闭'}",
                show_alert=True
            )

        # 重新显示设置菜单
        await group_settings_command(update, context)

    finally:
        db.close()


# 管理员快捷命令
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """禁言命令 /ban @username"""
    # 管理员功能，需要验证权限
    pass


async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """限时禁言命令 /mute @username duration"""
    pass


async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """踢出用户命令 /kick @username"""
    pass


async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """警告用户命令 /warn @username reason"""
    pass


async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """删除消息命令 /delete"""
    pass
