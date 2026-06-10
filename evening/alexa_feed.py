"""
生成/更新「晚安电台」Alexa Flash Briefing 所需的 JSON feed。
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
            "uid": f"evening-radio-{datetime.now().strftime('%Y%m%d')}",
            "updateDate": now_iso,
            "titleText": f"晚安电台 · {date_display}",
            "mainText": "",
            "streamUrl": audio_url,
            "redirectionUrl": audio_url,
        }
    ]

    Path(FEED_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(FEED_PATH, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)

    print(f"Alexa feed 已更新：{FEED_PATH}")
    print(f"音频 URL：{audio_url}")
