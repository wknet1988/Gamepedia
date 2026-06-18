import os
import time
import sqlite3
from flask import session
from .base import PlatformBase
from core.config import config
from core.cache import download_image, get_cache_path
from database import get_all_games, upsert_game, clear_shelves, add_shelf, add_game_to_shelf
from steam_client import fetch_owned_games, get_family_group_for_user, fetch_family_shared_games, parse_steam_groups

class SteamPlatform(PlatformBase):
    platform_id = "steam"
    display_name = "Steam"
    icon_url = "https://store.steampowered.com/favicon.ico"

    def get_auth_status(self):
        steamid = session.get('steamid') or config.get('steamid')
        api_key = session.get('api_key') or config.get('api_key')
        if steamid and api_key:
            return {"authenticated": True, "account_name": steamid}
        return {"authenticated": False, "account_name": None}

    def get_game_list(self):
        games = get_all_games()
        return [
            {
                "id": g["appid"],
                "name": g["name"],
                "image_url": f"/images/{g['appid']}.jpg",
                "type": g.get("type", "owned")
            }
            for g in games
        ]

    def get_store_url(self, game_id: str) -> str:
        return f"https://store.steampowered.com/app/{game_id}"

    def get_launch_url(self, game_id: str) -> str:
        return f"steam://run/{game_id}"

    def sync_library(self) -> bool:
        """同步 Steam 游戏库（含家庭组）"""
        steamid = session.get('steamid') or config.get('steamid')
        api_key = session.get('api_key') or config.get('api_key')
        steam_path = session.get('steam_path') or config.get('steam_path')
        if not steamid or not api_key:
            return False

        now = int(time.time())
        try:
            # 获取自己的游戏
            owned = fetch_owned_games(api_key, steamid)
            owned_appids = {g['appid'] for g in owned}
            for game in owned:
                upsert_game(game['appid'], game['name'], game['header_url'], now, 'owned')
                download_image(game['header_url'], 'steam', game['appid'])

            # 获取家庭共享游戏
            family_info = get_family_group_for_user(api_key, steamid)
            if family_info:
                shared = fetch_family_shared_games(api_key, family_info['family_groupid'])
                for game in shared:
                    if game['appid'] not in owned_appids:
                        upsert_game(game['appid'], game['name'], game['header_url'], now, 'shared')
                        download_image(game['header_url'], 'steam', game['appid'])

            # 解析 Steam 自定义列表（如果有路径）
            if steam_path:
                self._sync_shelves(steam_path, steamid)

            return True
        except Exception as e:
            print(f"Steam 同步失败: {e}")
            return False

    def _sync_shelves(self, steam_path: str, steamid: str):
        """解析 sharedconfig.vdf 更新货架"""
        groups = parse_steam_groups(steam_path, steamid)
        if not groups:
            return
        clear_shelves()
        for group_name, appids in groups.items():
            shelf_type = 'favorite' if group_name == '我的最爱' else 'custom'
            shelf_id = add_shelf(group_name, shelf_type)
            for idx, appid in enumerate(appids):
                add_game_to_shelf(shelf_id, appid, idx)