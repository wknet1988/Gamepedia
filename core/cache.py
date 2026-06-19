import os
import requests
import time
import json
import imghdr
from pathlib import Path

CACHE_DIR = Path("cache/images")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ---------- 图片校验函数 ----------
def is_image_valid(file_path: Path) -> bool:
    """检查图片文件是否有效（大小 > 1KB 且可识别图片格式）"""
    if not file_path.exists():
        return False
    if file_path.stat().st_size < 1024:  # 小于 1KB 视为无效
        return False
    img_type = imghdr.what(file_path)
    return img_type is not None

# ---------- 获取 GOG 封面 URL ----------
def get_gog_cover_url(game_id: str) -> str:
    """通过 GOG API 获取游戏封面图 URL"""
    api_url = f"https://api.gog.com/products/{game_id}?locale=en-US&expand=images"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        resp = requests.get(api_url, timeout=10, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            images = data.get('images', {})
            # 尝试 cover, background, logo 等字段
            for key in ['cover', 'background', 'logo']:
                if images.get(key):
                    return images[key]
        print(f"GOG API 获取封面失败: {api_url} - HTTP {resp.status_code}")
    except Exception as e:
        print(f"GOG API 请求异常: {e}")
    return ""

# ---------- 核心路径函数 ----------
def get_cache_path(platform: str, game_id: str) -> Path:
    platform_dir = CACHE_DIR / platform
    platform_dir.mkdir(parents=True, exist_ok=True)
    return platform_dir / f"{game_id}.jpg"

def get_platform_image_path(platform: str, game_id: str) -> Path:
    return get_cache_path(platform, game_id)

# ---------- 带校验的下载函数 ----------
def download_platform_image(url: str, platform: str, game_id: str, retries: int = 3, delay: int = 2) -> bool:
    if not url:
        return False
    if url.startswith('//'):
        url = 'https:' + url

    # GOG 特殊处理：优先从 API 获取封面
    if platform == 'gog':
        api_cover = get_gog_cover_url(game_id)
        if api_cover:
            if api_cover.startswith('//'):
                api_cover = 'https:' + api_cover
            url = api_cover
        else:
            print(f"GOG 图片获取失败，使用占位图: {game_id}")
            return False

    local_path = get_platform_image_path(platform, game_id)
    if local_path.exists() and is_image_valid(local_path):
        return True
    if local_path.exists():
        local_path.unlink()

    # 设置请求头（Epic 需要 Referer）
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    if platform == 'epic':
        headers['Referer'] = 'https://www.epicgames.com/'

    # 增加超时和重试
    for attempt in range(retries):
        try:
            resp = requests.get(url, stream=True, timeout=30, headers=headers, verify=False)  # timeout 增加到 30 秒
            if resp.status_code == 200:
                # ... 写入和校验逻辑 ...
                return True
            else:
                print(f"下载失败 (尝试 {attempt+1}/{retries}): {url} - HTTP {resp.status_code}")
        except Exception as e:
            print(f"下载异常 (尝试 {attempt+1}/{retries}): {url} - {e}")
        if attempt < retries - 1:
            time.sleep(delay)
    return False

# ---------- 旧版兼容函数 ----------
def get_cached_image_path(appid: int) -> Path:
    return get_cache_path('steam', str(appid))

def download_image(url: str, appid: int) -> bool:
    return download_platform_image(url, 'steam', str(appid))

def get_gog_image_path(game_id: str) -> Path:
    return get_cache_path('gog', game_id)

def download_gog_image(url: str, game_id: str) -> bool:
    return download_platform_image(url, 'gog', game_id)

def get_cubejoy_image_path(game_id: str) -> Path:
    return get_cache_path('cubejoy', game_id)

def download_cubejoy_image(url: str, game_id: str) -> bool:
    return download_platform_image(url, 'cubejoy', game_id)