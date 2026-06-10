"""
用 Claude 生成"夜读与放空"播客脚本。
结构：寓言/历史/书籍故事 → 故事揭晓 → 放松呼吸练习 → 晚安语
目标时长：约 50 分钟。
"""
import anthropic
from datetime import datetime, timedelta
from pathlib import Path
from config import CLAUDE_API_KEY

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

SCRIPT_DIR = Path(__file__).parent / "scripts"


def get_recent_stories(days: int = 7, max_chars: int = 600) -> str:
    """
    读取最近几天的「故事」开头片段，用于提示 Claude 不要选择重复的
    寓言/历史事件/书籍案例。
    """
    texts = []
    today = datetime.now().date()
    for i in range(1, days + 1):
        d = today - timedelta(days=i)
        p = SCRIPT_DIR / f"{d.strftime('%Y%m%d')}_evening_script.txt"
        if p.exists():
            content = p.read_text(encoding="utf-8")[:max_chars]
            texts.append(f"--- {d.strftime('%Y-%m-%d')} ---\n{content}")
    return "\n\n".join(texts)

SECTION_PROMPTS = {
    "story": {
        "title": "故事",
        "target_words": 3200,
        "max_tokens": 4500,
        "tts_rate": "+0%",
        "instruction": (
            "故事的素材来源，每天从以下三种里选一种（注意多样化，不要每天都选同一种）：\n"
            "① 原创寓言——从科学、哲学、心理学、经济学、数学、生物学、社会学等任意学术领域里，"
            "挑一个研究生水平的概念或理论，编织成一则原创寓言故事；\n"
            "② 真实历史事件——挑一个有意思的真实历史事件（比如重大科学发现的曲折过程、"
            "工程或商业史上的经典案例、影响深远的决策失误等），用讲故事的方式重新讲述，"
            "还原事件里关键人物的处境、决策和转折；\n"
            "③ 非虚构书籍里的故事——取材于一本有意思的纪实/科普/商业类书籍里的核心案例或故事，"
            "用讲故事的方式复述这个案例本身。\n"
            "无论选哪种，都不要在故事里直接点明对应的概念名称、历史事件名称或书名/作者——"
            "先把故事完整、生动地讲出来：要有具体的人物、场景、情节和转折，"
            "故事本身要能独立成立、引人入胜。"
            "让故事在结尾处自然达到一个「恍然大悟」式的转折或顿悟时刻——"
            "但这个顿悟仍然只停留在故事的语境里，不要说出对应的概念/事件/书名。"
            "直接开始讲故事，不要任何铺垫、不要说「今天要讲一个故事」之类的话。\n"
            "如果选历史事件或书籍案例，避免当代政治、军事冲突等敏感话题，"
            "优先选择年代较远或相对中性的题材（比如科学史、灾难调查、探险、商业史等）。"
        ),
    },
    "reveal": {
        "title": "故事揭晓",
        "target_words": 1700,
        "max_tokens": 3000,
        "tts_rate": "+0%",
        "instruction": (
            "承接上一段故事。现在揭晓这个故事的真实来源和背后的内容：\n"
            "- 如果是原创寓言对应的学术概念/理论，用通俗易懂的语言解释这个概念本身，"
            "然后逐一说明故事里的人物、场景、情节、转折分别对应概念的哪些部分；\n"
            "- 如果是真实历史事件，点出这是什么事件、发生在何时何地，补充一些背景和后续，"
            "说明故事里的细节哪些是真实的、这件事留下了什么影响或教训；\n"
            "- 如果是书籍里的案例，可以提一下这个案例出自哪本书（书名和作者），"
            "简单介绍一下这本书，再说明这个案例想说明的道理。\n"
            "无论哪种，都要建立起故事和揭晓内容之间清晰的对应关系，"
            "让听众有「原来如此」的恍然大悟感。可以再延伸聊聊这对日常生活、"
            "工作、人际关系或异乡生活心态的启发，但不要说教。"
            "最后几句话要自然地把情绪和语速往下带——比如想明白这些之后，"
            "脑子可以慢慢放空了，为接下来的呼吸放松做一个温和的过渡"
            "（不要出现「接下来」「下面」这类生硬的报幕词，也不要提到「音乐」）。"
            "避免涉及当代政治、军事冲突等敏感话题。"
        ),
    },
    "relax": {
        "title": "放松练习",
        "target_words": 950,
        "tts_rate": "-15%",
        "instruction": (
            "带听众做一段简单的呼吸放松练习，帮助准备入睡。语速要慢，多用「……」表示停顿，"
            "引导听众注意呼吸、放松身体各部位（从头到脚），可以用一些温和的意象（比如海浪、星空）。"
            "全程语气轻柔、缓慢、安抚，像睡前冥想引导。不需要互动提问，直接用引导语。"
            "结尾让听众的呼吸和心跳彻底平静下来，最后一句话非常轻地说类似"
            "「让自己沉浸在这片刻的宁静里」，停在这里就好，不需要再说别的。"
        ),
    },
    "goodnight": {
        "title": "晚安语",
        "target_words": 350,
        "tts_rate": "-15%",
        "instruction": (
            "用温暖、轻柔的语气做今晚的收尾。简短回顾一下今晚聊的内容（一句话带过即可），"
            "送给听众一句晚安祝福或者一句值得带入梦乡的话。语气要非常轻、慢，像哄人入睡。"
        ),
    },
}


def generate_section(section_key: str, context_text: str = "", avoid_repeat_context: str = "") -> str:
    cfg = SECTION_PROMPTS[section_key]
    date_str = datetime.now().strftime("%Y年%m月%d日")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday  = weekdays[datetime.now().weekday()]

    system = (
        "你是一档深夜播客「夜读与放空」的主持人，风格温暖、有思考深度，又不失轻松感。"
        "你的听众是在爱尔兰生活的华人，刚结束一天的工作，准备放松入睡。"
        "用自然流畅的中文口语，避免书面腔。不要用标题、不要用编号列表，"
        "写成连续的播客脚本，直接就是主持人说的话。"
        "不要说「好的」「当然」「接下来我们」等废话开头。"
    )

    avoid_block = (
        f"\n\n以下是最近几期节目开头的内容节选，仅供你判断哪些寓言/历史事件/书籍案例"
        f"最近讲过——今天请换一个新的，不要重复：\n{avoid_repeat_context}\n"
        if avoid_repeat_context else ""
    )

    user = (
        f"今天是{date_str}，{weekday}。\n\n"
        f"请为「{cfg['title']}」板块写约 {cfg['target_words']} 字的播客脚本。\n\n"
        f"要求：{cfg['instruction']}\n"
        f"{avoid_block}\n"
        f"{('参考素材：' + chr(10) + context_text) if context_text else ''}"
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


def generate_full_script() -> tuple[str, list[dict]]:
    """
    返回 (完整脚本文本, 各段落列表[{key, title, text, tts_rate}])
    """
    sections = []

    print("生成各板块脚本...")

    recent_stories = get_recent_stories()

    # 故事：寓言 / 真实历史 / 书籍案例，三选一，自由发挥
    print("  [故事]", end=" ", flush=True)
    story = generate_section("story", avoid_repeat_context=recent_stories)
    sections.append({"key": "story", "title": "故事", "text": story,
                      "tts_rate": SECTION_PROMPTS["story"]["tts_rate"]})
    print(f"✓ ({len(story)} 字)")

    # 故事揭晓：基于上面的故事
    print("  [故事揭晓]", end=" ", flush=True)
    reveal = generate_section("reveal", story)
    sections.append({"key": "reveal", "title": "故事揭晓", "text": reveal,
                      "tts_rate": SECTION_PROMPTS["reveal"]["tts_rate"]})
    print(f"✓ ({len(reveal)} 字)")

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
