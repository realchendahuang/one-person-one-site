#!/usr/bin/env python3
"""生成品牌静态资源：站点图标、iOS 图标与社交分享图。

这些图只用标准库 + Pillow 在本机/CI 生成一次，结果纳入版本控制，
构建页面时直接拷贝，运行期不产生任何外部请求。

用法：
    python3 scripts/build_assets.py
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
DATA = ROOT / "data" / "sites.json"

SIGNAL = (255, 106, 0)
SIGNAL_SOFT = (255, 140, 55)
INK_LIGHT = (247, 247, 248)
INK_DARK = (9, 9, 11)
MIST = (152, 152, 164)

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def load_font(size: int):
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, ValueError):
            continue
    return ImageFont.load_default(size=size)  # Pillow >= 10.1


def draw_mark(size: int) -> Image.Image:
    """品牌标记：信号橙圆环 + 中心点，暗色底方形圆角。"""
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    radius = max(2, int(size * 0.22))
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=INK_DARK)
    pad = size * 0.22
    draw.ellipse(
        (pad, pad, size - pad, size - pad),
        outline=SIGNAL,
        width=max(2, int(size * 0.075)),
    )
    dot = size * 0.10
    cx = cy = size / 2
    draw.ellipse((cx - dot, cy - dot, cx + dot, cy + dot), fill=INK_LIGHT)
    return image


def write_favicon_svg() -> None:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">\n'
        '  <rect width="100" height="100" rx="22" fill="#09090b"/>\n'
        '  <circle cx="50" cy="50" r="27" fill="none" stroke="#ff6a00" stroke-width="7.5"/>\n'
        '  <circle cx="50" cy="50" r="10" fill="#f7f7f8"/>\n'
        "</svg>\n"
    )
    (OUT / "favicon.svg").write_text(svg, encoding="utf-8")


def write_og_image(count: int, tags: list[str]) -> None:
    width, height = 1200, 630
    image = Image.new("RGB", (width, height), INK_DARK)
    draw = ImageDraw.Draw(image)

    # 左侧信号色竖条
    draw.rectangle((0, 0, 10, height), fill=SIGNAL)

    mark = draw_mark(150)
    image.paste(mark, (86, 92), mark)

    title_font = load_font(66)
    sub_font = load_font(34)
    small_font = load_font(27)

    draw.text((86, 268), "一人一站", font=title_font, fill=INK_LIGHT)
    draw.text((86, 352), "One Person, One Site", font=sub_font, fill=MIST)

    draw.text(
        (86, 428),
        "收集认真经营的独立博客与个人网站",
        font=small_font,
        fill=(200, 200, 208),
    )

    stat = f"{count} 个站点 · {len(tags)} 个标签 · 支持标签浏览与随机漫游"
    draw.text((86, 480), stat, font=small_font, fill=SIGNAL_SOFT)

    # 右下角装饰圆环
    ring = draw_mark(300)
    ring = ring.resize((300, 300), Image.LANCZOS)
    image.paste(ring, (width - 380, height - 330), ring)

    image.save(OUT / "og-image.png", "PNG", optimize=True)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    sites = json.loads(DATA.read_text(encoding="utf-8"))
    tags = sorted({tag for site in sites for tag in site.get("tags", [])})

    write_favicon_svg()

    for size, name in ((180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png")):
        draw_mark(size).save(OUT / name, "PNG", optimize=True)

    write_og_image(len(sites), tags)
    print(f"Generated assets/ (favicon.svg, apple-touch-icon.png, icon-192.png, icon-512.png, og-image.png)")


if __name__ == "__main__":
    main()
