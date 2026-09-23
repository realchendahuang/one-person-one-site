#!/usr/bin/env python3
"""构建产物的回归测试：防止关键质量属性被改回去。

这里检查的都是曾经真实出过问题的点：
  1. 卡片必须在 HTML 里静态渲染（曾整站依赖 JS 生成，爬虫看到空页面）；
  2. 页面不能依赖第三方 Favicon 服务（曾用 google.com，中国大陆访问不到）；
  3. 锚点里不能嵌 <button>（曾导致键盘焦点重复、读屏语义混乱）；
  4. 不能禁用用户缩放（maximum-scale=1 违反 WCAG 1.4.4）；
  5. robots / sitemap / OPML / 开放数据等产物必须齐全。

用法：
    python3 tests/test_build.py            # 假定 site/ 已构建
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data" / "sites.json"

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
SVG_TAGS = {"svg", "path", "circle", "rect", "line", "polyline", "polygon", "g", "defs", "use", "text", "ellipse", "stop"}


def load_sites() -> list[dict]:
    return json.loads(DATA.read_text(encoding="utf-8"))


def test_outputs_exist():
    sites = load_sites()
    for rel in (
        "index.html", "directory/index.html", "feeds.opml", "sitemap.xml",
        "robots.txt", "404.html", "data/sites.json", "favicon.svg",
        "apple-touch-icon.png", "og-image.png",
    ):
        assert (SITE / rel).exists(), f"缺少构建产物 site/{rel}"
    assert (SITE / "data" / "sites.json").read_text(encoding="utf-8") == \
        DATA.read_text(encoding="utf-8"), "site/data/sites.json 与源数据不一致"
    assert sites, "数据为空"


def test_cards_are_statically_rendered():
    """每一条收录数据都要在首屏 HTML 里出现，而不是等 JS 生成。"""
    html = (SITE / "index.html").read_text(encoding="utf-8")
    sites = load_sites()

    cards = re.findall(r'<article class="site-card".*?</article>', html, re.S)
    assert len(cards) == len(sites), f"卡片数 {len(cards)} 与站点数 {len(sites)} 不一致"

    for site in sites:
        assert f'data-url="{site["url"]}"' in html, f"卡片缺少 {site['url']}"
        assert f'href="{site["url"]}"' in html, f"缺少指向 {site['url']} 的真实链接"


def test_no_third_party_icon_service():
    for name in ("index.html", "directory/index.html"):
        html = (SITE / name).read_text(encoding="utf-8")
        for host in ("google.com/s2/favicons", "icons.duckduckgo.com", "favicon.im"):
            assert host not in html, f"{name} 仍依赖第三方图标服务 {host}"


def test_no_nested_interactive_elements():
    """<a> 内不得再出现按钮/输入框等交互元素。"""
    html = (SITE / "index.html").read_text(encoding="utf-8")
    for match in re.finditer(r"<a\b[^>]*>(.*?)</a>", html, re.S):
        inner = match.group(1)
        assert not re.search(r"<(button|input|select|textarea)\b", inner), \
            "锚点内部嵌入了交互元素"


def test_viewport_allows_zoom():
    html = (SITE / "index.html").read_text(encoding="utf-8")
    assert "maximum-scale=1" not in html, "不应禁用用户缩放"
    assert "user-scalable=no" not in html, "不应禁用用户缩放"


def test_metadata_present():
    html = (SITE / "index.html").read_text(encoding="utf-8")
    for needle in (
        'rel="canonical"', "application/ld+json", 'name="theme-color"',
        'property="og:image"', 'name="description"', "<h1",
    ):
        assert needle in html, f"缺少 {needle}"


def test_well_formed_html():
    """标签必须闭合，避免浏览器自行修复出意外结构。"""
    html = (SITE / "index.html").read_text(encoding="utf-8")
    stack: list[str] = []
    for token in re.finditer(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?(/?)>", html):
        closing, tag, self_closing = token.group(1), token.group(2).lower(), token.group(3)
        if tag in SVG_TAGS or tag in VOID_TAGS or self_closing:
            continue
        if closing:
            if stack and stack[-1] == tag:
                stack.pop()
            elif tag in stack:
                while stack and stack.pop() != tag:
                    pass
        else:
            stack.append(tag)
    assert not stack, f"存在未闭合标签: {stack[:5]}"


def test_feeds_opml():
    sites = load_sites()
    with_feed = [s for s in sites if s.get("feed")]
    root = ET.fromstring((SITE / "feeds.opml").read_text(encoding="utf-8"))
    outlines = root.findall(".//outline[@xmlUrl]")
    assert len(outlines) == len(with_feed), \
        f"OPML 条目数 {len(outlines)} 与带 feed 的站点数 {len(with_feed)} 不一致"
    urls = {o.get("xmlUrl") for o in outlines}
    for site in with_feed:
        assert site["feed"] in urls, f"OPML 缺少 {site['feed']}"


def test_sitemap_and_robots():
    root = ET.fromstring((SITE / "sitemap.xml").read_text(encoding="utf-8"))
    locs = [el.text for el in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    assert any(loc and loc.endswith("/") for loc in locs), "sitemap 缺少首页"
    assert any(loc and "directory" in loc for loc in locs), "sitemap 缺少目录页"

    robots = (SITE / "robots.txt").read_text(encoding="utf-8")
    assert "sitemap.xml" in robots, "robots.txt 未指向 sitemap"


def test_directory_page_lists_everything():
    html = (SITE / "directory" / "index.html").read_text(encoding="utf-8")
    for site in load_sites():
        assert site["url"] in html, f"目录页缺少 {site['url']}"


def test_local_favicons_copied():
    icons = list((SITE / "favicons").glob("*"))
    sources = [p for p in (ROOT / "data" / "favicons").glob("*") if p.suffix in {".png", ".svg"}]
    assert len(icons) >= len(sources), "本地图标未全部拷贝到 site/favicons/"


def test_no_template_placeholders():
    html = (SITE / "index.html").read_text(encoding="utf-8")
    leftover = re.findall(r"__[A-Z_]+__", html)
    assert not leftover, f"模板占位符残留: {leftover}"


def main() -> None:
    tests = [
        (name, fn)
        for name, fn in sorted(globals().items())
        if name.startswith("test_") and callable(fn)
    ]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"ERROR {name}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
