"""
申诉管理路由
"""

from datetime import datetime

from bot.database.connection import SessionLocal
from bot.database.models import Appeal, User
from bot.services.appeal_service import (
    approve_appeal as service_approve,
    reject_appeal as service_reject
)


def get_appeals(page: int = 1, per_page: int = 20, status: str = 'pending'):
    """获取申诉列表"""
    db = SessionLocal()
    try:
        query = db.query(Appeal)

        if status != 'all':
            query = query.filter(Appeal.status == status)

        total = query.count()
        appeals = query.order_by(Appeal.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

        result = []
        for appeal in appeals:
            user = db.query(User).filter(User.id == appeal.user_id).first()
            result.append({
                "id": appeal.id,
                "target_username": appeal.target_username,
                "target_user_id": appeal.target_user_id,
                "reason": appeal.reason[:100] + "..." if len(appeal.reason) > 100 else appeal.reason,
                "status": appeal.status,
                "user": {
                    "id": user.id if user else None,
                    "username": user.username if user else None
                } if user else None,
                "created_at": appeal.created_at.strftime("%Y-%m-%d %H:%M") if appeal.created_at else None
            })

        return {
            "success": True,
            "data": result,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page if total > 0 else 1
            }
        }

    finally:
        db.close()


def get_appeal_detail(appeal_id: str):
    """获取申诉详情"""
    db = SessionLocal()
    try:
        appeal = db.query(Appeal).filter(Appeal.id == appeal_id).first()
        if not appeal:
            return None

        user = db.query(User).filter(User.id == appeal.user_id).first()

        return {
            "success": True,
            "appeal": {
                "id": appeal.id,
                "target_username": appeal.target_username,
                "target_user_id": appeal.target_user_id,
                "reason": appeal.reason,
                "evidence_urls": appeal.evidence_urls or [],
                "status": appeal.status,
                "admin_response": appeal.admin_response,
                "processed_by": appeal.processed_by,
                "processed_at": appeal.processed_at.strftime("%Y-%m-%d %H:%M") if appeal.processed_at else None,
                "created_at": appeal.created_at.strftime("%Y-%m-%d %H:%M") if appeal.created_at else None,
                "user": {
                    "id": user.id if user else None,
                    "username": user.username if user else None,
                    "first_name": user.first_name if user else None
                } if user else None
            }
        }

    finally:
        db.close()


def approve_appeal(appeal_id: str, admin_id: int, response: str = None):
    """通过申诉"""
    return service_approve(appeal_id, admin_id, response)


def reject_appeal(appeal_id: str, admin_id: int, response: str = None):
    """拒绝申诉"""
    return service_reject(appeal_id, admin_id, response)
