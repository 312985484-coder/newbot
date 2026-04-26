"""
批量 API Key 生成模块
"""

import secrets
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from bot.database.connection import SessionLocal
from bot.database.models import User, ApiKey
from bot.config import settings


def generate_api_key() -> str:
    """生成单个 API Key"""
    return secrets.token_hex(32)


def batch_generate_api_keys(
    user_id: int,
    count: int = 10,
    expires_days: int = 365
) -> Dict:
    """
    批量生成 API Keys

    Args:
        user_id: 管理员用户ID
        count: 生成数量
        expires_days: 过期天数

    Returns:
        包含生成的Keys列表和统计信息
    """
    if count < 1 or count > 100:
        return {
            "success": False,
            "error": "数量必须在 1-100 之间"
        }

    db = SessionLocal()
    try:
        generated_keys = []
        expires_at = datetime.utcnow() + timedelta(days=expires_days)

        for _ in range(count):
            api_key = generate_api_key()
            key_id = str(uuid.uuid4())

            new_key = ApiKey(
                id=key_id,
                user_id=user_id,
                api_key=api_key,
                status="active",
                expires_at=expires_at
            )
            db.add(new_key)
            generated_keys.append(api_key)

        db.commit()

        return {
            "success": True,
            "count": count,
            "keys": generated_keys,
            "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"成功生成 {count} 个 API Key"
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        db.close()


def batch_generate_api_keys_with_users(
    admin_id: int,
    key_count: int = 10,
    expires_days: int = 365,
    bind_users: bool = False,
    user_ids: List[int] = None
) -> Dict:
    """
    批量生成 API Keys 并可选绑定用户

    Args:
        admin_id: 管理员ID
        key_count: 生成数量
        expires_days: 过期天数
        bind_users: 是否绑定到指定用户
        user_ids: 要绑定的用户ID列表

    Returns:
        生成结果
    """
    db = SessionLocal()
    try:
        generated = []
        expires_at = datetime.utcnow() + timedelta(days=expires_days)

        # 如果需要绑定用户
        if bind_users and user_ids:
            for user_id in user_ids[:key_count]:
                # 检查用户是否存在
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    continue

                api_key = generate_api_key()
                key_id = str(uuid.uuid4())

                new_key = ApiKey(
                    id=key_id,
                    user_id=user_id,
                    api_key=api_key,
                    status="active",
                    expires_at=expires_at
                )
                db.add(new_key)

                # 更新用户的密钥状态
                user.api_key = api_key
                user.key_status = "active"
                user.key_expires_at = expires_at

                generated.append({
                    "user_id": user_id,
                    "username": user.username,
                    "api_key": api_key
                })
        else:
            # 只生成Keys，不绑定用户
            for _ in range(key_count):
                api_key = generate_api_key()
                key_id = str(uuid.uuid4())

                new_key = ApiKey(
                    id=key_id,
                    user_id=0,  # 未分配
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
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        db.close()


def get_all_unused_api_keys() -> List[Dict]:
    """获取所有未使用的 API Keys"""
    db = SessionLocal()
    try:
        keys = db.query(ApiKey).filter(
            ApiKey.user_id == 0,
            ApiKey.status == "active"
        ).all()

        return [
            {
                "id": key.id,
                "api_key": key.api_key,
                "status": key.status,
                "expires_at": key.expires_at.strftime("%Y-%m-%d %H:%M:%S") if key.expires_at else None,
                "created_at": key.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for key in keys
        ]

    finally:
        db.close()


def get_api_keys_by_user(user_id: int) -> List[Dict]:
    """获取用户的所有 API Keys"""
    db = SessionLocal()
    try:
        keys = db.query(ApiKey).filter(
            ApiKey.user_id == user_id
        ).all()

        return [
            {
                "id": key.id,
                "api_key": key.api_key,
                "status": key.status,
                "request_count": key.request_count,
                "expires_at": key.expires_at.strftime("%Y-%m-%d %H:%M:%S") if key.expires_at else None,
                "created_at": key.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for key in keys
        ]

    finally:
        db.close()


def revoke_api_key(key_id: str) -> bool:
    """吊销单个 API Key"""
    db = SessionLocal()
    try:
        key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
        if key:
            key.status = "revoked"
            db.commit()
            return True
        return False

    except Exception:
        db.rollback()
        return False

    finally:
        db.close()


def revoke_expired_keys() -> int:
    """清理过期 Keys"""
    db = SessionLocal()
    try:
        expired_keys = db.query(ApiKey).filter(
            ApiKey.expires_at < datetime.utcnow(),
            ApiKey.status == "active"
        ).all()

        count = 0
        for key in expired_keys:
            key.status = "expired"
            count += 1

        db.commit()
        return count

    except Exception:
        db.rollback()
        return 0

    finally:
        db.close()
