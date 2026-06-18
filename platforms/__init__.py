# platforms/__init__.py
# 平台工厂方法，根据平台 ID 返回对应的平台实例
from .steam import SteamPlatform
from .epic import EpicPlatform
from .gog import GOGPlatform
from .cubejoy import CubejoyPlatform

PLATFORM_CLASSES = {
    "steam": SteamPlatform,
    "epic": EpicPlatform,
    "gog": GOGPlatform,
    "cubejoy": CubejoyPlatform,
}

def get_platform(platform_id: str):
    """根据平台 ID 获取平台实例"""
    cls = PLATFORM_CLASSES.get(platform_id)
    if cls:
        return cls()
    return None