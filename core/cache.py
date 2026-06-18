import os
import requests
from pathlib import Path
import imghdr

# 基础缓存目录
CACHE_DIR = Path("cache/images")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_path(platform: str, game_id: str) -> Path:
    """获取平台对应的缓存文件路径：cache/images/{platform}/{game_id}.jpg"""
    platform_dir = CACHE_DIR / platform
    platform_dir.mkdir(parents=True, exist_ok=True)
    return platform_dir / f"{game_id}.jpg"

def is_image_valid(file_path: Path) -> bool:
    """检查图片文件是否有效（存在、大小>1KB、可识别图片格式）"""
    if not file_path.exists() or file_path.stat().st_size < 1024:
        return False
    return imghdr.what(file_path) is not None

def download_image(url: str, platform: str, game_id: str) -> bool:
    """下载图片到缓存目录，并验证有效性"""
    local_path = get_cache_path(platform, game_id)
    # 如果已有有效缓存，直接返回
    if local_path.exists() and is_image_valid(local_path):
        return True
    # 删除无效文件
    if local_path.exists():
        local_path.unlink()
    try:
        resp = requests.get(url, stream=True, timeout=10, verify=False)
        if resp.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            return is_image_valid(local_path)
    except Exception:
        pass
    return False

# ---- 兼容旧函数名（逐步废弃） ----
def get_cached_image_path(appid: int) -> Path:
    """Steam 旧缓存路径（保留兼容）"""
    return CACHE_DIR / f"{appid}_header.jpg"

def get_platform_image_path(platform: str, game_id: str) -> Path:
    """旧函数名，实际调用 get_cache_path"""
    return get_cache_path(platform, game_id)

def get_gog_image_path(game_id: str) -> Path:
    return get_cache_path("gog", game_id)

def get_cubejoy_image_path(game_id: str) -> Path:
    return get_cache_path("cubejoy", game_id)

def download_platform_image(url: str, platform: str, game_id: str) -> bool:
    """旧函数名，实际调用 download_image"""
    return download_image(url, platform, game_id)

def download_gog_image(url: str, game_id: str) -> bool:
    return download_image(url, "gog", game_id)

def download_cubejoy_image(url: str, game_id: str) -> bool:
    return download_image(url, "cubejoy", game_id)