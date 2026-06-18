from flask import Blueprint, send_file, abort
from pathlib import Path
from core.cache import get_cache_path, download_image
import sqlite3
import os

images_bp = Blueprint('images', __name__, url_prefix='/images')

# ---- Steam 图片代理 ----
@images_bp.route('/<int:appid>.jpg')
def steam_image(appid):
    local_path = get_cache_path('steam', str(appid))
    if not local_path.exists():
        conn = sqlite3.connect('steam_games.db')
        c = conn.cursor()
        c.execute("SELECT header_url FROM games WHERE appid = ?", (appid,))
        row = c.fetchone()
        conn.close()
        if row:
            download_image(row[0], 'steam', str(appid))
    if local_path.exists():
        return send_file(local_path, mimetype='image/jpeg')
    else:
        abort(404)

# ---- Epic 图片代理 ----
@images_bp.route('/epic/<game_id>.jpg')
def epic_image(game_id):
    local_path = get_cache_path('epic', game_id)
    if not local_path.exists():
        conn = sqlite3.connect('epic_games.db')
        c = conn.cursor()
        c.execute("SELECT header_url FROM epic_games WHERE game_id = ?", (game_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            download_image(row[0], 'epic', game_id)
    if local_path.exists():
        return send_file(local_path, mimetype='image/jpeg')
    else:
        abort(404)

# ---- GOG 图片代理 ----
@images_bp.route('/gog/<game_id>.jpg')
def gog_image(game_id):
    local_path = get_cache_path('gog', game_id)
    if not local_path.exists():
        conn = sqlite3.connect('gog_games.db')
        c = conn.cursor()
        c.execute("SELECT image_url FROM gog_games WHERE game_id = ?", (game_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            download_image(row[0], 'gog', game_id)
    if local_path.exists():
        return send_file(local_path, mimetype='image/jpeg')
    else:
        abort(404)

# ---- Cubejoy 图片代理 ----
@images_bp.route('/cubejoy/<game_id>.jpg')
def cubejoy_image(game_id):
    local_path = get_cache_path('cubejoy', game_id)
    if not local_path.exists():
        conn = sqlite3.connect('cubejoy_games.db')
        c = conn.cursor()
        c.execute("SELECT image_url FROM cubejoy_games WHERE game_id = ?", (game_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            download_image(row[0], 'cubejoy', game_id)
    if local_path.exists():
        return send_file(local_path, mimetype='image/jpeg')
    else:
        abort(404)