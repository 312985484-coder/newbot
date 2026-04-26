"""
内联键盘定义
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard():
    """获取主菜单键盘"""
    keyboard = [
        [
            InlineKeyboardButton("🔍 查询用户", callback_data="search_user"),
            InlineKeyboardButton("🚨 举报骗子", callback_data="report_start")
        ],
        [
            InlineKeyboardButton("🛡️ 申诉通道", callback_data="appeal"),
            InlineKeyboardButton("👤 个人资料", callback_data="profile")
        ],
        [
            InlineKeyboardButton("📖 使用帮助", callback_data="help"),
            InlineKeyboardButton("📢 广告位招租", callback_data="advertise")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_report_keyboard():
    """获取举报菜单键盘"""
    keyboard = [
        [InlineKeyboardButton("🚨 开始举报", callback_data="report_start")],
        [InlineKeyboardButton("📜 举报历史", callback_data="report_history")],
        [InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_search_result_keyboard(user_id: int = None):
    """获取查询结果键盘"""
    keyboard = []

    if user_id:
        keyboard.append([
            InlineKeyboardButton(
                "📋 查看详情",
                callback_data=f"search_detail_{user_id}"
            )
        ])

    keyboard.extend([
        [InlineKeyboardButton("🔍 继续查询", callback_data="search_user")],
        [InlineKeyboardButton("🚨 举报此人", callback_data=f"report_target_{user_id}")],
        [InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu")]
    ])

    return InlineKeyboardMarkup(keyboard)


def get_admin_keyboard():
    """获取管理员菜单键盘"""
    keyboard = [
        [
            InlineKeyboardButton("📋 待审核举报", callback_data="admin_reports"),
            InlineKeyboardButton("📝 待处理申诉", callback_data="admin_appeals")
        ],
        [
            InlineKeyboardButton("👥 用户管理", callback_data="admin_users"),
            InlineKeyboardButton("📢 广告管理", callback_data="admin_ads")
        ],
        [
            InlineKeyboardButton("📊 全局统计", callback_data="admin_stats"),
            InlineKeyboardButton("🔧 系统设置", callback_data="admin_settings")
        ],
        [InlineKeyboardButton("🔙 返回", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_yes_no_keyboard(confirm_data: str, cancel_data: str = "main_menu"):
    """获取确认/取消键盘"""
    keyboard = [
        [
            InlineKeyboardButton("✅ 确认", callback_data=confirm_data),
            InlineKeyboardButton("❌ 取消", callback_data=cancel_data)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_pagination_keyboard(page: int, total_pages: int, prefix: str):
    """获取分页键盘"""
    keyboard = []

    # 上一页/下一页
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("◀️ 上一页", callback_data=f"{prefix}_page_{page-1}"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("下一页 ▶️", callback_data=f"{prefix}_page_{page+1}"))

    if nav_row:
        keyboard.append(nav_row)

    keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="main_menu")])

    return InlineKeyboardMarkup(keyboard)
