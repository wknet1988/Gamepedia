from flask import Blueprint, send_file, abort
import sqlite3
import os
import threading
from core.cache import get_platform_image_path, download_platform_image, is_image_valid, get_gog_image_path, download_gog_image
from gog_client import get_gog_box_art_image

images_bp = Blueprint('images', __name__, url_prefix='/images')

def get_placeholder_path(platform: str) -> str:
    filename = {
        'steam': 'steam_placeholder.png',
        'epic': 'epic_placeholder.png',
        'gog': 'gog_placeholder.png',
        'cubejoy': 'cubejoy_placeholder.png',
    }.get(platform, 'default_placeholder.png')
    return os.path.join(os.path.dirname(__file__), '..', 'static', filename)

def async_download(url, platform, game_id):
    def _download():
        download_platform_image(url, platform, game_id)
    thread = threading.Thread(target=_download)
    thread.daemon = True
    thread.start()

@images_bp.route('/steam/<int:appid>.jpg')
def steam_image(appid):
    local_path = get_platform_image_path('steam', str(appid))
    # 如果存在但无效，删除
    if local_path.exists() and not is_image_valid(local_path):
        local_path.unlink()
        print(f"检测到无效的 Steam 缓存，已删除: {local_path}")

    if not local_path.exists():
        conn = sqlite3.connect('steam_games.db')
        c = conn.cursor()
        c.execute("SELECT header_url FROM games WHERE appid = ?", (appid,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            async_download(row[0], 'steam', str(appid))
        placeholder = get_placeholder_path('steam')
        if os.path.exists(placeholder):
            return send_file(placeholder, mimetype='image/png')
        else:
            abort(404)
    else:
        return send_file(local_path, conditional=True, max_age=31536000)

@images_bp.route('/epic/<game_id>.jpg')
def epic_image(game_id):
    local_path = get_platform_image_path('epic', game_id)
    # 如果存在但无效，删除
    if local_path.exists() and not is_image_valid(local_path):
        local_path.unlink()
        print(f"检测到无效的 Epic 缓存，已删除: {local_path}")
    if not local_path.exists():
        conn = sqlite3.connect('epic_games.db')
        c = conn.cursor()
        c.execute("SELECT header_url FROM epic_games WHERE game_id = ?", (game_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            async_download(row[0], 'epic', game_id)
        placeholder = get_placeholder_path('epic')
        if os.path.exists(placeholder):
            return send_file(placeholder, mimetype='image/png')
        else:
            abort(404)
    else:
        return send_file(local_path, conditional=True, max_age=31536000)

@images_bp.route('/gog/<game_id>.jpg')
def gog_image(game_id):
    local_path = get_gog_image_path(game_id)
    if local_path.exists():
        return send_file(local_path, conditional=True, max_age=31536000)
    else:
        conn = sqlite3.connect('gog_games.db')
        c = conn.cursor()
        c.execute("SELECT image_url FROM gog_games WHERE game_id = ?", (game_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            url = row[0]
            # 尝试下载已有 URL
            if download_gog_image(url, game_id):
                if local_path.exists():
                    return send_file(local_path, conditional=True, max_age=31536000)
            else:
                # 旧链接失败，尝试通过 API 获取新链接
                new_url = get_gog_box_art_image(game_id)
                if new_url:
                    print(f"[GOG] 使用 API 获取新链接: {new_url}")
                    if download_gog_image(new_url, game_id):
                        # 更新数据库
                        conn = sqlite3.connect('gog_games.db')
                        c = conn.cursor()
                        c.execute("UPDATE gog_games SET image_url = ? WHERE game_id = ?", (new_url, game_id))
                        conn.commit()
                        conn.close()
                        if local_path.exists():
                            return send_file(local_path, conditional=True, max_age=31536000)
        # 最终返回占位图
        placeholder = get_placeholder_path('gog')
        if os.path.exists(placeholder):
            return send_file(placeholder, mimetype='image/png')
        else:
            abort(404)

@images_bp.route('/cubejoy/<game_id>.jpg')
def cubejoy_image(game_id):
    local_path = get_platform_image_path('cubejoy', game_id)
    # 如果存在但无效，删除
    if local_path.exists() and not is_image_valid(local_path):
        local_path.unlink()
        print(f"检测到无效的 CubeJoy 缓存，已删除: {local_path}")
    if not local_path.exists():
        conn = sqlite3.connect('cubejoy_games.db')
        c = conn.cursor()
        c.execute("SELECT image_url FROM cubejoy_games WHERE game_id = ?", (game_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            url = row[0]
            if url.startswith('//'):
                url = 'https:' + url
            async_download(url, 'cubejoy', game_id)
        placeholder = get_placeholder_path('cubejoy')
        if os.path.exists(placeholder):
            return send_file(placeholder, mimetype='image/png')
        else:
            abort(404)
    else:
        return send_file(local_path, conditional=True, max_age=31536000)