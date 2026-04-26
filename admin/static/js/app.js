/**
 * TeleGreat Admin Panel - JavaScript
 */

const API_BASE = '/api';
let authToken = localStorage.getItem('admin_token');

// ==================== 认证 ====================

async function login(username, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    if (data.token) {
        localStorage.setItem('admin_token', data.token);
        authToken = data.token;
        return true;
    }
    throw new Error(data.error || '登录失败');
}

function logout() {
    localStorage.removeItem('admin_token');
    authToken = null;
    window.location.href = '/login';
}

async function verifyToken() {
    if (!authToken) return false;
    try {
        const response = await fetch(`${API_BASE}/auth/verify`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        return response.ok;
    } catch {
        return false;
    }
}

async function apiRequest(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
        ...options.headers
    };

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || '请求失败');
    }
    return data;
}

// ==================== 登录页面 ====================

function initLoginPage() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorEl = document.getElementById('loginError');

        try {
            await login(username, password);
            window.location.href = '/';
        } catch (err) {
            errorEl.textContent = err.message;
            errorEl.style.display = 'block';
        }
    });
}

// ==================== 仪表盘 ====================

async function loadDashboard() {
    try {
        const data = await apiRequest('/admin/dashboard');
        renderDashboard(data.stats);
    } catch (err) {
        console.error('加载仪表盘失败:', err);
    }
}

function renderDashboard(stats) {
    // 用户统计
    document.getElementById('totalUsers').textContent = stats.users.total;
    document.getElementById('activeUsers').textContent = stats.users.active;

    // 举报统计
    document.getElementById('totalReports').textContent = stats.reports.total;
    document.getElementById('pendingReports').textContent = stats.reports.pending;

    // 申诉统计
    document.getElementById('totalAppeals').textContent = stats.appeals.total;
    document.getElementById('pendingAppeals').textContent = stats.appeals.pending;

    // 被举报用户
    document.getElementById('reportedUsers').textContent = stats.reported_users.total;
    document.getElementById('highRiskUsers').textContent = stats.reported_users.high_risk;

    // 金额
    document.getElementById('totalAmount').textContent = stats.finance.total_fraud_amount.toLocaleString();
}

// ==================== 举报管理 ====================

let reportsPage = 1;

async function loadReports(status = 'pending') {
    try {
        const data = await apiRequest(`/admin/reports?status=${status}&page=${reportsPage}`);
        renderReportsTable(data.data);
        renderPagination(data.pagination);
    } catch (err) {
        console.error('加载举报失败:', err);
    }
}

function renderReportsTable(reports) {
    const tbody = document.getElementById('reportsTableBody');
    if (!tbody) return;

    if (reports.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">暂无数据</td></tr>';
        return;
    }

    tbody.innerHTML = reports.map(r => `
        <tr>
            <td>${r.target_username || 'N/A'}</td>
            <td>${r.target_user_id || 'N/A'}</td>
            <td>${r.amount} ${r.currency}</td>
            <td>${r.description.substring(0, 30)}...</td>
            <td><span class="badge badge-${r.status}">${r.status}</span></td>
            <td>
                ${r.status === 'pending' ? `
                    <button class="btn btn-success btn-sm" onclick="approveReport('${r.id}')">通过</button>
                    <button class="btn btn-danger btn-sm" onclick="rejectReport('${r.id}')">拒绝</button>
                ` : `
                    <span class="badge badge-${r.status}">${r.status === 'approved' ? '已通过' : '已拒绝'}</span>
                `}
            </td>
        </tr>
    `).join('');
}

async function approveReport(id) {
    if (!confirm('确定通过此举报？')) return;
    try {
        await apiRequest(`/admin/reports/${id}/approve`, { method: 'POST' });
        alert('举报已通过');
        loadReports();
    } catch (err) {
        alert('操作失败: ' + err.message);
    }
}

async function rejectReport(id) {
    const reason = prompt('请输入拒绝原因:');
    if (reason === null) return;
    try {
        await apiRequest(`/admin/reports/${id}/reject`, {
            method: 'POST',
            body: JSON.stringify({ reason })
        });
        alert('举报已拒绝');
        loadReports();
    } catch (err) {
        alert('操作失败: ' + err.message);
    }
}

// ==================== API Key 管理 ====================

async function loadApiKeys() {
    try {
        const data = await apiRequest('/admin/api-keys');
        renderApiKeysTable(data.data);
    } catch (err) {
        console.error('加载API Keys失败:', err);
    }
}

function renderApiKeysTable(keys) {
    const tbody = document.getElementById('apiKeysTableBody');
    if (!tbody) return;

    if (keys.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">暂无数据</td></tr>';
        return;
    }

    tbody.innerHTML = keys.map(k => `
        <tr>
            <td>${k.user_id || 'N/A'}</td>
            <td>${k.username}</td>
            <td><code>${k.api_key.substring(0, 20)}...</code></td>
            <td>${k.request_count}</td>
            <td>${k.expires_at || '永久'}</td>
            <td><span class="badge badge-${k.status === 'active' ? 'active' : 'inactive'}">${k.status}</span></td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="revokeKey('${k.id}')">吊销</button>
            </td>
        </tr>
    `).join('');
}

async function revokeKey(id) {
    if (!confirm('确定吊销此API Key？')) return;
    try {
        await apiRequest(`/admin/api-keys/${id}/revoke`, { method: 'POST' });
        alert('API Key已吊销');
        loadApiKeys();
    } catch (err) {
        alert('操作失败: ' + err.message);
    }
}

async function generateKeys() {
    const count = parseInt(document.getElementById('keyCount').value) || 10;
    const expires = parseInt(document.getElementById('expiresDays').value) || 365;

    try {
        const result = await apiRequest('/admin/api-keys/generate', {
            method: 'POST',
            body: JSON.stringify({ count, expires_days: expires })
        });

        if (result.success) {
            let message = `成功生成 ${result.count} 个API Key:\n\n`;
            result.items.forEach((item, i) => {
                message += `${i + 1}. ${item.api_key}\n`;
            });
            alert(message);
            loadApiKeys();
        }
    } catch (err) {
        alert('生成失败: ' + err.message);
    }
}

// ==================== 广告管理 ====================

async function loadAds() {
    try {
        const data = await apiRequest('/admin/ads');
        renderAdsTable(data.data);
    } catch (err) {
        console.error('加载广告失败:', err);
    }
}

function renderAdsTable(ads) {
    const tbody = document.getElementById('adsTableBody');
    if (!tbody) return;

    if (ads.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">暂无数据</td></tr>';
        return;
    }

    tbody.innerHTML = ads.map(a => `
        <tr>
            <td>${a.title}</td>
            <td>${a.content.substring(0, 30)}...</td>
            <td><span class="badge badge-${a.type === 'pinned' ? 'active' : 'inactive'}">${a.type}</span></td>
            <td>${a.views}</td>
            <td>${a.clicks}</td>
            <td><span class="badge badge-${a.status === 'active' ? 'active' : 'inactive'}">${a.status}</span></td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick="toggleAd('${a.id}')">切换</button>
                <button class="btn btn-danger btn-sm" onclick="deleteAd('${a.id}')">删除</button>
            </td>
        </tr>
    `).join('');
}

async function createAd() {
    const title = document.getElementById('adTitle').value;
    const content = document.getElementById('adContent').value;
    const type = document.getElementById('adType').value;
    const linkUrl = document.getElementById('adLinkUrl').value;

    if (!title || !content) {
        alert('标题和内容不能为空');
        return;
    }

    try {
        await apiRequest('/admin/ads', {
            method: 'POST',
            body: JSON.stringify({ title, content, type, link_url: linkUrl })
        });
        alert('广告创建成功');
        loadAds();
        document.getElementById('createAdForm').reset();
    } catch (err) {
        alert('创建失败: ' + err.message);
    }
}

async function toggleAd(id) {
    try {
        await apiRequest(`/admin/ads/${id}/toggle`, { method: 'POST' });
        loadAds();
    } catch (err) {
        alert('操作失败: ' + err.message);
    }
}

async function deleteAd(id) {
    if (!confirm('确定删除此广告？')) return;
    try {
        await apiRequest(`/admin/ads/${id}`, { method: 'DELETE' });
        loadAds();
    } catch (err) {
        alert('删除失败: ' + err.message);
    }
}

// ==================== 广播 ====================

async function sendBroadcast() {
    const message = document.getElementById('broadcastMessage').value;
    if (!message) {
        alert('消息内容不能为空');
        return;
    }

    if (!confirm('确定向所有用户发送广播？')) return;

    try {
        const result = await apiRequest('/admin/broadcast', {
            method: 'POST',
            body: JSON.stringify({ message })
        });
        alert(`广播完成!\n成功: ${result.details.success}\n失败: ${result.details.failed}`);
        document.getElementById('broadcastMessage').value = '';
    } catch (err) {
        alert('广播失败: ' + err.message);
    }
}

// ==================== 分页 ====================

function renderPagination(pagination) {
    const el = document.getElementById('pagination');
    if (!el || pagination.pages <= 1) {
        if (el) el.innerHTML = '';
        return;
    }

    let html = `<button ${pagination.page <= 1 ? 'disabled' : ''} onclick="goPage(${pagination.page - 1})">上一页</button>`;
    html += `<span style="padding: 0 1rem;">第 ${pagination.page} / ${pagination.pages} 页</span>`;
    html += `<button ${pagination.page >= pagination.pages ? 'disabled' : ''} onclick="goPage(${pagination.page + 1})">下一页</button>`;

    el.innerHTML = html;
}

function goPage(page) {
    reportsPage = page;
    loadReports();
}

// ==================== 初始化 ====================

document.addEventListener('DOMContentLoaded', async () => {
    // 检查登录状态
    const isLoginPage = window.location.pathname === '/login';

    if (!isLoginPage) {
        const valid = await verifyToken();
        if (!valid) {
            window.location.href = '/login';
            return;
        }
    }

    // 初始化页面
    initLoginPage();

    if (document.getElementById('dashboardContent')) {
        loadDashboard();
    }
    if (document.getElementById('reportsTableBody')) {
        loadReports();
    }
    if (document.getElementById('apiKeysTableBody')) {
        loadApiKeys();
    }
    if (document.getElementById('adsTableBody')) {
        loadAds();
    }
});
