import os
from pathlib import Path
from dotenv import load_dotenv

_BASE = Path(__file__).parent          # .../morning-briefing/evening
_ROOT = _BASE.parent                   # .../morning-briefing

load_dotenv(_ROOT / ".env")

CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]
NEWSAPI_KEY    = os.environ.get("NEWSAPI_KEY", "")

# 音频与 feed 输出目录（本地）
AUDIO_DIR = str(_BASE / "audio")
FEED_PATH = str(_BASE / "feed.json")

# 公网 base URL：复用早报的 GitHub Pages 仓库，子路径 /evening
BASE_URL = os.environ.get("BASE_URL", "https://1938522821-glitch.github.io/morning-briefing") + "/evening"

# TTS 声音：温柔女声，适合晚间放松
TTS_VOICE = "zh-CN-XiaoxiaoNeural"

# 早报脚本所在目录（用于"今日回顾"取材）
MORNING_SCRIPT_DIR = _ROOT / "scripts"
