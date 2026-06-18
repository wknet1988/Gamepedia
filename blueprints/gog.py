from flask import Blueprint, request, jsonify
import time
from gog_db import init_gog_db, get_all_gog_games, upsert_gog_game, clear_gog_games, count_gog_games
from core.cache import download_image, get_cache_path

gog_bp = Blueprint('gog', __name__, url_prefix='/api/gog')

# 确保 GOG 数据库已初始化
init_gog_db()

@gog_bp.route('/sync_from_extension', methods=['POST'])
def gog_sync_from_extension():
    data = request.json
    games = data.get('games', [])
    if not games:
        return jsonify({"success": False, "error": "No games data"}), 400

    clear_gog_games()
    now = int(time.time())
    for game in games:
        game_id = str(game.get('game_id'))
        title = game.get('title', 'Unknown')
        image_url = game.get('image_url', '')
        if image_url:
            download_image(image_url, 'gog', game_id)
        upsert_gog_game(game_id, title, image_url, now)
    return jsonify({"success": True, "count": len(games)})

@gog_bp.route('/status')
def gog_status():
    # GOG 状态通过脚本同步，此处只检查数据库是否有数据（或返回固定状态）
    return jsonify({"authenticated": False})  # GOG 不需要登录

@gog_bp.route('/count')
def gog_count():
    count = count_gog_games()
    return jsonify({"count": count})