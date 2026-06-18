import time
import re

def escape_html(text: str) -> str:
    """转义 HTML 特殊字符，防止 XSS"""
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def normalize_name(name: str) -> str:
    """归一化游戏名称（用于模糊匹配）"""
    if not name:
        return ""
    # 转小写，去除特殊符号，保留字母数字和中文
    name = name.lower()
    name = re.sub(r'[^\w\u4e00-\u9fff]', '', name)
    return name

def timestamp_to_str(timestamp: int) -> str:
    """将时间戳转为可读字符串"""
    if not timestamp:
        return "无记录"
    t = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", t)

def safe_parse_json(text: str) -> dict:
    """安全解析 JSON，失败时返回空字典"""
    try:
        return json.loads(text)
    except:
        return {}