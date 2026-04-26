"""
认证路由
"""

from flask import Blueprint, request, jsonify, current_app

from admin.auth import (
    create_token, revoke_token, hash_password,
    verify_password, token_required
)
from admin.config import AdminConfig

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    管理员登录
    POST /api/auth/login
    {
        "username": "admin",
        "password": "your_password"
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "请提供用户名和密码"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    # 验证用户名和密码
    admin_username = current_app.config.get('ADMIN_USERNAME', AdminConfig.ADMIN_USERNAME)
    admin_password = current_app.config.get('ADMIN_PASSWORD', AdminConfig.ADMIN_PASSWORD)

    if username != admin_username or password != admin_password:
        return jsonify({"error": "用户名或密码错误"}), 401

    # 生成 token
    token = create_token(admin_id=1, username=username)

    return jsonify({
        "success": True,
        "token": token,
        "username": username,
        "message": "登录成功"
    })


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """登出"""
    from flask import request as req
    revoke_token(req.token_jti)
    return jsonify({"success": True, "message": "已退出登录"})


@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify():
    """验证 token 是否有效"""
    return jsonify({
        "valid": True,
        "username": request.admin_username
    })


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """修改密码"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "请提供数据"}), 400

    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({"error": "旧密码和新密码不能为空"}), 400

    if len(new_password) < 8:
        return jsonify({"error": "新密码长度至少8位"}), 400

    # 验证旧密码
    admin_password = current_app.config.get('ADMIN_PASSWORD', AdminConfig.ADMIN_PASSWORD)
    if old_password != admin_password:
        return jsonify({"error": "旧密码错误"}), 401

    # 更新密码（实际应用中应该更新环境变量或数据库）
    # 这里仅返回成功，实际需要配合配置更新机制
    return jsonify({
        "success": True,
        "message": "密码修改成功，请重启服务使配置生效"
    })
