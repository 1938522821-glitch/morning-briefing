"""
用 Claude 生成"晚安电台"播客脚本。
结构：今日回顾(放松) → 深度话题 → 读书/历史 → 放松呼吸练习 → 晚安语
目标时长：约 35-40 分钟。
"""
import anthropic
from datetime import datetime
from config import CLAUDE_API_KEY

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

SECTION_PROMPTS = {
    "review": {
        "title": "今日回顾",
        "target_words": 700,
        "tts_rate": "+0%",
        "instruction": (
            "用轻松、放松的语气，回顾一下今天早上节目里聊到的几个要点（国际形势、AI科技、市场、爱尔兰、全球热点）。"
            "不是重复念一遍，而是像一天结束后跟朋友闲聊「今天发生了点啥」，挑一两个最值得记住的点说说感想。"
            "语速感觉上要比早上的节目慢一点、更松弛。"
        ),
    },
    "deep_topic": {
        "title": "深度话题",
        "target_words": 2200,
        "tts_rate": "+0%",
        "instruction": (
            "从今天的新闻素材里选一个最值得深入聊的话题（可以是科技、社会、国际议题等），"
            "做一期有深度的探讨：背景是什么、为什么重要、有哪些不同角度的看法、你自己怎么看。"
            "可以适当引申到更大的趋势或哲学思考。语气沉稳、有思考的深度，但依然口语化、像朋友间的深聊，不要说教。"
        ),
    },
    "book_history": {
        "title": "读书与历史",
        "target_words": 1500,
        "tts_rate": "+0%",
        "instruction": (
            "分享一个和今天主题（或随便什么有意思的领域）相关的书籍推荐，或者一段历史上的今天/相关历史故事。"
            "讲清楚背景、有意思的细节、对今天的人有什么启发。语气像深夜读书节目主持人，娓娓道来，"
            "有画面感和故事性，让听众放松地听一个故事。"
        ),
    },
    "relax": {
        "title": "放松练习",
        "target_words": 700,
        "tts_rate": "-15%",
        "instruction": (
            "带听众做一段简单的呼吸放松练习，帮助准备入睡。语速要慢，多用「……」表示停顿，"
            "引导听众注意呼吸、放松身体各部位（从头到脚），可以用一些温和的意象（比如海浪、星空）。"
            "全程语气轻柔、缓慢、安抚，像睡前冥想引导。不需要互动提问，直接用引导语。"
        ),
    },
    "goodnight": {
        "title": "晚安语",
        "target_words": 250,
        "tts_rate": "-15%",
        "instruction": (
            "用温暖、轻柔的语气做今晚的收尾。简短回顾一下今晚聊的内容（一句话带过即可），"
            "送给听众一句晚安祝福或者一句值得带入梦乡的话。语气要非常轻、慢，像哄人入睡。"
        ),
    },
}


def _format_articles(articles: list[dict]) -> str:
    lines = []
    for i, a in enumerate(articles, 1):
        lines.append(f"{i}. 标题：{a['title']}")
        if a.get("summary"):
            lines.append(f"   摘要：{a['summary'][:300]}")
    return "\n".join(lines)


def generate_section(section_key: str, context_text: str = "") -> str:
    cfg = SECTION_PROMPTS[section_key]
    date_str = datetime.now().strftime("%Y年%m月%d日")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday  = weekdays[datetime.now().weekday()]

    system = (
        "你是一档深夜播客「晚安电台」的主持人，风格温暖、有思考深度，又不失轻松感。"
        "你的听众是在爱尔兰生活的华人，刚结束一天的工作，准备放松入睡。"
        "用自然流畅的中文口语，避免书面腔。不要用标题、不要用编号列表，"
        "写成连续的播客脚本，直接就是主持人说的话。"
        "不要说「好的」「当然」「接下来我们」等废话开头。"
    )

    user = (
        f"今天是{date_str}，{weekday}。\n\n"
        f"请为「{cfg['title']}」板块写约 {cfg['target_words']} 字的播客脚本。\n\n"
        f"要求：{cfg['instruction']}\n\n"
        f"{('参考素材：' + chr(10) + context_text) if context_text else ''}"
        f"\n\n直接输出脚本正文，不要任何多余说明。"
    )

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text.strip()


def generate_episode_title(full_text: str) -> str:
    """提炼今晚节目里最值得关注的几个话题关键词，用于单集标题。"""
    user = (
        "以下是今晚播客节目的完整脚本。请提炼出今晚最值得关注的2-4个话题关键词或短语，"
        "用「/」分隔，整体不超过30个字，不要标点编号、不要解释，直接输出关键词本身。\n\n"
        f"{full_text[:8000]}"
    )
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text.strip()


def generate_full_script(morning_script: str, topic_news: dict) -> tuple[str, list[dict]]:
    """
    返回 (完整脚本文本, 各段落列表[{key, title, text, tts_rate}])
    """
    sections = []

    print("生成各板块脚本...")

    # 今日回顾：用早报脚本作为素材
    print("  [今日回顾]", end=" ", flush=True)
    review_context = morning_script[:6000] if morning_script else ""
    review = generate_section("review", review_context)
    sections.append({"key": "review", "title": "今日回顾", "text": review,
                      "tts_rate": SECTION_PROMPTS["review"]["tts_rate"]})
    print(f"✓ ({len(review)} 字)")

    # 深度话题：从国际/AI/全球热点里挑素材
    print("  [深度话题]", end=" ", flush=True)
    candidates = (
        (topic_news.get("international") or [])
        + (topic_news.get("ai_tech") or [])
        + (topic_news.get("global_hot") or [])
    )
    topic_context = _format_articles(candidates[:15])
    deep_topic = generate_section("deep_topic", topic_context)
    sections.append({"key": "deep_topic", "title": "深度话题", "text": deep_topic,
                      "tts_rate": SECTION_PROMPTS["deep_topic"]["tts_rate"]})
    print(f"✓ ({len(deep_topic)} 字)")

    # 读书与历史：自由发挥
    print("  [读书与历史]", end=" ", flush=True)
    book_history = generate_section("book_history")
    sections.append({"key": "book_history", "title": "读书与历史", "text": book_history,
                      "tts_rate": SECTION_PROMPTS["book_history"]["tts_rate"]})
    print(f"✓ ({len(book_history)} 字)")

    # 放松练习
    print("  [放松练习]", end=" ", flush=True)
    relax = generate_section("relax")
    sections.append({"key": "relax", "title": "放松练习", "text": relax,
                      "tts_rate": SECTION_PROMPTS["relax"]["tts_rate"]})
    print(f"✓ ({len(relax)} 字)")

    # 晚安语
    print("  [晚安语]", end=" ", flush=True)
    goodnight = generate_section("goodnight")
    sections.append({"key": "goodnight", "title": "晚安语", "text": goodnight,
                      "tts_rate": SECTION_PROMPTS["goodnight"]["tts_rate"]})
    print(f"✓ ({len(goodnight)} 字)")

    full_text = "\n\n".join(s["text"] for s in sections)
    total = len(full_text)
    print(f"\n脚本总字数：{total}（约 {total // 150} 分钟）")

    return full_text, sections
