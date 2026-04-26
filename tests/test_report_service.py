"""
举报服务测试
"""

import pytest
from datetime import datetime

from bot.database.connection import SessionLocal, Base, engine
from bot.database.models import User, Report
from bot.services.report_service import (
    generate_api_key,
    create_report,
    create_api_key,
    validate_api_key
)


@pytest.fixture(scope="module")
def db():
    """创建测试数据库"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    user = User(
        id=123456789,
        username="test_user",
        first_name="Test",
        last_name="User"
    )
    db.add(user)
    db.commit()
    return user


class TestApiKeyGeneration:
    """API Key 生成测试"""

    def test_generate_key_format(self):
        """测试 Key 格式"""
        key = generate_api_key()
        assert len(key) == 64
        assert all(c in '0123456789abcdef' for c in key)


class TestCreateReport:
    """创建举报测试"""

    def test_create_report_success(self, db, test_user):
        """测试成功创建举报"""
        result = create_report(
            reporter_id=test_user.id,
            target_username="scammer_user",
            target_user_id=987654321,
            amount=500.0,
            currency="USDT",
            description="测试举报内容"
        )
        assert result["success"] is True
        assert "report_id" in result

    def test_create_report_updates_user_stats(self, db, test_user):
        """测试创建举报更新用户统计"""
        initial_count = test_user.total_reports
        create_report(
            reporter_id=test_user.id,
            target_username="scammer2",
            description="测试"
        )
        db.refresh(test_user)
        assert test_user.total_reports == initial_count + 1
