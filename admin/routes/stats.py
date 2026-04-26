"""
统计数据路由
"""

from datetime import datetime, timedelta

from bot.database.connection import SessionLocal
from bot.database.models import User, Report, ReportedUser, Appeal, Advertisement, ApiKey


def get_dashboard_stats():
    """获取仪表盘统计数据"""
    db = SessionLocal()
    try:
        # 用户统计
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.key_status == 'active').count()

        # 举报统计
        total_reports = db.query(Report).count()
        pending_reports = db.query(Report).filter(Report.status == 'pending').count()
        approved_reports = db.query(Report).filter(Report.status == 'approved').count()
        rejected_reports = db.query(Report).filter(Report.status == 'rejected').count()

        # 申诉统计
        total_appeals = db.query(Appeal).count()
        pending_appeals = db.query(Appeal).filter(Appeal.status == 'pending').count()

        # 被举报用户统计
        reported_users = db.query(ReportedUser).count()
        high_risk_users = db.query(ReportedUser).filter(
            ReportedUser.risk_level == 'high'
        ).count()

        # API Keys 统计
        total_keys = db.query(ApiKey).count()
        active_keys = db.query(ApiKey).filter(ApiKey.status == 'active').count()

        # 广告统计
        total_ads = db.query(Advertisement).count()
        active_ads = db.query(Advertisement).filter(Advertisement.status == 'active').count()

        # 今日新增
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())

        today_new_users = db.query(User).filter(
            User.created_at >= today_start
        ).count()

        today_new_reports = db.query(Report).filter(
            Report.created_at >= today_start
        ).count()

        # 7天趋势数据
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_reports = db.query(Report).filter(
            Report.created_at >= week_ago
        ).count()

        # 累计涉案金额
        total_fraud_amount = db.query(ReportedUser.total_amount).all()
        total_amount = sum([float(r[0] or 0) for r in total_fraud_amount])

        return {
            "success": True,
            "stats": {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "today_new": today_new_users
                },
                "reports": {
                    "total": total_reports,
                    "pending": pending_reports,
                    "approved": approved_reports,
                    "rejected": rejected_reports,
                    "today_new": today_new_reports,
                    "weekly": weekly_reports
                },
                "appeals": {
                    "total": total_appeals,
                    "pending": pending_appeals
                },
                "reported_users": {
                    "total": reported_users,
                    "high_risk": high_risk_users
                },
                "api_keys": {
                    "total": total_keys,
                    "active": active_keys
                },
                "advertisements": {
                    "total": total_ads,
                    "active": active_ads
                },
                "finance": {
                    "total_fraud_amount": round(total_amount, 2)
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    finally:
        db.close()
