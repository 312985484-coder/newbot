"""
管理后台认证模块
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, Blueprint, request, jsonify, current_app
import jwt
from jwt import PyJWTError

# 创建 auth 蓝图
auth_bp = Blueprint('auth', __name__)

# 存储活跃 token（生产环境应使用 Redis）
active_tokens = {}


def hash_password(password: str) -> str:
    """密码哈希"""
    salt = "telegreat_admin_salt"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed


def create_token(admin_id: int, username: str) -> str:
    """创建 JWT Token"""
    payload = {
        "admin_id": admin_id,
        "username": username,
        "exp": datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        "iat": datetime.utcnow(),
        "jti": secrets.token_hex(16)  # JWT ID
    }
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm="HS256"
    )
    active_tokens[payload['jti']] = payload
    return token


def revoke_token(jti: str) -> bool:
    """撤销 Token"""
    if jti in active_tokens:
        del active_tokens[jti]
        return True
    return False


def token_required(f):
    """Token 验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({"error": "未提供认证令牌"}), 401

        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=["HS256"]
            )
            # 检查 token 是否已撤销
            if payload['jti'] not in active_tokens:
                return jsonify({"error": "令牌已失效"}), 401

            request.admin_id = payload['admin_id']
            request.admin_username = payload['username']
            request.token_jti = payload['jti']

        except PyJWTError as e:
            return jsonify({"error": f"无效的令牌: {str(e)}"}), 401

        return f(*args, **kwargs)

    return decorated


def init_auth(app: Flask):
    """初始化认证"""
    @app.before_request
    def check_ip():
        """IP 黑名单检查（可选）"""
        pass


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "需要登录"}), 401
        return f(*args, **kwargs)
    return decorated


# ============== Auth Routes ==============

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """登录接口"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "请提供用户名和密码"}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400
    
    # 验证用户名和密码
    admin_username = current_app.config.get('ADMIN_USERNAME')
    admin_password = current_app.config.get('ADMIN_PASSWORD')
    
    # 简单验证（生产环境应使用数据库存储）
    if username == admin_username and password == admin_password:
        admin_id = 1  # 固定管理员 ID
        token = create_token(admin_id, username)
        
        return jsonify({
            "success": True,
            "token": token,
            "username": username
        })
    
    return jsonify({"error": "用户名或密码错误"}), 401


@auth_bp.route('/api/auth/logout', methods=['POST'])
@token_required
def logout():
    """登出接口"""
    jti = request.token_jti
    revoke_token(jti)
    return jsonify({"success": True, "message": "已退出登录"})


@auth_bp.route('/api/auth/verify', methods=['GET'])
@token_required
def verify():
    """验证 Token"""
    return jsonify({
        "success": True,
        "admin_id": request.admin_id,
        "username": request.admin_username
    })

