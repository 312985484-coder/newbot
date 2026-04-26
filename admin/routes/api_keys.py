"""
API Key 管理路由
"""

from datetime import datetime, timedelta

from bot.database.connection import SessionLocal
from bot.database.models import ApiKey, User
from bot.services.batch_key_service import generate_api_key


def generate_api_keys(admin_id: int, count: int = 10, expires_days: int = 365, bind_user_id: int = None):
    """批量生成 API Keys"""
    db = SessionLocal()
    try:
        if count < 1 or count > 100:
            return {"success": False, "error": "数量必须在 1-100 之间"}

        generated = []
        expires_at = datetime.utcnow() + timedelta(days=expires_days)

        if bind_user_id:
            # 绑定到指定用户
            user = db.query(User).filter(User.id == bind_user_id).first()
            if not user:
                return {"success": False, "error": "用户不存在"}

            api_key = generate_api_key()
            new_key = ApiKey(
                id=str(bind_user_id) + "_key",
                user_id=bind_user_id,
                api_key=api_key,
                status="active",
                expires_at=expires_at
            )
            db.add(new_key)

            # 更新用户
            user.api_key = api_key
            user.key_status = "active"
            user.key_expires_at = expires_at

            generated.append({
                "user_id": bind_user_id,
                "username": user.username,
                "api_key": api_key
            })
        else:
            # 生成未绑定 Keys
            for i in range(count):
                api_key = generate_api_key()
                new_key = ApiKey(
                    id=f"batch_{admin_id}_{i}_{datetime.utcnow().timestamp()}",
                    user_id=0,
                    api_key=api_key,
                    status="active",
                    expires_at=expires_at
                )
                db.add(new_key)
                generated.append({
                    "api_key": api_key
                })

        db.commit()

        return {
            "success": True,
            "count": len(generated),
            "items": generated,
            "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"成功生成 {len(generated)} 个 API Key"
        }

    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

    finally:
        db.close()


def get_api_keys(page: int = 1, per_page: int = 20, status: str = 'all'):
    """获取 API Keys 列表"""
    db = SessionLocal()
    try:
        query = db.query(ApiKey)

        if status != 'all':
            query = query.filter(ApiKey.status == status)

        total = query.count()
        keys = query.order_by(ApiKey.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

        result = []
        for key in keys:
            user = db.query(User).filter(User.id == key.user_id).first()
            result.append({
                "id": key.id,
                "user_id": key.user_id,
                "username": user.username if user else "未分配",
                "api_key": key.api_key,
                "status": key.status,
                "request_count": key.request_count,
                "expires_at": key.expires_at.strftime("%Y-%m-%d %H:%M") if key.expires_at else None,
                "created_at": key.created_at.strftime("%Y-%m-%d %H:%M") if key.created_at else None
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


def revoke_api_key(key_id: str):
    """吊销 API Key"""
    db = SessionLocal()
    try:
        key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
        if not key:
            return False

        key.status = "revoked"
        db.commit()
        return True

    except Exception:
        db.rollback()
        return False

    finally:
        db.close()


def delete_api_key(key_id: str):
    """删除 API Key"""
    db = SessionLocal()
    try:
        key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
        if not key:
            return False

        db.delete(key)
        db.commit()
        return True

    except Exception:
        db.rollback()
        return False

    finally:
        db.close()
