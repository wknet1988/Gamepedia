// ==================== 授权管理 ====================
const authModal = document.getElementById('auth-modal');
const authBtn = document.getElementById('auth-btn');
const closeAuthBtn = document.querySelector('.close-auth-modal');

authBtn?.addEventListener('click', () => {
    authModal.style.display = 'block';
    updateAuthStatus();
});

closeAuthBtn?.addEventListener('click', () => {
    authModal.style.display = 'none';
});
window.addEventListener('click', (e) => {
    if (e.target === authModal) authModal.style.display = 'none';
});

async function updateAuthStatus() {
    // Steam
    try {
        const resp = await fetch('/api/status');
        const data = await resp.json();
        const statusEl = document.getElementById('steam-status');
        if (data.logged_in) {
            statusEl.innerText = `✅ ${t.auth_logged_in} (${data.steamid})`;
            statusEl.style.color = '#6f6';
        } else {
            statusEl.innerText = `❌ ${t.auth_not_logged_in}`;
            statusEl.style.color = '#f66';
        }
    } catch(e) { console.error(e); }

    // Epic
    try {
        const resp = await fetch('/api/epic/status');
        const data = await resp.json();
        const statusEl = document.getElementById('epic-status');
        if (data.authenticated) {
            statusEl.innerText = `✅ ${t.auth_logged_in} (${data.account_name})`;
            statusEl.style.color = '#6f6';
        } else {
            statusEl.innerText = `❌ ${t.auth_not_logged_in}`;
            statusEl.style.color = '#f66';
        }
    } catch(e) { console.error(e); }

    // GOG
    try {
        const resp = await fetch('/api/gog/count');
        const data = await resp.json();
        const statusEl = document.getElementById('gog-status');
        if (data.count > 0) {
            statusEl.innerText = `✅ ${t.auth_sync} (${data.count} ${t.auth_gog_script})`;
            statusEl.style.color = '#6f6';
        } else {
            statusEl.innerText = `⏳ ${t.auth_gog_script}`;
            statusEl.style.color = '#ffa';
        }
    } catch(e) {
        console.error('GOG 状态检测失败', e);
        document.getElementById('gog-status').innerText = `❌ ${t.auth_not_logged_in}`;
        document.getElementById('gog-status').style.color = '#f66';
    }

    // Steam 家庭组
    try {
        const resp = await fetch('/api/family/count');
        const data = await resp.json();
        const statusEl = document.getElementById('family-status');
        if (data.count > 0) {
            statusEl.innerText = `✅ ${t.auth_family_sync} ${t.auth_family_count.replace('{count}', data.count)}`;
            statusEl.style.color = '#6f6';
        } else {
            statusEl.innerText = `⏳ ${t.auth_family_unsynced}`;
            statusEl.style.color = '#ffa';
        }
    } catch(e) {
        document.getElementById('family-status').innerText = `❌ ${t.auth_family_script}`;
        document.getElementById('family-status').style.color = '#aaa';
    }

    // Cubejoy
    try {
        const resp = await fetch('/api/cubejoy/count');
        const data = await resp.json();
        const statusEl = document.getElementById('cubejoy-status');
        if (data.count > 0) {
            statusEl.innerText = `✅ ${t.auth_sync} (${data.count} ${t.auth_cubejoy})`;
            statusEl.style.color = '#6f6';
        } else {
            statusEl.innerText = `⏳ ${t.auth_family_unsynced}`;
            statusEl.style.color = '#ffa';
        }
    } catch(e) {
        console.error('Cubejoy 状态检测失败', e);
        document.getElementById('cubejoy-status').innerText = `❌ ${t.auth_not_logged_in}`;
        document.getElementById('cubejoy-status').style.color = '#f66';
    }
}

// ---- Steam 副号 ----
document.getElementById('auth-steam-alt-login')?.addEventListener('click', async () => {
    try {
        const resp = await fetch('/api/alt/login');
        const data = await resp.json();
        if (data.login_url) {
            window.open(data.login_url, '_blank');
        } else {
            alert('无法获取登录链接');
        }
    } catch (err) {
        console.error('Steam 副号登录失败', err);
        alert('网络错误，请重试');
    }
});

document.getElementById('auth-steam-alt-save-api')?.addEventListener('click', async () => {
    const apiKey = document.getElementById('auth-steam-alt-api-key').value.trim();
    if (!apiKey) { alert('请输入 API Key'); return; }
    const resp = await fetch('/api/alt/set_api_key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey })
    });
    const data = await resp.json();
    if (data.success) {
        alert('副号 API Key 保存成功！');
        updateAuthStatus();
    } else {
        alert('保存失败');
    }
});

document.getElementById('auth-steam-alt-sync')?.addEventListener('click', async () => {
    const resp = await fetch('/api/alt/init_library', { method: 'POST' });
    const data = await resp.json();
    if (data.task_id) {
        showSyncProgress(data.task_id);
    } else if (data.success) {
        alert('副号同步已触发（无进度跟踪）');
        updateAuthStatus();
    } else {
        alert('同步失败：' + (data.error || '未知错误'));
    }
});

// 更新状态时增加副号
async function updateAuthStatus() {
    // ... 原有代码 ...
    // Steam 副号
    try {
        const resp = await fetch('/api/alt/status');
        const data = await resp.json();
        const statusEl = document.getElementById('steam-alt-status');
        if (data.logged_in) {
            statusEl.innerText = `✅ ${t.auth_logged_in} (${data.steamid})`;
            statusEl.style.color = '#6f6';
        } else if (data.need_api_key) {
            statusEl.innerText = `⏳ ${t.auth_not_logged_in} (需要 API Key)`;
            statusEl.style.color = '#ffa';
        } else {
            statusEl.innerText = `❌ ${t.auth_not_logged_in}`;
            statusEl.style.color = '#f66';
        }
    } catch(e) { console.error(e); }
}

// ---- 授权管理按钮事件 ----
document.getElementById('auth-steam-save-api')?.addEventListener('click', async () => {
    const apiKey = document.getElementById('auth-steam-api-key').value.trim();
    if (!apiKey) { alert(t.auth_not_logged_in); return; }
    const resp = await fetch('/api/set_api_key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey })
    });
    const data = await resp.json();
    if (data.success) {
        alert(t.auth_api_key_saved || 'API Key 保存成功！');
        updateAuthStatus();
    } else {
        alert(t.auth_api_key_save_failed || '保存失败');
    }
});

document.getElementById('auth-steam-login')?.addEventListener('click', async () => {
    try {
        const resp = await fetch('/api/login');
        const data = await resp.json();
        if (data.login_url) {
            window.open(data.login_url, '_blank');
        } else {
            alert('无法获取登录链接');
        }
    } catch (err) {
        console.error('Steam 登录失败', err);
        alert('网络错误，请重试');
    }
});

document.getElementById('auth-steam-sync')?.addEventListener('click', async () => {
    const resp = await fetch('/api/init_library', { method: 'POST' });
    const data = await resp.json();
    if (data.success) {
        alert('Steam 游戏库同步成功！');
        updateAuthStatus();
    } else {
        alert('同步失败，请检查 API Key 或网络');
    }
});

document.getElementById('auth-family-install')?.addEventListener('click', () => {
    window.open('/static/family_sync.user.js', '_blank');
    alert('脚本已下载，请安装到 Tampermonkey 中，然后访问 Steam 商店页面点击右下角同步按钮。');
});

document.getElementById('auth-family-open')?.addEventListener('click', () => {
    window.open('https://store.steampowered.com/account/', '_blank');
    alert('请在 Steam 商店页面点击右下角的“同步到GP游戏收藏馆”按钮同步家庭库。');
});

document.getElementById('auth-epic-login')?.addEventListener('click', () => {
    window.open('https://legendary.gl/epiclogin', '_blank');
});

document.getElementById('auth-epic-submit')?.addEventListener('click', async () => {
    const code = document.getElementById('auth-epic-code').value.trim();
    if (!code) { alert('请输入授权码'); return; }
    const resp = await fetch('/api/epic/auth_code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
    });
    const data = await resp.json();
    if (data.success) {
        alert(`Epic 认证成功！账号：${data.account_name}`);
        document.getElementById('auth-epic-code').value = '';
        updateAuthStatus();
        document.getElementById('auth-epic-sync').click();
    } else {
        alert('认证失败：' + (data.error || '未知错误'));
    }
});

document.getElementById('auth-epic-sync')?.addEventListener('click', async () => {
    const resp = await fetch('/api/epic/sync', { method: 'POST' });
    const data = await resp.json();
    if (data.success) {
        alert(`Epic 同步成功！共 ${data.count} 款游戏`);
        updateAuthStatus();
    } else {
        alert('同步失败：' + (data.error || '未知错误'));
    }
});

document.getElementById('auth-gog-install')?.addEventListener('click', () => {
    window.open('/static/gog_sync.user.js', '_blank');
    alert('脚本已下载，请安装到 Tampermonkey 中，然后访问 GOG 账户页面点击右下角同步。');
});

document.getElementById('auth-gog-store')?.addEventListener('click', () => {
    const lang = userLang === 'zh' ? 'zh' : 'en';
    window.open(`https://www.gog.com/${lang}/account`, '_blank');
});

document.getElementById('auth-cubejoy-install')?.addEventListener('click', () => {
    window.open('/static/cubejoy_sync.user.js', '_blank');
    alert('脚本已下载，请安装到 Tampermonkey 中，然后访问方块游戏“我的游戏”页面点击右下角同步。');
});

document.getElementById('auth-cubejoy-store')?.addEventListener('click', () => {
    window.open('https://account.cubejoy.com/Comment/MyGame', '_blank');
});