"""
抓取各板块新闻，返回结构化文章列表。
优先用免费 RSS，NewsAPI 作补充（需 key）。
"""
import re
import feedparser
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from config import NEWSAPI_KEY

SCRIPT_DIR = Path(__file__).parent / "scripts"


def get_recent_scripts(days: int = 1, max_chars: int = 6000) -> str:
    """
    读取最近几天的早报脚本，用于提示 Claude 避免重复昨天讲过的话题。
    每天的脚本截取前 max_chars 字符（避免 prompt 过长）。
    """
    texts = []
    today = datetime.now().date()
    for i in range(1, days + 1):
        d = today - timedelta(days=i)
        p = SCRIPT_DIR / f"{d.strftime('%Y%m%d')}_script.txt"
        if p.exists():
            content = p.read_text(encoding="utf-8")[:max_chars]
            texts.append(f"--- {d.strftime('%Y-%m-%d')} 的节目内容节选 ---\n{content}")
    return "\n\n".join(texts)

HEADERS = {"User-Agent": "MorningBriefing/1.0"}

# ── RSS 源配置 ─────────────────────────────────────────────────────────────
RSS_SOURCES = {
    "international": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://www.theguardian.com/world/rss",
    ],
    "ai_tech": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://hnrss.org/frontpage?points=100",
        "https://www.wired.com/feed/rss",
    ],
    "stocks": [
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://www.marketwatch.com/rss/topstories",
        "https://feeds.content.dowjones.io/public/rss/mw_marketpulse",
    ],
    "ireland": [
        "https://www.irishtimes.com/arc/outboundfeeds/rss/",
        "https://www.thejournal.ie/feed/",
        "https://www.rte.ie/feeds/rss/?index=/news/&limit=20",
    ],
    "global_hot": [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
    ],
}


def _fetch_rss(url: str, limit: int = 6) -> list[dict]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        items = []
        for entry in feed.entries[:limit]:
            title   = entry.get("title", "").strip()
            summary = entry.get("summary", entry.get("description", "")).strip()
            summary = re.sub(r"<[^>]+>", "", summary)[:500]
            link    = entry.get("link", "")
            if title:
                items.append({"title": title, "summary": summary, "url": link})
        return items
    except Exception as e:
        print(f"[RSS error] {url}: {e}")
        return []


def _fetch_newsapi(query: str, limit: int = 5) -> list[dict]:
    if not NEWSAPI_KEY:
        return []
    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "sortBy": "publishedAt",
                "pageSize": limit,
                "language": "en",
                "apiKey": NEWSAPI_KEY,
            },
            timeout=10,
            headers=HEADERS,
        )
        data = resp.json()
        items = []
        for a in data.get("articles", []):
            title   = (a.get("title") or "").strip()
            summary = (a.get("description") or "").strip()[:500]
            url     = a.get("url", "")
            if title and "[Removed]" not in title:
                items.append({"title": title, "summary": summary, "url": url})
        return items
    except Exception as e:
        print(f"[NewsAPI error] {query}: {e}")
        return []


def fetch_all() -> dict[str, list[dict]]:
    # 收集所有 (section, url) 任务并发执行
    tasks = [(section, url) for section, urls in RSS_SOURCES.items() for url in urls]

    section_articles: dict[str, list[dict]] = {s: [] for s in RSS_SOURCES}

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {executor.submit(_fetch_rss, url, 5): section for section, url in tasks}
        for future in as_completed(future_map):
            section = future_map[future]
            try:
                section_articles[section].extend(future.result())
            except Exception:
                pass

    result = {}
    for section, articles in section_articles.items():
        seen = set()
        deduped = []
        for a in articles:
            key = a["title"][:30]
            if key not in seen:
                seen.add(key)
                deduped.append(a)
        cap = 18 if section == "ireland" else 12
        result[section] = deduped[:cap]
        print(f"  {section}: {len(result[section])} 条")

    result["ai_tech"] = (result.get("ai_tech") or []) + _fetch_newsapi("artificial intelligence OR ChatGPT OR LLM", 5)

    return result
