"""
广告管理路由
"""

from datetime import datetime, timedelta

from bot.database.connection import SessionLocal
from bot.database.models import Advertisement
import uuid


def get_ads():
    """获取广告列表"""
    db = SessionLocal()
    try:
        ads = db.query(Advertisement).order_by(Advertisement.created_at.desc()).all()

        return {
            "success": True,
            "data": [ad_to_dict(ad) for ad in ads]
        }

    finally:
        db.close()


def create_ad(data: dict, admin_id: int):
    """创建广告"""
    db = SessionLocal()
    try:
        title = data.get('title')
        content = data.get('content')
        ad_type = data.get('type', 'random')

        if not title or not content:
            return {"success": False, "error": "标题和内容不能为空"}

        # 检查置顶广告数量
        if ad_type == 'pinned':
            pinned_count = db.query(Advertisement).filter(
                Advertisement.type == 'pinned',
                Advertisement.status == 'active'
            ).count()
            if pinned_count >= 2:
                return {"success": False, "error": "置顶广告位已满（最多2个）"}

        ad = Advertisement(
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            image_url=data.get('image_url'),
            link_url=data.get('link_url'),
            link_text=data.get('link_text', '查看详情'),
            type=ad_type,
            priority=data.get('priority', 5),
            status='active',
            created_by=admin_id,
            expires_at=datetime.strptime(data['expires_at'], '%Y-%m-%d') if data.get('expires_at') else None
        )

        db.add(ad)
        db.commit()

        return {
            "success": True,
            "message": "广告创建成功",
            "ad": ad_to_dict(ad)
        }

    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

    finally:
        db.close()


def update_ad(ad_id: str, data: dict):
    """更新广告"""
    db = SessionLocal()
    try:
        ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
        if not ad:
            return None

        if 'title' in data:
            ad.title = data['title']
        if 'content' in data:
            ad.content = data['content']
        if 'image_url' in data:
            ad.image_url = data['image_url']
        if 'link_url' in data:
            ad.link_url = data['link_url']
        if 'link_text' in data:
            ad.link_text = data['link_text']
        if 'priority' in data:
            ad.priority = data['priority']
        if 'type' in data:
            ad.type = data['type']
        if 'expires_at' in data and data['expires_at']:
            ad.expires_at = datetime.strptime(data['expires_at'], '%Y-%m-%d')

        db.commit()
        return {"success": True, "ad": ad_to_dict(ad)}

    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

    finally:
        db.close()


def delete_ad(ad_id: str):
    """删除广告"""
    db = SessionLocal()
    try:
        ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
        if not ad:
            return False

        ad.status = 'deleted'
        db.commit()
        return True

    except Exception:
        db.rollback()
        return False

    finally:
        db.close()


def toggle_ad(ad_id: str):
    """切换广告状态"""
    db = SessionLocal()
    try:
        ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
        if not ad:
            return False

        ad.status = 'paused' if ad.status == 'active' else 'active'
        db.commit()

        return {
            "success": True,
            "status": ad.status,
            "message": f"广告已{'暂停' if ad.status == 'paused' else '启用'}"
        }

    except Exception:
        db.rollback()
        return False

    finally:
        db.close()


def ad_to_dict(ad: Advertisement) -> dict:
    """广告对象转字典"""
    return {
        "id": ad.id,
        "title": ad.title,
        "content": ad.content,
        "image_url": ad.image_url,
        "link_url": ad.link_url,
        "link_text": ad.link_text,
        "type": ad.type,
        "priority": ad.priority,
        "status": ad.status,
        "views": ad.views,
        "clicks": ad.clicks,
        "expires_at": ad.expires_at.strftime("%Y-%m-%d") if ad.expires_at else None,
        "created_at": ad.created_at.strftime("%Y-%m-%d %H:%M") if ad.created_at else None
    }
