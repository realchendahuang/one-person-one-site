# One Person, One Site

> A curated collection of remarkable personal websites, independent blogs, digital gardens, portfolios, and other spaces people truly own on the web.

We believe:

> Everyone deserves a place on the Internet that is truly their own.

This repository is not a collection of website templates. It is a directory of **real people and the websites they maintain over time**.

[中文](./README.md) · [Browse online](https://realchendahuang.github.io/one-person-one-site/) · [Contribute](./CONTRIBUTING.md)

---

## Sites in the directory

<!-- SITES_TABLE:START -->
| Site | Owner | Description | Language | Tags |
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
| [Personal Website AI](https://personal-website-ai.chendahuang.com) | 陈大黄 | AI 时代，每个人都该有一个自己的网站。12 个真实上线的模板任选，三天上线并绑定自己的域名。 | zh-CN | maker, portfolio, indie-hacker |
| [Station Cat](https://wwwstationcat.org) | Station Cat | 一座深夜还亮着灯的个人小站，收集猫、早餐、文章与观察、工具和奇怪想法。 | zh-TW, en, ja | blog, writer, notes |
| [Su · AI Structure & Workflow Studio](https://su-uni.cc) | Su | AI 结构与工作流工作室：定制工作流 / Agent / 自动化，兼顾架构、原型与商业物料。 | zh-CN, en | designer, portfolio, indie-hacker |
| [陈大黄 - 作品与内容](https://chendahuang.com) | 陈大黄 | 陈大黄的个人作品与内容陈列站。收录项目、文章和精选帖子。 | zh-CN | blog, developer, portfolio |
<!-- SITES_TABLE:END -->

Full details (including RSS feeds) live in [DIRECTORY.md](./DIRECTORY.md), or [search and filter online](https://realchendahuang.github.io/one-person-one-site/).

## What belongs here?

We welcome:

- Personal websites
- Independent blogs
- Digital gardens
- Portfolios
- Personal knowledge bases
- Creator websites
- Indie hacker websites
- Long-running sites with a strong personal voice

We generally avoid company sites, social profile pages, scraper sites, SEO spam, deceptive websites, and mass-generated content farms with little genuine personal expression.

## How to submit a site

Use the **Submit a site** issue template, or edit `data/sites.json` and open a pull request.

Example entry:

```json
{
  "name": "Site Name",
  "url": "https://example.com",
  "owner": "Creator Name",
  "description": "A short description.",
  "languages": ["en"],
  "region": "Global",
  "tags": ["blog", "developer"],
  "feed": "https://example.com/rss.xml"
}
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full rules.

## Local validation

```bash
python3 scripts/validate.py
python3 scripts/generate_directory.py
python3 scripts/generate_site.py   # build the static site into site/ (gitignored)
```

`generate_directory.py` regenerates `DIRECTORY.md` and the sites table at the top of this file (the `SITES_TABLE` block). Commit the regenerated files together with your data change — CI verifies they are in sync.

## License

Code is released under the [MIT License](./LICENSE).
