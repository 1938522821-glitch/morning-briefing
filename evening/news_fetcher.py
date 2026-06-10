"""
晚安电台素材抓取：
1. 读取今天早报脚本（用于"今日回顾"）
2. 复用早报的新闻抓取（用于"深度话题"挑选素材）
"""
import importlib.util
from datetime import datetime
from pathlib import Path

from config import MORNING_SCRIPT_DIR


def _load_morning_news_fetcher():
    """通过文件路径加载上级目录的 news_fetcher 模块（避免与本文件同名冲突）。"""
    path = Path(__file__).parent.parent / "news_fetcher.py"
    spec = importlib.util.spec_from_file_location("morning_news_fetcher", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_morning_script() -> str:
    """读取今天早上的早报脚本全文，没有就返回空字符串。"""
    date_str = datetime.now().strftime("%Y%m%d")
    path = MORNING_SCRIPT_DIR / f"{date_str}_script.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def get_topic_news() -> dict:
    """复用早报的新闻抓取结果，给"深度话题"板块挑选素材。"""
    morning_news_fetcher = _load_morning_news_fetcher()
    return morning_news_fetcher.fetch_all()
