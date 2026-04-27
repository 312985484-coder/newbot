"""
管理员功能处理器
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.database.connection import SessionLocal
from bot.database.models import User, Report, Appeal, Advertisement, ReportedUser
from bot.config import settings
from bot.keyboards.inline import get_admin_keyboard, get_main_menu_keyboard


def is_admin(user_id: int) -> bool:
    """检查是否为管理员"""
    return user_id in settings.get_admin_ids()


def is_super_admin(user_id: int) -> bool:
    """检查是否为超级管理员"""
    return user_id in settings.get_super_admin_ids()


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /admin 命令"""
    user = update.effective_user
    chat_id = update.effective_chat.id

    if not is_admin(user.id):
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ 您没有管理员权限"
        )
        return

    # 获取统计数据
    db = SessionLocal()
    try:
        pending_reports = db.query(Report).filter(Report.status == "pending").count()
        pending_appeals = db.query(Appeal).filter(Appeal.status == "pending").count()

        total_users = db.query(User).count()
        total_reports = db.query(Report).filter(Report.status == "approved").count()

        stats_text = f"""
🔧 <b>管理面板</b>

👤 管理员：{user.first_name}

📊 <b>数据统计</b>
• 总用户：{total_users}
• 总举报（已通过）：{total_reports}
• 待审核举报：{pending_reports}
• 待处理申诉：{pending_appeals}
        """

        await context.bot.send_message(
            chat_id=chat_id,
            text=stats_text,
            parse_mode="HTML",
            reply_markup=get_admin_keyboard()
        )
    finally:
        db.close()


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理管理员回调"""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data
    chat_id = query.message.chat_id

    if not is_admin(user.id):
        await query.answer("❌ 无权限", show_alert=True)
        return

    db = SessionLocal()
    try:
        if data == "admin_reports":
            # 待审核举报列表
            reports = db.query(Report).filter(
                Report.status == "pending"
            ).limit(5).all()

            if not reports:
                await query.edit_message_text(
                    text="✅ 暂无待审核的举报",
                    reply_markup=get_admin_keyboard()
                )
                return

            text = "📋 <b>待审核举报</b>\n\n"
            keyboard = []

            for i, report in enumerate(reports, 1):
                text += f"""
{i}️⃣ ID: <code>{report.id[:8]}</code>
👤 被举报：@{report.target_username or 'unknown'}
💰 金额：{report.amount} {report.currency}
📝 描述：{report.description[:50]}...
⏰ 时间：{report.created_at.strftime('%Y-%m-%d')}
                """
                keyboard.append([
                    InlineKeyboardButton(
                        f"✅ 通过 #{report.id[:6]}",
                        callback_data=f"approve_{report.id}"
                    ),
                    InlineKeyboardButton(
                        f"❌ 拒绝 #{report.id[:6]}",
                        callback_data=f"reject_{report.id}"
                    )
                ])

            keyboard.append([
                InlineKeyboardButton("🔙 返回", callback_data="admin_back")
            ])

            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data == "admin_appeals":
            # 待处理申诉列表
            appeals = db.query(Appeal).filter(
                Appeal.status == "pending"
            ).limit(5).all()

            if not appeals:
                await query.edit_message_text(
                    text="✅ 暂无待处理的申诉",
                    reply_markup=get_admin_keyboard()
                )
                return

            text = "📋 <b>待处理申诉</b>\n\n"
            keyboard = []

            for i, appeal in enumerate(appeals, 1):
                text += f"""
{i}️⃣ ID: <code>{appeal.id[:8]}</code>
👤 申诉人：{appeal.user_id}
📋 原因：{appeal.reason[:50]}...
⏰ 时间：{appeal.created_at.strftime('%Y-%m-%d')}
                """
                keyboard.append([
                    InlineKeyboardButton(
                        f"✅ 通过 #{appeal.id[:6]}",
                        callback_data=f"appeal_approve_{appeal.id}"
                    ),
                    InlineKeyboardButton(
                        f"❌ 拒绝 #{appeal.id[:6]}",
                        callback_data=f"appeal_reject_{appeal.id}"
                    )
                ])

            keyboard.append([
                InlineKeyboardButton("🔙 返回", callback_data="admin_back")
            ])

            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data == "admin_ads":
            # 广告管理
            ads = db.query(Advertisement).filter(
                Advertisement.status == "active"
            ).all()

            pinned = [a for a in ads if a.type == "pinned"]
            random_ads = [a for a in ads if a.type == "random"]

            text = f"""
📢 <b>广告管理</b>

📌 置顶广告：{len(pinned)}/2
🎲 随机广告：{len(random_ads)}

💡 置顶广告会在所有回复中显示
🎲 随机广告每次随机抽取3条
            """

            keyboard = [
                [InlineKeyboardButton("➕ 添加置顶广告", callback_data="ad_add_pinned")],
                [InlineKeyboardButton("➕ 添加随机广告", callback_data="ad_add_random")],
                [InlineKeyboardButton("📋 管理现有广告", callback_data="ad_list")],
                [InlineKeyboardButton("🔙 返回", callback_data="admin_back")]
            ]

            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data.startswith("approve_"):
            # 通过举报
            report_id = data.replace("approve_", "")
            report = db.query(Report).filter(Report.id == report_id).first()

            if report:
                report.status = "approved"
                report.approved_by = user.id
                from datetime import datetime
                report.approved_at = datetime.utcnow()

                # 更新 ReportedUser 表
                reported_user = db.query(ReportedUser).filter(
                    ReportedUser.user_id == report.target_user_id
                ).first()

                if reported_user:
                    reported_user.report_count += 1
                    from sqlalchemy import func
                    reported_user.total_amount = float(reported_user.total_amount or 0) + float(report.amount or 0)
                    reported_user.last_reported_at = datetime.utcnow()
                else:
                    from bot.database.models import ReportedUser as RU
                    new_reported = RU(
                        user_id=report.target_user_id,
                        username=report.target_username,
                        first_name=report.target_first_name,
                        last_name=report.target_last_name,
                        report_count=1,
                        total_amount=report.amount,
                        risk_level="low",
                        first_reported_at=datetime.utcnow(),
                        last_reported_at=datetime.utcnow()
                    )
                    db.add(new_reported)

                db.commit()
                await query.answer("✅ 举报已通过！", show_alert=True)

        elif data.startswith("reject_"):
            # 拒绝举报
            report_id = data.replace("reject_", "")
            report = db.query(Report).filter(Report.id == report_id).first()

            if report:
                report.status = "rejected"
                db.commit()
                await query.answer("❌ 举报已拒绝", show_alert=True)

        elif data == "admin_back":
            # 返回管理面板
            await admin_command(update, context)

        elif data == "admin_users":
            # 用户管理
            users = db.query(User).order_by(User.created_at.desc()).limit(10).all()

            if not users:
                await query.edit_message_text(
                    text="📭 暂无用户数据",
                    reply_markup=get_admin_keyboard()
                )
                return

            text = "👥 <b>用户列表</b>\n\n"
            keyboard = []

            for i, user in enumerate(users, 1):
                text += f"{i}. {user.first_name or '未知'}\n"
                text += f"   ID: <code>{user.user_id}</code>\n"
                text += f"   注册: {user.created_at.strftime('%Y-%m-%d')}\n\n"

            keyboard.append([
                InlineKeyboardButton("🔙 返回", callback_data="admin_back")
            ])

            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data == "admin_stats":
            # 全局统计
            total_users = db.query(User).count()
            total_reports = db.query(Report).count()
            approved_reports = db.query(Report).filter(Report.status == "approved").count()
            pending_reports = db.query(Report).filter(Report.status == "pending").count()
            total_appeals = db.query(Appeal).count()
            pending_appeals = db.query(Appeal).filter(Appeal.status == "pending").count()

            text = f"""
📊 <b>全局统计数据</b>

👥 <b>用户</b>
• 总用户数：{total_users}

🚨 <b>举报</b>
• 总举报数：{total_reports}
• 已通过：{approved_reports}
• 待审核：{pending_reports}

🛡️ <b>申诉</b>
• 总申诉数：{total_appeals}
• 待处理：{pending_appeals}
            """

            keyboard = [
                [InlineKeyboardButton("🔙 返回", callback_data="admin_back")]
            ]

            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data == "admin_settings":
            # 系统设置
            text = """
🔧 <b>系统设置</b>

当前版本：v1.0.0

💡 设置功能正在开发中...
            """

            keyboard = [
                [InlineKeyboardButton("🔙 返回", callback_data="admin_back")]
            ]

            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data.startswith("appeal_approve_"):
            # 通过申诉
            appeal_id = data.replace("appeal_approve_", "")
            appeal = db.query(Appeal).filter(Appeal.id == appeal_id).first()
            if appeal:
                appeal.status = "approved"
                db.commit()
                await query.answer("✅ 申诉已通过！", show_alert=True)
                try:
                    await context.bot.send_message(
                        chat_id=appeal.user_id,
                        text="✅ 您的申诉已通过审核！"
                    )
                except:
                    pass

        elif data.startswith("appeal_reject_"):
            # 拒绝申诉
            appeal_id = data.replace("appeal_reject_", "")
            appeal = db.query(Appeal).filter(Appeal.id == appeal_id).first()
            if appeal:
                appeal.status = "rejected"
                db.commit()
                await query.answer("❌ 申诉已拒绝", show_alert=True)
                try:
                    await context.bot.send_message(
                        chat_id=appeal.user_id,
                        text="❌ 您的申诉已被拒绝。"
                    )
                except:
                    pass

    finally:
        db.close()
