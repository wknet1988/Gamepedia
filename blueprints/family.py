from flask import Blueprint, request, jsonify
import sqlite3
import time
from core.cache import download_image, get_cached_image_path
from database import DB_PATH
from steam_client import get_family_info_with_token, get_family_shared_games_with_token

family_bp = Blueprint('family', __name__, url_prefix='/api/family')

@family_bp.route('/sync', methods=['POST'])
def api_sync_family_library():
    data = request.json
    access_token = data.get('access_token')
    steamid = data.get('steamid')
    if not access_token or not steamid:
        return jsonify({"success": False, "error": "Missing access_token or steamid"}), 400

    family_info = get_family_info_with_token(access_token, steamid)
    if not family_info:
        return jsonify({"success": False, "error": "Cannot get family info. Make sure you are in a Steam Family."}), 400

    family_games = get_family_shared_games_with_token(access_token, family_info['family_groupid'])

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = int(time.time())

    # 获取自己购买的游戏 ID (type='owned')
    c.execute("SELECT appid FROM games WHERE type = 'owned'")
    owned_appids = {row[0] for row in c.fetchall()}

    for game in family_games:
        appid = game['appid']
        name = game['name']
        header_url = game['header_url']

        if appid in owned_appids:
            continue

        c.execute("SELECT 1 FROM games WHERE appid = ?", (appid,))
        exists = c.fetchone() is not None
        if exists:
            c.execute("UPDATE games SET name = ?, header_url = ?, last_updated = ? WHERE appid = ?",
                      (name, header_url, now, appid))
        else:
            c.execute("INSERT INTO games (appid, name, header_url, last_updated, type) VALUES (?, ?, ?, ?, ?)",
                      (appid, name, header_url, now, 'shared'))

        if not get_cached_image_path(appid).exists():
            download_image(header_url, appid)

    conn.commit()
    conn.close()

    return jsonify({"success": True, "family_name": family_info['family_name'], "games_count": len(family_games)})

@family_bp.route('/count')
def family_count():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM games WHERE type = 'shared'")
    count = c.fetchone()[0]
    conn.close()
    return jsonify({"count": count})