#!/usr/bin/env python3
"""为收录站点抓取并缓存 Favicon，输出到 data/favicons/<slug>.png。

为什么要在构建期缓存，而不是让浏览器直接去第三方取图：

- 原先页面使用 `https://www.google.com/s2/favicons`，而 google.com 在中国大陆
  无法直连。本目录的收录站点与访客以中文用户为主，会导致大量图标退化成
  首字母色块，整站视觉打折。
- 图标一旦落到本仓库，就与第三方服务的可用性、限流、跨境网络无关，
  且不再向任何第三方泄露访客的浏览行为。

抓取顺序（逐个尝试，任一成功即停止）：
    1. Google s2（在 CI 上可用，质量稳定，结果随后被固化进仓库）
    2. 站点自身的 /favicon.ico
    3. DuckDuckGo icons

抓不到时不会中断构建：generate_site.py 会为该站点生成渐变首字母 SVG 兜底。

用法：
    python3 scripts/fetch_favicons.py            # 只补齐缺失的图标
    python3 scripts/fetch_favicons.py --force    # 全部重新抓取
    python3 scripts/fetch_favicons.py --check    # 只报告缺失情况，不写文件
"""
from __future__ import annotations

import base64
import binascii
import io
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sites.json"
OUT_DIR = ROOT / "data" / "favicons"

TIMEOUT = 15
CANVAS = 64
MAX_BYTES = 2_000_000
MIN_SIDE = 16
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def slug_for(domain: str) -> str:
    """把域名转成稳定的文件名，例如 blackman99.github.io → blackman99-github-io。"""
    slug = re.sub(r"[^a-z0-9]+", "-", domain.lower()).strip("-")
    return slug or "site"


def domain_of(url: str) -> str:
    match = re.match(r"^https?://([^/]+)", url, re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).split(":")[0].lower()


def sources_for(domain: str) -> list[str]:
    return [
        f"https://{domain}/favicon.svg",
        f"https://www.google.com/s2/favicons?domain={domain}&sz=128",
        f"https://{domain}/favicon.ico",
        f"https://icons.duckduckgo.com/ip3/{domain}.ico",
    ]


ICON_LINK_RE = re.compile(
    # href 可能被单引号或双引号包裹，而 data: URI 内部又会包含另一种引号
    # （例如 href="data:image/svg+xml,...xmlns='...'"），所以两侧要分开处理。
    r"<link\b[^>]*?(?:rel=[\"'][^\"']*icon[^\"']*[\"'][^>]*?href=(?:\"([^\"]*)\"|'([^']*)')"
    r"|href=(?:\"([^\"]*)\"|'([^']*)')[^>]*?rel=[\"'][^\"']*icon[^\"']*[\"'])",
    re.IGNORECASE,
)


def declared_icon_urls(domain: str) -> list[str]:
    """从站点 HTML 的 <link rel="icon"> 里取出图标地址，支持 data: URI。

    有些站点（例如用 data: URI 内联 SVG 的）没有可抓取的 /favicon.ico，
    只有这一条路能拿到它的真实图标。相对路径（./favicon.svg、/icon.png）用
    urljoin 按站点根解析，否则会被当成非法 URL 直接抛错。
    """
    base = f"https://{domain}/"
    request = urllib.request.Request(base, headers={"User-Agent": BROWSER_UA})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            html = response.read(400_000).decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return []

    urls: list[str] = []
    for match in ICON_LINK_RE.finditer(html):
        href = next((g for g in match.groups() if g), "").strip()
        if not href:
            continue
        if href.startswith("data:"):
            urls.append(href)
            continue
        urls.append(urllib.parse.urljoin(base, href))
    return urls


def download(url: str) -> bytes | None:
    if url.startswith("data:"):
        return decode_data_uri(url)
    request = urllib.request.Request(
        url, headers={"User-Agent": BROWSER_UA, "Accept": "image/*,*/*;q=0.8"}
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            if response.status != 200:
                return None
            raw = response.read(MAX_BYTES + 1)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None
    if not raw or len(raw) > MAX_BYTES:
        return None
    return raw


def decode_data_uri(url: str) -> bytes | None:
    header, _, payload = url.partition(",")
    if not payload:
        return None
    try:
        if ";base64" in header:
            return base64.b64decode(payload, validate=False)
        return urllib.parse.unquote_to_bytes(payload)
    except (ValueError, binascii.Error):
        return None


def as_svg(raw: bytes) -> bytes | None:
    """校验并规范化 SVG 图标，去掉脚本与外部引用后原样保存。"""
    text = raw.decode("utf-8", "replace").strip()
    if "<svg" not in text.lower():
        return None
    if len(text) > 40_000:
        return None
    # 图标是别人站点的内容，剔除 <script> 与外部引用后再落盘
    text = re.sub(r"<script\b.*?</script\s*>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"\son\w+\s*=\s*[\"'][^\"']*[\"']", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<foreignObject\b.*?</foreignObject\s*>", "", text, flags=re.IGNORECASE | re.DOTALL)
    if "javascript:" in text.lower():
        return None
    return text.encode("utf-8")


def normalize(raw: bytes) -> bytes | None:
    """把位图图标统一成 64x64 PNG，保留透明背景。

    先按不透明内容裁掉多余留白：Google s2 等服务返回的图标常带大片透明边距，
    直接缩放会让图标在卡片里显得又小又空。
    """
    try:
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            if min(image.size) < MIN_SIDE:
                return None
            frame = image.convert("RGBA")
            box = frame.split()[-1].getbbox()
            if box:
                frame = frame.crop(box)
            if min(frame.size) < 1:
                return None
            # 统一放大到铺满画布：不同站点图标自带的留白与原始尺寸差别很大，
            # 不归一化的话，卡片里会出现有的图标小一圈、有的顶满格。
            frame = frame.resize(
                (
                    max(1, round(frame.width * CANVAS / max(frame.size))),
                    max(1, round(frame.height * CANVAS / max(frame.size))),
                ),
                Image.LANCZOS,
            )
            canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
            canvas.paste(
                frame,
                ((CANVAS - frame.width) // 2, (CANVAS - frame.height) // 2),
                frame,
            )
            buffer = io.BytesIO()
            canvas.save(buffer, format="PNG", optimize=True)
            return buffer.getvalue()
    except (OSError, ValueError):
        return None


def fetch_one(domain: str) -> tuple[str, bytes] | None:
    """返回 (扩展名, 文件内容)，抓不到返回 None。"""
    candidates = declared_icon_urls(domain) + sources_for(domain)
    for url in candidates:
        raw = download(url)
        if not raw:
            continue
        if url.lower().split("?")[0].endswith(".svg") or raw.lstrip()[:4] == b"<svg" or b"<svg" in raw[:200].lower():
            svg = as_svg(raw)
            if svg:
                return ("svg", svg)
        png = normalize(raw)
        if png:
            return ("png", png)
    return None


def main() -> None:
    force = "--force" in sys.argv
    check_only = "--check" in sys.argv

    sites = json.loads(DATA.read_text(encoding="utf-8"))
    domains: list[str] = []
    for site in sites:
        domain = domain_of(site.get("url", ""))
        if domain and domain not in domains:
            domains.append(domain)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fetched: list[str] = []
    missing: list[str] = []
    for domain in domains:
        slug = slug_for(domain)
        if not force and not check_only and (
            (OUT_DIR / f"{slug}.png").exists() or (OUT_DIR / f"{slug}.svg").exists()
        ):
            continue
        if check_only:
            if not (
                (OUT_DIR / f"{slug}.png").exists() or (OUT_DIR / f"{slug}.svg").exists()
            ):
                missing.append(domain)
            continue
        result = fetch_one(domain)
        if result:
            ext, payload = result
            # 同一域名只保留一个文件，否则换过来源后会留下旧格式的孤儿图标，
            # 而 generate_site.py 按 png→svg 的顺序查找，会一直用到旧文件。
            for other in ("png", "svg"):
                if other != ext:
                    stale = OUT_DIR / f"{slug}.{other}"
                    if stale.exists():
                        stale.unlink()
            (OUT_DIR / f"{slug}.{ext}").write_bytes(payload)
            fetched.append(domain)
        else:
            missing.append(domain)

    if check_only:
        print(f"{len(missing)} domain(s) without cached favicon: {', '.join(missing) or '-'}")
        return

    print(f"OK: {len(fetched)} favicon(s) fetched, {len(missing)} to fall back to letter avatar")
    for domain in fetched:
        print(f"  + {domain}")
    for domain in missing:
        print(f"  - {domain} (将使用首字母兜底)")


if __name__ == "__main__":
    main()
