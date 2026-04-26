"""
配置管理模块
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Settings(BaseSettings):
    """机器人配置"""

    # Telegram 配置
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")

    # 管理员配置
    admin_user_ids: str = Field(default="", alias="ADMIN_USER_IDS")
    super_admin_user_ids: str = Field(default="", alias="SUPER_ADMIN_USER_IDS")

    # 服务器配置
    bot_host: str = Field(default="0.0.0.0", alias="BOT_HOST")
    bot_port: int = Field(default=801, alias="BOT_PORT")

    # 数据库配置
    database_url: str = Field(default="sqlite:///telegreat.db", alias="DATABASE_URL")

    # 安全配置
    api_key_secret: str = Field(default="", alias="API_KEY_SECRET")

    # Redis 配置（可选）
    redis_url: str = Field(default="", alias="REDIS_URL")

    # 日志配置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="telegreat.log", alias="LOG_FILE")

    # 广告配置
    pinned_ad_count: int = 2
    random_ad_count: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_admin_ids(self) -> list[int]:
        """获取管理员 ID 列表"""
        if not self.admin_user_ids:
            return []
        return [int(id.strip()) for id in self.admin_user_ids.split(",") if id.strip()]

    def get_super_admin_ids(self) -> list[int]:
        """获取超级管理员 ID 列表"""
        if not self.super_admin_user_ids:
            return []
        return [int(id.strip()) for id in self.super_admin_user_ids.split(",") if id.strip()]


# 全局配置实例
settings = Settings()
