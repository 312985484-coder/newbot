"""
查询服务
"""

from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy.orm import Session

from bot.database.connection import SessionLocal
from bot.database.models import ReportedUser, Report


def calculate_risk_level(report_count: int, total_amount: float) -> str:
    """计算风险等级"""
    if report_count >= 5 or total_amount >= 5000:
        return "high"
    elif report_count >= 3 or total_amount >= 1000:
        return "medium"
    elif report_count >= 1:
        return "low"
    return "safe"


def get_risk_level_display(risk_level: str) -> str:
    """获取风险等级显示文本"""
    displays = {
        "safe": "安全",
        "low": "低风险",
        "medium": "中风险",
        "high": "高风险"
    }
    return displays.get(risk_level, "未知")


async def search_by_username(username: str) -> Optional[Dict]:
    """通过用户名查询"""
    db = SessionLocal()
    try:
        # 先尝试查找被举报用户
        reported_user = db.query(ReportedUser).filter(
            ReportedUser.username == username
        ).first()

        if reported_user:
            # 获取最近举报记录
            reports = db.query(Report).filter(
                Report.target_user_id == reported_user.user_id,
                Report.status == "approved"
            ).order_by(Report.created_at.desc()).limit(10).all()

            return {
                "user_id": reported_user.user_id,
                "username": reported_user.username,
                "first_name": reported_user.first_name,
                "last_name": reported_user.last_name,
                "report_count": reported_user.report_count,
                "total_amount": float(reported_user.total_amount or 0),
                "risk_level": reported_user.risk_level,
                "recent_reports": [
                    {
                        "id": r.id,
                        "scam_time": r.scam_time.strftime("%Y-%m-%d") if r.scam_time else "未知",
                        "amount": float(r.amount or 0),
                        "currency": r.currency,
                        "description": r.description
                    }
                    for r in reports
                ]
            }

        return None

    finally:
        db.close()


async def search_by_user_id(user_id: int) -> Optional[Dict]:
    """通过用户ID查询"""
    db = SessionLocal()
    try:
        reported_user = db.query(ReportedUser).filter(
            ReportedUser.user_id == user_id
        ).first()

        if reported_user:
            reports = db.query(Report).filter(
                Report.target_user_id == user_id,
                Report.status == "approved"
            ).order_by(Report.created_at.desc()).limit(10).all()

            return {
                "user_id": reported_user.user_id,
                "username": reported_user.username,
                "first_name": reported_user.first_name,
                "last_name": reported_user.last_name,
                "report_count": reported_user.report_count,
                "total_amount": float(reported_user.total_amount or 0),
                "risk_level": reported_user.risk_level,
                "recent_reports": [
                    {
                        "id": r.id,
                        "scam_time": r.scam_time.strftime("%Y-%m-%d") if r.scam_time else "未知",
                        "amount": float(r.amount or 0),
                        "currency": r.currency,
                        "description": r.description
                    }
                    for r in reports
                ]
            }

        return None

    finally:
        db.close()


async def get_user_report_history(user_id: int, page: int = 1, limit: int = 10) -> Dict:
    """获取用户的举报历史"""
    db = SessionLocal()
    try:
        offset = (page - 1) * limit

        reports = db.query(Report).filter(
            Report.target_user_id == user_id,
            Report.status == "approved"
        ).order_by(Report.created_at.desc()).limit(limit).offset(offset).all()

        total = db.query(Report).filter(
            Report.target_user_id == user_id,
            Report.status == "approved"
        ).count()

        return {
            "reports": [
                {
                    "id": r.id,
                    "scam_time": r.scam_time,
                    "amount": float(r.amount or 0),
                    "currency": r.currency,
                    "description": r.description,
                    "evidence_urls": r.evidence_urls or [],
                    "created_at": r.created_at
                }
                for r in reports
            ],
            "total": total,
            "page": page,
            "total_pages": (total + limit - 1) // limit
        }

    finally:
        db.close()


async def check_user_risk(user_id: int) -> Dict:
    """检查用户风险状态"""
    result = await search_by_user_id(user_id)

    if not result:
        return {
            "is_risky": False,
            "risk_level": "safe",
            "message": "未发现风险"
        }

    return {
        "is_risky": result["risk_level"] in ["medium", "high"],
        "risk_level": result["risk_level"],
        "report_count": result["report_count"],
        "total_amount": result["total_amount"],
        "message": f"发现 {result['report_count']} 条举报记录"
    }
