import os
import time
import json
from .base import PlatformBase
from core.config import config
from core.cache import download_image, get_cache_path
from epic_db import get_all_epic_games, clear_epic_games, upsert_epic_game, count_epic_games
from epic_client import fetch_epic_games

LEGENDARY_CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'legendary_config')

class EpicPlatform(PlatformBase):
    platform_id = "epic"
    display_name = "Epic Games"
    icon_url = "https://www.epicgames.com/favicon.ico"

    def _is_authenticated(self):
        # 检查凭证文件是否存在
        user_json = os.path.join(LEGENDARY_CONFIG_DIR, 'user.json')
        return os.path.exists(user_json)

    def get_auth_status(self):
        if self._is_authenticated():
            # 尝试读取用户名
            account_name = "Epic User"
            user_json = os.path.join(LEGENDARY_CONFIG_DIR, 'user.json')
            if os.path.exists(user_json):
                try:
                    with open(user_json, 'r') as f:
                        data = json.load(f)
                        account_name = data.get('displayName', 'Epic User')
                except:
                    pass
            return {"authenticated": True, "account_name": account_name}
        return {"authenticated": False, "account_name": None}

    def get_game_list(self):
        games = get_all_epic_games()
        return [
            {
                "id": g["game_id"],
                "name": g["name"],
                "image_url": f"/images_epic/{g['game_id']}.jpg"
            }
            for g in games
        ]

    def get_store_url(self, game_id: str) -> str:
        # Epic 商店游戏页面可用 slug 或 id，此处使用搜索作为备选
        # 但 Epic 的 game_id 通常是 app_name，可直接构造
        return f"https://store.epicgames.com/browse?q={game_id}"

    def get_launch_url(self, game_id: str) -> str:
        return f"com.epicgames.launcher://apps/{game_id}?action=launch"

    def sync_library(self) -> bool:
        """同步 Epic 游戏库（需要 access_token）"""
        # 由于 Epic 需要 access_token，而该 token 由前端通过油猴脚本传递到 /api/epic/auth_code
        # 这里不直接实现同步，而是由专门的 /api/epic/sync 路由处理（因涉及凭证刷新）
        # 因此该方法留空或返回 False
        return False