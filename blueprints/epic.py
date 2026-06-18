from flask import Blueprint, request, jsonify, redirect
import time
import subprocess
import json
import os
import sys
from core.config import config
from epic_db import upsert_epic_game, clear_epic_games, save_epic_auth, get_epic_auth
from cache_manager import download_platform_image

epic_bp = Blueprint('epic', __name__, url_prefix='/api/epic')

# 配置目录（与旧版保持一致）
LEGENDARY_CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'legendary_config')
os.makedirs(LEGENDARY_CONFIG_DIR, exist_ok=True)

def find_legendary():
    """查找 legendary 可执行文件"""
    import shutil
    legendary = shutil.which('legendary')
    if legendary:
        return legendary
    scripts_dir = os.path.join(sys.prefix, 'Scripts')
    legendary_exe = os.path.join(scripts_dir, 'legendary.exe')
    if os.path.exists(legendary_exe):
        return legendary_exe
    raise FileNotFoundError("legendary not found")

def run_legendary(args):
    """运行 legendary 命令"""
    legendary_exe = find_legendary()
    env = os.environ.copy()
    env['LEGENDARY_CONFIG_PATH'] = LEGENDARY_CONFIG_DIR
    return subprocess.run(
        [legendary_exe] + args,
        capture_output=True,
        text=True,
        env=env,
        timeout=60
    )

def is_epic_authenticated():
    """检查是否已登录"""
    result = run_legendary(["list-games", "--json", "--limit=1"])
    return result.returncode == 0

def get_epic_account_name():
    """从 user.json 获取账号名"""
    user_json = os.path.join(LEGENDARY_CONFIG_DIR, 'user.json')
    if os.path.exists(user_json):
        with open(user_json, 'r') as f:
            data = json.load(f)
            return data.get('displayName', 'Epic User')
    return None

# ---- 路由 ----
@epic_bp.route('/login')
def epic_login():
    return jsonify({"login_url": "https://legendary.gl/epiclogin"})

@epic_bp.route('/auth_code', methods=['POST'])
def epic_auth_code():
    data = request.json
    code = data.get('code')
    if not code:
        return jsonify({"success": False, "error": "Missing code"}), 400
    try:
        result = run_legendary(["auth", "--code", code])
        if result.returncode != 0:
            return jsonify({"success": False, "error": result.stderr}), 400
        if is_epic_authenticated():
            return jsonify({"success": True, "account_name": get_epic_account_name()})
        else:
            return jsonify({"success": False, "error": "Authentication failed"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@epic_bp.route('/status')
def epic_status():
    if is_epic_authenticated():
        return jsonify({"authenticated": True, "account_name": get_epic_account_name()})
    return jsonify({"authenticated": False})

@epic_bp.route('/sync', methods=['POST'])
def sync_epic_library():
    if not is_epic_authenticated():
        return jsonify({"success": False, "error": "Not logged in"}), 401

    result = run_legendary(["list-games", "--json"])
    if result.returncode != 0:
        return jsonify({"success": False, "error": result.stderr}), 500

    games = json.loads(result.stdout)
    from epic_db import clear_epic_games, upsert_epic_game
    clear_epic_games()
    now = int(time.time())
    for game in games:
        app_name = game.get('app_name')
        title = game.get('app_title')
        cover_url = f"https://cdn2.epicgames.com/{app_name}/offer/{app_name}.jpg"
        download_platform_image(cover_url, 'epic', app_name)
        upsert_epic_game(app_name, title, cover_url, app_name, now)

    return jsonify({"success": True, "count": len(games)})

# 可选：保留旧版 callback 路由（如果前端仍跳转至此）
@epic_bp.route('/callback')
def epic_callback():
    # 此路由在旧版中用于 OAuth 回调，但新版已改用授权码方式，可忽略
    return redirect('/')