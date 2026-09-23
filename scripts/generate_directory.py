#!/usr/bin/env python3
"""从 data/sites.json 生成 DIRECTORY.md，并同步 README / README_EN 顶部的站点表格。

README 中的维护区间（脚本只替换区间内部，区间外的内容不会被改动）：

    <!-- SITES_TABLE:START -->
    ...自动生成内容...
    <!-- SITES_TABLE:END -->
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
BLOCK_PATTERN = re.compile(
    re.escape(START) + r".*?" + re.escape(END), re.DOTALL
)


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
        lines.append(" · ".join(f"`{tag}` ({count})" for tag, count in sorted(tag_counts.items())))
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {OUT.relative_to(ROOT)} with {len(sites)} site(s)")

    for lang, path in README_FILES.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if START not in text or END not in text:
            print(f"WARN: {path.name} 缺少 {START}/{END} 标记，跳过同步")
            continue
        new_text = BLOCK_PATTERN.sub(
            lambda _: build_readme_block(sites, lang), text, count=1
        )
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            print(f"Synced sites table in {path.name}")
        else:
            print(f"{path.name} sites table already up to date")


if __name__ == "__main__":
    main()