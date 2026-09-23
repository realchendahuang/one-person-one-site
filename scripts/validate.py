#!/usr/bin/env python3
"""校验 data/sites.json 的结构与收录规范。

这里是收录数据的唯一守门人：本地提交、CI 校验、Issue 自动收录三条路径
最终都要经过它。校验规则与 CONTRIBUTING.md 的字段说明保持一致。

用法：
    python3 scripts/validate.py
    python3 scripts/validate.py --data other.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "sites.json"

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


def main() -> None:
    parser = argparse.ArgumentParser(description="校验收录数据")
    parser.add_argument("--data", default=str(DEFAULT_DATA), help="数据文件路径")
    args = parser.parse_args()

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
