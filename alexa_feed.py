"""
生成/更新 Alexa Flash Briefing 所需的 JSON feed。
Alexa 每次拉取这个 URL，如果 updateDate 变了就播放新内容。
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from config import FEED_PATH, BASE_URL


def update_feed(audio_path: str) -> None:
    filename = os.path.basename(audio_path)
    audio_url = f"{BASE_URL}/audio/{filename}"

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_display = datetime.now().strftime("%Y年%m月%d日")

    feed = [
        {
            "uid": f"morning-briefing-{datetime.now().strftime('%Y%m%d')}",
            "updateDate": now_iso,
            "titleText": f"每日早报 · {date_display}",
            "mainText": "",           # AUDIO 模式留空
            "streamUrl": audio_url,
            "redirectionUrl": audio_url,
        }
    ]

    feed_path = FEED_PATH if not FEED_PATH.startswith("/opt") else str(Path(__file__).parent / "feed.json")
    Path(feed_path).parent.mkdir(parents=True, exist_ok=True)
    with open(feed_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)

    print(f"Alexa feed 已更新：{FEED_PATH}")
    print(f"音频 URL：{audio_url}")
