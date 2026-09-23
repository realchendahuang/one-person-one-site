# 贡献指南 (Contributing Guide)

感谢你关注并参与「一人一站 · One Person, One Site」。

这个项目的初衷，是为互联网上认真记录生活、沉淀思考与打磨作品的独立个人，建立一个长期可信、低噪音、纯粹而有温度的个人网站目录。我们始终坚信：**质量重于数量，真诚重于形式。**

---

## 快速提交方式

### 方式一：GitHub Issue（最简便捷，小白推荐）

直接使用 GitHub Issue 模板提交：
👉 [**Submit a site / 提交网站**](https://github.com/realchendahuang/one-person-one-site/issues/new?template=submit-site.yml)

按表单提示填写网站名称、网址、站长/作者与一句话简介。**提交后由 GitHub Actions 自动处理**：

1. 解析表单字段并做格式校验；
2. 自动探测站点是否可访问（HTTP 状态码）；
3. 通过后写入 `data/sites.json`、重新生成目录、提交并部署到 GitHub Pages；
4. 在 Issue 下回复结果并自动关闭。

正常情况下**一两分钟内即可在线上看到你的站点**，无需人工干预。

以下情况会收到提示而非直接收录：

| 提示 | 原因 | 处理方式 |
|---|---|---|
| 缺少必填内容 | 表单有字段未填写 | 直接编辑 Issue 正文补齐，会自动重新处理 |
| 未能访问站点 | 探测失败（地域限制 / 反爬 / 临时故障） | 维护者添加 `accepted` 标签即可跳过探测 |
| 判定为平台账号页 | 命中了不支持的类型（如小红书、X 主页） | 如有误判，维护者添加 `accepted` 标签放行 |
| 已收录 | 站点已在目录中 | 无需处理，可直接查看线上效果 |

> 维护者放行方式：在 Issue 上添加 `accepted` 标签，工作流会自动跳过探测与类型检查重新收录。

---

### 方式二：Pull Request（开发者推荐）

1. **Fork 本仓库** 到你的 GitHub 账号，并克隆到本地。
2. **编辑 `data/sites.json`**，在数组尾部添加你的站点信息对象（见后文格式）。
3. **运行本地校验与生成脚本**：
   ```bash
   python3 scripts/validate.py          # 格式与必填字段合规校验
   python3 scripts/generate_directory.py # 自动同步 DIRECTORY.md 与 README 站点表格
   python3 scripts/generate_site.py      # 本地构建预览页面
   ```
4. **提交代码并创建 PR**：
   将 `data/sites.json` 与自动同步更新的 `DIRECTORY.md`、`README.md`、`README_EN.md` 一并提交。

> 💡 **提示**：GitHub Actions 会在每次推送至 `main` 分支时自动将静态网站部署到 GitHub Pages，你无需手动提交 `site/` 目录中的生成文件。

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

### 字段说明与约束：

| 字段 | 类型 | 是否必填 | 规范说明 |
|---|---|---|---|
| `name` | string | **必填** | 站点全称或常用名称，不超过 40 字符 |
| `url` | string | **必填** | 网站主页，必须为 `http://` 或 `https://`，指向主页根路径（非某篇文章） |
| `owner` | string | **必填** | 站长或创作者的常用名 / 昵称 / 签名 |
| `description` | string | **必填** | 简明扼要的介绍，15~240 字符以内，避免浮夸营销用词 |
| `languages` | string[] | **必填** | 内容主要使用的语言代码，如 `zh-CN`, `en`, `zh-TW`, `ja` 等（至少 1 项） |
| `region` | string | **必填** | 所属地区或国家，例如 `China`, `Global`, `US`, `Japan` 等 |
| `tags` | string[] | **必填** | 1 到 8 个简洁分类标签，全小写，多词以中划线连接（如 `indie-hacker`） |
| `feed` | string | 可选 | RSS / Atom / JSON Feed 订阅源 URL（需为有效 http/https 链接） |

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

感谢你为开放、独立、长青的个人互联网生态贡献力量！✨
