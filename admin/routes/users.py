"""
用户管理路由
"""

from datetime import datetime

from bot.database.connection import SessionLocal
from bot.database.models import User, ApiKey, Report


def get_users(page: int = 1, per_page: int = 20, search: str = ''):
    """获取用户列表"""
    db = SessionLocal()
    try:
        query = db.query(User)

        if search:
            query = query.filter(
                (User.username.contains(search)) |
                (User.first_name.contains(search)) |
                (User.id == int(search) if search.isdigit() else False)
            )

        total = query.count()
        users = query.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

        return {
            "success": True,
            "data": [user_to_dict(u) for u in users],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page if total > 0 else 1
            }
        }

    finally:
        db.close()


def get_user_detail(user_id: int):
    """获取用户详情"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # 获取用户的举报记录
        reports = db.query(Report).filter(Report.reporter_id == user_id).all()

        # 获取用户的 API Keys
        api_keys = db.query(ApiKey).filter(ApiKey.user_id == user_id).all()

        return {
            "success": True,
            "user": user_to_dict(user),
            "reports_count": len(reports),
            "api_keys": [key_to_dict(k) for k in api_keys],
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }

    finally:
        db.close()


def update_user(user_id: int, data: dict):
    """更新用户"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # 允许更新的字段
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        if 'is_super_admin' in data:
            user.is_super_admin = data['is_super_admin']
        if 'key_status' in data:
            user.key_status = data['key_status']
        if 'reputation_score' in data:
            user.reputation_score = data['reputation_score']
        if 'warning_count' in data:
            user.warning_count = data['warning_count']

        db.commit()

        return {
            "success": True,
            "message": "用户更新成功",
            "user": user_to_dict(user)
        }

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()


def search_users(keyword: str):
    """搜索用户"""
    db = SessionLocal()
    try:
        query = db.query(User)

        if keyword.isdigit():
            query = query.filter(User.id == int(keyword))
        else:
            query = query.filter(
                (User.username.contains(keyword)) |
                (User.first_name.contains(keyword))
            )

        users = query.limit(20).all()

        return {
            "success": True,
            "data": [user_to_dict(u) for u in users],
            "count": len(users)
        }

    finally:
        db.close()


def get_user_api_keys(user_id: int):
    """获取用户的 API Keys"""
    db = SessionLocal()
    try:
        keys = db.query(ApiKey).filter(ApiKey.user_id == user_id).all()

        return {
            "success": True,
            "data": [key_to_dict(k) for k in keys]
        }

    finally:
        db.close()


def user_to_dict(user: User) -> dict:
    """用户对象转字典"""
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "key_status": user.key_status,
        "total_reports": user.total_reports,
        "successful_reports": user.successful_reports,
        "reputation_score": user.reputation_score,
        "is_admin": user.is_admin,
        "is_super_admin": user.is_super_admin,
        "warning_count": user.warning_count,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else None
    }


def key_to_dict(key: ApiKey) -> dict:
    """API Key 对象转字典"""
    return {
        "id": key.id,
        "api_key": key.api_key,
        "status": key.status,
        "request_count": key.request_count,
        "expires_at": key.expires_at.strftime("%Y-%m-%d %H:%M") if key.expires_at else None,
        "created_at": key.created_at.strftime("%Y-%m-%d %H:%M") if key.created_at else None
    }
