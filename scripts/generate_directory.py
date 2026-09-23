#!/usr/bin/env python3
"""从 data/sites.json 生成 DIRECTORY.md，并同步 README / README_EN 的表格与统计。

README 中的维护区间（脚本只替换区间内部，区间外的内容不会被改动）：

    <!-- SITES_TABLE:START -->
    ...自动生成内容...
    <!-- SITES_TABLE:END -->

    <!-- STATS:START -->
    ...自动生成内容...
    <!-- STATS:END -->

统计数字随收录增长自动更新，避免 README 里的数字慢慢变成谎话。
"""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sites.json"
OUT = ROOT / "DIRECTORY.md"
README_FILES = {
    "zh": ROOT / "README.md",
    "en": ROOT / "README_EN.md",
}

START = "<!-- SITES_TABLE:START -->"
END = "<!-- SITES_TABLE:END -->"
STATS_START = "<!-- STATS:START -->"
STATS_END = "<!-- STATS:END -->"
BLOCK_PATTERN = re.compile(
    re.escape(START) + r".*?" + re.escape(END), re.DOTALL
)
STATS_PATTERN = re.compile(
    re.escape(STATS_START) + r".*?" + re.escape(STATS_END), re.DOTALL
)

# 代表「内容形态」的标签；其余标签视为身份或主题，避免两类混在一起展示
FORM_TAGS = ["blog", "digital-garden", "notes", "portfolio", "newsletter"]


def esc(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def build_table(sites: list) -> list[str]:
    lines = [
        "| 网站 | 站长 / 创作者 | 简介 | 语言 | 标签 |",
        "|---|---|---|---|---|",
    ]
    for site in sites:
        name = f"[{esc(site['name'])}]({site['url']})"
        lines.append(
            f"| {name} | {esc(site['owner'])} | {esc(site['description'])} | "
            f"{', '.join(site['languages'])} | {', '.join(site['tags'])} |"
        )
    return lines


def build_readme_block(sites: list, lang: str) -> str:
    if lang == "en":
        lines = [
            "| Site | Owner | Description | Language | Tags |",
            "|---|---|---|---|---|",
        ]
        for site in sites:
            name = f"[{esc(site['name'])}]({site['url']})"
            lines.append(
                f"| {name} | {esc(site['owner'])} | {esc(site['description'])} | "
                f"{', '.join(site['languages'])} | {', '.join(site['tags'])} |"
            )
    else:
        lines = build_table(sites)
    return "\n".join([START, *lines, END])


def build_stats_block(sites: list, lang: str) -> str:
    tag_counts = Counter(tag for site in sites for tag in site.get("tags", []))
    lang_counts = Counter(code for site in sites for code in site.get("languages", []))
    regions = Counter(site.get("region", "") for site in sites if site.get("region"))
    feeds = sum(1 for site in sites if site.get("feed"))

    forms = [(t, tag_counts[t]) for t in FORM_TAGS if tag_counts.get(t)]
    topics = [(t, c) for t, c in tag_counts.most_common() if t not in FORM_TAGS][:8]

    if lang == "en":
        lines = [
            f"- **{len(sites)}** independent sites from **{len(regions)}** regions, "
            f"written in {len(lang_counts)} languages.",
            f"- **{feeds}** of them publish an RSS / Atom feed — import the whole list "
            "at once with [feeds.opml](./site/feeds.opml).",
            "- Content types: " + ", ".join(f"{t} ({c})" for t, c in forms) + ".",
            "- Common topics: " + ", ".join(f"{t} ({c})" for t, c in topics) + ".",
        ]
    else:
        lines = [
            f"- 目前收录 **{len(sites)}** 个站点，来自 **{len(regions)}** 个地区，"
            f"使用 {len(lang_counts)} 种语言写作。",
            f"- 其中 **{feeds}** 个提供 RSS / Atom 订阅源，可通过 "
            "[feeds.opml](./site/feeds.opml) 一次性导入阅读器。",
            "- 内容形态：" + "、".join(f"`{t}` ({c})" for t, c in forms) + "。",
            "- 常见主题：" + "、".join(f"`{t}` ({c})" for t, c in topics) + "。",
        ]
    return "\n".join([STATS_START, *lines, STATS_END])


def main() -> None:
    sites = json.loads(DATA.read_text(encoding="utf-8"))
    sites = sorted(sites, key=lambda x: (x.get("name", "").lower(), x.get("url", "")))

    lines = [
        "# 一人一站目录 / Directory",
        "",
        "> 此文件由 `data/sites.json` 自动生成，请不要直接编辑。",
        "",
        f"当前共收录 **{len(sites)}** 个站点。",
        "",
    ]

    if not sites:
        lines += [
            "暂无站点。欢迎成为第一批贡献者：请使用 Issue 模板或修改 `data/sites.json` 提交 PR。",
            "",
        ]
    else:
        lines += build_table(sites)
        lines += ["", "## 标签统计", ""]
        tag_counts = Counter(tag for site in sites for tag in site.get("tags", []))
        lines.append(
            " · ".join(
                f"`{tag}` ({count})"
                for tag, count in sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0]))
            )
        )
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {OUT.relative_to(ROOT)} with {len(sites)} site(s)")

    for lang, path in README_FILES.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")

        if START in text and END in text:
            text = BLOCK_PATTERN.sub(
                lambda _: build_readme_block(sites, lang), text, count=1
            )
        else:
            print(f"WARN: {path.name} 缺少 {START}/{END} 标记，跳过站点表格")

        if STATS_START in text and STATS_END in text:
            text = STATS_PATTERN.sub(
                lambda _: build_stats_block(sites, lang), text, count=1
            )
        else:
            print(f"WARN: {path.name} 缺少 {STATS_START}/{STATS_END} 标记，跳过统计")

        path.write_text(text, encoding="utf-8")
        print(f"Synced {path.name}")


if __name__ == "__main__":
    main()
