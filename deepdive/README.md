# 深度思考 🌍（深度国际局势解读）

每天自动生成的深度时事分析播客：从今天的早报里挑一个最值得深入分析的国际/地缘局势话题，做一期有态度、多视角的深度解读。

**仅发布到 Spotify，不提交小宇宙** —— 所以内容上可以放开聊敏感的国际政治、军事、外交话题，不用担心审核标记。

- **订阅地址（Podcast RSS）**：`https://1938522821-glitch.github.io/morning-briefing/deepdive/podcast.xml`
- **时长**：约 20-25 分钟
- **声音**：`zh-CN-YunyangNeural`（沉稳新闻男声）

## 节目结构

| 板块 | 篇幅 | 内容 |
| --- | --- | --- |
| 开场 | ~200字 | 预告今晚要深入聊的话题 |
| 深度解读 | ~3000字 | 从早报素材里选1-2个最值得深挖的国际/地缘政治/军事/外交话题：来龙去脉、各方立场与利益、为什么重要、可能走向、对普通人（含海外华人）的影响、主持人自己的判断 |
| 结语 | ~200字 | 总结要点，留一个开放性问题，正常收尾 |

## 与「夜读与放空」的关系

两档节目都取材于早报，但定位不同：
- **夜读与放空**：寓言/历史/书籍故事 + 放松练习，面向小宇宙 + Spotify，避开敏感话题
- **深度思考**（本节目）：深度时事分析，只面向 Spotify，可以放开讲敏感的国际局势

## 流水线（`run.py`）

```
【1/3】读取今天早报脚本（取材用）
【2/3】生成播客脚本 (script_generator.py，Claude)
        - 深度解读 → 开场 → 结语
        - 提炼今晚话题关键词 → .meta.json（用于单集标题）
【3/4】TTS 合成 (tts_generator.py，edge-tts)
        - 更新 Podcast RSS (podcast_feed.py)
【4/4】git commit & push 到 GitHub Pages（复用早报仓库的 deepdive/ 子目录）
```

## 文件结构

```
config.py            # API key、路径、声音、BASE_URL（早报仓库 + /deepdive）
script_generator.py   # Claude 生成各板块脚本 + 单集标题
tts_generator.py       # edge-tts 合成 + ffmpeg 拼接
podcast_feed.py         # 标准 Podcast RSS（podcast.xml）+ 封面图
audio/                  # 生成的 mp3 + .meta.json
scripts/                # 历史脚本备份（gitignore，仅本地）
cover.jpg, podcast.xml  # 发布到 GitHub Pages 的产物
```

`podcast_common.py` 等共用工具在上级目录 `../`，通过 `sys.path` 引入。

## 运行

```bash
cd /Users/zixuanwang/Developer/morning-briefing/deepdive
python3 run.py
```

### 定时任务

无定时任务——按需手动运行。建议在早报（6:30）生成之后再跑，这样能取材当天的早报内容。

## 上线步骤

1. 跑一次 `run.py`，确认 `podcast.xml` 和 `cover.jpg` 已推送到 GitHub Pages
2. 在 Spotify for Creators 后台用 RSS 地址新建一档节目（流程同"爱尔兰早咖啡"）
3. **不要**提交到小宇宙
