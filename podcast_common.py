"""
共享工具：生成播客封面图 + RSS feed（标准 podcast RSS，可被任意播客 App 订阅）。
"""
import re
import subprocess
from pathlib import Path
from datetime import datetime
from email.utils import formatdate
from xml.sax.saxutils import escape

FFPROBE = "/opt/homebrew/bin/ffprobe" if Path("/opt/homebrew/bin/ffprobe").exists() else "ffprobe"


def make_cover_image(path: str, title: str, subtitle: str = "",
                      bg=(30, 30, 46), fg=(255, 255, 255)) -> None:
    """生成一张 1400x1400 的封面图（如果还不存在）。"""
    if Path(path).exists():
        return
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (1400, 1400), bg)
    draw = ImageDraw.Draw(img)

    font_path = None
    for fp in ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Light.ttc"]:
        if Path(fp).exists():
            font_path = fp
            break

    title_font = ImageFont.truetype(font_path, 130) if font_path else ImageFont.load_default()
    sub_font = ImageFont.truetype(font_path, 55) if font_path else ImageFont.load_default()

    bbox = draw.textbbox((0, 0), title, font=title_font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((1400 - w) / 2, (1400 - h) / 2 - 80), title, font=title_font, fill=fg)

    if subtitle:
        bbox2 = draw.textbbox((0, 0), subtitle, font=sub_font)
        w2, h2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
        draw.text(((1400 - w2) / 2, (1400 - h2) / 2 + 100), subtitle, font=sub_font, fill=fg)

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=90)


def _get_duration(path: str) -> str:
    try:
        out = subprocess.run(
            [FFPROBE, "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path],
            capture_output=True, text=True,
        )
        seconds = float(out.stdout.strip())
        h, rem = divmod(int(seconds), 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    except Exception:
        return "00:00:00"


def build_rss(channel_title: str, channel_desc: str, channel_link: str,
               audio_base_url: str, audio_dir: str, pattern: str,
               title_fn, cover_url: str, output_path: str,
               author: str = "Zixuan", category: str = "News") -> None:
    files = sorted(Path(audio_dir).glob(pattern), reverse=True)

    items_xml = []
    for f in files:
        m = re.match(r"(\d{8})_", f.name)
        if m:
            dt = datetime.strptime(m.group(1), "%Y%m%d")
        else:
            dt = datetime.fromtimestamp(f.stat().st_mtime)

        pub_date = formatdate(f.stat().st_mtime, usegmt=True)
        size = f.stat().st_size
        duration = _get_duration(str(f))
        title = escape(title_fn(dt))
        url = f"{audio_base_url}/{f.name}"

        items_xml.append(f"""
    <item>
      <title>{title}</title>
      <pubDate>{pub_date}</pubDate>
      <enclosure url="{escape(url)}" length="{size}" type="audio/mpeg"/>
      <guid isPermaLink="false">{escape(f.name)}</guid>
      <itunes:duration>{duration}</itunes:duration>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{escape(channel_title)}</title>
    <link>{escape(channel_link)}</link>
    <language>zh-cn</language>
    <description>{escape(channel_desc)}</description>
    <itunes:author>{escape(author)}</itunes:author>
    <itunes:image href="{escape(cover_url)}"/>
    <itunes:category text="{escape(category)}"/>
    <itunes:explicit>false</itunes:explicit>
    <image>
      <url>{escape(cover_url)}</url>
      <title>{escape(channel_title)}</title>
      <link>{escape(channel_link)}</link>
    </image>{''.join(items_xml)}
  </channel>
</rss>
"""
    Path(output_path).write_text(rss, encoding="utf-8")
    print(f"Podcast feed 已更新：{output_path}（{len(files)} 集）")
