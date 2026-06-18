from abc import ABC, abstractmethod
from typing import List, Dict, Any

class PlatformBase(ABC):
    """所有平台必须实现的抽象基类"""
    
    platform_id: str
    display_name: str
    icon_url: str

    @abstractmethod
    def get_auth_status(self) -> Dict[str, Any]:
        """返回认证状态，至少包含 authenticated (bool) 和 account_name (str)"""
        pass

    @abstractmethod
    def get_game_list(self) -> List[Dict[str, Any]]:
        """获取游戏列表，每个游戏至少包含 id, name, image_url"""
        pass

    @abstractmethod
    def get_store_url(self, game_id: str) -> str:
        """生成商店页面的 URL"""
        pass

    @abstractmethod
    def get_launch_url(self, game_id: str) -> str:
        """生成启动游戏的 URL（协议）"""
        pass

    def sync_library(self) -> bool:
        """同步游戏库，子类可重写"""
        raise NotImplementedError("sync_library not implemented for this platform")

    def get_game_list_with_extra(self) -> List[Dict[str, Any]]:
        """获取带额外字段的游戏列表（如 Cubejoy 的 s_id），默认调用 get_game_list"""
        return self.get_game_list()