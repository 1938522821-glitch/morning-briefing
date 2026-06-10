# 夜读与放空 🌙

每天自动生成的中文深夜播客，用一段故事引出一个有趣的概念/事件/书籍，再带一段呼吸放松练习，伴一段安眠音乐入睡。发布为标准 Podcast RSS，可在 Spotify / 小宇宙 等任意播客 App 订阅。

- **订阅地址（Podcast RSS）**：`https://1938522821-glitch.github.io/morning-briefing/evening/podcast.xml`
- **时长**：约 50 分钟
- **声音**：`zh-CN-XiaoxiaoNeural`（温柔女声，pitch -15Hz 更低沉柔和）

## 节目结构

| 板块 | 篇幅 | 语速 | 内容 |
| --- | --- | --- | --- |
| 故事 | ~3200字 | 正常 | 每天三选一：① 原创寓言（对应一个研究生水平的学术概念）② 真实历史事件（科学史/工程商业史/灾难调查等）③ 非虚构书籍里的核心案例。先完整讲故事，结尾留"恍然大悟"的钩子，不点明来源 |
| 故事揭晓 | ~1700字 | 正常 | 揭晓故事的真实来源——对应的概念/历史事件/书籍（含书名作者），建立故事与内容的映射关系，延伸聊聊对生活/工作/异乡心态的启发，结尾自然过渡到放松 |
| 放松练习 | ~950字 | -15% | 呼吸引导 + 身体放松（从头到脚），意象用海浪/星空，结尾让心跳平静下来 |
| 晚安语 | ~350字 | -15% | 温暖收尾 + 晚安祝福 |
| 安眠音乐 | ~4分钟 | — | 拼接在最后的环境音乐（`assets/sleep_music.mp3`） |

> 之前版本有"今日回顾"板块（复述早报内容），但容易带出国际冲突等敏感话题导致小宇宙审核被标记，已移除。现在内容完全独立于早报。历史事件/书籍类素材会优先选年代较远或中性的题材（科学史、灾难调查、探险、商业史等），避开当代政治/军事冲突。

### 防重复

每天生成时会读取**最近 7 天**节目脚本的开头片段（`scripts/`，限本地，不入库），提示 Claude 不要选择最近讲过的同一个寓言/历史事件/书籍，确保每天都是新内容。

## 流水线（`run.py`）

```
【1/3】生成播客脚本 (script_generator.py，Claude)
        - 故事 → 故事揭晓 → 放松练习 → 晚安语
        - 提炼今晚亮点关键词 → .meta.json（用于单集标题）
【2/3】TTS 合成 (tts_generator.py，edge-tts)
        - 各板块分别合成（不同语速）
        - 拼接安眠音乐，统一重新编码为 mp3
        - 更新 Alexa feed (alexa_feed.py) + Podcast RSS (podcast_feed.py)
【3/3】git commit & push 到 GitHub Pages（复用早报仓库的 evening/ 子目录）
```

## 文件结构

```
config.py            # API key、路径、声音、BASE_URL（早报仓库 + /evening）
script_generator.py   # Claude 生成各板块脚本 + 单集标题
tts_generator.py       # edge-tts 合成 + ffmpeg 拼接安眠音乐
alexa_feed.py           # Alexa Flash Briefing feed.json（历史遗留，未在用）
podcast_feed.py         # 标准 Podcast RSS（podcast.xml）+ 封面图
assets/sleep_music.mp3  # 安眠音乐素材（ffmpeg 生成的环境音）
audio/                  # 生成的 mp3 + .meta.json
scripts/                # 历史脚本备份（gitignore，仅本地）
cover.jpg, podcast.xml  # 发布到 GitHub Pages 的产物
```

`podcast_common.py` 等共用工具在上级目录 `../`，通过 `sys.path` 引入。

## 运行

```bash
cd /Users/zixuanwang/Developer/morning-briefing/evening
python3 run.py
```

### 定时任务

无定时任务——按需手动运行。双击桌面的 `生成夜读与放空.command` 即可一键生成新一期。

## 命名历史

晚安电台 → 晚安时刻 → 晚安故事屋 → **夜读与放空**（多次因"违规字符"/敏感内容被小宇宙标记，最终改为纯寓言/故事内容）。
