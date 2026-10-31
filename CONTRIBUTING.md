# 贡献指南 (Contributing Guide)

感谢你关注「一人一站 · One Person, One Site」。

这份目录只收由真人长期经营的个人网站，宁可少收，也不收不合适的站。收录标准见 [README 的收录标准](./README.md#收录标准)，提交前请先看一眼。

---

## 提交方式

### 方式一：Issue 表单（推荐）

打开 [**提交网站表单**](https://github.com/realchendahuang/one-person-one-site/issues/new?template=submit-site.yml)，按提示填写网站名称、网址、站长与一句话简介。

维护者会在本地用仓库里的脚本做格式校验、可用性探测和收录，通常**一两天内**处理完，结果会回复在你的 Issue 里。如果缺少必填内容，维护者会在 Issue 里指出，直接编辑 Issue 正文补齐即可。

### 方式二：Pull Request

1. **Fork 本仓库**并克隆到本地。
2. **编辑 `data/sites.json`**，在数组末尾添加你的站点（格式见下文）。
3. **运行本地校验与生成脚本**：
   ```bash
   python3 scripts/validate.py            # 数据格式与收录规范校验
   python3 scripts/generate_directory.py  # 同步 DIRECTORY.md 与 README 表格、统计
   python3 scripts/generate_site.py       # 本地构建静态站点（site/）
   python3 tests/test_validate.py         # 规则测试
   python3 tests/test_build.py            # 构建产物测试（需先构建）
   ```
   如果站点还没有本地图标缓存，可以运行 `python3 scripts/fetch_favicons.py` 抓取
   （需要 `pillow`）。抓不到也不影响收录，页面上会显示首字母色块。
4. **提交并创建 PR**：把 `data/sites.json` 与生成器更新过的 `DIRECTORY.md`、`README.md`、`README_EN.md` 一并提交。

> `site/` 是构建产物（已被 gitignore），不需要提交。构建与发布由维护者完成。

---

## 数据格式

每个站点在 `data/sites.json` 中是一个 JSON 对象：

```json
{
  "name": "站点名称",
  "url": "https://example.com",
  "owner": "站长 / 创作者昵称",
  "description": "一位后端工程师的技术博客，记录分布式系统与数据库的实践笔记。",
  "languages": ["zh-CN"],
  "region": "China",
  "tags": ["blog", "developer", "notes"],
  "feed": "https://example.com/rss.xml"
}
```

有多个订阅源时，`feed` 写成数组：

```json
"feed": ["https://example.com/rss.xml", "https://example.com/en/rss/"]
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | **必填** | 站点全称或常用名，不超过 40 个字符 |
| `url` | string | **必填** | 网站首页，`http://` 或 `https://` 开头，不要填某一篇文章 |
| `owner` | string | **必填** | 站长或创作者的常用名 / 昵称 |
| `description` | string | **必填** | 15~240 个字符。用第三人称客观描述这是谁的站、主要写什么，不写「值得收录」之类的话 |
| `languages` | string[] | **必填** | 语言代码，主语言小写、地区大写：`zh-CN`、`zh-TW`、`en`、`ja`（至少 1 项，不可重复） |
| `region` | string | **必填** | 所在地区，例如 `China`、`Taiwan`、`Japan`、`US`、`Global` |
| `tags` | string[] | **必填** | 1~8 个标签，全小写，多词用中划线（如 `indie-hacker`），不可重复 |
| `feed` | string \| string[] | 可选 | RSS / Atom / JSON Feed 地址；多个订阅源（如双语站点的两份 RSS）用数组，最多 5 条 |

> 这些约束由 `scripts/validate.py` 执行，机读版本在 [`schema/site.schema.json`](./schema/site.schema.json)。
> 两者的一致性由 `tests/test_validate.py` 保证，改了一边没改另一边，测试会失败。

### 简介怎么写

- 写清楚两件事：**这是谁的站**，**主要写什么或做什么**。
- 用第三人称，客观平实。不写「值得被收录」「最好的」「操盘手」之类的自我宣传。
- 中文简介用全角标点，中英文之间加空格（如「记录 AI 与 Linux」）。
- 不确定怎么写时，可以参考已收录条目，例如「资深软件工程师的独立博客：记录 AI Agent、RAG、后端与信息安全的实践笔记与技术取舍。」

维护者可能会为了统一风格润色你的简介，但不会改变事实。

---

## 推荐标签

请尽量从下表里选。用了表外的标签不会被拒，但 `validate.py` 会给出提示，维护者可能会换成相近的推荐标签。标签表的唯一来源是 `scripts/siteutil.py` 里的 `TAG_GROUPS`，首页的中文标签名也从这里来。

| 分类 | 标签 |
|---|---|
| **内容形态** | `blog`（博客）· `digital-garden`（数字花园）· `notes`（笔记）· `portfolio`（作品集）· `newsletter`（通讯） |
| **作者身份** | `developer`（开发者）· `designer`（设计师）· `writer`（写作者）· `maker`（创客）· `indie-hacker`（独立开发）· `photographer`（摄影师）· `researcher`（研究者） |
| **主题** | `ai` · `open-source`（开源）· `security`（安全）· `devops` · `game`（游戏）· `tech`（科技）· `life`（生活） |

---

## Pull Request 规范

- 每个 PR 只做一件事。
- PR 标题推荐格式：
  - `Add: example.com (网站名称)`
  - `Update: 更新 example.com 的 RSS 订阅地址`
  - `Docs: 完善贡献指南`

---

## 维护与本地流程

项目**不使用 GitHub Actions**。`.github/` 目录里只有 Issue 表单和 PR 模板，校验、收录、构建、发布与巡检都由维护者在本地运行脚本完成，`data/sites.json` 是唯一的数据源。

维护者处理一个收录 Issue 的完整流程：

```bash
gh issue view N --json body -q .body > issue-body.md
python3 scripts/ingest_issue.py issue-body.md   # 解析 Issue 表单并写入 data/sites.json
python3 scripts/fetch_favicons.py               # 抓取新站图标（需 pillow，抓不到自动兜底）
python3 scripts/validate.py                     # 数据格式与收录规范校验
python3 scripts/generate_directory.py           # 同步 DIRECTORY.md 与 README 表格、统计
python3 scripts/generate_site.py                # 构建 site/
python3 tests/test_validate.py && python3 tests/test_build.py  # 规则与产物测试
git push                                        # 推送 main
python3 scripts/deploy.py                       # 构建并发布到 gh-pages 分支（Pages 从该分支上线）
```

巡检用 `scripts/check_health.py`（可加 `--issue-body report.md` 生成能直接贴到 Issue 的报告）。脚本**只报告，不删数据**：很多正常站点会对脚本请求返回 403/429、拒绝 HEAD 或按地域限流，自动下架很容易误伤。只有返回明确失效信号（404/410、域名无法解析）的站点会被列为「疑似失效」，最后仍由维护者手动确认后移除。

### 本地复现构建

```bash
python3 scripts/build_assets.py     # 生成品牌图标与分享图（需 pillow）
python3 scripts/fetch_favicons.py   # 抓取站点图标（需 pillow，可跳过）
python3 scripts/generate_site.py    # 构建 site/
python3 tests/test_build.py         # 校验构建产物
```

构建产物包括主页面、完整目录页、`feeds.opml` 订阅合集、`robots.txt`、`sitemap.xml`、`404.html`，以及开放数据 `site/data/sites.json`。

---

## 收录数据的使用

`data/sites.json` 是这份目录的完整数据，以 MIT 许可开放，任何人都可以复用：

- 仓库内：[`data/sites.json`](./data/sites.json)
- 线上地址：`https://realchendahuang.github.io/one-person-one-site/data/sites.json`
- 订阅合集：`https://realchendahuang.github.io/one-person-one-site/feeds.opml`

收录站点的内容与知识产权归各自作者所有，本目录只做索引。
