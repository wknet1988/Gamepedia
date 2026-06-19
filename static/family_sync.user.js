// ==UserScript==
// @name         Steam Family Sync to Gamepedia
// @name-zh      Steam 家庭库同步到GP游戏收藏馆
// @namespace    http://localhost:5000
// @version      1.2.3
// @description  Fetch Steam family library and sync to Gamepedia
// @description-zh  从 Steam 家庭库同步游戏列表到本地 GP 游戏收藏馆
// @author       Gamepedia
// @match        https://store.steampowered.com/account/*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// @connect      127.0.0.1
// ==/UserScript==

(function() {
    'use strict';

    // 国际化文本
    const i18n = {
        zh: {
            sync_btn: '📀 同步到GP游戏收藏馆',
            sync_btn_syncing: '同步中...',
            login_error: '无法获取登录信息，请确保已登录 Steam 商店',
            sync_success: (family_name, count) => `同步成功！家庭组：${family_name}，共 ${count} 款游戏`,
            sync_failed: (error) => `同步失败：${error || '未知错误'}`,
            network_error: '网络错误，请确保本地GP游戏收藏馆服务已启动 (http://localhost:5000)'
        },
        en: {
            sync_btn: '📀 Sync to Gamepedia',
            sync_btn_syncing: 'Syncing...',
            login_error: 'Failed to get login info, please ensure you are logged into Steam Store',
            sync_success: (family_name, count) => `Sync successful! Family group: ${family_name}, ${count} games`,
            sync_failed: (error) => `Sync failed: ${error || 'Unknown error'}`,
            network_error: 'Network error, please ensure Gamepedia service is running (http://localhost:5000)'
        }
    };

    const userLang = (navigator.language && navigator.language.startsWith('zh')) ? 'zh' : 'en';
    const t = i18n[userLang];

    const API_URL = 'http://localhost:5000/api/sync_family_library';

    function getAccessToken() {
        const configElem = document.querySelector('[data-store_user_config]');
        if (!configElem) return null;
        try {
            const config = JSON.parse(configElem.getAttribute('data-store_user_config'));
            return config.webapi_token;
        } catch(e) { return null; }
    }

    function getSteamId() {
        const userInfoElem = document.querySelector('[data-userinfo]');
        if (!userInfoElem) return null;
        try {
            const info = JSON.parse(userInfoElem.getAttribute('data-userinfo'));
            return info.steamid;
        } catch(e) { return null; }
    }

    async function syncFamily() {
        const access_token = getAccessToken();
        const steamid = getSteamId();
        if (!access_token || !steamid) {
            alert(t.login_error);
            return;
        }

        // 禁用按钮并显示同步中
        btn.disabled = true;
        btn.innerText = t.sync_btn_syncing;
        btn.style.opacity = '0.7';

        GM_xmlhttpRequest({
            method: 'POST',
            url: API_URL,
            headers: { 'Content-Type': 'application/json' },
            data: JSON.stringify({ access_token, steamid }),
            onload: function(resp) {
                try {
                    const data = JSON.parse(resp.responseText);
                    if (data.success) {
                        alert(t.sync_success(data.family_name, data.games_count));
                        if (window.opener && !window.opener.closed) {
                            window.opener.location.reload();
                        }
                    } else {
                        alert(t.sync_failed(data.error));
                    }
                } catch(e) {
                    alert(t.sync_failed('Invalid response'));
                }
                // 恢复按钮
                btn.disabled = false;
                btn.innerText = t.sync_btn;
                btn.style.opacity = '0.35';
            },
            onerror: function() {
                alert(t.network_error);
                btn.disabled = false;
                btn.innerText = t.sync_btn;
                btn.style.opacity = '0.35';
            }
        });
    }

    const btn = document.createElement('button');
    btn.innerText = t.sync_btn;
    btn.style.position = 'fixed';
    btn.style.bottom = '20px';
    btn.style.right = '20px';
    btn.style.zIndex = '9999';
    btn.style.padding = '8px 16px';
    btn.style.background = '#2c5a2e';
    btn.style.color = 'white';
    btn.style.border = 'none';
    btn.style.borderRadius = '30px';
    btn.style.cursor = 'pointer';
    btn.style.fontWeight = 'bold';
    btn.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';
    btn.style.opacity = '0.35';
    btn.style.transition = 'opacity 0.2s ease';
    btn.style.backdropFilter = 'blur(2px)';

    btn.addEventListener('mouseenter', () => { btn.style.opacity = '1'; });
    btn.addEventListener('mouseleave', () => { btn.style.opacity = '0.35'; });

    btn.onclick = syncFamily;
    document.body.appendChild(btn);
})();