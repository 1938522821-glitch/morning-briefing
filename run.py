#!/usr/bin/env python3
"""
早报生成主程序。
用法：python run.py
"""
import sys
from datetime import datetime

def main():
    print(f"\n{'='*50}")
    print(f"每日早报生成开始 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    # 1. 抓新闻
    print("【1/3】抓取新闻...")
    from news_fetcher import fetch_all
    news = fetch_all()
    for section, articles in news.items():
        print(f"  {section}: {len(articles)} 条")

    # 2. 生成脚本
    print("\n【2/3】生成播客脚本（Claude）...")
    from script_generator import generate_full_script
    full_text, sections = generate_full_script(news)

    # 保存脚本备份
    from pathlib import Path
    script_dir = Path(__file__).parent / "scripts"
    script_dir.mkdir(parents=True, exist_ok=True)
    script_path = script_dir / f"{datetime.now().strftime('%Y%m%d')}_script.txt"
    script_path.write_text(full_text, encoding="utf-8")
    print(f"脚本已保存：{script_path}")

    # 3. TTS 合成
    print("\n【3/3】TTS 语音合成（edge-tts）...")
    from tts_generator import synthesize_sections
    audio_path = synthesize_sections(sections)

    # 3.5 提炼今日热点关键词，写入 .meta.json（供播客单集标题使用）
    from script_generator import generate_episode_title
    import json
    highlights = generate_episode_title(full_text)
    print(f"今日亮点：{highlights}")
    meta_path = Path(audio_path).with_suffix(".meta.json")
    meta_path.write_text(json.dumps({"highlights": highlights}, ensure_ascii=False), encoding="utf-8")

    # 4. 更新 Alexa feed + 播客 RSS feed
    from alexa_feed import update_feed
    update_feed(audio_path)

    from podcast_feed import update_podcast_feed
    update_podcast_feed()

    # 5. 推送到 GitHub Pages
    print("\n【4/4】推送到 GitHub...")
    import subprocess
    from config import FEED_PATH
    repo_dir = Path(__file__).parent
    subprocess.run(["git", "-C", str(repo_dir), "add", "feed.json", "podcast.xml", "cover.jpg",
                    f"audio/{Path(audio_path).name}", f"audio/{meta_path.name}"], check=True)
    subprocess.run(["git", "-C", str(repo_dir), "commit", "-m", f"briefing {datetime.now().strftime('%Y-%m-%d')}"], check=True)
    import os
    remote = os.environ.get("GITHUB_REMOTE", "origin")
    subprocess.run(["git", "-C", str(repo_dir), "push", remote, "main"], check=True)
    print("推送完成！")

    print(f"\n{'='*50}")
    print("早报生成完成！")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
