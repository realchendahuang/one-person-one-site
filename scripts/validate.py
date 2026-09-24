#!/usr/bin/env python3
"""校验 data/sites.json 的结构与收录规范。

这里是收录数据的唯一守门人：本地提交、CI 校验、Issue 自动收录三条路径
最终都要经过它。校验规则与 CONTRIBUTING.md 的字段说明保持一致。

用法：
    python3 scripts/validate.py
    python3 scripts/validate.py --data other.json
    python3 scripts/validate.py --check   # 重跑生成器，检查生成物已提交

--check 的豁免规则：README 的 HISTORY 区间由 git log 生成，天生落后一个
提交（生成时 HEAD 尚未包含当前提交），因此只要求区块存在，不比对内容。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "sites.json"

# README 里由 git log 生成的历史区块：内容允许落后一个提交，检查时整块豁免
HISTORY_BLOCK_RE = re.compile(
    r"<!-- HISTORY:START -->.*?<!-- HISTORY:END -->", re.DOTALL
)
GENERATED_FILES = ("DIRECTORY.md", "README.md", "README_EN.md")

REQUIRED = ["name", "url", "owner", "description", "languages", "region", "tags"]
OPTIONAL = ["feed"]

MAX_NAME = 40
MIN_DESCRIPTION = 15
MAX_DESCRIPTION = 240
MAX_TAGS = 8

# 标签统一小写、多词用中划线，便于全站聚合筛选
TAG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# 语言代码：BCP 47 的常见写法——主语言小写，地区/文字子标签以大写开头
# 例如 zh-CN、zh-TW、zh-Hant、en、ja、pt-BR
LANGUAGE_RE = re.compile(r"^[a-z]{2,3}(?:-[A-Z][A-Za-z0-9]{1,7})*$")


class Invalid(Exception):
    """一条收录数据不符合规范。"""


def valid_http_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except ValueError:
        return False


def check_site(site: object, index: int) -> None:
    """校验单条数据，不符合则抛 Invalid。"""
    where = f"第 #{index} 条"

    if not isinstance(site, dict):
        raise Invalid(f"{where} 必须是一个 JSON 对象")

    missing = [key for key in REQUIRED if key not in site]
    if missing:
        raise Invalid(f"{where} 缺少必填字段: {', '.join(missing)}")

    unsupported = sorted(set(site) - set(REQUIRED) - set(OPTIONAL))
    if unsupported:
        raise Invalid(f"{where} 包含不支持的字段: {', '.join(unsupported)}")

    for field in ("name", "owner", "description", "region"):
        value = site[field]
        if not isinstance(value, str) or not value.strip():
            raise Invalid(f"{where} 的 '{field}' 必须是非空字符串")

    if len(site["name"]) > MAX_NAME:
        raise Invalid(f"{where} 的 name 超过 {MAX_NAME} 字符: {site['name']}")

    if len(site["description"]) < MIN_DESCRIPTION:
        raise Invalid(
            f"{where} 的 description 少于 {MIN_DESCRIPTION} 字符，请写清楚站点内容"
        )
    if len(site["description"]) > MAX_DESCRIPTION:
        raise Invalid(f"{where} 的 description 超过 {MAX_DESCRIPTION} 字符")

    if not valid_http_url(site["url"]):
        raise Invalid(f"{where} 的 url 不是有效的 http/https 地址: {site['url']}")

    languages = site["languages"]
    if not isinstance(languages, list) or not languages:
        raise Invalid(f"{where} 的 languages 必须是非空数组")
    for lang in languages:
        if not isinstance(lang, str) or not LANGUAGE_RE.match(lang):
            raise Invalid(
                f"{where} 的语言代码不规范: {lang!r}（示例: zh-CN, zh-TW, en, ja）"
            )
    if len(languages) != len(set(languages)):
        raise Invalid(f"{where} 的 languages 存在重复项")

    tags = site["tags"]
    if not isinstance(tags, list) or not (1 <= len(tags) <= MAX_TAGS):
        raise Invalid(f"{where} 的 tags 需要 1 到 {MAX_TAGS} 个")
    for tag in tags:
        if not isinstance(tag, str) or not TAG_RE.match(tag):
            raise Invalid(
                f"{where} 的标签不规范: {tag!r}（要求全小写，多词用中划线，如 indie-hacker）"
            )
    if len(tags) != len(set(tags)):
        raise Invalid(f"{where} 的 tags 存在重复项")

    feed = site.get("feed")
    if feed is not None:
        if not isinstance(feed, str) or not valid_http_url(feed):
            raise Invalid(f"{where} 的 feed 不是有效的 http/https 地址: {feed}")


def canonical(url: str) -> str:
    return url.rstrip("/").lower()


def validate(sites: object) -> int:
    """校验整个数据文件，返回条目数；不符合则抛 Invalid。"""
    if not isinstance(sites, list):
        raise Invalid("data/sites.json 顶层必须是一个数组")

    seen: dict[str, int] = {}
    for index, site in enumerate(sites, start=1):
        check_site(site, index)
        key = canonical(site["url"])
        if key in seen:
            raise Invalid(
                f"第 #{index} 条与第 #{seen[key]} 条的网址重复: {site['url']}"
            )
        seen[key] = index

    return len(sites)


def strip_history_blocks(text: str) -> str:
    """去掉历史区块内容，仅保留空区块占位，供生成物比对豁免使用。"""
    return HISTORY_BLOCK_RE.sub("<!-- HISTORY:START --><!-- HISTORY:END -->", text)


def check_generated_files() -> int:
    """重跑生成器并检查生成物已提交；返回非零表示有未提交的漂移。"""
    try:
        subprocess.run(
            ["python3", str(ROOT / "scripts" / "generate_directory.py")],
            capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"ERROR: 重跑生成器失败: {exc}")
        return 1

    drift = False
    for name in GENERATED_FILES:
        path = ROOT / name
        before = strip_history_blocks(path.read_text(encoding="utf-8"))
        try:
            after = subprocess.run(
                ["git", "show", f"HEAD:{name}"],
                capture_output=True, text=True, check=True,
            ).stdout
        except subprocess.CalledProcessError:
            print(f"FAIL: {name} 未纳入版本控制")
            drift = True
            continue
        if before != strip_history_blocks(after):
            print(f"FAIL: {name} 与 data/sites.json 不同步，请运行 "
                  "python3 scripts/generate_directory.py 并提交")
            drift = True

    if drift:
        return 1
    print(f"OK: 生成物已提交（HISTORY 区间豁免逐字比对）")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="校验收录数据")
    parser.add_argument("--data", default=str(DEFAULT_DATA), help="数据文件路径")
    parser.add_argument(
        "--check", action="store_true",
        help="重跑生成器，检查 DIRECTORY.md / README 生成物已提交",
    )
    args = parser.parse_args()

    if args.check:
        sys.exit(check_generated_files())

    path = Path(args.data)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: 无法读取 {path}: {exc}")
        sys.exit(1)

    try:
        sites = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: {path} 不是合法的 JSON: {exc}")
        sys.exit(1)

    try:
        count = validate(sites)
    except Invalid as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    print(f"OK: validated {count} site(s)")


if __name__ == "__main__":
    main()
