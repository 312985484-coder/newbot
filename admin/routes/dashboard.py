"""
管理后台主路由
"""

from flask import Blueprint, request, jsonify

from admin.auth import token_required
from admin.routes.stats import get_dashboard_stats
from admin.routes.users import (
    get_users, get_user_detail, update_user,
    search_users, get_user_api_keys
)
from admin.routes.reports import (
    get_reports, get_report_detail, approve_report, reject_report
)
from admin.routes.appeals import (
    get_appeals, get_appeal_detail, approve_appeal, reject_appeal
)
from admin.routes.api_keys import (
    generate_api_keys, get_api_keys, revoke_api_key, delete_api_key
)
from admin.routes.ads import (
    get_ads, create_ad, update_ad, delete_ad, toggle_ad
)
from admin.routes.broadcast import send_broadcast

admin_bp = Blueprint('admin', __name__)


# ==================== 仪表盘 ====================

@admin_bp.route('/dashboard', methods=['GET'])
@token_required
def dashboard():
    """获取仪表盘数据"""
    stats = get_dashboard_stats()
    return jsonify(stats)


# ==================== 用户管理 ====================

@admin_bp.route('/users', methods=['GET'])
@token_required
def list_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')

    result = get_users(page, per_page, search)
    return jsonify(result)


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def user_detail(user_id):
    """获取用户详情"""
    detail = get_user_detail(user_id)
    if not detail:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify(detail)


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def user_update(user_id):
    """更新用户"""
    data = request.get_json()
    result = update_user(user_id, data)
    if not result:
        return jsonify({"error": "更新失败"}), 400
    return jsonify(result)


@admin_bp.route('/users/search', methods=['GET'])
@token_required
def search_users_route():
    """搜索用户"""
    keyword = request.args.get('q', '')
    result = search_users(keyword)
    return jsonify(result)


@admin_bp.route('/users/<int:user_id>/api-keys', methods=['GET'])
@token_required
def user_api_keys(user_id):
    """获取用户的 API Keys"""
    keys = get_user_api_keys(user_id)
    return jsonify(keys)


# ==================== 举报管理 ====================

@admin_bp.route('/reports', methods=['GET'])
@token_required
def list_reports():
    """获取举报列表"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'pending')

    result = get_reports(page, 20, status)
    return jsonify(result)


@admin_bp.route('/reports/<report_id>', methods=['GET'])
@token_required
def report_detail(report_id):
    """获取举报详情"""
    detail = get_report_detail(report_id)
    if not detail:
        return jsonify({"error": "举报不存在"}), 404
    return jsonify(detail)


@admin_bp.route('/reports/<report_id>/approve', methods=['POST'])
@token_required
def report_approve(report_id):
    """通过举报"""
    result = approve_report(report_id, request.admin_id)
    if not result:
        return jsonify({"error": "操作失败"}), 400
    return jsonify({"success": True, "message": "举报已通过"})


@admin_bp.route('/reports/<report_id>/reject', methods=['POST'])
@token_required
def report_reject(report_id):
    """拒绝举报"""
    data = request.get_json() or {}
    reason = data.get('reason', '')
    result = reject_report(report_id, request.admin_id, reason)
    if not result:
        return jsonify({"error": "操作失败"}), 400
    return jsonify({"success": True, "message": "举报已拒绝"})


# ==================== 申诉管理 ====================

@admin_bp.route('/appeals', methods=['GET'])
@token_required
def list_appeals():
    """获取申诉列表"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'pending')

    result = get_appeals(page, 20, status)
    return jsonify(result)


@admin_bp.route('/appeals/<appeal_id>', methods=['GET'])
@token_required
def appeal_detail(appeal_id):
    """获取申诉详情"""
    detail = get_appeal_detail(appeal_id)
    if not detail:
        return jsonify({"error": "申诉不存在"}), 404
    return jsonify(detail)


@admin_bp.route('/appeals/<appeal_id>/approve', methods=['POST'])
@token_required
def appeal_approve(appeal_id):
    """通过申诉"""
    data = request.get_json() or {}
    response = data.get('response', '')
    result = approve_appeal(appeal_id, request.admin_id, response)
    if not result:
        return jsonify({"error": "操作失败"}), 400
    return jsonify({"success": True, "message": "申诉已通过"})


@admin_bp.route('/appeals/<appeal_id>/reject', methods=['POST'])
@token_required
def appeal_reject(appeal_id):
    """拒绝申诉"""
    data = request.get_json() or {}
    response = data.get('response', '')
    result = reject_appeal(appeal_id, request.admin_id, response)
    if not result:
        return jsonify({"error": "操作失败"}), 400
    return jsonify({"success": True, "message": "申诉已拒绝"})


# ==================== API Key 管理 ====================

@admin_bp.route('/api-keys/generate', methods=['POST'])
@token_required
def generate_keys():
    """批量生成 API Keys"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请提供参数"}), 400

    count = data.get('count', 10)
    expires_days = data.get('expires_days', 365)
    bind_user_id = data.get('bind_user_id')

    result = generate_api_keys(request.admin_id, count, expires_days, bind_user_id)
    return jsonify(result)


@admin_bp.route('/api-keys', methods=['GET'])
@token_required
def list_api_keys():
    """获取 API Keys 列表"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')

    result = get_api_keys(page, 20, status)
    return jsonify(result)


@admin_bp.route('/api-keys/<key_id>/revoke', methods=['POST'])
@token_required
def revoke_key(key_id):
    """吊销 API Key"""
    result = revoke_api_key(key_id)
    if not result:
        return jsonify({"error": "吊销失败"}), 400
    return jsonify({"success": True, "message": "API Key 已吊销"})


@admin_bp.route('/api-keys/<key_id>', methods=['DELETE'])
@token_required
def delete_key(key_id):
    """删除 API Key"""
    result = delete_api_key(key_id)
    if not result:
        return jsonify({"error": "删除失败"}), 400
    return jsonify({"success": True, "message": "API Key 已删除"})


# ==================== 广告管理 ====================

@admin_bp.route('/ads', methods=['GET'])
@token_required
def list_ads():
    """获取广告列表"""
    result = get_ads()
    return jsonify(result)


@admin_bp.route('/ads', methods=['POST'])
@token_required
def create_advertisement():
    """创建广告"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请提供广告内容"}), 400

    result = create_ad(data, request.admin_id)
    if not result.get('success'):
        return jsonify(result), 400
    return jsonify(result)


@admin_bp.route('/ads/<ad_id>', methods=['PUT'])
@token_required
def update_advertisement(ad_id):
    """更新广告"""
    data = request.get_json()
    result = update_ad(ad_id, data)
    if not result:
        return jsonify({"error": "更新失败"}), 400
    return jsonify(result)


@admin_bp.route('/ads/<ad_id>', methods=['DELETE'])
@token_required
def delete_advertisement(ad_id):
    """删除广告"""
    result = delete_ad(ad_id)
    if not result:
        return jsonify({"error": "删除失败"}), 400
    return jsonify({"success": True, "message": "广告已删除"})


@admin_bp.route('/ads/<ad_id>/toggle', methods=['POST'])
@token_required
def toggle_advertisement(ad_id):
    """切换广告状态"""
    result = toggle_ad(ad_id)
    if not result:
        return jsonify({"error": "操作失败"}), 400
    return jsonify(result)


# ==================== 广播 ====================

@admin_bp.route('/broadcast', methods=['POST'])
@token_required
def broadcast_message():
    """广播消息"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请提供消息内容"}), 400

    message = data.get('message')
    if not message:
        return jsonify({"error": "消息内容不能为空"}), 400

    result = send_broadcast(message)
    return jsonify(result)
