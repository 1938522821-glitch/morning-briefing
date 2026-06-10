"""
生成"每日早报"的标准 podcast RSS feed，可在任意播客 App 中订阅。
"""
from pathlib import Path
from podcast_common import build_rss, make_cover_image
from config import AUDIO_DIR, BASE_URL


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
        title_fn=lambda dt: f"爱尔兰早咖啡 · {dt.strftime('%Y年%m月%d日')}",
        cover_url=cover_url,
        output_path=str(base / "podcast.xml"),
    )
