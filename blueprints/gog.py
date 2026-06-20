from flask import Blueprint, request, jsonify
import time
import sqlite3
from gog_db import clear_gog_games, upsert_gog_game, count_gog_games, get_local_gog_ids, delete_gog_games_not_in
from cache_manager import download_gog_image
from gog_client import get_gog_games, load_gog_token

gog_bp = Blueprint('gog', __name__, url_prefix='/api/gog')

@gog_bp.route('/sync', methods=['POST'])
def sync_gog_library():
    if not load_gog_token():
        return jsonify({"success": False, "error": "Not logged in"}), 401

    # 获取本地已有 ID
    local_ids = get_local_gog_ids()

    games = get_gog_games()
    if not games:
        return jsonify({"success": False, "error": "No games found"}), 404

    remote_ids = {game['game_id'] for game in games}
    now = int(time.time())

    # 插入或更新（仅新游戏）
    for game in games:
        game_id = game['game_id']
        if game_id in local_ids:
            continue  # 已存在，跳过
        title = game['title']
        image_url = game['image_url']
        if image_url:
            download_gog_image(image_url, game_id)
        upsert_gog_game(game_id, title, image_url, now)

    # 删除本地多余游戏
    to_delete = local_ids - remote_ids
    if to_delete:
        delete_gog_games_not_in(remote_ids)

    return jsonify({"success": True, "count": len(games), "deleted": len(to_delete)})

@gog_bp.route('/sync_from_extension', methods=['POST'])
def gog_sync_from_extension():
    data = request.json
    games = data.get('games', [])
    if not games:
        return jsonify({"success": False, "error": "No games data"}), 400

    local_ids = get_local_gog_ids()
    remote_ids = {str(game.get('game_id')) for game in games}
    now = int(time.time())

    for game in games:
        game_id = str(game.get('game_id'))
        if game_id in local_ids:
            continue
        title = game.get('title', 'Unknown')
        image_url = game.get('image_url', '')
        if image_url:
            download_gog_image(image_url, game_id)
        upsert_gog_game(game_id, title, image_url, now)

    to_delete = local_ids - remote_ids
    if to_delete:
        delete_gog_games_not_in(remote_ids)

    return jsonify({"success": True, "count": len(games), "deleted": len(to_delete)})

@gog_bp.route('/count')
def gog_count():
    count = count_gog_games()
    return jsonify({"count": count})

@gog_bp.route('/status')
def gog_status():
    if load_gog_token():
        return jsonify({"authenticated": True, "account_name": "GOG User"})
    return jsonify({"authenticated": False})