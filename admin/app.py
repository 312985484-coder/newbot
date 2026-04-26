"""
Flask 管理后台应用
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS

from admin.routes import admin_bp
from admin.auth import auth_bp, init_auth
from admin.config import AdminConfig

app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
app.config.from_object(AdminConfig)

# 启用 CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 初始化认证
init_auth(app)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')


@app.route('/')
def index():
    """首页/仪表盘"""
    return render_template('dashboard.html')


@app.route('/login')
def login_page():
    """登录页"""
    return render_template('login.html')


@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "service": "telegreat-admin", "port": AdminConfig.PORT})


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host=AdminConfig.HOST, port=AdminConfig.PORT, debug=debug)
