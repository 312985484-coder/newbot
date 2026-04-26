"""
举报服务
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
import uuid

from bot.database.connection import SessionLocal
from bot.database.models import Report, User, ReportedUser, ApiKey


def generate_api_key() -> str:
    """生成 API Key"""
    return secrets.token_hex(32)


def hash_api_key(api_key: str) -> str:
    """哈希 API Key"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def create_api_key(user_id: int, expires_days: int = 365) -> str:
    """为用户创建 API Key"""
    db = SessionLocal()
    try:
        api_key = generate_api_key()

        new_key = ApiKey(
            id=str(uuid.uuid4()),
            user_id=user_id,
            api_key=api_key,
            status="active",
            expires_at=datetime.utcnow() + timedelta(days=expires_days)
        )
        db.add(new_key)

        # 更新用户的密钥状态
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.api_key = api_key
            user.key_status = "active"
            user.key_expires_at = new_key.expires_at

        db.commit()
        return api_key

    finally:
        db.close()


def validate_api_key(api_key: str) -> bool:
    """验证 API Key"""
    if not api_key:
        return False

    db = SessionLocal()
    try:
        key_record = db.query(ApiKey).filter(
            ApiKey.api_key == api_key,
            ApiKey.status == "active"
        ).first()

        if not key_record:
            return False

        # 检查是否过期
        if key_record.expires_at and key_record.expires_at < datetime.utcnow():
            key_record.status = "expired"
            db.commit()
            return False

        # 增加请求计数
        key_record.request_count += 1
        db.commit()

        return True

    finally:
        db.close()


def revoke_api_key(api_key: str) -> bool:
    """吊销 API Key"""
    db = SessionLocal()
    try:
        key_record = db.query(ApiKey).filter(
            ApiKey.api_key == api_key
        ).first()

        if key_record:
            key_record.status = "revoked"
            db.commit()
            return True

        return False

    finally:
        db.close()


def create_report(
    reporter_id: int,
    target_username: str = None,
    target_user_id: int = None,
    target_first_name: str = None,
    target_last_name: str = None,
    scam_time: datetime = None,
    amount: float = 0,
    currency: str = "USDT",
    description: str = None,
    evidence_urls: list = None
) -> Dict:
    """创建举报记录"""
    db = SessionLocal()
    try:
        # 生成举报ID
        report_id = str(uuid.uuid4())

        # 创建举报记录
        report = Report(
            id=report_id,
            reporter_id=reporter_id,
            target_username=target_username,
            target_user_id=target_user_id,
            target_first_name=target_first_name,
            target_last_name=target_last_name,
            scam_time=scam_time,
            amount=amount,
            currency=currency,
            description=description,
            evidence_urls=evidence_urls or [],
            status="pending"
        )
        db.add(report)

        # 更新举报者的统计
        reporter = db.query(User).filter(User.id == reporter_id).first()
        if reporter:
            reporter.total_reports += 1

        db.commit()

        return {
            "success": True,
            "report_id": report_id,
            "message": "举报已提交，等待管理员审核"
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        db.close()


def get_pending_reports(page: int = 1, limit: int = 10) -> Dict:
    """获取待审核举报列表"""
    db = SessionLocal()
    try:
        offset = (page - 1) * limit

        reports = db.query(Report).filter(
            Report.status == "pending"
        ).order_by(Report.created_at.asc()).limit(limit).offset(offset).all()

        total = db.query(Report).filter(
            Report.status == "pending"
        ).count()

        return {
            "reports": [
                {
                    "id": r.id,
                    "target_username": r.target_username,
                    "target_user_id": r.target_user_id,
                    "amount": float(r.amount or 0),
                    "currency": r.currency,
                    "description": r.description,
                    "created_at": r.created_at
                }
                for r in reports
            ],
            "total": total,
            "page": page,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1
        }

    finally:
        db.close()


def approve_report(report_id: int, admin_id: int) -> bool:
    """审核通过举报"""
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report or report.status != "pending":
            return False

        report.status = "approved"
        report.approved_by = admin_id
        report.approved_at = datetime.utcnow()

        # 更新或创建 ReportedUser 记录
        reported_user = db.query(ReportedUser).filter(
            ReportedUser.user_id == report.target_user_id
        ).first()

        if reported_user:
            reported_user.report_count += 1
            reported_user.total_amount = float(reported_user.total_amount or 0) + float(report.amount or 0)
            reported_user.last_reported_at = datetime.utcnow()
            # 重新计算风险等级
            from bot.services.search_service import calculate_risk_level
            reported_user.risk_level = calculate_risk_level(
                reported_user.report_count,
                float(reported_user.total_amount)
            )
        else:
            from bot.services.search_service import calculate_risk_level
            new_reported = ReportedUser(
                user_id=report.target_user_id,
                username=report.target_username,
                first_name=report.target_first_name,
                last_name=report.target_last_name,
                report_count=1,
                total_amount=report.amount,
                risk_level=calculate_risk_level(1, float(report.amount or 0)),
                first_reported_at=datetime.utcnow(),
                last_reported_at=datetime.utcnow()
            )
            db.add(new_reported)

        # 更新举报者统计
        reporter = db.query(User).filter(User.id == report.reporter_id).first()
        if reporter:
            reporter.successful_reports += 1
            reporter.reputation_score += 10  # 奖励积分

        db.commit()
        return True

    except Exception:
        db.rollback()
        return False

    finally:
        db.close()


def reject_report(report_id: int, admin_id: int, reason: str = None) -> bool:
    """拒绝举报"""
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report or report.status != "pending":
            return False

        report.status = "rejected"
        report.rejection_reason = reason
        db.commit()
        return True

    except Exception:
        db.rollback()
        return False

    finally:
        db.close()
