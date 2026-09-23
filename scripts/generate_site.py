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

CARD_GRADIENT = [
    "linear-gradient(135deg, #ff6a00, #ff8c37)",
    "linear-gradient(135deg, #0284c7, #38bdf8)",
    "linear-gradient(135deg, #059669, #34d399)",
    "linear-gradient(135deg, #7c3aed, #a78bfa)",
    "linear-gradient(135deg, #d97706, #fbbf24)",
]

ICON_RSS = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
    '<path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1"/></svg>'
)
ICON_COPY = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
    '<rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>'
    '<path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>'
)
ICON_ARROW = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">'
    '<path d="M7 17 17 7"/><path d="M7 7h10v10"/></svg>'
)

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
                f'<img src="./favicons/{slug}.{ext}" alt="" width="30" height="30"'
                f' decoding="async"{loading}>'
            )
    char = esc(first_char(site.get("name", ""), domain))
    gradient = CARD_GRADIENT[(ord(char[0]) if char else 0) % len(CARD_GRADIENT)]
    return f'<span class="site-favicon-letter" style="background:{gradient}">{char}</span>'


def card_html(site: dict, index: int) -> str:
    url = site.get("url", "")
    domain = domain_of(url)
    owner = site.get("owner", "")
    sub = " · ".join(part for part in (owner, domain) if part)
    tags = "".join(
        f'<span class="card-tag">{esc(tag)}</span>' for tag in site.get("tags", [])[:3]
    )

    actions = ""
    if site.get("feed"):
        actions += (
            f'<button type="button" class="mini-action-btn" data-copy="{esc(site["feed"])}"'
            f' data-copy-label="已复制 RSS 源" title="复制 RSS 订阅源"'
            f' aria-label="复制 {esc(site["name"])} 的 RSS 订阅源">{ICON_RSS}</button>'
        )
    actions += (
        f'<button type="button" class="mini-action-btn" data-copy="{esc(url)}"'
        f' data-copy-label="已复制网址" aria-label="复制 {esc(site["name"])} 的网址"'
        f' title="复制网址">{ICON_COPY}</button>'
    )

    return f"""    <article class="site-card" data-url="{esc(url)}">
      <div class="card-top">
        <div class="card-header-main">
          <span class="site-favicon">{favicon_markup(site, index)}</span>
          <div class="card-title-wrap">
            <h3 class="site-name"><a class="site-link" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(site.get("name", ""))}</a></h3>
            <div class="site-owner-sub">{esc(sub)}</div>
          </div>
        </div>
        <div class="card-arrow-icon">{ICON_ARROW}</div>
      </div>
      <p class="site-desc">{esc(site.get("description", ""))}</p>
      <div class="card-bottom">
        <div class="card-tags">{tags}</div>
        <div class="card-actions">{actions}</div>
      </div>
    </article>"""


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
        members = [s for s in sites if tag in s.get("tags", [])]
        items = "".join(
            f'<li><a href="{esc(s.get("url", ""))}" target="_blank" rel="noopener noreferrer">'
            f'{esc(s.get("name", ""))}</a>'
            f'<span>{esc(s.get("owner", ""))}</span></li>'
            for s in members
        )
        by_tag.append(
            f'<section class="tag-group"><h3>{esc(tag)} <span class="count">{count}</span></h3>'
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
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>完整目录 · {SITE_TITLE}</title>
<meta name="description" content="一人一站收录的全部 {len(sites)} 个独立博客、数字花园与个人网站，按标签与名称两种方式列出。">
<link rel="canonical" href="{SITE_URL}directory/">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#f7f7f8" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#09090b" media="(prefers-color-scheme: dark)">
<style>
{style}
.dir-nav {{ margin-bottom: 1.5rem; font-size: 0.85rem; }}
.dir-intro {{ color: var(--mist); font-size: 0.9rem; margin: 0 0 1.5rem; }}
.tag-group ul {{ list-style: none; margin: 0 0 0.4rem; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 0.35rem; }}
.tag-group li {{ display: flex; align-items: baseline; gap: 0.5rem; font-size: 0.86rem; padding: 0.35rem 0.6rem; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius-sm); }}
.tag-group li span {{ color: var(--fog); font-size: 0.76rem; }}
.tag-group a {{ text-decoration: none; font-weight: 600; }}
.tag-group a:hover {{ color: var(--signal); }}
.tag-group h3 {{ font-size: 0.95rem; margin: 1.6rem 0 0.6rem; }}
.tag-group .count {{ color: var(--fog); font-weight: 400; font-size: 0.8rem; }}
.all-list ul {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.3rem; }}
.all-list li {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.6rem; padding: 0.5rem 0.7rem; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius-sm); }}
.all-list a {{ text-decoration: none; font-weight: 650; font-size: 0.9rem; }}
.all-list a:hover {{ color: var(--signal); }}
.all-list .who {{ color: var(--mist); font-size: 0.78rem; }}
.all-list .desc {{ color: var(--fog); font-size: 0.8rem; flex: 1 1 100%; }}
h1 {{ font-size: 1.5rem; margin: 0 0 0.5rem; }}
h2 {{ font-size: 1.1rem; margin: 2.2rem 0 0.6rem; }}
</style>
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <a href="../" class="brand" aria-label="{SITE_TITLE} 首页">
      <span class="brand-pulse"></span>
      <span>{SITE_TITLE}</span>
      <span class="brand-sub">One Person, One Site</span>
    </a>
  </div>
</header>

<main class="main-wrapper">
  <h1>完整目录</h1>
  <p class="dir-intro">共收录 {len(sites)} 个站点，均来自真实创作者独立经营的博客、数字花园或作品集。其中 {len(feeds)} 个提供 RSS 订阅源，可通过 <a href="../feeds.opml">订阅合集</a> 一键导入阅读器。</p>
  <p class="dir-nav"><a href="../">← 返回首页</a></p>

  <h2>按标签浏览</h2>
  {"".join(by_tag)}

  <h2>按名称列出</h2>
  <section class="all-list"><ul>{alphabetical}</ul></section>
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
  <div>{SITE_TITLE} · 属于每一个人的独立互联网家园</div>
</footer>
</body>
</html>
"""


def build_404(style: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>页面不存在 · {SITE_TITLE}</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/one-person-one-site/favicon.svg" type="image/svg+xml">
<style>
{style}
.notfound {{ text-align: center; padding: 5rem 1rem; }}
.notfound h1 {{ font-size: 1.4rem; margin: 0 0 0.6rem; }}
.notfound p {{ color: var(--mist); font-size: 0.9rem; margin: 0 0 1.5rem; }}
</style>
</head>
<body>
<main class="main-wrapper">
  <div class="notfound">
    <h1>这里没有内容</h1>
    <p>你要找的页面不存在，或已经被移动。</p>
    <a class="h-btn h-btn-primary" href="/one-person-one-site/">回到一人一站首页</a>
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

    page = template
    page = page.replace("/*__STYLES__*/", styles)
    page = page.replace("//__APP__", app_js)
    page = page.replace("__JSONLD__", build_jsonld(sites))
    page = page.replace("__SITE_COUNT__", str(len(sites)))
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
    # 图标文件名随域名变化，先清空再拷贝，否则换过图标来源的域名会在产物里
    # 同时留下新旧两个文件（旧的还可能被优先命中）。
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
