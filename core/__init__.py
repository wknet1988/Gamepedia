# core/__init__.py
# 导出核心模块，方便外部引用
from .config import config, load_config, save_config
from .cache import (
    CACHE_DIR,
    get_cache_path,
    is_image_valid,
    download_image,
    # 如果保留旧函数名，可在此导出
    get_cached_image_path,
    get_platform_image_path,
    get_gog_image_path,
    get_cubejoy_image_path,
    download_platform_image,
    download_gog_image,
    download_cubejoy_image,
)
from .utils import escape_html, normalize_name, timestamp_to_str