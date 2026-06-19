// ==================== 全局变量与基础辅助 ====================
let currentPlatform = null;
let currentSearch = '';
let totalGames = 0;
let loadedCount = 0;
let isLoading = false;
let hasMore = true;
const PAGE_LIMIT = 28;

// DOM 引用（部分）
const settingsModal = document.getElementById('settings-modal');
const settingsApiKeyInput = document.getElementById('settings-api-key');
const saveApiKeyBtn = document.getElementById('save-api-key-settings');
const refreshLibraryBtn = document.getElementById('refresh-library-btn');
const settingsMessage = document.getElementById('settings-message');
const closeSettingsBtn = document.querySelector('.close-settings-modal');
const settingsBtn = document.getElementById('settings-btn');
const bgImageUpload = document.getElementById('bg-image-upload');
const clearBgBtn = document.getElementById('clear-bg-btn');
const steamPathModal = document.getElementById('steam-path-modal');
const steamPathInput = document.getElementById('modal-steam-path');
const saveSteamPathBtn = document.getElementById('modal-save-steam-path');
const pathError = document.getElementById('path-error');
const closePathModalBtn = document.querySelector('.close-path-modal');

// 辅助函数
function showLoadingMore(show) {
    const el = document.getElementById('loading-more');
    if (el) el.style.display = show ? 'block' : 'none';
}

function ensureCounterElement() {
    let counterEl = document.getElementById('game-counter');
    if (!counterEl) {
        counterEl = document.createElement('div');
        counterEl.id = 'game-counter';
        counterEl.className = 'dynamic-island';
        document.body.appendChild(counterEl);
    }
    // 强制内联样式
    const style = counterEl.style;
    style.position = 'fixed';
    style.bottom = '20px';
    style.right = '20px';
    style.backgroundColor = 'rgba(0, 0, 0, 0.85)';
    style.backdropFilter = 'blur(10px)';
    style.color = 'white';
    style.padding = '6px 16px';
    style.borderRadius = '30px';
    style.fontSize = '14px';
    style.fontWeight = '500';
    style.zIndex = '99999';
    style.whiteSpace = 'nowrap';
    style.pointerEvents = 'none';
    style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';
    style.fontFamily = "system-ui, -apple-system, 'Segoe UI', sans-serif";
    return counterEl;
}

function updateCounter() {
    const counterEl = ensureCounterElement();
    const displayLoaded = Math.min(loadedCount, totalGames);
    const text = t.counter_text.replace('{loaded}', displayLoaded).replace('{total}', totalGames);
    counterEl.innerText = text;
}

function escapeHtml(str) {
    return str.replace(/[&<>]/g, m => {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

function showLoading() {
    const ld = document.getElementById('loading');
    if (ld) ld.style.display = 'block';
}
function hideLoading() {
    const ld = document.getElementById('loading');
    if (ld) ld.style.display = 'none';
}