# 贡献指南 (Contributing Guide)

感谢你关注并参与「一人一站 · One Person, One Site」。

这个项目的初衷，是为互联网上认真记录生活、沉淀思考与打磨作品的独立个人，建立一个长期可信、低噪音、纯粹而有温度的个人网站目录。我们始终坚信：**质量重于数量，真诚重于形式。**

---

## 快速提交方式

### 方式一：GitHub Issue（最简便捷，小白推荐）

直接使用 GitHub Issue 模板提交：
👉 [**Submit a site / 提交网站**](https://github.com/realchendahuang/one-person-one-site/issues/new?template=submit-site.yml)

按表单提示填写网站名称、网址、站长/作者与一句话简介。提交后由维护者处理：格式校验、可用性探测与收录都是用仓库内的脚本完成的，通常**一两天内**就会出现在线上目录，处理结果会回复在你的 Issue 里。

如果缺少必填内容，维护者会在 Issue 里指出，直接编辑 Issue 正文补齐即可。

---

### 方式二：Pull Request（开发者推荐）

1. **Fork 本仓库** 到你的 GitHub 账号，并克隆到本地。
2. **编辑 `data/sites.json`**，在数组尾部添加你的站点信息对象（见后文格式）。
3. **运行本地校验与生成脚本**：
   ```bash
   python3 scripts/validate.py            # 数据格式与收录规范校验
   python3 scripts/generate_directory.py  # 同步 DIRECTORY.md 与 README 表格、统计
   python3 scripts/generate_site.py       # 本地构建静态站点（site/）
   python3 tests/test_validate.py         # 规则测试
   python3 tests/test_build.py            # 构建产物测试（需先构建）
   ```
   如果站点还没有本地图标缓存，可以运行 `python3 scripts/fetch_favicons.py` 抓取
   （需要 `pillow`）；抓不到不影响收录，页面上会退化成首字母色块。
4. **提交代码并创建 PR**：
   将 `data/sites.json` 与自动同步更新的 `DIRECTORY.md`、`README.md`、`README_EN.md` 一并提交。

> 💡 **提示**：`site/` 是构建产物（已被 gitignore），PR 里只需要提交 `data/sites.json` 与生成器同步更新的 `DIRECTORY.md`、`README.md`、`README_EN.md`；构建与部署由维护者完成。

---

## 数据格式规范

每个站点在 `data/sites.json` 中为一个独立的 JSON 对象，字段定义如下：

```json
{
  "name": "站点名称",
  "url": "https://example.com",
  "owner": "站长 / 创作者昵称",
  "description": "用客观、真诚、简洁的一到两句话介绍你的站点特色或主要内容。",
  "languages": ["zh-CN"],
  "region": "China",
  "tags": ["blog", "developer", "digital-garden"],
  "feed": "https://example.com/rss.xml"
}
```

多订阅源时 `feed` 用数组：

```json
"feed": ["https://example.com/rss.xml", "https://example.com/en/rss/"]
```

### 字段说明与约束：

| 字段 | 类型 | 是否必填 | 规范说明 |
|---|---|---|---|
| `name` | string | **必填** | 站点全称或常用名称，不超过 40 字符 |
| `url` | string | **必填** | 网站主页，必须为 `http://` 或 `https://`，指向主页根路径（非某篇文章） |
| `owner` | string | **必填** | 站长或创作者的常用名 / 昵称 / 签名 |
| `description` | string | **必填** | 简明扼要的介绍，15~240 字符以内，避免浮夸营销用词 |
| `languages` | string[] | **必填** | 语言代码，主语言小写、地区大写：`zh-CN`、`zh-TW`、`en`、`ja`（至少 1 项，不可重复） |
| `region` | string | **必填** | 所属地区或国家，例如 `China`, `Global`, `US`, `Japan` 等 |
| `tags` | string[] | **必填** | 1 到 8 个标签，全小写，多词以中划线连接（如 `indie-hacker`），不可重复 |
| `feed` | string \| string[] | 可选 | RSS / Atom / JSON Feed 订阅源 URL（需为有效 http/https 链接）；多订阅源（如双语站点的日文/英文 RSS）可用数组，最多 5 条 |

> 这些约束由 `scripts/validate.py` 执行，机读版本在 [`schema/site.schema.json`](./schema/site.schema.json)。
> 两者的一致性由 `tests/test_validate.py` 保证——改了一边而没改另一边，测试会失败。

---

## 收录标准与审核原则

### 优先收录：
1. **真实的人与持续表达**：站点背后有真实、可持续的个人身份或创作主体，而非一次性的 Demo 或短期空壳。
2. **原创与深度内容**：拥有自主撰写的文章、深度笔记、代表作品集、独立开源项目或生活纪实。
3. **独立性与稳定性**：拥有独立顶级域名或稳定的托管服务，排版舒适，阅读体验良好。
4. **开放互联精神**：尊重访客隐私，不过度弹窗推销，不设恶意跳转，倡导开放网络精神。

### 明确拒绝收录：
- 商业企业官网、团队外包广告页、产品转化 Landing Page。
- 单纯的第三方社交平台个人账号页面（如 X、微信公众号、小红书等）。
- 爬虫采集站、镜像站、垃圾外链站、SEO 伪原创农场。
- 大量使用 AI 批量生产、毫无个人见解与思考的流水线垃圾站。
- 含有恶意脚本、钓鱼诈骗、盗版侵权或违反法律法规的网站。

---

## 常用推荐标签

尽量复用社区已有的通用标签，便于全站聚合与筛选：

- **内容形态**：`blog`（独立博客）, `digital-garden`（数字花园）, `notes`（个人笔记）, `portfolio`（作品集）, `newsletter`（通讯订阅）
- **创作者身份**：`developer`（开发者）, `designer`（设计师）, `writer`（作者/写作者）, `maker`（创作者）, `indie-hacker`（独立黑客）, `photographer`（摄影师）, `researcher`（研究者）
- **主题领域**：`tech`, `ai`, `open-source`, `philosophy`, `lifestyle`, `minimalism`, `reading`

---

## Pull Request 规范

- 请保持每次提交目的明确。
- PR 标题推荐格式：
  - `Add: example.com (网站名称)`
  - `Update: 更新 example.com 的 RSS 订阅地址`
  - `Docs: 完善贡献指南相关说明`

---

## 维护与本地流程

项目当前**不依赖 GitHub Actions**：校验、构建、部署与巡检全部用仓库内的脚本在本地完成，`data/sites.json` 是唯一的数据源。

维护者处理一个新收录 Issue 的完整流程：

```bash
python3 scripts/ingest_issue.py issue-body.md   # 解析 Issue 表单并写入 data/sites.json
python3 scripts/fetch_favicons.py               # 抓取新站图标（需 pillow，抓不到自动兜底）
python3 scripts/validate.py                     # 数据格式与收录规范校验
python3 scripts/generate_directory.py           # 同步 DIRECTORY.md 与 README 表格、统计
python3 scripts/generate_site.py                # 构建 site/
python3 tests/test_validate.py && python3 tests/test_build.py  # 规则与产物测试
git push                                        # 推送 main
python3 scripts/deploy.py                       # 构建并发布到 gh-pages 分支（Pages 从该分支上线）
```

巡检用 `scripts/check_health.py`（可加 `--issue-body report.md` 产出可直接贴到 Issue 的报告）。脚本**只报告，不删数据**：很多正常站点会对脚本请求返回 403/429、拒绝 HEAD 或按地域限流，自动下架极易误伤。只有返回明确失效信号（404/410、域名无法解析）的站点会被列为「疑似失效」，最终仍由维护者手动确认后移除。

### 本地复现构建

```bash
python3 scripts/build_assets.py     # 生成品牌图标与分享图（需 pillow）
python3 scripts/fetch_favicons.py   # 抓取站点图标（需 pillow，可跳过）
python3 scripts/generate_site.py    # 构建 site/
python3 tests/test_build.py         # 校验构建产物
```

生成物包括主页面、完整目录页、`feeds.opml` 订阅合集、`robots.txt`、`sitemap.xml`、
`404.html`，以及开放数据 `site/data/sites.json`。

---

## 收录数据的使用

`data/sites.json` 是这份目录的完整数据，任何人都可以复用（MIT）：

- 仓库内：[`data/sites.json`](./data/sites.json)
- 线上地址：`https://realchendahuang.github.io/one-person-one-site/data/sites.json`
- 订阅合集：`https://realchendahuang.github.io/one-person-one-site/feeds.opml`

收录站点的内容与知识产权归各自作者所有，本目录只做索引。

感谢你为开放、独立、长青的个人互联网生态贡献力量！✨
