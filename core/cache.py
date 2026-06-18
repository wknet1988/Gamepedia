import os
import requests
import time
from pathlib import Path

CACHE_DIR = Path("cache/images")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ---------- 核心路径函数 ----------
def get_cache_path(platform: str, game_id: str) -> Path:
    """统一缓存路径：cache/images/{platform}/{game_id}.jpg"""
    platform_dir = CACHE_DIR / platform
    platform_dir.mkdir(parents=True, exist_ok=True)
    return platform_dir / f"{game_id}.jpg"

# ---------- 带重试的下载函数 ----------
def download_platform_image(url: str, platform: str, game_id: str, retries: int = 3, delay: int = 2) -> bool:
    """通用平台下载，失败时重试多次"""
    if not url:
        return False
    if url.startswith('//'):
        url = 'https:' + url

    local_path = get_platform_image_path(platform, game_id)
    if local_path.exists():
        return True

    for attempt in range(retries):
        try:
            resp = requests.get(url, stream=True, timeout=10, verify=False)
            if resp.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in resp.iter_content(1024):
                        f.write(chunk)
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
    """Steam 旧版函数，返回新路径"""
    return get_cache_path('steam', str(appid))

def download_image(url: str, appid: int) -> bool:
    """Steam 旧版下载函数，使用新路径（调用带重试的通用函数）"""
    return download_platform_image(url, 'steam', str(appid))

def get_platform_image_path(platform: str, game_id: str) -> Path:
    """通用平台路径"""
    return get_cache_path(platform, game_id)

def get_gog_image_path(game_id: str) -> Path:
    return get_cache_path('gog', game_id)

def download_gog_image(url: str, game_id: str) -> bool:
    """GOG 专用下载（调用带重试的通用函数）"""
    return download_platform_image(url, 'gog', game_id)

def get_cubejoy_image_path(game_id: str) -> Path:
    return get_cache_path('cubejoy', game_id)

def download_cubejoy_image(url: str, game_id: str) -> bool:
    """Cubejoy 专用下载（调用带重试的通用函数）"""
    return download_platform_image(url, 'cubejoy', game_id)

# 旧版兼容的空校验函数（旧版并未真正使用，保留以兼容导入）
def is_image_valid(file_path):
    """旧版兼容函数，直接返回 True（不进行实际校验）"""
    return True