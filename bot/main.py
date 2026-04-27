"""
TeleGreat 机器人主入口
"""

import logging
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from bot.config import settings
from bot.database.migrations import run_migrations

# 导入处理器
from bot.handlers.start import start_command, help_command, profile_command
from bot.handlers.report import report_command, quick_report
from bot.handlers.search import search_command, search_via_forward, search_detail_callback
from bot.handlers.appeal import appeal_command, appeal_callback
from bot.handlers.admin import admin_command, admin_callback
from bot.handlers.group import (
    new_member_handler,
    left_member_handler,
    group_settings_command,
    group_callback
)
from bot.keyboards.inline import get_main_menu_keyboard

# 配置日志
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, settings.log_level),
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.log_file, encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """错误处理"""
    logger.error(f"错误: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ 发生错误，请稍后重试。"
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query
    await query.answer()

    data = query.data

    # 主菜单按钮
    if data == "main_menu":
        await start_command(update, context)
        return

    # 查询用户
    if data == "search_user":
        await search_command(update, context)
        return

    # 举报
    if data == "report_start":
        await report_command(update, context)
        return

    # 申诉
    if data == "appeal":
        await appeal_command(update, context)
        return

    # 个人资料
    if data == "profile":
        await profile_command(update, context)
        return

    # 帮助
    if data == "help":
        await help_command(update, context)
        return

    # 广告位招租
    if data == "advertise":
        await query.edit_message_text(
            text=f"""
📢 <b>广告位招租</b>

我们提供以下广告位：

📌 <b>置顶广告位（2个）</b>
• 出现在所有回复底部
• 永久展示，高曝光
• 价格：联系管理员

🎯 <b>随机广告位（3个）</b>
• 随机展示，增加曝光
• 价格更优惠
• 适合各类产品推广

💡 <b>优势：</b>
• 用户活跃度高
• 精准触达目标用户
• 多渠道展示

📞 联系方式：
👤 {settings.admin_contact}
            """,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
        return

    # 购买密钥
    if data == "buy_key":
        await query.edit_message_text(
            text=f"""
🔑 <b>获取 API 密钥</b>

举报功能需要有效的 API 密钥。

💡 <b>获取方式：</b>
1️⃣ 联系管理员购买
2️⃣ 参与社区活动获取
3️⃣ 邀请好友获得奖励

📞 联系方式：
👤 {settings.admin_contact}
            """,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
        return

    # 未知按钮
    logger.warning(f"未知按钮: {data}")


async def post_init(application: Application):
    """机器人初始化后的回调"""
    # 设置命令菜单
    commands = [
        BotCommand("start", "启动机器人"),
        BotCommand("help", "显示帮助"),
        BotCommand("search", "查询用户"),
        BotCommand("report", "举报骗子"),
        BotCommand("appeal", "申诉通道"),
        BotCommand("profile", "个人资料"),
        BotCommand("admin", "管理面板"),
        BotCommand("group", "群组设置")
    ]
    await application.bot.set_my_commands(commands)
    logger.info("命令菜单已设置")


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("TeleGreat 防骗举报机器人启动中...")
    logger.info("=" * 50)

    # 初始化数据库
    logger.info("初始化数据库...")
    run_migrations()

    # 创建应用
    application = Application.builder().token(settings.telegram_bot_token).build()

    # 添加初始化回调
    application.post_init = post_init

    # 添加错误处理
    application.add_error_handler(error_handler)

    # 用户命令
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_command))

    # 查询命令
    application.add_handler(CommandHandler("search", search_command))

    # 举报命令
    application.add_handler(CommandHandler("report", report_command))

    # 申诉命令
    application.add_handler(CommandHandler("appeal", appeal_command))

    # 管理员命令
    application.add_handler(CommandHandler("admin", admin_command))

    # 群组设置命令
    application.add_handler(CommandHandler("group", group_settings_command))

    # 回调处理器（按钮）
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern=r"^(admin_|approve_|reject_)"))
    application.add_handler(CallbackQueryHandler(search_detail_callback, pattern=r"^search_detail_"))
    application.add_handler(CallbackQueryHandler(appeal_callback, pattern=r"^(appeal|appeal_approve_|appeal_reject_)"))

    # 消息处理器
    # 处理转发的消息（用于查询）
    application.add_handler(MessageHandler(
        filters.FORWARDED & ~filters.COMMAND,
        search_via_forward
    ))

    # 群组消息处理器
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        new_member_handler
    ))

    application.add_handler(MessageHandler(
        filters.StatusUpdate.LEFT_CHAT_MEMBER,
        left_member_handler
    ))

    # 启动机器人
    logger.info("机器人已启动，开始监听消息...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
