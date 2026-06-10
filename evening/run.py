#!/usr/bin/env python3
"""
晚安电台生成主程序。
用法：python run.py
"""
from datetime import datetime
from pathlib import Path


def main():
    print(f"\n{'='*50}")
    print(f"晚安电台生成开始 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    # 1. 取材：今天早报脚本 + 新闻素材
    print("【1/4】准备素材...")
    from news_fetcher import get_morning_script, get_topic_news
    morning_script = get_morning_script()
    if morning_script:
        print(f"  早报脚本：{len(morning_script)} 字")
    else:
        print("  未找到今天的早报脚本，今日回顾将自由发挥")
    topic_news = get_topic_news()

    # 2. 生成脚本
    print("\n【2/4】生成播客脚本（Claude）...")
    from script_generator import generate_full_script
    full_text, sections = generate_full_script(morning_script, topic_news)

    script_dir = Path(__file__).parent / "scripts"
    script_dir.mkdir(parents=True, exist_ok=True)
    script_path = script_dir / f"{datetime.now().strftime('%Y%m%d')}_evening_script.txt"
    script_path.write_text(full_text, encoding="utf-8")
    print(f"脚本已保存：{script_path}")

    # 3. TTS 合成
    print("\n【3/4】TTS 语音合成（edge-tts）...")
    from tts_generator import synthesize_sections
    audio_path = synthesize_sections(sections)

    # 3.5 提炼今晚话题关键词，写入 .meta.json（供播客单集标题使用）
    from script_generator import generate_episode_title
    import json
    highlights = generate_episode_title(full_text)
    print(f"今晚亮点：{highlights}")
    meta_path = Path(audio_path).with_suffix(".meta.json")
    meta_path.write_text(json.dumps({"highlights": highlights}, ensure_ascii=False), encoding="utf-8")

    # 4. 更新 Alexa feed + 播客 RSS feed
    from alexa_feed import update_feed
    update_feed(audio_path)

    from podcast_feed import update_podcast_feed
    update_podcast_feed()

    # 5. 推送到 GitHub Pages（复用早报仓库的 evening/ 子目录）
    print("\n【4/4】推送到 GitHub...")
    import subprocess
    repo_dir = Path(__file__).parent.parent
    rel_audio = f"evening/audio/{Path(audio_path).name}"
    rel_meta = f"evening/audio/{meta_path.name}"
    subprocess.run(["git", "-C", str(repo_dir), "add", "evening/feed.json", "evening/podcast.xml",
                    "evening/cover.jpg", rel_audio, rel_meta], check=True)
    subprocess.run(["git", "-C", str(repo_dir), "commit", "-m", f"evening radio {datetime.now().strftime('%Y-%m-%d')}"], check=True)
    import os
    remote = os.environ.get("GITHUB_REMOTE", "origin")
    subprocess.run(["git", "-C", str(repo_dir), "push", remote, "main"], check=True)
    print("推送完成！")

    print(f"\n{'='*50}")
    print("晚安电台生成完成！")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
