from flask import Blueprint, request, jsonify, redirect
import time
import os
from core.config import config
from epic_client import get_epic_auth_url, exchange_code_for_token, refresh_access_token, fetch_epic_games
from epic_db import (
    init_epic_db, get_all_epic_games, upsert_epic_game,
    clear_epic_games, save_epic_auth, get_epic_auth
)
from core.cache import download_image, get_cache_path

epic_bp = Blueprint('epic', __name__, url_prefix='/api/epic')

# 确保 Epic 数据库已初始化
init_epic_db()

# Epic OAuth 配置
EPIC_CLIENT_ID = config.get('epic_client_id', '')
EPIC_CLIENT_SECRET = config.get('epic_client_secret', '')
EPIC_REDIRECT_URI = "http://localhost:5000/api/epic/callback"

@epic_bp.route('/login')
def epic_login():
    if not EPIC_CLIENT_ID:
        return jsonify({"error": "Epic Client ID not configured"}), 500
    url = get_epic_auth_url(EPIC_CLIENT_ID, EPIC_REDIRECT_URI)
    return jsonify({"login_url": url})

@epic_bp.route('/callback')
def epic_callback():
    code = request.args.get('code')
    if not code:
        return "Missing code", 400
    token_data = exchange_code_for_token(EPIC_CLIENT_ID, EPIC_CLIENT_SECRET, code, EPIC_REDIRECT_URI)
    if not token_data:
        return "Token exchange failed", 400
    save_epic_auth('access_token', token_data['access_token'])
    save_epic_auth('refresh_token', token_data.get('refresh_token', ''))
    save_epic_auth('user_id', token_data.get('account_id', ''))
    save_epic_auth('expires_at', str(int(time.time()) + token_data.get('expires_in', 3600)))
    save_epic_auth('account_name', token_data.get('display_name', ''))
    # 自动同步
    _sync_epic_library()
    return redirect('/')

@epic_bp.route('/status')
def epic_status():
    account_name = get_epic_auth('account_name')
    if account_name:
        return jsonify({"authenticated": True, "account_name": account_name})
    return jsonify({"authenticated": False})

@epic_bp.route('/auth_code', methods=['POST'])
def epic_auth_code():
    data = request.json
    code = data.get('code')
    if not code:
        return jsonify({"success": False, "error": "Missing code"}), 400
    try:
        token_data = exchange_code_for_token(EPIC_CLIENT_ID, EPIC_CLIENT_SECRET, code, EPIC_REDIRECT_URI)
        if not token_data:
            return jsonify({"success": False, "error": "Token exchange failed"}), 400
        save_epic_auth('access_token', token_data['access_token'])
        save_epic_auth('refresh_token', token_data.get('refresh_token', ''))
        save_epic_auth('user_id', token_data.get('account_id', ''))
        save_epic_auth('expires_at', str(int(time.time()) + token_data.get('expires_in', 3600)))
        save_epic_auth('account_name', token_data.get('display_name', ''))
        _sync_epic_library()
        return jsonify({"success": True, "account_name": token_data.get('display_name', 'Epic User')})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@epic_bp.route('/sync', methods=['POST'])
def epic_sync():
    if not get_epic_auth('access_token'):
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    _sync_epic_library()
    games = get_all_epic_games()
    return jsonify({"success": True, "count": len(games)})

def _sync_epic_library():
    access_token = get_epic_auth('access_token')
    refresh_token = get_epic_auth('refresh_token')
    expires_at = get_epic_auth('expires_at')
    if not access_token:
        return
    # 刷新 token 如果过期
    if expires_at and int(expires_at) < int(time.time()):
        if refresh_token:
            new_token = refresh_access_token(EPIC_CLIENT_ID, EPIC_CLIENT_SECRET, refresh_token)
            if new_token:
                access_token = new_token['access_token']
                save_epic_auth('access_token', access_token)
                save_epic_auth('refresh_token', new_token.get('refresh_token', refresh_token))
                save_epic_auth('expires_at', str(int(time.time()) + new_token.get('expires_in', 3600)))
            else:
                print("Epic token refresh failed")
                return
        else:
            return
    games = fetch_epic_games(access_token)
    now = int(time.time())
    clear_epic_games()
    for game in games:
        app_name = game['app_name']
        title = game['app_title']
        cover_url = game.get('header_url')
        if cover_url:
            download_image(cover_url, 'epic', app_name)
        upsert_epic_game(app_name, title, cover_url, app_name, now)