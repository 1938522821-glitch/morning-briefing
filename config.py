import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]
NEWSAPI_KEY    = os.environ.get("NEWSAPI_KEY", "")

# 音频输出目录（nginx 静态托管）
_BASE          = Path(__file__).parent
AUDIO_DIR      = os.environ.get("AUDIO_DIR", str(_BASE / "audio"))
FEED_PATH      = os.environ.get("FEED_PATH", str(_BASE / "feed.json"))

# 公网可访问的 base URL（Alexa 必须 https）
BASE_URL       = os.environ.get("BASE_URL", "https://zlifelog.xin/briefing")

# TTS 声音（edge-tts）
TTS_VOICE      = "zh-CN-YunxiNeural"   # 男声播客风

# 每天几点生成（服务器本地时间，UTC+0；爱尔兰 7:00 = UTC 6:00 或 7:00）
CRON_HOUR      = int(os.environ.get("CRON_HOUR", "6"))
