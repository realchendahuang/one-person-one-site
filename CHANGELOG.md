# Changelog

本文件记录项目的重要变更。新收录的站点不逐条列出，见 [提交历史](https://github.com/realchendahuang/one-person-one-site/commits/main)。

格式参考 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)。

## [Unreleased]

### Added
- 恢复 `.github/ISSUE_TEMPLATE/` 里的提交表单（`submit-site.yml`）和数据纠错表单（`data-fix.yml`），以及 PR 模板。只恢复模板，不恢复 GitHub Actions。
- 推荐标签表集中到 `scripts/siteutil.py` 的 `TAG_GROUPS`，首页、目录页与前端共用；`validate.py` 对表外标签给出提示。
- 首页新增「地区」「写作语言」统计。
- README 新增「和其他目录有什么不同」，收录标准补充「已经有内容」「不收接单服务页与平台型产品」，并写明不要求自有域名。

### Changed
- 重写首页文案：去掉「+100% 独立」「赛道」「社群」等说法，排序按钮「推荐」改为「默认」，页脚标语与 README 统一为「让认真写字的人被找到」。
- 统一标签中文名（如 `blog` → 博客、`maker` → 创客、`writer` → 写作者）。
- 整理部分收录条目的简介与标签：修正标点、去掉自我宣传用语、把一次性标签换成推荐标签；`rateministere.com` 的名称与简介按站点实际内容更正。
- CONTRIBUTING 与 README 的标签表、字段说明保持一致，新增「简介怎么写」。

### Fixed
- README 顶部导航锚点失效。
- README 统计区里的 `feeds.opml` 链到了未入库的 `site/` 目录，改为线上地址。
- 首页把开放数据标为 CC0，与 LICENSE 的 MIT 不一致。

## [0.2.0] - 2026-10-30

### Changed
- 移除 GitHub Actions，校验、收录、构建、发布与巡检全部改为本地脚本（`deploy.py` 发布到 `gh-pages`）。

### Added
- `feed` 字段支持数组形式的多个订阅源。
- `ingest_issue.py` 支持手写列表格式的提交，增加商业落地页识别。

### Fixed
- Issue 收录中的命令注入、模板占位符污染与证书校验缺失。
- 子路径站点的图标抓取、`deploy.py` 发布路径导致的 Pages 404。

## [0.1.0] - 2026-09-25

### Added
- 首批站点与在线目录：静态渲染卡片、标签筛选、全文搜索、随机漫游。
- RSS 订阅合集 `feeds.opml`、开放数据 `sites.json`、完整目录页。
- README 站点表格、统计与项目历史由脚本自动同步。
- 站点巡检脚本 `check_health.py`，只报告不删数据。
