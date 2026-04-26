"""
查询功能处理器
"""

from telegram import Update
from telegram.ext import ContextTypes

from bot.database.connection import SessionLocal
from bot.database.models import User, Report, ReportedUser
from bot.keyboards.inline import get_search_result_keyboard, get_main_menu_keyboard
from bot.services.search_service import (
    search_by_username, search_by_user_id,
    get_risk_level_display, calculate_risk_level
)
from bot.services.ad_service import get_ad_display


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /search 命令"""
    chat_id = update.effective_chat.id

    # 检查是否提供了搜索参数
    if not context.args:
        await context.bot.send_message(
            chat_id=chat_id,
            text="""
🔍 <b>用户查询</b>

请提供要查询的用户信息：

方式1：使用命令查询
/search @username

方式2：直接输入用户ID
/search 123456789

方式3：转发该用户的消息给我
/search (然后转发消息)
            """,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
        return

    query = context.args[0].lstrip("@")

    # 判断是用户名还是用户ID
    if query.isdigit():
        result = await search_by_user_id(int(query))
    else:
        result = await search_by_username(query)

    await send_search_result(update, context, result)


async def search_via_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理转发的消息进行查询"""
    if not update.message.forward_from:
        await update.message.reply_text("❌ 无法识别转发的消息来源")
        return

    forward_from = update.message.forward_from
    result = await search_by_user_id(forward_from.id)
    await send_search_result(update, context, result)


async def send_search_result(update: Update, context: ContextTypes.DEFAULT_TYPE, result: dict):
    """发送查询结果"""
    chat_id = update.effective_chat.id

    # 获取广告
    ads_text = await get_ad_display()

    if not result or result.get("report_count", 0) == 0:
        # 未被举报的用户
        search_text = f"""
🔍 <b>查询结果</b>

👤 用户：@{result.get('username', 'unknown') if result else query}
📛 名字：{result.get('first_name', '未知') if result else '未知'}

✅ <b>安全</b> - 该账号暂无举报记录

💡 <b>温馨提示</b>：
虽然该账号暂无记录，但仍需保持警惕！
不要轻信陌生人的转账要求。

━━━━━━━━━━━━━━━━━━━━
        """
        await context.bot.send_message(
            chat_id=chat_id,
            text=search_text + ads_text,
            parse_mode="HTML"
        )
    else:
        # 有举报记录的用户
        risk_display = get_risk_level_display(result["risk_level"])
        risk_emoji = {
            "safe": "✅",
            "low": "🟡",
            "medium": "🟠",
            "high": "🔴"
        }.get(result["risk_level"], "⚪")

        search_text = f"""
🔍 <b>查询结果</b>

👤 用户：@{result.get('username', 'unknown')}
📛 名字：{result.get('first_name', '未知')}

⚠️ <b>该账号已被举报</b>

📊 举报次数：{result['report_count']} 次
💰 累积金额：{result['total_amount']} USDT

{risk_emoji} 风险等级：{risk_display}

📋 <b>历史记录</b>
{'-' * 20}
        """

        # 添加最近3条举报简略信息
        for i, report in enumerate(result.get("recent_reports", [])[:3], 1):
            search_text += f"""
{i}️⃣ {report['scam_time']} - {report['amount']} USDT
   简要：{report['description'][:30]}...
            """

        search_text += f"""
{'-' * 20}

⚠️ <b>警告</b>：交易需谨慎！
🆘 如被骗请联系管理员申诉

💡 <b>查看详情</b>：点击下方按钮
        """

        await context.bot.send_message(
            chat_id=chat_id,
            text=search_text,
            parse_mode="HTML",
            reply_markup=get_search_result_keyboard(result.get("user_id"))
        )

        # 发送广告
        await context.bot.send_message(
            chat_id=chat_id,
            text=ads_text,
            parse_mode="HTML"
        )


async def search_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理查看详情的回调"""
    query = update.callback_query
    await query.answer()

    # TODO: 实现详情查询和展示
    data = query.data
    if data.startswith("search_detail_"):
        user_id = data.replace("search_detail_", "")
        # 发送详细信息
        await query.edit_message_text(
            text="""
📋 <b>详细信息</b>

功能开发中...
请稍后再试
            """,
            parse_mode="HTML"
        )
