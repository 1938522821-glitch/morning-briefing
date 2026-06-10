"""
生成"夜读与放空"的标准 podcast RSS feed，可在任意播客 App 中订阅。
"""
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))  # 共享 podcast_common
from podcast_common import build_rss, make_cover_image, load_episode_meta
from config import AUDIO_DIR, BASE_URL


def _title_fn(f: Path) -> str:
    m = re.match(r"(\d{8})_", f.name)
    dt = datetime.strptime(m.group(1), "%Y%m%d") if m else datetime.fromtimestamp(f.stat().st_mtime)
    base = f"夜读与放空 · {dt.strftime('%Y年%m月%d日')}"
    highlights = load_episode_meta(f).get("highlights", "")
    return f"{base} | {highlights}" if highlights else base


def update_podcast_feed() -> None:
    base = Path(__file__).parent
    cover_path = base / "cover.jpg"
    make_cover_image(str(cover_path), "夜读与放空", "回顾 · 深聊 · 故事 · 放松", bg=(20, 20, 60))
    cover_url = f"{BASE_URL}/cover.jpg"

    build_rss(
        channel_title="夜读与放空",
        channel_desc="每晚陪你回顾今日要点、深聊一个话题、讲一段故事，再做一段放松练习的中文播客",
        channel_link=BASE_URL,
        audio_base_url=f"{BASE_URL}/audio",
        audio_dir=AUDIO_DIR,
        pattern="*_evening.mp3",
        title_fn=_title_fn,
        cover_url=cover_url,
        output_path=str(base / "podcast.xml"),
    )
