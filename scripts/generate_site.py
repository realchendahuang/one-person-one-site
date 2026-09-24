#!/usr/bin/env python3
"""把 data/sites.json 构建成一个纯静态网站，输出到 site/。

设计取舍：

- 卡片在构建期渲染成真实 HTML，而不是等浏览器执行 JS 再生成。目录站的价值
  在于让每个收录站点被看见；如果首屏内容只存在于 JS 里，不执行脚本的爬虫
  看到的是一片空白。JS 只作为筛选、排序、搜索的渐进增强。
- 站点图标在构建期缓存到本地（scripts/fetch_favicons.py），不再依赖第三方
  Favicon 服务，既避免跨境网络问题，也不向第三方泄露访客行为。
- 整站保持零运行时依赖：没有框架、没有 CDN、没有外部字体。

产物清单：
    site/index.html            主页面（首屏静态渲染）
    site/directory/index.html  完整目录页（可被爬虫抓取的纯静态列表）
    site/feeds.opml            收录站点的 RSS 合集，可一键导入阅读器
    site/data/sites.json       开放数据，供他人复用
    site/robots.txt            放行抓取并指向 sitemap
    site/sitemap.xml
    site/404.html
    site/DIRECTORY.md          仓库目录的 Markdown 副本
    site/favicon.svg, apple-touch-icon.png, og-image.png, favicons/*
"""
from __future__ import annotations

import html
import json
import re
import shutil
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sites.json"
FAVICON_DIR = ROOT / "data" / "favicons"
TEMPLATES = ROOT / "scripts" / "templates"
ASSETS = ROOT / "assets"
OUT = ROOT / "site"

SITE_URL = "https://realchendahuang.github.io/one-person-one-site/"
REPO_URL = "https://github.com/realchendahuang/one-person-one-site"
SUBMIT_URL = f"{REPO_URL}/issues/new?template=submit-site.yml"
SITE_TITLE = "一人一站"
SITE_SUBTITLE = "收集认真经营的独立博客与个人网站"
SITE_DESC = (
    "一人一站收录真实创作者独立经营的博客、数字花园与个人作品集，"
    "支持按标签浏览、全文检索与随机漫游，帮助你在平台围墙之外发现值得长期阅读的个人网站。"
)

ICON_RSS = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
    '<path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1"/></svg>'
)
ICON_ARROW = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">'
    '<path d="M7 17 17 7"/><path d="M7 7h10v10"/></svg>'
)

TAG_DISPLAY_NAMES = {
    "developer": "开发者",
    "blog": "独立博客",
    "portfolio": "作品集",
    "maker": "创作者",
    "indie-hacker": "独立开发",
    "notes": "数字笔记",
    "designer": "设计师",
    "ai": "人工智能",
    "digital-garden": "数字花园",
    "open-source": "开源作品",
    "writer": "文字创作者",
    "security": "网络安全",
    "photographer": "摄影日常",
    "game": "独立游戏",
    "research": "学术研究",
    "devops": "DevOps",
    "sre": "SRE 运维",
    "agent": "AI Agent",
    "personal-website": "个人主页",
}

TAG_COLORS = [
    "var(--tag-violet)",
    "var(--tag-orange)",
    "var(--tag-amber)",
    "var(--tag-gold)",
    "var(--tag-sky)",
    "var(--tag-emerald)",
    "var(--tag-rose)",
    "var(--tag-slate)",
]

# 首屏内的图标优先加载，其余懒加载
EAGER_ICONS = 12


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def domain_of(url: str) -> str:
    match = re.match(r"^https?://([^/]+)", url or "", re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).split(":")[0].lower()


def slug_for(domain: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", domain.lower()).strip("-") or "site"


def first_char(name: str, domain: str) -> str:
    clean = re.sub(r"^https?://", "", (name or domain or "").strip())
    return clean[0].upper() if clean else "?"


def favicon_markup(site: dict, index: int) -> str:
    """本地缓存的图标；没有缓存时用首字母色块兜底（构建期就确定，无额外请求）。"""
    domain = domain_of(site.get("url", ""))
    slug = slug_for(domain)
    for ext in ("png", "svg"):
        if (FAVICON_DIR / f"{slug}.{ext}").exists():
            loading = "" if index < EAGER_ICONS else ' loading="lazy"'
            return (
                f'<img src="./favicons/{slug}.{ext}" alt="" width="42" height="42"'
                f' decoding="async"{loading}>'
            )
    char = esc(first_char(site.get("name", ""), domain))
    return f'<span class="site-favicon-letter">{char}</span>'


def card_html(site: dict, index: int) -> str:
    url = site.get("url", "")
    domain = domain_of(url)
    owner = site.get("owner", "")
    sub_parts = []
    if owner:
        sub_parts.append(f'<span class="sub-owner">{esc(owner)}</span>')
    if domain:
        sub_parts.append(f'<span class="sub-domain">{esc(domain)}</span>')
    sub = '<span class="sub-sep">·</span>'.join(sub_parts)
    tags = "".join(
        f'<span class="card-tag">#{esc(tag)}</span>' for tag in site.get("tags", [])[:3]
    )

    actions = ""
    if site.get("feed"):
        actions += (
            f'<button type="button" class="mini-action-btn" data-copy="{esc(site["feed"])}"'
            f' data-copy-label="已复制 RSS 订阅源" title="复制 RSS 订阅源"'
            f' aria-label="复制 {esc(site["name"])} 的 RSS 订阅源">{ICON_RSS}</button>'
        )

    return f"""    <article class="site-card" data-url="{esc(url)}">
      <div class="card-top">
        <div class="card-header-main">
          <span class="site-favicon">{favicon_markup(site, index)}</span>
          <div class="card-title-wrap">
            <h3 class="site-name"><a class="site-link" href="{esc(url)}" target="_blank" rel="noopener noreferrer" title="{esc(site.get("name", ""))}">{esc(site.get("name", ""))}</a></h3>
            <div class="site-owner-sub">{sub}</div>
          </div>
        </div>
        <div class="card-arrow-icon" aria-hidden="true">{ICON_ARROW}</div>
      </div>
      <p class="site-desc">{esc(site.get("description", ""))}</p>
      <div class="card-bottom">
        <div class="card-tags">{tags}</div>
        <div class="card-actions">{actions}</div>
      </div>
    </article>"""


def build_milestones_markup(sites: list[dict]) -> tuple[str, str]:
    tag_counts = Counter(tag for site in sites for tag in site.get("tags", []))
    total_tags_instances = sum(tag_counts.values()) or 1

    sorted_tags = sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    top_tags = sorted_tags[:8]

    bar_segments = []
    for idx, (tag, count) in enumerate(top_tags):
        color = TAG_COLORS[idx % len(TAG_COLORS)]
        label = TAG_DISPLAY_NAMES.get(tag, tag)
        pct = max(1, round(count / total_tags_instances * 100))
        bar_segments.append(
            f'<button type="button" class="milestone-segment" data-tag="{esc(tag)}" '
            f'style="flex-grow:{count};flex-basis:0;background:{color}" '
            f'aria-label="{esc(label)} {count} 个站点，占 {pct}%" '
            f'title="{esc(label)}: {count} 个站点 ({pct}%)"></button>'
        )

    remaining_count = sum(count for tag, count in sorted_tags[8:])
    if remaining_count > 0:
        bar_segments.append(
            f'<button type="button" class="milestone-segment" data-tag="" '
            f'style="flex-grow:{remaining_count};flex-basis:0;background:var(--tag-slate)" '
            f'aria-label="其他赛道 {remaining_count} 个" title="其他赛道: {remaining_count} 个"></button>'
        )

    milestone_pills = []
    for idx, (tag, count) in enumerate(sorted_tags[:14]):
        color = TAG_COLORS[idx % len(TAG_COLORS)] if idx < len(top_tags) else "var(--tag-slate)"
        label = TAG_DISPLAY_NAMES.get(tag, tag)
        milestone_pills.append(
            f'<button type="button" class="milestone-pill" data-tag="{esc(tag)}">'
            f'<span class="milestone-dot" style="background:{color}" aria-hidden="true"></span>'
            f'{esc(label)} <b class="tabular-nums">{count}</b></button>'
        )

    return "".join(bar_segments), "".join(milestone_pills)


def build_jsonld(sites: list[dict]) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": f"{SITE_TITLE} · {SITE_SUBTITLE}",
        "description": SITE_DESC,
        "url": SITE_URL,
        "inLanguage": "zh-CN",
        "isFamilyFriendly": True,
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(sites),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index,
                    "name": site.get("name", ""),
                    "url": site.get("url", ""),
                    "description": site.get("description", ""),
                }
                for index, site in enumerate(sites, start=1)
            ],
        },
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def build_opml(sites: list[dict]) -> str:
    feeds = [s for s in sites if s.get("feed")]
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<opml version="2.0">',
        "  <head>",
        f"    <title>{esc(SITE_TITLE)} · 订阅合集</title>",
        f"    <dateCreated>{date.today().isoformat()}</dateCreated>",
        f"    <docs>{esc(SITE_URL)}</docs>",
        "  </head>",
        "  <body>",
        f'    <outline text="{esc(SITE_TITLE)} · 收录站点" title="{esc(SITE_TITLE)} · 收录站点">',
    ]
    for site in feeds:
        name = esc(site.get("name", ""))
        lines.append(
            f'      <outline type="rss" text="{name}" title="{name}"'
            f' xmlUrl="{esc(site["feed"])}" htmlUrl="{esc(site.get("url", ""))}"/>'
        )
    lines += ["    </outline>", "  </body>", "</opml>", ""]
    return "\n".join(lines)


def build_directory_page(sites: list[dict], style: str) -> str:
    """完整目录页：纯静态可被抓取的列表，替代直接从页脚下载裸 Markdown。"""
    tag_counts = Counter(tag for site in sites for tag in site.get("tags", []))

    by_tag: list[str] = []
    for tag, count in sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        label = TAG_DISPLAY_NAMES.get(tag, tag)
        members = [s for s in sites if tag in s.get("tags", [])]
        items = "".join(
            f'<li><a href="{esc(s.get("url", ""))}" target="_blank" rel="noopener noreferrer">'
            f'{esc(s.get("name", ""))}</a>'
            f'<span>{esc(s.get("owner", ""))}</span></li>'
            for s in members
        )
        by_tag.append(
            f'<section class="tag-group panel-card"><h3><span>{esc(label)} <small style="color:var(--fog);font-weight:400">#{esc(tag)}</small></span> <span class="count">{count}</span></h3>'
            f"<ul>{items}</ul></section>"
        )

    alphabetical = "".join(
        f'<li><a href="{esc(s.get("url", ""))}" target="_blank" rel="noopener noreferrer">'
        f'{esc(s.get("name", ""))}</a>'
        f'<span class="who">{esc(s.get("owner", ""))}</span>'
        f'<span class="desc">{esc(s.get("description", ""))}</span></li>'
        for s in sorted(sites, key=lambda s: s.get("name", "").lower())
    )

    feeds = [s for s in sites if s.get("feed")]

    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme-mode="system">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>完整目录 · {SITE_TITLE}</title>
<meta name="description" content="一人一站收录的全部 {len(sites)} 个独立博客、数字花园与个人网站，按标签与名称两种方式列出。">
<link rel="canonical" href="{SITE_URL}directory/">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#0a0a0a">
<script>
  (function() {{
    var stored = "dark";
    try {{ stored = localStorage.getItem("opos-theme") || "dark"; }} catch(e) {{}}
    document.documentElement.setAttribute("data-theme-mode", stored);
    var prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    var isDark = stored === "dark" || (stored === "system" && prefersDark);
    if (isDark) {{
      document.documentElement.classList.add("dark");
    }} else {{
      document.documentElement.classList.remove("dark");
    }}
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", isDark ? "#0a0a0a" : "#f5f6f7");
  }})();
</script>
<style>
{style}
.dir-nav {{ margin-bottom: 1.5rem; font-size: 0.88rem; }}
.dir-nav a {{ color: var(--signal); text-decoration: none; font-weight: 600; }}
.dir-nav a:hover {{ text-decoration: underline; }}
.dir-intro {{ color: var(--mist); font-size: 0.95rem; margin: 0 0 1.8rem; line-height: 1.6; }}
.tag-group {{ padding: 1.2rem 1.5rem; margin-bottom: 1rem; }}
.tag-group ul {{ list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 0.5rem; }}
.tag-group li {{ display: flex; align-items: baseline; justify-content: space-between; gap: 0.5rem; font-size: 0.88rem; padding: 0.5rem 0.75rem; background: var(--soft-surface); border: 1px solid var(--line); border-radius: var(--radius-sm); }}
.tag-group li span {{ color: var(--fog); font-size: 0.76rem; }}
.tag-group a {{ text-decoration: none; font-weight: 600; color: var(--ink); }}
.tag-group a:hover {{ color: var(--signal); }}
.tag-group h3 {{ font-size: 1.05rem; font-weight: 800; margin: 0 0 0.85rem; color: var(--ink); display: flex; align-items: center; justify-content: space-between; }}
.tag-group .count {{ color: var(--mist); font-weight: 600; font-size: 0.8rem; font-variant-numeric: tabular-nums; }}
.all-list {{ padding: 1.2rem 1.5rem; }}
.all-list ul {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.45rem; }}
.all-list li {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.6rem; padding: 0.65rem 0.85rem; background: var(--soft-surface); border: 1px solid var(--line); border-radius: var(--radius-sm); }}
.all-list a {{ text-decoration: none; font-weight: 700; font-size: 0.92rem; color: var(--ink); }}
.all-list a:hover {{ color: var(--signal); }}
.all-list .who {{ color: var(--mist); font-size: 0.8rem; }}
.all-list .desc {{ color: var(--fog); font-size: 0.82rem; flex: 1 1 100%; margin-top: 0.15rem; }}
h1 {{ font-size: 1.85rem; font-weight: 800; letter-spacing: -0.025em; margin: 0 0 0.5rem; }}
h2 {{ font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em; margin: 2rem 0 0.8rem; }}
</style>
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <a href="../" class="brand" aria-label="{SITE_TITLE} 首页">
      <span class="brand-pulse"></span>
      <span class="brand-title">{SITE_TITLE}</span>
      <span class="brand-sub">One Person, One Site</span>
    </a>
    <nav class="nav-pills" aria-label="导航">
      <a href="../" class="nav-pill">首页</a>
      <a href="./" class="nav-pill active" aria-current="page">完整目录</a>
      <a href="../feeds.opml" download class="nav-pill">订阅合集</a>
      <a href="{SUBMIT_URL}" target="_blank" rel="noopener" class="nav-pill">提交新站</a>
    </nav>
  </div>
</header>

<main class="main-wrapper">
  <h1>完整目录</h1>
  <p class="dir-intro">共收录 {len(sites)} 个站点，均来自真实创作者独立经营的博客、数字花园或作品集。其中 {len(feeds)} 个提供 RSS 订阅源，可通过 <a href="../feeds.opml">订阅合集</a> 一键导入阅读器。</p>
  <p class="dir-nav"><a href="../">← 返回首页</a></p>

  <h2>按标签浏览</h2>
  {"".join(by_tag)}

  <h2>按名称列出</h2>
  <section class="all-list panel-card"><ul>{alphabetical}</ul></section>
</main>

<footer class="site-footer">
  <div class="footer-links">
    <a href="../">首页</a>
    <span aria-hidden="true">·</span>
    <a href="../feeds.opml">订阅合集</a>
    <span aria-hidden="true">·</span>
    <a href="{REPO_URL}" target="_blank" rel="noopener">GitHub</a>
    <span aria-hidden="true">·</span>
    <a href="{SUBMIT_URL}" target="_blank" rel="noopener">提交新站</a>
  </div>
  <div class="footer-motto">{SITE_TITLE} · 属于每一个人的独立互联网家园</div>
</footer>
</body>
</html>
"""


def build_404(style: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme-mode="system">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>页面不存在 · {SITE_TITLE}</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/one-person-one-site/favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#0a0a0a">
<script>
  (function() {{
    var stored = "dark";
    try {{ stored = localStorage.getItem("opos-theme") || "dark"; }} catch(e) {{}}
    document.documentElement.setAttribute("data-theme-mode", stored);
    var prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    var isDark = stored === "dark" || (stored === "system" && prefersDark);
    if (isDark) {{
      document.documentElement.classList.add("dark");
    }} else {{
      document.documentElement.classList.remove("dark");
    }}
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", isDark ? "#0a0a0a" : "#f5f6f7");
  }})();
</script>
<style>
{style}
.notfound-wrap {{ display: flex; align-items: center; justify-content: center; min-height: 60vh; }}
.notfound {{ text-align: center; padding: 3rem 2rem; max-width: 480px; width: 100%; }}
.notfound-code {{ font-size: 4rem; font-weight: 800; letter-spacing: -0.04em; color: var(--signal); line-height: 1; margin-bottom: 0.6rem; }}
.notfound h1 {{ font-size: 1.4rem; font-weight: 800; margin: 0 0 0.6rem; color: var(--ink); }}
.notfound p {{ color: var(--mist); font-size: 0.92rem; margin: 0 0 1.8rem; line-height: 1.6; }}
</style>
</head>
<body>
<main class="main-wrapper notfound-wrap">
  <div class="panel-card notfound">
    <div class="notfound-code">404</div>
    <h1>这里没有内容</h1>
    <p>你要找的页面不存在，或已经被移动到其他位置。</p>
    <a class="hero-action-btn primary" href="/one-person-one-site/">回到一人一站首页</a>
  </div>
</main>
</body>
</html>
"""


def build_sitemap() -> str:
    today = date.today().isoformat()
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{SITE_URL}</loc><lastmod>{today}</lastmod>"
        "<changefreq>daily</changefreq><priority>1.0</priority></url>\n"
        f"  <url><loc>{SITE_URL}directory/</loc><lastmod>{today}</lastmod>"
        "<changefreq>weekly</changefreq><priority>0.7</priority></url>\n"
        "</urlset>\n"
    )


def build_robots() -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n"


def main() -> None:
    sites = json.loads(DATA.read_text(encoding="utf-8"))
    styles = (TEMPLATES / "styles.css").read_text(encoding="utf-8")
    template = (TEMPLATES / "index.html").read_text(encoding="utf-8")
    app_js = (TEMPLATES / "app.js").read_text(encoding="utf-8")

    payload = json.dumps({"sites": sites}, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")

    feeds_count = sum(1 for s in sites if s.get("feed"))
    feed_percent = f"{(feeds_count / len(sites) * 100):.1f}" if sites else "0.0"

    custom_domains = sum(
        1 for s in sites
        if not any(domain_of(s.get("url", "")).endswith(sub) for sub in (".pages.dev", ".github.io", ".vercel.app"))
    )
    domain_percent = f"{(custom_domains / len(sites) * 100):.1f}" if sites else "0.0"

    owners_count = len(set(s.get("owner", "") for s in sites if s.get("owner")))
    tag_counts = Counter(tag for site in sites for tag in site.get("tags", []))
    tag_count = len(tag_counts)

    bar_html, pills_html = build_milestones_markup(sites)

    page = template
    page = page.replace("/*__STYLES__*/", styles)
    page = page.replace("//__APP__", app_js)
    page = page.replace("__JSONLD__", build_jsonld(sites))
    page = page.replace("__SITE_COUNT__", str(len(sites)))
    page = page.replace("__FEED_COUNT__", str(feeds_count))
    page = page.replace("__FEED_PERCENT__", feed_percent)
    page = page.replace("__DOMAIN_PERCENT__", domain_percent)
    page = page.replace("__OWNER_COUNT__", str(owners_count))
    page = page.replace("__TAG_COUNT__", str(tag_count))
    page = page.replace("__MILESTONE_BAR__", bar_html)
    page = page.replace("__MILESTONE_TAGS__", pills_html)
    page = page.replace(
        "__CARDS__", "\n".join(card_html(site, i) for i, site in enumerate(sites))
    )
    page = page.replace("__SITES_DATA__", payload)

    leftovers = sorted(set(re.findall(r"__[A-Z_]+__", page)))
    if leftovers:
        raise SystemExit(f"模板占位符未全部替换: {', '.join(leftovers)}")

    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / "robots.txt").write_text(build_robots(), encoding="utf-8")
    (OUT / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    (OUT / "404.html").write_text(build_404(styles), encoding="utf-8")
    (OUT / "feeds.opml").write_text(build_opml(sites), encoding="utf-8")

    (OUT / "directory").mkdir(exist_ok=True)
    (OUT / "directory" / "index.html").write_text(
        build_directory_page(sites, styles), encoding="utf-8"
    )

    # 开放数据：让别人可以复用这份目录，而不必抓取页面
    (OUT / "data").mkdir(exist_ok=True)
    shutil.copyfile(DATA, OUT / "data" / "sites.json")

    directory_md = ROOT / "DIRECTORY.md"
    if directory_md.exists():
        shutil.copyfile(directory_md, OUT / "DIRECTORY.md")

    # 站点图标与品牌资源
    icons_out = OUT / "favicons"
    if icons_out.exists():
        shutil.rmtree(icons_out)
    icons_out.mkdir(parents=True)
    for icon in FAVICON_DIR.glob("*"):
        if icon.suffix in {".png", ".svg"}:
            shutil.copyfile(icon, icons_out / icon.name)
    for asset in ("favicon.svg", "apple-touch-icon.png", "og-image.png"):
        source = ASSETS / asset
        if source.exists():
            shutil.copyfile(source, OUT / asset)
        else:
            print(f"WARN: 缺少 assets/{asset}，请运行 python3 scripts/build_assets.py")

    missing_icons = [
        domain_of(s["url"])
        for s in sites
        if not any(
            (FAVICON_DIR / f"{slug_for(domain_of(s['url']))}.{ext}").exists()
            for ext in ("png", "svg")
        )
    ]
    print(f"Generated site/ with {len(sites)} site(s)")
    if missing_icons:
        print(f"NOTE: {len(missing_icons)} 个站点使用首字母兜底图标: {', '.join(missing_icons)}")


if __name__ == "__main__":
    main()
