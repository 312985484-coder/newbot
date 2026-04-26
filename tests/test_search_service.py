"""
搜索服务测试
"""

import pytest
from datetime import datetime

from bot.database.connection import SessionLocal, Base, engine
from bot.database.models import ReportedUser, Report
from bot.services.search_service import (
    calculate_risk_level,
    search_by_username,
    search_by_user_id,
    get_risk_level_display
)


@pytest.fixture(scope="module")
def db():
    """创建测试数据库"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


class TestRiskCalculation:
    """风险等级计算测试"""

    def test_safe_level(self):
        """测试安全等级"""
        assert calculate_risk_level(0, 0) == "safe"

    def test_low_risk(self):
        """测试低风险"""
        assert calculate_risk_level(1, 0) == "low"
        assert calculate_risk_level(2, 500) == "low"

    def test_medium_risk(self):
        """测试中风险"""
        assert calculate_risk_level(3, 0) == "medium"
        assert calculate_risk_level(1, 1000) == "medium"

    def test_high_risk(self):
        """测试高风险"""
        assert calculate_risk_level(5, 0) == "high"
        assert calculate_risk_level(1, 5000) == "high"


class TestRiskLevelDisplay:
    """风险等级显示测试"""

    def test_display_texts(self):
        """测试显示文本"""
        assert get_risk_level_display("safe") == "安全"
        assert get_risk_level_display("low") == "低风险"
        assert get_risk_level_display("medium") == "中风险"
        assert get_risk_level_display("high") == "高风险"


class TestSearchFunction:
    """搜索功能测试"""

    def test_search_nonexistent_user(self, db):
        """测试搜索不存在的用户"""
        result = db.query(ReportedUser).filter(
            ReportedUser.username == "nonexistent_user_12345"
        ).first()
        assert result is None
