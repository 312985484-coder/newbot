"""
管理后台路由模块
"""

from admin.routes.dashboard import admin_bp
from admin.routes.auth import auth_bp

__all__ = ['admin_bp', 'auth_bp']

