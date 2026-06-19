// ==================== 游戏展示与滚动加载 ====================
function initLazyLoading() {
    const lazyImages = document.querySelectorAll('.lazy-img');
    if (lazyImages.length === 0) return;
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                const src = img.getAttribute('data-src');
                if (src) {
                    img.src = src;
                    img.removeAttribute('data-src');
                }
                observer.unobserve(img);
            }
        });
    }, { rootMargin: '200px' });
    lazyImages.forEach(img => observer.observe(img));
}

function appendGames(games) {
    const grid = document.getElementById('games-grid');
    if (!grid) return;
    if (games.length === 0 && loadedCount === 0) {
        grid.innerHTML = `<div style="text-align:center;padding:50px;">${t.no_games}</div>`;
        return;
    }

    let placeholderPath = '/static/steam_placeholder.png';
    if (currentPlatform.id === 'epic') {
        placeholderPath = '/static/epic_placeholder.png';
    } else if (currentPlatform.id === 'gog') {
        placeholderPath = '/static/gog_placeholder.png';
    } else if (currentPlatform.id === 'cubejoy') {
        placeholderPath = '/static/cubejoy_placeholder.png';
    }

    for (const game of games) {
        const card = document.createElement('div');
        card.className = 'game-card';

        let storeUrl = '';
        if (currentPlatform.id === 'steam') {
            storeUrl = `https://store.steampowered.com/app/${game.id}`;
        } else if (currentPlatform.id === 'epic') {
            const searchQuery = encodeURIComponent(game.name);
            storeUrl = `https://store.epicgames.com/browse?q=${searchQuery}`;
        } else if (currentPlatform.id === 'gog') {
            const searchQuery = encodeURIComponent(game.name);
            storeUrl = `https://www.gog.com/zh/games?query=${searchQuery}`;
        } else if (currentPlatform.id === 'cubejoy') {
            const sId = game.s_id || '';
            storeUrl = `https://store.cubejoy.com/html/en/store/goodsdetail/detail${sId}.html`;
        }

        let iconUrl = '';
        if (currentPlatform.id === 'steam') {
            iconUrl = 'https://store.steampowered.com/favicon.ico';
        } else if (currentPlatform.id === 'epic') {
            iconUrl = 'https://www.epicgames.com/favicon.ico';
        } else if (currentPlatform.id === 'gog') {
            iconUrl = 'https://www.gog.com/favicon.ico';
        } else if (currentPlatform.id === 'cubejoy') {
            iconUrl = 'https://www.cubejoy.com/favicon.ico';
        }
        const iconHtml = iconUrl ? `<img src="${iconUrl}" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">` : '';

        let badgeHtml = '';
        if (currentPlatform.id === 'steam') {
            if (game.type === 'shared') {
                badgeHtml = `<div style="position: absolute; top: 5px; right: 5px; background: rgba(0,0,0,0.7); color: #ffd700; font-size: 11px; padding: 2px 6px; border-radius: 20px; z-index: 10; backdrop-filter: blur(2px);">🏠 家庭库</div>`;
            } else if (game.type === 'alt') {
                badgeHtml = `<div style="position: absolute; top: 5px; right: 5px; background: rgba(0,0,0,0.7); color: #66c0f4; font-size: 11px; padding: 2px 6px; border-radius: 20px; z-index: 10; backdrop-filter: blur(2px);">👤 副号</div>`;
            }
        }

        let actionsHtml = '';
        if (currentPlatform.id !== 'gog') {
            let runData = '';
            if (currentPlatform.id === 'cubejoy') {
                const id = game.id || game.game_id;
                if (id) {
                    const runUrl = `asuka://runapp/?id=${id}`;
                    runData = `data-runurl="${runUrl}"`;
                }
            } else {
                runData = `data-id="${game.id}" data-platform="${currentPlatform.id}"`;
            }
            if (runData) {
                actionsHtml = `
                    <div class="actions">
                        <button class="run-btn" ${runData}>
                            ${iconHtml} ${t.run}
                        </button>
                    </div>
                `;
            }
        }

        const proxyUrl = game.image_url || '';
        const originalUrl = game.original_url || '';
        const placeholderSvg = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 100'%3E%3Crect width='200' height='100' fill='%232a3e55'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='%2389a3b5'%3ELoading...%3C/text%3E%3C/svg%3E";

        const onerrorHandler = `
            if (!this.dataset.retry) {
                this.dataset.retry = '1';
                if (this.dataset.original) {
                    this.src = this.dataset.original;
                    this.dataset.retry = '2';
                } else {
                    this.onerror = null;
                    this.src = '${placeholderPath}';
                }
            } else if (this.dataset.retry === '1') {
                if (this.dataset.original) {
                    this.src = this.dataset.original;
                    this.dataset.retry = '2';
                } else {
                    this.onerror = null;
                    this.src = '${placeholderPath}';
                }
            } else {
                this.onerror = null;
                this.src = '${placeholderPath}';
            }
        `;

        card.innerHTML = `
            <div class="game-image-container" style="position: relative;">
                <a href="${storeUrl}" target="_blank" rel="noopener noreferrer" style="display: block;">
                    <img class="lazy-img" data-src="${proxyUrl}" 
                         data-original="${originalUrl}"
                         src="${placeholderSvg}" 
                         alt="${escapeHtml(game.name)}"
                         onerror="${onerrorHandler}">
                </a>
                ${badgeHtml}
            </div>
            <div class="game-name">${escapeHtml(game.name)}</div>
            ${actionsHtml}
        `;
        grid.appendChild(card);
    }

    document.querySelectorAll('.run-btn').forEach(btn => {
        btn.removeEventListener('click', runGameHandler);
        btn.addEventListener('click', runGameHandler);
    });

    initLazyLoading();
}

function runGameHandler(e) {
    const btn = e.currentTarget;
    const runUrl = btn.dataset.runurl;
    if (runUrl) {
        window.location.href = runUrl;
        return;
    }
    const id = btn.dataset.id;
    const platform = btn.dataset.platform;
    if (platform === 'steam') {
        window.location.href = `steam://run/${id}`;
    } else if (platform === 'epic') {
        window.location.href = `com.epicgames.launcher://apps/${id}?action=launch`;
    }
}

// 滚动监听
let scrollListenerAttached = false;
let scrollTimer = null;

function onScroll() {
    if (isLoading || !hasMore) return;
    if (scrollTimer) clearTimeout(scrollTimer);
    scrollTimer = setTimeout(() => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop || window.scrollY || 0;
        const windowHeight = window.innerHeight || document.documentElement.clientHeight || 0;
        const docHeight = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight,
            document.body.offsetHeight,
            document.documentElement.offsetHeight
        );
        if (scrollTop + windowHeight >= docHeight - 300) {
            loadMoreGames();
        }
        scrollTimer = null;
    }, 100);
}

function attachScrollListener() {
    if (scrollListenerAttached) return;
    window.addEventListener('scroll', onScroll, { passive: true });
    scrollListenerAttached = true;
}

function detachScrollListener() {
    if (!scrollListenerAttached) return;
    window.removeEventListener('scroll', onScroll, { passive: true });
    scrollListenerAttached = false;
}

async function loadMoreGames() {
    if (isLoading || !hasMore || !currentPlatform) return;
    isLoading = true;
    showLoadingMore(true);
    detachScrollListener();

    const offset = loadedCount;
    let url = `/api/games?platform=${currentPlatform.id}&limit=${PAGE_LIMIT}&offset=${offset}`;
    if (currentSearch) url += `&search=${encodeURIComponent(currentSearch)}`;

    try {
        const resp = await fetch(url);
        const data = await resp.json();
        if (data.total !== undefined) totalGames = data.total;
        const newGames = data.games || [];
        if (newGames.length === 0 || loadedCount + newGames.length >= totalGames) {
            hasMore = false;
        }
        appendGames(newGames);
        loadedCount += newGames.length;
        updateCounter();
        let title = currentPlatform.name;
        if (currentSearch) title = `${t.search_result_prefix}${currentSearch}${t.search_result_suffix} - ${title}`;
        document.getElementById('current-shelf-title').innerText = title;
    } catch (err) {
        console.error('加载失败', err);
    } finally {
        isLoading = false;
        showLoadingMore(false);
        if (hasMore) attachScrollListener();
        else detachScrollListener();
    }
}

function resetAndLoadGames() {
    detachScrollListener();
    const grid = document.getElementById('games-grid');
    if (grid) grid.innerHTML = '';
    loadedCount = 0;
    hasMore = true;
    totalGames = 0;
    isLoading = false;
    updateCounter();
    loadMoreGames();
}