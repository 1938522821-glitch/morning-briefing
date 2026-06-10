"""
用 edge-tts 把晚安电台脚本转为 MP3，按板块分段生成（不同语速）再合并。
"""
import asyncio
import os
import subprocess
from pathlib import Path
from datetime import datetime
import edge_tts
from config import AUDIO_DIR, TTS_VOICE, TTS_PITCH


SLEEP_MUSIC = Path(__file__).parent / "assets" / "sleep_music.mp3"


def _audio_dir() -> Path:
    d = Path(AUDIO_DIR)
    d.mkdir(parents=True, exist_ok=True)
    return d


async def _synthesize(text: str, out_path: str, rate: str = "+0%") -> None:
    communicate = edge_tts.Communicate(text, TTS_VOICE, rate=rate, pitch=TTS_PITCH)
    await communicate.save(out_path)


def synthesize_sections(sections: list[dict]) -> str:
    """
    把各板块分别合成 MP3（各自语速），再用 ffmpeg 拼接成一个文件。
    返回最终 MP3 的路径。
    """
    audio_dir = _audio_dir()
    stamp     = datetime.now().strftime("%Y%m%d_%H%M")
    parts     = []

    for i, section in enumerate(sections):
        part_path = str(audio_dir / f"{stamp}_part{i:02d}_{section['key']}.mp3")
        rate = section.get("tts_rate", "+0%")
        print(f"  TTS [{section['title']}] (rate {rate})", end=" ", flush=True)
        asyncio.run(_synthesize(section["text"], part_path, rate))
        parts.append(part_path)
        print("✓")

    final_path = str(audio_dir / f"{stamp}_evening.mp3")
    list_file  = str(audio_dir / f"{stamp}_parts.txt")

    concat_files = list(parts)
    if SLEEP_MUSIC.exists():
        concat_files.append(str(SLEEP_MUSIC))
    else:
        print(f"  （未找到安眠音乐素材：{SLEEP_MUSIC}，跳过）")

    with open(list_file, "w") as f:
        for p in concat_files:
            f.write(f"file '{p}'\n")

    ffmpeg_bin = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"
    # 各分段语速/格式不完全一致，且最后接的安眠音乐采样率不同，统一重新编码避免拼接异常
    result = subprocess.run(
        [ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", "-i", list_file,
         "-c:a", "libmp3lame", "-b:a", "96k", "-ar", "44100", final_path],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 拼接失败：{result.stderr.decode()}")

    for p in parts:
        os.remove(p)
    os.remove(list_file)

    size_mb = os.path.getsize(final_path) / 1024 / 1024
    print(f"音频生成完成：{final_path}（{size_mb:.1f} MB）")
    return final_path
