"""
用 edge-tts 把脚本转为 MP3，按板块分段生成再合并。
"""
import asyncio
import os
import subprocess
from pathlib import Path
from datetime import datetime
import edge_tts
from config import AUDIO_DIR, TTS_VOICE


def _audio_dir() -> Path:
    d = Path(AUDIO_DIR) if Path(AUDIO_DIR).is_absolute() and not AUDIO_DIR.startswith("/opt") else Path(__file__).parent / "audio"
    d.mkdir(parents=True, exist_ok=True)
    return d


async def _synthesize(text: str, out_path: str) -> None:
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    await communicate.save(out_path)


def synthesize_sections(sections: list[dict]) -> str:
    """
    把各板块分别合成 MP3，再用 ffmpeg 拼接成一个文件。
    返回最终 MP3 的路径。
    """
    audio_dir = _audio_dir()
    date_str  = datetime.now().strftime("%Y%m%d")
    parts     = []

    for i, section in enumerate(sections):
        part_path = str(audio_dir / f"{date_str}_part{i:02d}_{section['key']}.mp3")
        print(f"  TTS [{section['title']}]", end=" ", flush=True)
        asyncio.run(_synthesize(section["text"], part_path))
        parts.append(part_path)
        print("✓")

    # 用 ffmpeg 拼接
    final_path = str(audio_dir / f"{date_str}_briefing.mp3")
    list_file  = str(audio_dir / f"{date_str}_parts.txt")

    with open(list_file, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")

    ffmpeg_bin = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"
    result = subprocess.run(
        [ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", "-i", list_file,
         "-c", "copy", final_path],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 拼接失败：{result.stderr.decode()}")

    # 清理分段文件
    for p in parts:
        os.remove(p)
    os.remove(list_file)

    size_mb = os.path.getsize(final_path) / 1024 / 1024
    print(f"音频生成完成：{final_path}（{size_mb:.1f} MB）")
    return final_path
