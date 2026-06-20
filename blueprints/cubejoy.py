from flask import Blueprint, request, jsonify
import time
from cubejoy_db import init_cubejoy_db, upsert_cubejoy_game, count_cubejoy_games, get_local_cubejoy_ids, delete_cubejoy_games_not_in
from cache_manager import download_cubejoy_image

cubejoy_bp = Blueprint('cubejoy', __name__, url_prefix='/api/cubejoy')

# 确保 Cubejoy 数据库已初始化
init_cubejoy_db()

@cubejoy_bp.route('/sync', methods=['POST'])
def cubejoy_sync():
    data = request.json
    games = data.get('games', [])
    if not games:
        return jsonify({"success": False, "error": "No games data"}), 400

    # 获取本地已有 ID
    local_ids = get_local_cubejoy_ids()
    remote_ids = {str(game.get('game_id')) for game in games}
    now = int(time.time())

    # 插入或更新（仅新游戏）
    for game in games:
        game_id = str(game.get('game_id'))
        if game_id in local_ids:
            continue  # 已存在，跳过
        s_id = game.get('s_id', '')
        title = game.get('title', 'Unknown')
        image_url = game.get('image_url', '')
        if image_url:
            download_cubejoy_image(image_url, game_id)
        upsert_cubejoy_game(game_id, s_id, title, image_url, now)

    # 删除本地多余游戏
    to_delete = local_ids - remote_ids
    if to_delete:
        delete_cubejoy_games_not_in(remote_ids)

    return jsonify({"success": True, "count": len(games), "deleted": len(to_delete)})

@cubejoy_bp.route('/count')
def cubejoy_count():
    count = count_cubejoy_games()
    return jsonify({"count": count})