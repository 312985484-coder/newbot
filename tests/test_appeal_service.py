"""
申诉服务测试
"""

import pytest
from datetime import datetime

from bot.database.connection import SessionLocal, Base, engine
from bot.database.models import User, Appeal
from bot.services.appeal_service import (
    create_appeal,
    get_pending_appeals,
    approve_appeal,
    reject_appeal
)


@pytest.fixture(scope="module")
def db():
    """创建测试数据库"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


class TestAppealCreation:
    """申诉创建测试"""

    def test_create_appeal_success(self, db):
        """测试成功创建申诉"""
        result = create_appeal(
            user_id=123456789,
            target_user_id=987654321,
            target_username="wrongly_reported",
            reason="这是错误的举报，我没有诈骗"
        )
        assert result["success"] is True
        assert "appeal_id" in result


class TestAppealProcessing:
    """申诉处理测试"""

    def test_get_pending_appeals(self, db):
        """测试获取待处理申诉"""
        result = get_pending_appeals()
        assert "appeals" in result
        assert "total" in result
        assert "page" in result
