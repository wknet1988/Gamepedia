from .games import games_bp
from .images import images_bp
from .platforms import platform_bp  # 改为 platforms
from .auth import auth_bp
from .family import family_bp
from .epic import epic_bp
from .gog import gog_bp
from .cubejoy import cubejoy_bp

__all__ = [
    'games_bp', 'images_bp', 'platform_bp', 'auth_bp',
    'family_bp', 'epic_bp', 'gog_bp', 'cubejoy_bp'
]