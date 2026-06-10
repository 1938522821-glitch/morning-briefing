"""
用 Claude 把原始新闻列表生成播客风格中文脚本。
目标时长：约 60 分钟（~8500 字）。
"""
import anthropic
from datetime import datetime
from config import CLAUDE_API_KEY

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

SECTION_PROMPTS = {
    "intro": {
        "title": "开场",
        "target_words": 300,
        "instruction": "写一段热情的播客开场白，像一个聪明幽默的朋友早上见面一样。提到今天是{date}，{weekday}。预告今天节目的几个亮点话题（从后面板块中挑两三个最有趣的）。语气轻松，偶尔开个小玩笑。",
    },
    "international": {
        "title": "国际形势",
        "target_words": 1400,
        "instruction": "解读国际新闻，条数不固定——重要的事件多花时间深入讲（发生了什么→为什么重要→你的点评），次要的简单带过甚至跳过。要有观点，不要只念稿子。用播客主持人的口吻，像在和朋友聊天。",
    },
    "ai_tech": {
        "title": "AI 与科技",
        "target_words": 1400,
        "instruction": "解读 AI 和科技新闻，条数不固定，按重要性和趣味性分配篇幅。对 AI 进展要有判断：这是真突破还是炒概念？对科技公司动态要有态度。可以兴奋、可以质疑，但要言之有物。用中文，但专有名词（如 GPT-5、Claude 等）保留英文。",
    },
    "stocks": {
        "title": "市场与股票",
        "target_words": 1100,
        "instruction": "解读财经市场新闻，条数不固定。提到主要指数表现（美股三大指数、相关板块）。分析背后的逻辑，不要只报数字。如果今天市场平淡没有大新闻，可以简短带过，把篇幅留给更有料的板块。可以提醒听众注意什么机会或风险，但不要给具体投资建议。轻松幽默地聊，不要太严肃。",
    },
    "ireland": {
        "title": "爱尔兰综合",
        "target_words": 1800,
        "instruction": (
            "解读爱尔兰相关新闻，重点关注：就业市场动态（招聘/裁员/行业变化）、"
            "房地产市场（租金/房价/政策）。其他本地政治社会民生新闻可以作为补充。"
            "不需要每个方面都强行覆盖——如果今天某个方面没有重要新闻就跳过，"
            "如果某条新闻特别重要或特别有意思，可以多花时间深入讲。要有在当地生活的人才有的视角，接地气，"
            "对找工作、租房买房的听众有实用价值。"
        ),
    },
    "global_hot": {
        "title": "全球热点",
        "target_words": 1200,
        "instruction": "选今天最热的全球话题，数量不限——少则1-2个深聊，多则3-4个简单带过，根据话题本身的分量决定篇幅。可以轻松一点，社会热点、趣事、争议话题都行。这是节目的「聊天区」，像朋友之间聊八卦一样，但要有深度。",
    },
    "outro": {
        "title": "结尾",
        "target_words": 400,
        "instruction": "节目收尾。用一两句话总结今天每个板块的核心信息。最后送给听众一句话作为今天的心态或行动建议。温暖收场，期待明天再见。",
    },
}


def _format_articles(articles: list[dict]) -> str:
    lines = []
    for i, a in enumerate(articles, 1):
        lines.append(f"{i}. 标题：{a['title']}")
        if a.get("summary"):
            lines.append(f"   摘要：{a['summary'][:300]}")
    return "\n".join(lines)


def generate_section(section_key: str, articles: list[dict], all_sections_preview: str = "") -> str:
    cfg = SECTION_PROMPTS[section_key]
    date_str = datetime.now().strftime("%Y年%m月%d日")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday  = weekdays[datetime.now().weekday()]

    instruction = cfg["instruction"].format(date=date_str, weekday=weekday)

    articles_text = _format_articles(articles) if articles else "（暂无具体新闻，请根据常识发挥）"

    system = (
        "你是一位受欢迎的中文播客主持人，风格像「得到」和「故事FM」的结合体——"
        "有深度、有观点、有温度、偶尔幽默。"
        "你的听众是在爱尔兰生活的华人，关心国际形势、科技、投资和本地生活。"
        "用自然流畅的中文口语，避免书面腔。不要用标题、不要用编号列表，"
        "写成连续的播客脚本，直接就是主持人说的话。"
        "不要说「好的」「当然」「接下来我们」等废话开头。"
    )

    user = (
        f"请为「{cfg['title']}」板块写约 {cfg['target_words']} 字的播客脚本。\n\n"
        f"要求：{instruction}\n\n"
        f"今日新闻原料：\n{articles_text}\n\n"
        f"{('今日节目整体预览（开场板块参考用）：' + chr(10) + all_sections_preview) if all_sections_preview else ''}"
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
    """提炼今天节目里最值得关注的几个热点关键词，用于单集标题。"""
    user = (
        "以下是今天播客节目的完整脚本。请提炼出今天最值得关注的2-4个话题关键词或短语，"
        "用「/」分隔，整体不超过30个字，不要标点编号、不要解释，直接输出关键词本身。\n\n"
        f"{full_text[:8000]}"
    )
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text.strip()


def generate_full_script(news: dict[str, list[dict]]) -> tuple[str, list[dict]]:
    """
    返回 (完整脚本文本, 各段落列表[{title, text}])
    """
    sections = []

    # 先生成各内容板块（除开场/结尾）
    content_keys = ["international", "ai_tech", "stocks", "ireland", "global_hot"]

    print("生成各板块脚本...")
    for key in content_keys:
        print(f"  [{SECTION_PROMPTS[key]['title']}]", end=" ", flush=True)
        text = generate_section(key, news.get(key, []))
        sections.append({"key": key, "title": SECTION_PROMPTS[key]["title"], "text": text})
        print(f"✓ ({len(text)} 字)")

    # 用各板块标题给开场用
    preview = "\n".join(f"- {s['title']}" for s in sections)

    print("  [开场]", end=" ", flush=True)
    intro = generate_section("intro", [], all_sections_preview=preview)
    print(f"✓ ({len(intro)} 字)")

    print("  [结尾]", end=" ", flush=True)
    outro_articles = [{"title": s["title"], "summary": s["text"][:100]} for s in sections]
    outro = generate_section("outro", outro_articles)
    print(f"✓ ({len(outro)} 字)")

    ordered = (
        [{"key": "intro", "title": "开场", "text": intro}]
        + sections
        + [{"key": "outro", "title": "结尾", "text": outro}]
    )

    full_text = "\n\n".join(s["text"] for s in ordered)
    total = len(full_text)
    print(f"\n脚本总字数：{total}（约 {total // 150} 分钟）")

    return full_text, ordered
