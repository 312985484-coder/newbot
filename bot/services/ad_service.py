"""
广告服务
"""

import random
from datetime import datetime
from typing import List, Dict, Optional

from bot.database.connection import SessionLocal
from bot.database.models import Advertisement
from bot.config import settings


async def get_ad_display() -> str:
    """获取广告展示文本"""
    db = SessionLocal()
    try:
        # 获取置顶广告
        pinned_ads = db.query(Advertisement).filter(
            Advertisement.type == "pinned",
            Advertisement.status == "active",
            (Advertisement.expires_at.is_(None)) | (Advertisement.expires_at > datetime.utcnow())
        ).order_by(Advertisement.priority.desc()).limit(settings.pinned_ad_count).all()

        # 获取随机广告
        random_ads = db.query(Advertisement).filter(
            Advertisement.type == "random",
            Advertisement.status == "active",
            (Advertisement.expires_at.is_(None)) | (Advertisement.expires_at > datetime.utcnow())
        ).all()

        # 随机选取
        selected_random = random.sample(
            random_ads,
            min(settings.random_ad_count, len(random_ads))
        )

        # 增加浏览计数
        for ad in pinned_ads:
            ad.views += 1
        for ad in selected_random:
            ad.views += 1
        db.commit()

        # 构建广告文本
        ads_text = build_ads_text(pinned_ads, selected_random)
        return ads_text

    finally:
        db.close()


def build_ads_text(pinned_ads: List, random_ads: List) -> str:
    """构建广告文本"""
    lines = ["\n━━━━━━━━━━━━━━━━━━━━", "📢 <b>广告</b>", ""]

    # 置顶广告
    for ad in pinned_ads:
        lines.append(f"📌 {ad.title}")
        lines.append(ad.content)
        if ad.link_url:
            lines.append(f"🔗 {ad.link_text}: {ad.link_url}")
        lines.append("")

    # 随机广告
    for ad in random_ads:
        lines.append(f"🎯 {ad.title}")
        lines.append(ad.content)
        if ad.link_url:
            lines.append(f"🔗 {ad.link_text}: {ad.link_url}")
        lines.append("")

    lines.append(f"💰 广告投放联系：{settings.admin_contact}")
    lines.append("")

    return "\n".join(lines)


def create_advertisement(
    title: str,
    content: str,
    ad_type: str = "random",
    image_url: str = None,
    link_url: str = None,
    link_text: str = "查看详情",
    priority: int = 5,
    created_by: int = None,
    expires_at: datetime = None
) -> Dict:
    """创建广告"""
    import uuid

    db = SessionLocal()
    try:
        ad_id = str(uuid.uuid4())

        ad = Advertisement(
            id=ad_id,
            title=title,
            content=content,
            image_url=image_url,
            link_url=link_url,
            link_text=link_text,
            type=ad_type,
            priority=priority,
            status="active",
            created_by=created_by,
            expires_at=expires_at
        )
        db.add(ad)
        db.commit()

        return {
            "success": True,
            "ad_id": ad_id,
            "message": "广告创建成功"
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        db.close()


def update_advertisement(ad_id: str, **kwargs) -> bool:
    """更新广告"""
    db = SessionLocal()
    try:
        ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
        if not ad:
            return False

        for key, value in kwargs.items():
            if hasattr(ad, key):
                setattr(ad, key, value)

        db.commit()
        return True

    except Exception:
        db.rollback()
        return False

    finally:
        db.close()


def delete_advertisement(ad_id: str) -> bool:
    """删除广告"""
    db = SessionLocal()
    try:
        ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
        if not ad:
            return False

        ad.status = "deleted"
        db.commit()
        return True

    except Exception:
        db.rollback()
        return False

    finally:
        db.close()


def get_all_ads(include_deleted: bool = False) -> List[Dict]:
    """获取所有广告"""
    db = SessionLocal()
    try:
        query = db.query(Advertisement)
        if not include_deleted:
            query = query.filter(Advertisement.status != "deleted")

        ads = query.order_by(Advertisement.created_at.desc()).all()

        return [
            {
                "id": ad.id,
                "title": ad.title,
                "content": ad.content,
                "type": ad.type,
                "status": ad.status,
                "priority": ad.priority,
                "views": ad.views,
                "clicks": ad.clicks,
                "created_at": ad.created_at,
                "expires_at": ad.expires_at
            }
            for ad in ads
        ]

    finally:
        db.close()


def record_ad_click(ad_id: str) -> bool:
    """记录广告点击"""
    db = SessionLocal()
    try:
        ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
        if ad:
            ad.clicks += 1
            db.commit()
            return True
        return False

    except Exception:
        db.rollback()
        return False

    finally:
        db.close()
