import os
from pathlib import Path
from dotenv import load_dotenv

_BASE = Path(__file__).parent          # .../morning-briefing/deepdive
_ROOT = _BASE.parent                   # .../morning-briefing

load_dotenv(_ROOT / ".env")

CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]

# 音频与 feed 输出目录（本地）
AUDIO_DIR = str(_BASE / "audio")
FEED_PATH = str(_BASE / "feed.json")

# 公网 base URL：复用早报的 GitHub Pages 仓库，子路径 /deepdive
BASE_URL = os.environ.get("BASE_URL", "https://1938522821-glitch.github.io/morning-briefing") + "/deepdive"

# TTS 声音：稳重新闻感男声，适合深度时事分析
TTS_VOICE = "zh-CN-YunyangNeural"

# 早报脚本所在目录（用于取材）
MORNING_SCRIPT_DIR = _ROOT / "scripts"
