"""
辅助函数
"""

from datetime import datetime
from typing import Optional


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """格式化日期时间"""
    if not dt:
        return "未知"
    return dt.strftime(format_str)


def format_amount(amount: float, currency: str = "USDT") -> str:
    """格式化金额"""
    if amount == 0:
        return f"0 {currency}"
    if amount < 1:
        return f"{amount:.4f} {currency}"
    if amount < 1000:
        return f"{amount:.2f} {currency}"
    return f"{amount:,.2f} {currency}"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """截断文本"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def escape_markdown(text: str) -> str:
    """转义 Markdown 特殊字符"""
    if not text:
        return text
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text


def get_user_display_name(user) -> str:
    """获取用户显示名称"""
    if user.username:
        return f"@{user.username}"
    name = user.first_name or ""
    if user.last_name:
        name += f" {user.last_name}"
    return name or f"用户{user.id}"


def validate_username(username: str) -> bool:
    """验证用户名格式"""
    if not username:
        return False
    # Telegram 用户名必须是 5-32 个字符，以 @ 开头
    if len(username) < 5 or len(username) > 33:
        return False
    if not username.startswith('@'):
        username = '@' + username
    return username[1:].replace('_', '').isalnum()


def get_risk_level_emoji(level: str) -> str:
    """获取风险等级表情"""
    emojis = {
        "safe": "✅",
        "low": "🟡",
        "medium": "🟠",
        "high": "🔴"
    }
    return emojis.get(level, "⚪")


def calculate_percentage(value: int, total: int) -> str:
    """计算百分比"""
    if total == 0:
        return "0%"
    return f"{value / total * 100:.1f}%"
