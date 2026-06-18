from .base import PlatformBase
from core.cache import download_image, get_cache_path
from gog_db import get_all_gog_games, count_gog_games

class GOGPlatform(PlatformBase):
    platform_id = "gog"
    display_name = "GOG"
    icon_url = "https://www.gog.com/favicon.ico"

    def get_auth_status(self):
        # GOG 无需登录，仅检测是否有游戏数据
        count = count_gog_games()
        if count > 0:
            return {"authenticated": True, "account_name": "GOG (Script Sync)"}
        return {"authenticated": False, "account_name": None}

    def get_game_list(self):
        games = get_all_gog_games()
        return [
            {
                "id": g["game_id"],
                "name": g["name"],
                "image_url": f"/images_gog/{g['game_id']}.jpg"
            }
            for g in games
        ]

    def get_store_url(self, game_id: str) -> str:
        # GOG 使用搜索页面
        return f"https://www.gog.com/zh/games?query={game_id}"

    def get_launch_url(self, game_id: str) -> str:
        # GOG 没有通用启动协议，返回空
        return ""

    def sync_library(self) -> bool:
        # GOG 同步由油猴脚本完成，后端无需操作
        return True  # 无操作，视为成功