# 爱尔兰早咖啡 ☕️

每天早上自动生成的中文新闻播客，用 Claude 写稿、edge-tts 配音，发布为标准 Podcast RSS，可在 Spotify / 小宇宙 等任意播客 App 订阅。

- **订阅地址（Podcast RSS）**：`https://1938522821-glitch.github.io/morning-briefing/podcast.xml`
- **时长**：约 60 分钟
- **声音**：`zh-CN-YunxiNeural`（男声）

## 本仓库的三档节目

| 节目 | 目录 | 定位 | 发布渠道 |
| --- | --- | --- | --- |
| 爱尔兰早咖啡（本节目） | `/` | 早间新闻综述 | Spotify + 小宇宙 |
| 夜读与放空 | `evening/` | 寓言/历史/书籍故事 + 放松练习 + 安眠音乐 | Spotify + 小宇宙 |
| 深度思考 | `deepdive/` | 深度国际局势解读（可聊敏感话题） | 仅 Spotify |

## 节目结构

| 板块 | 篇幅 | 内容 |
| --- | --- | --- |
| 开场 | ~300字 | 预告今天几个亮点话题 |
| 国际形势 | ~1400字 | 解读重要国际新闻 |
| AI 与科技 | ~1400字 | AI / 科技动态点评 |
| 市场与股票 | ~1100字 | 财经市场分析 |
| 爱尔兰综合 | ~1800字 | 重点关注就业市场（招聘/裁员）和房地产（租金/房价/政策），其他本地新闻补充 |
| 全球热点 | ~1200字 | 1-4 个全球热门话题闲聊 |
| 结尾 | ~400字 | 总结 + 一句心态/行动建议 |

### 话题去重

每天生成时会自动读取**最近一期**的脚本（`scripts/`，限本地，不入库），提示 Claude：
- 已经讲过的话题不要原样重复；
- 如果有新进展/新角度，可以更新或深化；
- 否则跳过，把篇幅留给真正的新内容。

## 流水线（`run.py`）

```
【1/3】抓取新闻 (news_fetcher.py)
        - 各板块 RSS 源 + NewsAPI 补充（AI/科技）
        - 读取最近一期脚本用于去重
【2/3】生成播客脚本 (script_generator.py，Claude)
        - 各板块 → 开场/结尾
        - 提炼今日亮点关键词 → .meta.json（用于单集标题）
【3/3】TTS 合成 (tts_generator.py，edge-tts)
        - 更新 Alexa feed (alexa_feed.py) + Podcast RSS (podcast_feed.py)
        - git commit & push 到 GitHub Pages
```

## 文件结构

```
config.py            # API key、路径、声音、BASE_URL 等配置
news_fetcher.py       # 抓新闻 + 读取最近一期脚本（去重用）
script_generator.py   # Claude 生成各板块脚本 + 单集标题
tts_generator.py       # edge-tts 合成音频
alexa_feed.py          # Alexa Flash Briefing feed.json（历史遗留，未在用）
podcast_feed.py        # 标准 Podcast RSS（podcast.xml）+ 封面图
podcast_common.py      # 两档节目共用的 RSS / 封面图 / meta 工具
audio/                  # 生成的 mp3 + .meta.json
scripts/                # 历史脚本备份（gitignore，仅本地）
cover.jpg, podcast.xml  # 发布到 GitHub Pages 的产物
```

## 运行

```bash
cd /Users/zixuanwang/Developer/morning-briefing
python3 run.py
```

### 定时任务

`com.zixuan.morningbriefing.plist`（launchd），每天 6:30 运行，配合 `pmset repeat wake MTWRFSU 06:20:00` 唤醒电脑。

## 环境变量（`.env`）

见 `.env.example`：`CLAUDE_API_KEY`、`NEWSAPI_KEY`（可选）、`BASE_URL` 等。
