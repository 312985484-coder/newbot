"""
广播消息功能
"""

from telegram import Bot

from bot.database.connection import SessionLocal
from bot.database.models import User
from bot.config import settings


def send_broadcast(message: str):
    """广播消息给所有用户"""
    try:
        bot = Bot(token=settings.telegram_bot_token)

        db = SessionLocal()
        try:
            users = db.query(User).all()
            success_count = 0
            fail_count = 0

            for user in users:
                try:
                    bot.send_message(
                        chat_id=user.id,
                        text=f"📢 <b>管理员通知</b>\n\n{message}",
                        parse_mode="HTML"
                    )
                    success_count += 1
                except Exception:
                    fail_count += 1

            return {
                "success": True,
                "message": f"广播完成",
                "details": {
                    "total": len(users),
                    "success": success_count,
                    "failed": fail_count
                }
            }

        finally:
            db.close()

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
