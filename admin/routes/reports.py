"""
举报管理路由
"""

from datetime import datetime

from bot.database.connection import SessionLocal
from bot.database.models import Report, User, ReportedUser
from bot.services.report_service import approve_report as service_approve, reject_report as service_reject


def get_reports(page: int = 1, per_page: int = 20, status: str = 'pending'):
    """获取举报列表"""
    db = SessionLocal()
    try:
        query = db.query(Report)

        if status != 'all':
            query = query.filter(Report.status == status)

        total = query.count()
        reports = query.order_by(Report.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

        # 获取举报者信息
        result = []
        for report in reports:
            reporter = db.query(User).filter(User.id == report.reporter_id).first()
            result.append({
                "id": report.id,
                "target_username": report.target_username,
                "target_user_id": report.target_user_id,
                "target_first_name": report.target_first_name,
                "amount": float(report.amount or 0),
                "currency": report.currency,
                "description": report.description,
                "status": report.status,
                "reporter": {
                    "id": reporter.id if reporter else None,
                    "username": reporter.username if reporter else None
                } if reporter else None,
                "created_at": report.created_at.strftime("%Y-%m-%d %H:%M") if report.created_at else None
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


def get_report_detail(report_id: str):
    """获取举报详情"""
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return None

        reporter = db.query(User).filter(User.id == report.reporter_id).first()

        return {
            "success": True,
            "report": {
                "id": report.id,
                "target_username": report.target_username,
                "target_user_id": report.target_user_id,
                "target_first_name": report.target_first_name,
                "target_last_name": report.target_last_name,
                "scam_time": report.scam_time.strftime("%Y-%m-%d %H:%M") if report.scam_time else None,
                "amount": float(report.amount or 0),
                "currency": report.currency,
                "description": report.description,
                "evidence_urls": report.evidence_urls or [],
                "status": report.status,
                "rejection_reason": report.rejection_reason,
                "approved_by": report.approved_by,
                "approved_at": report.approved_at.strftime("%Y-%m-%d %H:%M") if report.approved_at else None,
                "created_at": report.created_at.strftime("%Y-%m-%d %H:%M") if report.created_at else None,
                "reporter": {
                    "id": reporter.id if reporter else None,
                    "username": reporter.username if reporter else None,
                    "first_name": reporter.first_name if reporter else None
                } if reporter else None
            }
        }

    finally:
        db.close()


def approve_report(report_id: str, admin_id: int):
    """通过举报"""
    return service_approve(report_id, admin_id)


def reject_report(report_id: str, admin_id: int, reason: str = None):
    """拒绝举报"""
    return service_reject(report_id, admin_id, reason)
