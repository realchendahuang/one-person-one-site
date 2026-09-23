# 一人一站 · One Person, One Site

> 🌐 收集值得关注的个人网站、独立博客与数字花园。发现那些在平台之外，认真经营自己互联网家园的人。

**One Person, One Site** 是一个开放、长期维护的个人网站与独立博客目录。

我们相信：

> 每个人，都应该在互联网上拥有一个真正属于自己的地方。

这个项目不收集“建站模板”，而是收集**真实的人，以及他们长期经营的网站**。

[English](./README_EN.md) · [在线浏览](https://realchendahuang.github.io/one-person-one-site/) · [完整目录](./DIRECTORY.md) · [提交网站](#提交你的网站)

---

## 收录的站点

<!-- SITES_TABLE:START -->
| 网站 | 站长 / 创作者 | 简介 | 语言 | 标签 |
|---|---|---|---|---|
| [CouCouYa 可可鸭](https://coucouya.com) | CouCouYa | KOSX.ai 社群增长操盘手，分享 AI、Web3、金融与公开学习。 | zh-CN | blog, maker, notes |
| [Edison AI Workshop](https://edison-zwteam.pages.dev) | Edison | AI 产品开发者，专注信息流自动化、研究效率工具、内容分发系统和 Discord 自动化。 | zh-CN | developer, portfolio, indie-hacker |
| [Gdemoni's World](https://zshgdemoni.me) | Gdemoni | 一名大三学生的个人数字花园：AI 编程项目、文章笔记与大学成长经历。 | zh-CN, en | digital-garden, developer, blog |
| [Jack Flux](https://jack0813y.github.io) | Jack | 一个制造业工程师的 AI 探索记录：Agent、自动化、Vibe Coding 与真实构建过程。 | zh-CN | blog, developer, digital-garden |
| [Jasper Wei](https://jasper-wei.vast-beech-4429.chatgpt.site) | Jasper Wei | 前汽车工程师，AI Innovation Consultant，记录项目、想法与生活。 | zh-CN | portfolio, blog, maker |
| [Kim AI Workshop](https://kim-ai-workshop.com) | Kim | Practical AI systems, market intelligence, reusable Skills and automated workflows. | en | developer, indie-hacker, maker |
| [LINC.WANG](https://linc.wang) | Linc Wang | 室内设计师、设计公司负责人，也在持续构建自己的 AI 产品。 | zh-CN | designer, portfolio, indie-hacker |
| [Mike Lam](https://mc9world.com) | Mike Lam | 正在创业的个人主页，分享餐饮、投资、猎头和 Marketing 的事业经验。 | zh-CN | blog, maker |
| [MoonInAI](https://mooninai.top) | MoonInAI | 传统企业 AI 系统顾问 / AI 副业陪跑者。用 AI 改造真实业务，用系统拆解学习、副业和增长。 | zh-CN | developer, notes, indie-hacker |
| [Station Cat](https://wwwstationcat.org) | Station Cat | 一座深夜还亮着灯的个人小站，收集猫、早餐、文章与观察、工具和奇怪想法。 | zh-TW, en, ja | blog, writer, notes |
| [Su · AI Structure & Workflow Studio](https://su-uni.cc) | Su | AI 结构与工作流工作室：定制工作流 / Agent / 自动化，兼顾架构、原型与商业物料。 | zh-CN, en | designer, portfolio, indie-hacker |
| [陈大黄 - 作品与内容](https://chendahuang.com) | 陈大黄 | 陈大黄的个人作品与内容陈列站。收录项目、文章和精选帖子。 | zh-CN | blog, developer, portfolio |
<!-- SITES_TABLE:END -->

完整信息（含 RSS 订阅地址）见 [DIRECTORY.md](./DIRECTORY.md)，也可以在[在线网站](https://realchendahuang.github.io/one-person-one-site/)中搜索和按标签筛选。

## 我们收录什么？

优先收录：

- 个人主页 / Personal Website
- 独立博客 / Independent Blog
- 数字花园 / Digital Garden
- 个人作品集 / Portfolio
- 个人知识库 / Knowledge Base
- 独立创作者主页 / Creator Website
- 独立开发者主页 / Indie Hacker Website
- 长期维护、有明显个人表达的网站

不鼓励收录：

- 纯公司官网、营销落地页
- 纯社交平台主页
- 镜像站、采集站、SEO 垃圾站
- 大量 AI 批量生成、缺乏真实个人表达的内容农场
- 明显违法、欺诈或恶意内容

## 收录原则

我们更看重：

1. **真实的人**：网站背后有清晰、持续的个人身份或创作主体。
2. **长期主义**：不是一次性项目页，而是持续维护的数字空间。
3. **独立表达**：有自己的内容、观点、作品、笔记或生活记录。
4. **可访问性**：网站当前可以正常访问，并有基本可读性。
5. **尊重互联网**：不过度追踪、不恶意跳转、不用欺骗性方式获取用户信息。

## 提交你的网站

最简单的方式：

1. 打开 **Issues → Submit a site**
2. 填写网站信息
3. 或直接修改 `data/sites.json` 后提交 Pull Request

字段说明：

```json
{
  "name": "网站名称",
  "url": "https://example.com",
  "owner": "站长 / 创作者名称",
  "description": "一句话介绍",
  "languages": ["zh-CN"],
  "region": "Global",
  "tags": ["blog", "developer"],
  "feed": "https://example.com/rss.xml"
}
```

详细规则见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## 标签建议

常用标签包括：

`blog` · `developer` · `designer` · `writer` · `researcher` · `maker` · `photography` · `digital-garden` · `portfolio` · `newsletter` · `notes` · `indie-hacker`

你也可以提出新的标签，但建议保持简洁、可复用。

## 本地校验

```bash
python3 scripts/validate.py
python3 scripts/generate_directory.py
python3 scripts/generate_site.py   # 构建静态网站到 site/（已 gitignore）
```

`generate_directory.py` 会同时更新 `DIRECTORY.md` 和本文件顶部的站点表格（`SITES_TABLE` 标记区间），提交 PR 时请一并提交所有生成文件的改动。

提交 PR 时，GitHub Actions 会自动检查：

- JSON 格式是否正确
- URL 是否为 http/https
- 是否存在重复网址
- 必填字段是否齐全
- `DIRECTORY.md` 与 README 表格是否与数据一致

## 项目结构

```text
one-person-one-site/
├── data/
│   ├── sites.json
│   └── sites.example.json
├── scripts/
│   ├── validate.py
│   ├── generate_directory.py
│   └── generate_site.py
├── schema/
│   └── site.schema.json
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
├── README.md
├── README_EN.md
├── DIRECTORY.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── LICENSE
```

## 在线网站

目录以纯静态网站的形式发布在 GitHub Pages：

👉 **https://realchendahuang.github.io/one-person-one-site/**

网站由 `data/sites.json` 自动构建（GitHub Actions 每次 push 到 main 自动部署），支持搜索和按标签筛选，无需任何服务器。

## 路线图

- [x] 建立第一批高质量个人网站种子库
- [ ] 按语言、地区、职业与主题分类
- [ ] 增加 RSS / Atom Feed 信息
- [ ] 增加站点截图与历史快照（可选）
- [ ] 建立“本周一人一站”精选机制
- [ ] 建立网站失效检测
- [x] 生成可搜索的静态网站（GitHub Pages 已上线）
- [ ] 支持 OPML / JSON / CSV 导出
- [ ] 建立社区推荐与年度精选

## 为什么叫「一人一站」？

平台会变化，算法会变化，账号也可能消失。

但个人网站是互联网上少数仍然可以由个人真正拥有、设计、组织和长期沉淀的空间。

**一人一站，不是要求每个人都成为站长。**

它更像一个倡议：重新拥有自己的互联网身份、内容和关系。

## License

项目代码采用 [MIT License](./LICENSE)。目录数据可在遵循仓库许可与来源说明的前提下使用。

---

如果你也有一个认真维护的个人网站，欢迎把它带到这里。
