"""
生成"深度思考"的标准 podcast RSS feed。
仅供 Spotify 订阅使用（不提交小宇宙），可以放开聊敏感的国际局势话题。
"""
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))  # 共享 podcast_common
from podcast_common import build_rss, make_cover_image, load_episode_meta
from config import AUDIO_DIR, BASE_URL


def _title_fn(f: Path) -> str:
    highlights = load_episode_meta(f).get("highlights", "")
    if highlights:
        return f"深度思考｜{highlights}"
    m = re.match(r"(\d{8})_", f.name)
    dt = datetime.strptime(m.group(1), "%Y%m%d") if m else datetime.fromtimestamp(f.stat().st_mtime)
    return f"深度思考 · {dt.strftime('%Y年%m月%d日')}"


def update_podcast_feed() -> None:
    base = Path(__file__).parent
    cover_path = base / "cover.jpg"
    make_cover_image(str(cover_path), "深度思考", "国际局势 · 深度解读", bg=(40, 20, 20), fg=(230, 220, 200))
    cover_url = f"{BASE_URL}/cover.jpg"

    build_rss(
        channel_title="深度思考",
        channel_desc="每晚深入解读一个国际/地缘局势话题：来龙去脉、各方视角、可能走向，给关心世界的你",
        channel_link=BASE_URL,
        audio_base_url=f"{BASE_URL}/audio",
        audio_dir=AUDIO_DIR,
        pattern="*_deepdive.mp3",
        title_fn=_title_fn,
        cover_url=cover_url,
        output_path=str(base / "podcast.xml"),
    )
