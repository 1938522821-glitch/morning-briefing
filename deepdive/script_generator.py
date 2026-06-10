"""
用 Claude 生成"深度思考"播客脚本——深度国际/地缘局势分析。
仅发布到 Spotify（不提交小宇宙），所以可以放开聊敏感的国际政治/军事话题。
结构：开场 → 深度解读 → 结语
目标时长：约 20-25 分钟。
"""
import anthropic
from datetime import datetime
from config import CLAUDE_API_KEY

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

SECTION_PROMPTS = {
    "intro": {
        "title": "开场",
        "target_words": 200,
        "max_tokens": 600,
        "instruction": (
            "简短开场，告诉听众今晚要深入聊一个国际/地缘局势话题。"
            "可以提一句为什么今天选这个话题、它为什么值得花时间深入了解。"
            "语气沉稳但不沉闷，像资深时事评论员开场。"
        ),
    },
    "deepdive": {
        "title": "深度解读",
        "target_words": 3000,
        "max_tokens": 4500,
        "instruction": (
            "从今天的新闻素材里，挑选1个（最多2个）今天最值得深入分析的国际/地缘政治/军事/外交话题。"
            "做一期真正有深度的解读，可以包括：\n"
            "- 事情的来龙去脉（不只是今天发生了什么，还有它的历史背景和发展脉络）\n"
            "- 涉及各方的立场、利益和策略——尽量呈现多个视角，不要只站一边\n"
            "- 这件事为什么重要、可能如何发展、有哪些情景\n"
            "- 对普通人（包括在海外生活的华人）可能产生的实际影响\n"
            "- 你自己的分析判断和观点，可以有态度，但要言之有据，避免简单的立场宣泄或情绪化表达\n"
            "可以适当使用历史类比、数据、专家观点等增加深度。"
            "用自然的口语，但内容密度要高，像深度新闻播客（如《忽左忽右》《日谈公园》时事篇）的水准。"
        ),
    },
    "outro": {
        "title": "结语",
        "target_words": 200,
        "max_tokens": 600,
        "instruction": (
            "简短收尾。一两句话总结今天聊的话题最关键的一点，"
            "可以留一个开放性的思考问题给听众，最后说一句期待下次见面的话。"
            "不需要晚安/睡眠相关的语气，正常的播客收尾即可。"
        ),
    },
}


def generate_section(section_key: str, source_material: str = "", context_text: str = "") -> str:
    cfg = SECTION_PROMPTS[section_key]
    date_str = datetime.now().strftime("%Y年%m月%d日")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday  = weekdays[datetime.now().weekday()]

    system = (
        "你是一档深度时事分析播客「深度思考」的主持人，风格类似资深国际新闻评论员——"
        "见解犀利、有知识深度，敢于讨论敏感的国际政治、军事、外交话题，"
        "但保持理性、多角度，不传播未经核实的极端说法。"
        "你的听众是关心国际局势、希望被当作成年人对待、想听到真实分析而不是和稀泥的人。"
        "用自然流畅的中文口语，避免书面腔。不要用标题、不要用编号列表，"
        "写成连续的播客脚本，直接就是主持人说的话。"
        "不要说「好的」「当然」「接下来我们」等废话开头。"
    )

    user = (
        f"今天是{date_str}，{weekday}。\n\n"
        f"请为「{cfg['title']}」板块写约 {cfg['target_words']} 字的播客脚本。\n\n"
        f"要求：{cfg['instruction']}\n\n"
        f"{('今日新闻素材（来自早报脚本，可从中挑选话题，也可以结合你自己的知识补充背景）：' + chr(10) + source_material) if source_material else ''}\n"
        f"{('今晚已经选定/讲过的话题（用于其他板块呼应）：' + chr(10) + context_text) if context_text else ''}"
        f"\n\n直接输出脚本正文，不要任何多余说明。"
    )

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=cfg.get("max_tokens", 3000),
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text.strip()


def generate_episode_title(full_text: str) -> str:
    """提炼今晚深度话题的关键词，用于单集标题。"""
    user = (
        "以下是今晚播客节目的完整脚本。请提炼出今晚深度解读的话题，"
        "用「/」分隔的2-4个关键词或短语概括，整体不超过30个字，"
        "不要标点编号、不要解释，直接输出关键词本身。\n\n"
        f"{full_text[:8000]}"
    )
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text.strip()


def generate_full_script(morning_script: str) -> tuple[str, list[dict]]:
    """
    返回 (完整脚本文本, 各段落列表[{key, title, text}])
    morning_script: 今天早报脚本全文，作为深度解读的话题素材来源。
    """
    sections = []
    print("生成各板块脚本...")

    source_material = morning_script[:10000] if morning_script else ""

    # 深度解读：先生成主体内容，决定今天聊什么话题
    print("  [深度解读]", end=" ", flush=True)
    deepdive = generate_section("deepdive", source_material=source_material)
    sections.append({"key": "deepdive", "title": "深度解读", "text": deepdive})
    print(f"✓ ({len(deepdive)} 字)")

    # 开场：基于深度解读内容生成预告
    print("  [开场]", end=" ", flush=True)
    intro = generate_section("intro", context_text=deepdive[:1500])
    sections.insert(0, {"key": "intro", "title": "开场", "text": intro})
    print(f"✓ ({len(intro)} 字)")

    # 结语：基于深度解读内容总结
    print("  [结语]", end=" ", flush=True)
    outro = generate_section("outro", context_text=deepdive[-1500:])
    sections.append({"key": "outro", "title": "结语", "text": outro})
    print(f"✓ ({len(outro)} 字)")

    full_text = "\n\n".join(s["text"] for s in sections)
    total = len(full_text)
    print(f"\n脚本总字数：{total}（约 {total // 150} 分钟）")

    return full_text, sections
