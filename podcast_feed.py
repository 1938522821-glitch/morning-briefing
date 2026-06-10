"""
生成"每日早报"的标准 podcast RSS feed，可在任意播客 App 中订阅。
"""
import re
from datetime import datetime
from pathlib import Path
from podcast_common import build_rss, make_cover_image, load_episode_meta
from config import AUDIO_DIR, BASE_URL


def _title_fn(f: Path) -> str:
    m = re.match(r"(\d{8})_", f.name)
    dt = datetime.strptime(m.group(1), "%Y%m%d") if m else datetime.fromtimestamp(f.stat().st_mtime)
    base = f"爱尔兰早咖啡 · {dt.strftime('%Y年%m月%d日')}"
    highlights = load_episode_meta(f).get("highlights", "")
    return f"{base} | {highlights}" if highlights else base


def update_podcast_feed() -> None:
    base = Path(__file__).parent
    cover_path = base / "cover.jpg"
    make_cover_image(str(cover_path), "爱尔兰早咖啡", "国际 · AI · 科技 · 财经 · 爱尔兰")
    cover_url = f"{BASE_URL}/cover.jpg"

    build_rss(
        channel_title="爱尔兰早咖啡",
        channel_desc="每天早上为你播报国际形势、AI与科技、财经市场、爱尔兰本地新闻和全球热点的中文播客",
        channel_link=BASE_URL,
        audio_base_url=f"{BASE_URL}/audio",
        audio_dir=AUDIO_DIR,
        pattern="*_briefing.mp3",
        title_fn=_title_fn,
        cover_url=cover_url,
        output_path=str(base / "podcast.xml"),
    )
