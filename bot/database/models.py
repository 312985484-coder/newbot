"""
数据模型定义
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, BigInteger, Boolean, DateTime,
    Text, Numeric, JSON
)
from bot.database.connection import Base


def generate_uuid() -> str:
    """生成 UUID"""
    return str(uuid.uuid4())


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # Telegram User ID
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    api_key = Column(String(64), unique=True, nullable=True)
    key_status = Column(String(20), default="inactive")
    key_expires_at = Column(DateTime, nullable=True)
    total_reports = Column(Integer, default=0)
    successful_reports = Column(Integer, default=0)
    reputation_score = Column(Integer, default=100)
    is_admin = Column(Boolean, default=False)
    is_super_admin = Column(Boolean, default=False)
    warning_count = Column(Integer, default=0)
    banned_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Report(Base):
    """举报表"""
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    reporter_id = Column(BigInteger, nullable=False)
    target_username = Column(String(255), nullable=True)
    target_user_id = Column(BigInteger, nullable=True)
    target_first_name = Column(String(255), nullable=True)
    target_last_name = Column(String(255), nullable=True)
    scam_time = Column(DateTime, nullable=True)
    amount = Column(Numeric(18, 8), default=0)
    currency = Column(String(20), default="USDT")
    description = Column(Text, nullable=False)
    evidence_urls = Column(JSON, default=list)
    status = Column(String(20), default="pending")
    rejection_reason = Column(Text, nullable=True)
    approved_by = Column(BigInteger, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReportedUser(Base):
    """被举报用户汇总表"""
    __tablename__ = "reported_users"

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    report_count = Column(Integer, default=0)
    total_amount = Column(Numeric(18, 8), default=0)
    risk_level = Column(String(20), default="safe")
    first_reported_at = Column(DateTime, nullable=True)
    last_reported_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Appeal(Base):
    """申诉表"""
    __tablename__ = "appeals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(BigInteger, nullable=False)
    target_user_id = Column(BigInteger, nullable=True)
    target_username = Column(String(255), nullable=True)
    reason = Column(Text, nullable=False)
    evidence_urls = Column(JSON, default=list)
    status = Column(String(20), default="pending")
    admin_response = Column(Text, nullable=True)
    processed_by = Column(BigInteger, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Advertisement(Base):
    """广告表"""
    __tablename__ = "advertisements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    link_url = Column(String(500), nullable=True)
    link_text = Column(String(100), default="查看详情")
    type = Column(String(20), default="random")
    priority = Column(Integer, default=5)
    status = Column(String(20), default="active")
    views = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    created_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


class GroupSettings(Base):
    """群组设置表"""
    __tablename__ = "group_settings"

    chat_id = Column(BigInteger, primary_key=True)
    chat_title = Column(String(255), nullable=True)
    welcome_message = Column(Text, nullable=True)
    welcome_enabled = Column(Boolean, default=True)
    antispam_enabled = Column(Boolean, default=True)
    security_level = Column(String(20), default="medium")
    auto_mute_reported_users = Column(Boolean, default=True)
    muted_keywords = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApiKey(Base):
    """API密钥表"""
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(BigInteger, nullable=False)
    api_key = Column(String(64), unique=True, nullable=False)
    status = Column(String(20), default="active")
    request_count = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)