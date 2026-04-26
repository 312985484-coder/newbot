"""
管理后台配置
"""

import os
from datetime import timedelta


class AdminConfig:
    """管理后台配置"""

    # 服务器配置
    HOST = os.environ.get('ADMIN_HOST', '0.0.0.0')
    PORT = int(os.environ.get('ADMIN_PORT', 811))

    # 密钥配置
    SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', 'your-super-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

    # 会话配置
    SESSION_COOKIE_SECURE = os.environ.get('HTTPS_ENABLED', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # 管理员账号配置
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change-me-in-production')

    # 速率限制
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_HEADERS_ENABLED = True
