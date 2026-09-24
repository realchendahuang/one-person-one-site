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

    <!-- HISTORY:START -->
    ...自动生成内容...
    <!-- HISTORY:END -->

历史区块由 git log 生成，展示提交总数与里程碑摘要。它天生「落后一个提交」
（生成时 HEAD 还没包含当前这次），因此 validate.py 的生成物检查会对这个
区间做豁免，只要求区块存在、不要求逐字一致。
"""
import json
import re
import subprocess
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
HISTORY_START = "<!-- HISTORY:START -->"
HISTORY_END = "<!-- HISTORY:END -->"
BLOCK_PATTERN = re.compile(
    re.escape(START) + r".*?" + re.escape(END), re.DOTALL
)
STATS_PATTERN = re.compile(
    re.escape(STATS_START) + r".*?" + re.escape(STATS_END), re.DOTALL
)
HISTORY_PATTERN = re.compile(
    re.escape(HISTORY_START) + r".*?" + re.escape(HISTORY_END), re.DOTALL
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


# 里程碑：按提交信息前缀归类的提交，会以「累计数量 + 最新提交」的形式进入历史区块
HISTORY_MILESTONES = {
    "feat: 收录": {"zh": "收录新站点", "en": "New site listings"},
    "feat:": {"zh": "功能", "en": "Features"},
    "fix:": {"zh": "修复", "en": "Fixes"},
    "refactor:": {"zh": "重构", "en": "Refactors"},
}


def git_history_summary(lang: str) -> str | None:
    """从 git log 生成历史区块内容；仓库不可用（如非 git 环境）时返回 None。"""
    try:
        count = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        first_date = subprocess.run(
            ["git", "log", "--reverse", "--date=short", "--format=%as"],
            capture_output=True, text=True, check=True,
        ).stdout.splitlines()[0]
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError, OSError):
        return None

    milestones = []
    for prefix, labels in HISTORY_MILESTONES.items():
        try:
            hits = subprocess.run(
                ["git", "log", "--format=%s", f"--grep=^{re.escape(prefix)}", "-E"],
                capture_output=True, text=True, check=True,
            ).stdout.splitlines()
        except (subprocess.CalledProcessError, OSError):
            continue
        if hits:
            milestones.append((labels[lang], len(hits), hits[0]))

    repo = "realchendahuang/one-person-one-site"
    if lang == "en":
        lines = [
            f"- **{count}** commits since **{first_date}** — see the full "
            f"[commit history](https://github.com/{repo}/commits/main).",
        ]
        lines += [
            f"- {label}: **{total}** commits, latest: “{esc(subject)}”."
            for label, total, subject in milestones
        ]
    else:
        lines = [
            f"- 自 **{first_date}** 以来共 **{count}** 次提交，完整记录见 "
            f"[提交历史](https://github.com/{repo}/commits/main)。",
        ]
        lines += [
            f"- {label}：**{total}** 次，最近一次「{esc(subject)}」。"
            for label, total, subject in milestones
        ]
    return "\n".join(lines)


def build_history_block(lang: str, text: str) -> str:
    """历史区块；拿不到 git 信息时保留原区块不动。"""
    summary = git_history_summary(lang)
    if summary is None:
        return text
    return f"{HISTORY_START}\n{summary}\n{HISTORY_END}"


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

        if HISTORY_START in text and HISTORY_END in text:
            text = HISTORY_PATTERN.sub(
                lambda match: build_history_block(lang, match.group(0)), text, count=1
            )
        else:
            print(f"WARN: {path.name} 缺少 {HISTORY_START}/{HISTORY_END} 标记，跳过历史区块")

        path.write_text(text, encoding="utf-8")
        print(f"Synced {path.name}")


if __name__ == "__main__":
    main()
