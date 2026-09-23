#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sites.json"
OUT = ROOT / "DIRECTORY.md"


def esc(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


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
        lines += [
            "| 网站 | 站长 / 创作者 | 简介 | 语言 | 地区 | 标签 | RSS |",
            "|---|---|---|---|---|---|---|",
        ]
        for site in sites:
            name = f"[{esc(site['name'])}]({site['url']})"
            feed = f"[Feed]({site['feed']})" if site.get("feed") else "—"
            lines.append(
                f"| {name} | {esc(site['owner'])} | {esc(site['description'])} | "
                f"{', '.join(site['languages'])} | {esc(site['region'])} | "
                f"{', '.join(site['tags'])} | {feed} |"
            )

        tag_counts = Counter(tag for site in sites for tag in site.get("tags", []))
        if tag_counts:
            lines += ["", "## 标签统计", ""]
            lines.append(" · ".join(f"`{tag}` ({count})" for tag, count in sorted(tag_counts.items())))
            lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {OUT.relative_to(ROOT)} with {len(sites)} site(s)")


if __name__ == "__main__":
    main()
