from flask import Blueprint, request, jsonify, session, redirect
from core.config import config, save_config
from steam_client import get_steam_login_url, validate_steam_callback
from database import init_db

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/login')
def api_login():
    return_to = request.url_root.rstrip('/') + '/api/auth'
    login_url = get_steam_login_url(return_to)
    return jsonify({"login_url": login_url})

@auth_bp.route('/auth')
def api_auth():
    callback_url = request.url
    steamid = validate_steam_callback(callback_url)
    if steamid:
        session['steamid'] = steamid
        config['steamid'] = steamid
        save_config(config)
        return redirect('/')
    else:
        return "登录失败", 400

@auth_bp.route('/status')
def api_status():
    if not session.get('steamid') and config.get('steamid'):
        session['steamid'] = config['steamid']
    if not session.get('api_key') and config.get('api_key'):
        session['api_key'] = config['api_key']
    if not session.get('steam_path') and config.get('steam_path'):
        session['steam_path'] = config['steam_path']

    steamid = session.get('steamid')
    api_key = session.get('api_key')
    steam_path = session.get('steam_path')
    if steamid and api_key and steam_path:
        return jsonify({"logged_in": True, "steamid": steamid, "has_steam_path": True})
    elif steamid and api_key:
        return jsonify({"logged_in": False, "steamid": steamid, "need_steam_path": True})
    elif steamid:
        return jsonify({"logged_in": False, "steamid": steamid, "need_api_key": True})
    else:
        return jsonify({"logged_in": False})

@auth_bp.route('/set_api_key', methods=['POST'])
def api_set_api_key():
    data = request.json
    api_key = data.get('api_key')
    if api_key:
        session['api_key'] = api_key
        config['api_key'] = api_key
        save_config(config)
        # 触发 Steam 游戏库同步（可移到后台任务）
        from steam_client import refresh_games_library
        refresh_games_library(force=True)
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@auth_bp.route('/set_steam_path', methods=['POST'])
def api_set_steam_path():
    data = request.json
    steam_path = data.get('steam_path')
    if steam_path and os.path.exists(steam_path):
        session['steam_path'] = steam_path
        config['steam_path'] = steam_path
        save_config(config)
        # 刷新 Steam 自定义列表
        from steam_client import refresh_shelves_from_steam
        refresh_shelves_from_steam()
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "路径无效"}), 400

@auth_bp.route('/init_library', methods=['POST'])
def api_init_library():
    from steam_client import refresh_games_library
    success = refresh_games_library(force=True)
    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 500