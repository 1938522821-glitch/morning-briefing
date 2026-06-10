#!/usr/bin/env python3
"""
深度思考（深度国际局势解读）生成主程序。
仅发布到 Spotify，不提交小宇宙——所以脚本可以放开聊敏感的国际政治/军事话题。
用法：python run.py
"""
from datetime import datetime
from pathlib import Path

from config import MORNING_SCRIPT_DIR


def get_morning_script() -> str:
    """读取今天早上的早报脚本全文，没有就返回空字符串。"""
    date_str = datetime.now().strftime("%Y%m%d")
    path = MORNING_SCRIPT_DIR / f"{date_str}_script.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def main():
    print(f"\n{'='*50}")
    print(f"深度思考生成开始 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    # 1. 取材：今天早报脚本（用于挑选今晚深度解读的话题）
    print("【1/3】准备素材...")
    morning_script = get_morning_script()
    if morning_script:
        print(f"  早报脚本：{len(morning_script)} 字")
    else:
        print("  未找到今天的早报脚本，将由 Claude 自由选择话题")

    # 2. 生成脚本
    print("\n【2/3】生成播客脚本（Claude）...")
    from script_generator import generate_full_script
    full_text, sections = generate_full_script(morning_script)

    script_dir = Path(__file__).parent / "scripts"
    script_dir.mkdir(parents=True, exist_ok=True)
    script_path = script_dir / f"{datetime.now().strftime('%Y%m%d')}_deepdive_script.txt"
    script_path.write_text(full_text, encoding="utf-8")
    print(f"脚本已保存：{script_path}")

    # 3. TTS 合成
    print("\n【3/4】TTS 语音合成（edge-tts）...")
    from tts_generator import synthesize_sections
    audio_path = synthesize_sections(sections)

    # 提炼今晚话题关键词，写入 .meta.json（供播客单集标题使用）
    from script_generator import generate_episode_title
    import json
    highlights = generate_episode_title(full_text)
    print(f"今晚话题：{highlights}")
    meta_path = Path(audio_path).with_suffix(".meta.json")
    meta_path.write_text(json.dumps({"highlights": highlights}, ensure_ascii=False), encoding="utf-8")

    # 更新播客 RSS feed
    from podcast_feed import update_podcast_feed
    update_podcast_feed()

    # 4. 推送到 GitHub Pages（复用早报仓库的 deepdive/ 子目录）
    print("\n【4/4】推送到 GitHub...")
    import subprocess
    repo_dir = Path(__file__).parent.parent
    rel_audio = f"deepdive/audio/{Path(audio_path).name}"
    rel_meta = f"deepdive/audio/{meta_path.name}"
    subprocess.run(["git", "-C", str(repo_dir), "add", "deepdive/podcast.xml",
                    "deepdive/cover.jpg", rel_audio, rel_meta], check=True)
    subprocess.run(["git", "-C", str(repo_dir), "commit", "-m", f"deepdive {datetime.now().strftime('%Y-%m-%d')}"], check=True)
    import os
    remote = os.environ.get("GITHUB_REMOTE", "origin")
    subprocess.run(["git", "-C", str(repo_dir), "push", remote, "main"], check=True)
    print("推送完成！")

    print(f"\n{'='*50}")
    print("深度思考生成完成！")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
