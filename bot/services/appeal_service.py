"""
申诉服务
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, List

from bot.database.connection import SessionLocal
from bot.database.models import Appeal, ReportedUser, Report, User


def create_appeal(
    user_id: int,
    target_user_id: int = None,
    target_username: str = None,
    reason: str = None,
    evidence_urls: list = None
) -> Dict:
    """创建申诉"""
    db = SessionLocal()
    try:
        appeal_id = str(uuid.uuid4())

        appeal = Appeal(
            id=appeal_id,
            user_id=user_id,
            target_user_id=target_user_id,
            target_username=target_username,
            reason=reason,
            evidence_urls=evidence_urls or [],
            status="pending"
        )
        db.add(appeal)
        db.commit()

        return {
            "success": True,
            "appeal_id": appeal_id,
            "message": "申诉已提交，等待管理员审核"
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        db.close()


def get_pending_appeals(page: int = 1, limit: int = 10) -> Dict:
    """获取待处理申诉列表"""
    db = SessionLocal()
    try:
        offset = (page - 1) * limit

        appeals = db.query(Appeal).filter(
            Appeal.status == "pending"
        ).order_by(Appeal.created_at.asc()).limit(limit).offset(offset).all()

        total = db.query(Appeal).filter(
            Appeal.status == "pending"
        ).count()

        return {
            "appeals": [
                {
                    "id": a.id,
                    "user_id": a.user_id,
                    "target_user_id": a.target_user_id,
                    "target_username": a.target_username,
                    "reason": a.reason,
                    "evidence_urls": a.evidence_urls or [],
                    "created_at": a.created_at
                }
                for a in appeals
            ],
            "total": total,
            "page": page,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1
        }

    finally:
        db.close()


def approve_appeal(appeal_id: int, admin_id: int, response: str = None) -> bool:
    """通过申诉 - 删除该用户的所有举报记录"""
    db = SessionLocal()
    try:
        appeal = db.query(Appeal).filter(Appeal.id == appeal_id).first()
        if not appeal or appeal.status != "pending":
            return False

        # 将该被举报用户的所有举报标记为已撤销（这里用rejected表示被申诉成功）
        reports = db.query(Report).filter(
            Report.target_user_id == appeal.target_user_id,
            Report.status == "approved"
        ).all()

        for report in reports:
            report.status = "rejected"
            report.rejection_reason = f"申诉通过：{response or '管理员已处理'}"

        # 更新或删除 ReportedUser 记录
        reported_user = db.query(ReportedUser).filter(
            ReportedUser.user_id == appeal.target_user_id
        ).first()

        if reported_user:
            reported_user.report_count = 0
            reported_user.total_amount = 0
            reported_user.risk_level = "safe"
            # 也可以直接删除该记录
            # db.delete(reported_user)

        # 更新申诉状态
        appeal.status = "approved"
        appeal.admin_response = response
        appeal.processed_by = admin_id
        appeal.processed_at = datetime.utcnow()

        db.commit()
        return True

    except Exception:
        db.rollback()
        return False

    finally:
        db.close()


def reject_appeal(appeal_id: int, admin_id: int, response: str = None) -> bool:
    """拒绝申诉"""
    db = SessionLocal()
    try:
        appeal = db.query(Appeal).filter(Appeal.id == appeal_id).first()
        if not appeal or appeal.status != "pending":
            return False

        appeal.status = "rejected"
        appeal.admin_response = response
        appeal.processed_by = admin_id
        appeal.processed_at = datetime.utcnow()

        db.commit()
        return True

    finally:
        db.close()


def get_user_appeals(user_id: int) -> List[Dict]:
    """获取用户的申诉历史"""
    db = SessionLocal()
    try:
        appeals = db.query(Appeal).filter(
            Appeal.user_id == user_id
        ).order_by(Appeal.created_at.desc()).all()

        return [
            {
                "id": a.id,
                "target_username": a.target_username,
                "reason": a.reason,
                "status": a.status,
                "admin_response": a.admin_response,
                "created_at": a.created_at,
                "processed_at": a.processed_at
            }
            for a in appeals
        ]

    finally:
        db.close()
