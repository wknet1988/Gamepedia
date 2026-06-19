// ==================== 应用入口 ====================
// ---- 模态框控制 ----
function showSettingsModal() {
    if (settingsModal) settingsModal.style.display = 'block';
    if (settingsMessage) settingsMessage.innerText = '';
    updateVersionDisplay();
}
function hideSettingsModal() { if (settingsModal) settingsModal.style.display = 'none'; }
function showSteamPathModal() { if (steamPathModal) steamPathModal.style.display = 'block'; }
function hideSteamPathModal() { if (steamPathModal) steamPathModal.style.display = 'none'; }

// ---- 版本号 ----
async function updateVersionDisplay() {
    try {
        const resp = await fetch('/api/version');
        const data = await resp.json();
        const verEl = document.getElementById('app-version');
        if (verEl) {
            verEl.innerText = `版本: ${data.version}`;
        }
    } catch(e) {
        console.error('获取版本失败', e);
    }
}

// ---- API 交互 ----
async function saveApiKey() {
    const apiKey = settingsApiKeyInput.value.trim();
    if (!apiKey) { if (settingsMessage) settingsMessage.innerText = '请输入 API Key'; return; }
    saveApiKeyBtn.disabled = true;
    saveApiKeyBtn.innerText = '保存中...';
    try {
        const resp = await fetch('/api/set_api_key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });
        if (!resp.ok) throw new Error('保存失败');
        const initResp = await fetch('/api/init_library', { method: 'POST' });
        if (!initResp.ok) throw new Error('游戏库初始化失败');
        if (settingsMessage) settingsMessage.innerText = '✓ API Key 已保存，游戏库已更新';
        setTimeout(() => { hideSettingsModal(); window.location.reload(); }, 1500);
    } catch (err) {
        if (settingsMessage) settingsMessage.innerText = '错误：' + err.message;
    } finally {
        saveApiKeyBtn.disabled = false;
        saveApiKeyBtn.innerText = t.save_api_key;
    }
}

async function refreshLibrary() {
    if (!confirm('重新拉取游戏库会覆盖本地缓存，确定吗？')) return;
    refreshLibraryBtn.disabled = true;
    refreshLibraryBtn.innerText = '刷新中...';
    if (settingsMessage) settingsMessage.innerText = '正在从 Steam 下载游戏数据...';
    try {
        const resp = await fetch('/api/init_library', { method: 'POST' });
        if (!resp.ok) throw new Error('刷新失败');
        if (settingsMessage) settingsMessage.innerText = '✓ 游戏库已更新，页面即将刷新';
        setTimeout(() => window.location.reload(), 1500);
    } catch (err) {
        if (settingsMessage) settingsMessage.innerText = '错误：' + err.message;
    } finally {
        refreshLibraryBtn.disabled = false;
        refreshLibraryBtn.innerText = t.refresh_library;
    }
}

async function saveSteamPath() {
    const path = steamPathInput.value.trim();
    if (!path) { if (pathError) pathError.innerText = '请输入 Steam 安装路径'; return; }
    saveSteamPathBtn.disabled = true;
    try {
        const resp = await fetch('/api/set_steam_path', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ steam_path: path })
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || '路径无效');
        }
        hideSteamPathModal();
        window.location.reload();
    } catch (err) {
        if (pathError) pathError.innerText = err.message;
    } finally {
        saveSteamPathBtn.disabled = false;
    }
}

// ---- 登录状态 ----
async function checkStatus() {
    try {
        const resp = await fetch('/api/status');
        const data = await resp.json();
        if (data.logged_in) {
            document.getElementById('login-panel').style.display = 'none';
            document.getElementById('app').style.display = 'flex';
            loadBackgroundFromStorage();
            await loadShelves();
            resetAndLoadGames();
        } else {
            document.getElementById('login-panel').style.display = 'block';
            document.getElementById('app').style.display = 'none';
            if (data.need_api_key) showSettingsModal();
            else if (data.need_steam_path) showSteamPathModal();
        }
    } catch (err) { console.error(err); }
}

// ---- 事件绑定 ----
document.getElementById('search-btn')?.addEventListener('click', onSearch);
document.getElementById('search-input')?.addEventListener('keypress', (e) => { if(e.key === 'Enter') onSearch(); });
document.getElementById('steam-login-btn')?.addEventListener('click', async () => {
    const resp = await fetch('/api/login');
    const data = await resp.json();
    if (data.login_url) window.location.href = data.login_url;
});
settingsBtn?.addEventListener('click', showSettingsModal);
saveApiKeyBtn?.addEventListener('click', saveApiKey);
refreshLibraryBtn?.addEventListener('click', refreshLibrary);
closeSettingsBtn?.addEventListener('click', hideSettingsModal);
saveSteamPathBtn?.addEventListener('click', saveSteamPath);
closePathModalBtn?.addEventListener('click', hideSteamPathModal);
bgImageUpload?.addEventListener('change', (e) => { if(e.target.files[0]) saveBackgroundImage(e.target.files[0]); });
clearBgBtn?.addEventListener('click', clearBackground);
window.addEventListener('click', (e) => {
    if (e.target === settingsModal) hideSettingsModal();
    if (e.target === steamPathModal) hideSteamPathModal();
});

// ---- 启动 ----
applyI18n();
setTimeout(() => {
    ensureCounterElement();
    updateCounter();
}, 100);
checkStatus();

// 安装脚本（油猴）
const installScriptBtn = document.getElementById('install-script-btn');
if (installScriptBtn) {
    installScriptBtn.addEventListener('click', () => {
        window.open('/static/family_sync.user.js', '_blank');
        alert('脚本已下载，请打开 Tampermonkey 管理面板 → 实用程序 → 从文件安装，选择刚下载的文件。');
    });
}