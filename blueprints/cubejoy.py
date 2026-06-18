from flask import Blueprint, request, jsonify
import time
from cubejoy_db import init_cubejoy_db, get_all_cubejoy_games, upsert_cubejoy_game, clear_cubejoy_games, count_cubejoy_games
from core.cache import download_image, get_cache_path

cubejoy_bp = Blueprint('cubejoy', __name__, url_prefix='/api/cubejoy')

# 确保 Cubejoy 数据库已初始化
init_cubejoy_db()

@cubejoy_bp.route('/sync', methods=['POST'])
def cubejoy_sync():
    data = request.json
    games = data.get('games', [])
    if not games:
        return jsonify({"success": False, "error": "No games data"}), 400

    clear_cubejoy_games()
    now = int(time.time())
    for game in games:
        game_id = str(game.get('game_id'))
        s_id = game.get('s_id', '')
        title = game.get('title', 'Unknown')
        image_url = game.get('image_url', '')
        if image_url:
            download_image(image_url, 'cubejoy', game_id)
        upsert_cubejoy_game(game_id, s_id, title, image_url, now)
    return jsonify({"success": True, "count": len(games)})

@cubejoy_bp.route('/count')
def cubejoy_count():
    count = count_cubejoy_games()
    return jsonify({"count": count})