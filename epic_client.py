import subprocess
import json
import os
import sys
import shutil
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def find_legendary():
    legendary = shutil.which('legendary')
    if legendary:
        return legendary
    scripts_dir = os.path.join(sys.prefix, 'Scripts')
    legendary_exe = os.path.join(scripts_dir, 'legendary.exe')
    if os.path.exists(legendary_exe):
        return legendary_exe
    raise FileNotFoundError("legendary not found")

def run_legendary(args, config_dir=None, timeout=60):
    legendary_exe = find_legendary()
    env = os.environ.copy()
    if config_dir:
        env['LEGENDARY_CONFIG_PATH'] = config_dir
    try:
        return subprocess.run(
            [legendary_exe] + args,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        print(f"Legendary 命令超时 ({timeout}s): {' '.join(args)}")
        return None

def is_epic_authenticated(config_dir=None):
    if not config_dir:
        config_dir = os.path.expanduser("~/.config/legendary")
    result = run_legendary(["list-games", "--json", "--limit=1"], config_dir, timeout=10)
    return result is not None and result.returncode == 0

def get_epic_account_name(config_dir=None):
    if not config_dir:
        config_dir = os.path.expanduser("~/.config/legendary")
    user_json = os.path.join(config_dir, 'user.json')
    if os.path.exists(user_json):
        with open(user_json, 'r') as f:
            data = json.load(f)
            return data.get('displayName', 'Epic User')
    return None

def fetch_epic_games(access_token=None, config_dir=None):
    """仅获取游戏列表，封面图用构造 URL，不调用 info（避免超时）"""
    if not config_dir:
        config_dir = os.path.expanduser("~/.config/legendary")
    result = run_legendary(["list-games", "--json"], config_dir, timeout=30)
    if result is None or result.returncode != 0:
        return []
    try:
        games = json.loads(result.stdout)
        game_list = []
        for game in games:
            app_name = game.get('app_name')
            title = game.get('app_title')
            # 构造封面图 URL（不一定有效，但至少不会超时）
            cover_url = f"https://cdn2.epicgames.com/{app_name}/offer/{app_name}.jpg"
            game_list.append({
                'game_id': app_name,
                'name': title,
                'header_url': cover_url,
                'sandbox': app_name,
            })
        return game_list
    except Exception as e:
        print(f"解析 Epic 游戏列表失败: {e}")
        return []