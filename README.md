# 一人一站 · One Person, One Site

> 🌐 收集值得关注的个人网站、独立博客与数字花园。发现那些在平台之外，认真经营自己互联网家园的人。

**One Person, One Site** 是一个开放、长期维护的个人网站与独立博客目录。

我们相信：

> 每个人，都应该在互联网上拥有一个真正属于自己的地方。

这个项目不收集“建站模板”，而是收集**真实的人，以及他们长期经营的网站**。

[English](./README_EN.md) · [浏览全部站点](./DIRECTORY.md) · [提交网站](#提交你的网站)

---

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

## 在线网站

目录以纯静态网站的形式发布在 GitHub Pages：

👉 **https://realchendahuang.github.io/one-person-one-site/**

网站由 `data/sites.json` 自动构建（GitHub Actions 每次 push 到 main 自动部署），支持搜索和按标签筛选，无需任何服务器。

## 目录

完整站点列表由 `data/sites.json` 自动生成：

👉 **[DIRECTORY.md](./DIRECTORY.md)**

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

提交 PR 时，GitHub Actions 会自动检查：

- JSON 格式是否正确
- URL 是否为 http/https
- 是否存在重复网址
- 必填字段是否齐全
- `DIRECTORY.md` 是否与数据一致

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

## 路线图

- [ ] 建立第一批高质量个人网站种子库
- [ ] 按语言、地区、职业与主题分类
- [ ] 增加 RSS / Atom Feed 信息
- [ ] 增加站点截图与历史快照（可选）
- [ ] 建立“本周一人一站”精选机制
- [ ] 建立网站失效检测
- [x] 生成可搜索的静态网站（GitHub Pages 已上线）
- [ ] 建立“本周一人一站”精选机制
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
