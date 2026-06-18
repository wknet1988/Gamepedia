from .base import PlatformBase
from core.cache import download_image, get_cache_path
from cubejoy_db import get_all_cubejoy_games, count_cubejoy_games

class CubejoyPlatform(PlatformBase):
    platform_id = "cubejoy"
    display_name = "Cubejoy 方块游戏"
    icon_url = "https://www.cubejoy.com/favicon.ico"

    def get_auth_status(self):
        count = count_cubejoy_games()
        if count > 0:
            return {"authenticated": True, "account_name": "Cubejoy (Script Sync)"}
        return {"authenticated": False, "account_name": None}

    def get_game_list(self):
        games = get_all_cubejoy_games()
        return [
            {
                "id": g["game_id"],
                "s_id": g.get("s_id", ""),
                "name": g["name"],
                "image_url": f"/images_cubejoy/{g['game_id']}.jpg"
            }
            for g in games
        ]

    def get_store_url(self, game_id: str) -> str:
        # 需要 s_id 构造商店链接，但此处无法直接获取 s_id，需在渲染时处理
        # 因此此方法不会直接使用，具体在 appendGames 中判断
        return ""

    def get_launch_url(self, game_id: str) -> str:
        return f"asuka://runapp/?id={game_id}"

    # 重写获取列表方法，以便前端获取 s_id
    def get_game_list_with_extra(self):
        return self.get_game_list()

    def sync_library(self) -> bool:
        # Cubejoy 同步由油猴脚本完成
        return True