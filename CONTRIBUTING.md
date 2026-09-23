# 贡献指南

感谢你参与「一人一站」。这个项目希望建立一个长期可信、低噪音的个人网站目录，所以我们更重视质量，而不是数量。

## 提交方式

### 方式一：Issue

使用 GitHub 的 **Submit a site** Issue 模板提交。

### 方式二：Pull Request

编辑 `data/sites.json`，新增一个对象，并运行：

```bash
python3 scripts/validate.py
python3 scripts/generate_directory.py
```

然后同时提交数据文件与重新生成的 `DIRECTORY.md`。

## 必填字段

- `name`: 网站名称
- `url`: 网站主页，必须使用 `http://` 或 `https://`
- `owner`: 网站主要维护者 / 创作者
- `description`: 一句话介绍
- `languages`: 内容主要语言数组，例如 `zh-CN`、`en`、`ja`
- `region`: 地区，可写国家、地区或 `Global`
- `tags`: 1–8 个简洁标签

## 可选字段

- `feed`: RSS / Atom Feed 地址

## 内容标准

我们优先收录：

- 明显由个人长期维护的网站
- 有原创文章、作品、笔记、项目、研究或生活记录
- 具有独立域名或稳定 URL
- 网站本身具有一定信息价值、设计价值或社区参考价值

通常不收录：

- 纯商业公司网站
- 纯产品 Landing Page
- 社交平台账号主页
- 采集、镜像、抄袭网站
- SEO 垃圾站或批量内容农场
- 恶意软件、钓鱼、欺诈或违法站点

## 数据规范

1. `url` 应指向网站主页，不要提交具体文章页。
2. 同一网站只保留一条记录。
3. 标签尽量复用已有词汇。
4. 描述应客观、简洁，不使用夸张营销用语。
5. 不要在描述里加入排名、评分或“最佳”等主观标签。

## Pull Request 建议

一个 PR 可以提交一个或多个网站，但请尽量保持主题清晰。

PR 标题示例：

```text
Add: example.com
Add: 5 Chinese indie blogs
Fix: update broken feed URL
```
