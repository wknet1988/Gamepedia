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
            const githubSvg = `<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="display:inline-block; vertical-align:middle;"><path d="M10.226 17.284c-2.965-.36-5.054-2.493-5.054-5.256 0-1.123.404-2.336 1.078-3.144-.292-.741-.247-2.314.09-2.965.898-.112 2.111.36 2.83 1.01.853-.269 1.752-.404 2.853-.404 1.1 0 1.999.135 2.807.382.696-.629 1.932-1.1 2.83-.988.315.606.36 2.179.067 2.942.72.854 1.101 2 1.101 3.167 0 2.763-2.089 4.852-5.098 5.234.763.494 1.28 1.572 1.28 2.807v2.336c0 .674.561 1.056 1.235.786 4.066-1.55 7.255-5.615 7.255-10.646C23.5 6.188 18.334 1 11.978 1 5.62 1 .5 6.188.5 12.545c0 4.986 3.167 9.12 7.435 10.669.606.225 1.19-.18 1.19-.786V20.63a2.9 2.9 0 0 1-1.078.224c-1.483 0-2.359-.808-2.987-2.313-.247-.607-.517-.966-1.034-1.033-.27-.023-.359-.135-.359-.27 0-.27.45-.471.898-.471.652 0 1.213.404 1.797 1.235.45.651.921.943 1.483.943.561 0 .92-.202 1.437-.719.382-.381.674-.718.944-.943z"/></svg>`;
            verEl.innerHTML = `
                <div>${t.version_label} ${data.version}</div>
                <div><a href="https://github.com/wknet1988/Gamepedia" target="_blank" style="color:#888; text-decoration:none; font-size:13px;">${githubSvg} ${t.github_label}</a></div>
            `;
        }
        const year = new Date().getFullYear();
        const copyEl = document.getElementById('app-copyright');
        if (copyEl) {
            copyEl.innerText = `© ${year} Grandisoft`;
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

// 赞助模态框
const donateModal = document.getElementById('donate-modal');
const donateBtn = document.getElementById('donate-btn');
const closeDonateBtn = document.querySelector('.close-donate-modal');

donateBtn?.addEventListener('click', () => {
    donateModal.style.display = 'block';
});

closeDonateBtn?.addEventListener('click', () => {
    donateModal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === donateModal) {
        donateModal.style.display = 'none';
    }
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