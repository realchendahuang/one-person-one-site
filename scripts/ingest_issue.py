#!/usr/bin/env python3
"""解析 GitHub Issue 表单里的站点提交，追加写入 data/sites.json。

配套 .github/workflows/ingest-issue.yml 使用：提交者填完「提交一个网站」
Issue 表单后，工作流调用本脚本解析结构化字段、做格式校验与可用性探测，
通过则提交、部署并回复关闭 Issue，全程无人参与。

用法：
    python3 scripts/ingest_issue.py <issue-body.md> --result <result.json> \
        [--comment-file <comment.md>] [--marker-file <marker.txt>] \
        [--github-output <outputs.txt>] [--issue-number N] [--force]

结果状态：
    skipped      不是站点提交（例如 bug 反馈），工作流不应做任何回应
    invalid      解析失败或必填字段缺失，需要提交者补充（--force 不覆盖）
    blocked      命中公开排除清单（第三方社交平台账号页等），--force 可覆盖
    unreachable  可用性探测失败，--force 可覆盖
    duplicate    站点已在目录中，无需收录
    accepted     已写入 data/sites.json

环境变量：
    OPOS_SITES_FILE  覆盖数据文件路径（供测试使用）

--force 供维护者在 Issue 上添加 accepted 标签后人工放行。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("OPOS_SITES_FILE", ROOT / "data" / "sites.json"))

# 维护者本人的站点固定排在数组末尾，新收录站点插在它之前
HOME_SITE_HOST = "chendahuang.com"

# 公开排除清单：第三方社交 / 平台账号页，不符合「独立个人网站」收录标准
SOCIAL_HOSTS = {
    "x.com", "twitter.com", "weibo.com", "zhihu.com", "xiaohongshu.com",
    "douyin.com", "tiktok.com", "instagram.com", "facebook.com", "threads.net",
    "bilibili.com", "youtube.com", "reddit.com", "linkedin.com",
}

MAX_DESCRIPTION = 240
MAX_NAME = 60
MAX_OWNER = 60
MAX_TAGS = 8
REQUEST_TIMEOUT = 20
SITE_URL = "https://realchendahuang.github.io/one-person-one-site/"
NOTICE = "https://github.com/realchendahuang/one-person-one-site/issues/new?template=submit-site.yml"
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

HEADER_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
CHECKBOX_RE = re.compile(r"-\s*\[x\]", re.IGNORECASE)
NO_RESPONSE = {"_no response_", "no response", "-", "—"}

FIELD_KEYWORDS = {
    "name": ("site name", "网站名称"),
    "url": ("url", "网站地址"),
    "owner": ("owner", "站长"),
    "description": ("description", "介绍"),
    "languages": ("languages", "语言"),
    "region": ("region", "地区"),
    "tags": ("tags", "标签"),
    "feed": ("rss", "atom", "订阅"),
    "confirm": ("提交确认",),
}

LANG_ALIASES = {
    "zh": "zh-CN", "cn": "zh-CN", "zh-cn": "zh-CN",
    "中文": "zh-CN", "简体中文": "zh-CN", "简体": "zh-CN",
    "zh-tw": "zh-TW", "zh-hant": "zh-TW", "繁体中文": "zh-TW", "繁體中文": "zh-TW",
    "en": "en", "english": "en", "英文": "en", "英语": "en",
    "ja": "ja", "jp": "ja", "日文": "ja", "日语": "ja",
    "ko": "ko", "韩文": "ko",
}

REGION_ALIASES = {
    "中国": "China", "china": "China",
    "台湾": "Taiwan", "台灣": "Taiwan", "taiwan": "Taiwan",
    "日本": "Japan", "japan": "Japan",
    "美国": "US", "us": "US", "usa": "US",
    "全球": "Global", "global": "Global",
}

SPLIT_RE = re.compile(r"[,，、;；/\n]+")

MARKERS = {
    "accepted": "opos-ingest:accepted",
    "duplicate": "opos-ingest:duplicate",
    "invalid": "opos-ingest:invalid",
    "blocked": "opos-ingest:blocked",
    "unreachable": "opos-ingest:unreachable",
}


def body_hash(body: str) -> str:
    """Issue 正文的内容指纹，用于幂等判断：正文未变则不重复评论。"""
    return hashlib.sha256((body or "").strip().encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------- 表单解析

def parse_form(body: str) -> dict[str, str]:
    """把 Issue 表单正文拆成 {字段标题: 字段值}。"""
    fields: dict[str, str] = {}
    matches = list(HEADER_RE.finditer(body or ""))
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        fields[match.group(1).strip()] = body[start:end].strip()
    return fields


def pick(fields: dict[str, str], keywords) -> str:
    for label, value in fields.items():
        low = label.lower()
        if any(keyword in low for keyword in keywords):
            return value
    return ""


def recognize(fields: dict[str, str]) -> int:
    """统计能识别为提交表单字段的标题数量，用于区分提交与普通 Issue。"""
    hits = set()
    for label in fields:
        low = label.lower()
        for key, keywords in FIELD_KEYWORDS.items():
            if any(keyword in low for keyword in keywords):
                hits.add(key)
    return len(hits)


# ------------------------------------------------------------ 字段规范化

def collapse(text: str) -> str:
    return " ".join((text or "").split())


def clamp(text: str, limit: int) -> str:
    text = collapse(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def normalize_url(raw: str) -> str:
    url = collapse(raw)
    if not url or url.lower() in NO_RESPONSE:
        return ""
    url = url.split()[0].strip("<>()[]，。,.")
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url
    if not re.match(r"^https?://[^\s/]+\.[^\s/]+", url, re.IGNORECASE):
        return ""
    return url


def normalize_languages(raw: str) -> list[str]:
    out: list[str] = []
    for item in SPLIT_RE.split(raw or ""):
        token = item.strip()
        if not token:
            continue
        value = LANG_ALIASES.get(token.lower(), token)
        if len(value) < 2:
            continue
        if value not in out:
            out.append(value)
    return out


def normalize_region(raw: str) -> str:
    token = collapse(raw)
    if not token:
        return ""
    return REGION_ALIASES.get(token.lower(), token)


def normalize_tags(raw: str) -> list[str]:
    out: list[str] = []
    for item in SPLIT_RE.split(raw or ""):
        token = item.strip().lower()
        token = re.sub(r"\s+", "-", token)
        token = re.sub(r"-{2,}", "-", token).strip("-")
        if token and token not in out:
            out.append(token)
    return out[:MAX_TAGS]


def canonical_url(url: str) -> str:
    return url.rstrip("/").lower()


def is_social_host(url: str) -> bool:
    host = re.sub(r"^https?://", "", url.lower()).split("/")[0].split(":")[0]
    host = host.removeprefix("www.")
    return any(host == blocked or host.endswith("." + blocked) for blocked in SOCIAL_HOSTS)


# ---------------------------------------------------------------- 可用性探测

def check_reachable(url: str) -> tuple[bool, str]:
    """探测站点是否可访问：域名能解析、服务器有响应即视为可用。"""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": BROWSER_UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            status = int(getattr(response, "status", 200))
            response.read(4096)
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
    except Exception as exc:  # DNS 失败、连接超时、证书错误等
        return False, f"{type(exc).__name__}: {exc}"

    if 200 <= status < 400:
        return True, f"HTTP {status}"
    if status in (401, 403, 429):
        # 常见于反爬拦截，域名本身是活的，按可访问处理
        return True, f"HTTP {status}（疑似反爬拦截，已放行）"
    return False, f"HTTP {status}"


# ---------------------------------------------------------------- 数据写入

def render(sites: list[dict]) -> str:
    """按仓库既有格式输出 sites.json：每站一个对象，字段一行，数组内联。"""
    blocks = []
    for site in sites:
        lines = ",\n".join(
            f"    {json.dumps(key, ensure_ascii=False)}: {json.dumps(value, ensure_ascii=False)}"
            for key, value in site.items()
        )
        blocks.append("  {\n" + lines + "\n  }")
    return "[\n" + ",\n".join(blocks) + "\n]\n"


def insert_before_home(sites: list[dict], entry: dict) -> None:
    index = next(
        (i for i, site in enumerate(sites) if HOME_SITE_HOST in site.get("url", "").lower()),
        len(sites),
    )
    sites.insert(index, entry)


def make_result(
    status: str,
    comment: str,
    name: str = "",
    url: str = "",
    issue_number: str = "",
    revision: str = "",
) -> dict:
    if status == "accepted" and name:
        message = f"feat: 收录新站点「{name}」"
        if issue_number:
            message += f"（issue #{issue_number}）"
    else:
        message = ""
    # 标记带上正文指纹：正文没变时不重复评论，改动后会允许重新给出结论
    marker = ""
    if status in MARKERS and revision:
        marker = f"<!-- {MARKERS[status]}:{revision} -->"
    body = f"{comment}\n\n{marker}".strip() if comment else ""
    return {
        "status": status,
        "name": name,
        "url": url,
        "marker": marker,
        "is_accepted": "true" if status == "accepted" else "false",
        "comment": body,
        "commit_message": message,
    }


# ---------------------------------------------------------------- 主流程

def ingest(body: str, force: bool = False, issue_number: str = "") -> dict:
    fields = parse_form(body)
    revision = body_hash(body)

    confirm = pick(fields, FIELD_KEYWORDS["confirm"])
    if not confirm.strip():
        # 不是站点提交（例如 bug 反馈），静默跳过，不打扰提交者
        if recognize(fields) < 3:
            return make_result("skipped", "")
        return make_result(
            "invalid",
            "暂时没能收录 ⏳\n\n"
            "没有识别到「提交一个网站」表单里的提交确认。请通过模板提交（"
            f"{NOTICE}），或直接修改 `data/sites.json` 发 Pull Request。",
            revision=revision,
        )
    if len(CHECKBOX_RE.findall(confirm)) < 2:
        return make_result(
            "invalid",
            "暂时没能收录 ⏳\n\n"
            "请先勾选表单底部的两项确认：站点是真实个人长期维护的网站，且当前可以正常访问。",
            revision=revision,
        )

    name = clamp(pick(fields, FIELD_KEYWORDS["name"]), MAX_NAME)
    url = normalize_url(pick(fields, FIELD_KEYWORDS["url"]))
    owner = clamp(pick(fields, FIELD_KEYWORDS["owner"]), MAX_OWNER)
    description = clamp(pick(fields, FIELD_KEYWORDS["description"]), MAX_DESCRIPTION)
    languages = normalize_languages(pick(fields, FIELD_KEYWORDS["languages"]))
    region = normalize_region(pick(fields, FIELD_KEYWORDS["region"]))
    tags = normalize_tags(pick(fields, FIELD_KEYWORDS["tags"]))
    feed = normalize_url(pick(fields, FIELD_KEYWORDS["feed"]))

    missing = [
        label
        for label, value in (
            ("网站名称", name),
            ("网站地址", url),
            ("站长 / 创作者", owner),
            ("一句话介绍", description),
            ("主要语言", languages),
            ("地区", region),
            ("标签", tags),
        )
        if not value
    ]
    if missing:
        return make_result(
            "invalid",
            "暂时没能收录 ⏳\n\n表单缺少必填内容：" + "、".join(missing) +
            "\n\n请直接编辑本 Issue 正文补齐，编辑后会自动重新处理。",
            name=name,
            url=url,
            revision=revision,
        )

    if is_social_host(url) and not force:
        return make_result(
            "blocked",
            "暂时没能收录 ⏳\n\n"
            f"`{url}` 看起来是第三方平台的账号主页，本目录只收录拥有独立域名或稳定托管服务的个人网站"
            "（详见收录标准）。\n\n"
            "如果判断有误，请维护者在本 Issue 上添加 `accepted` 标签，工作流会跳过检查并重新收录。",
            name=name,
            url=url,
            revision=revision,
        )

    sites = json.loads(DATA.read_text(encoding="utf-8"))
    target = canonical_url(url)
    for site in sites:
        if canonical_url(site.get("url", "")) == target:
            return make_result(
                "duplicate",
                f"已收录 ✅ 这个站点已经在目录里了：[{site.get('name', url)}]({site.get('url', url)})，无需重复提交。\n\n"
                f"线上浏览：{SITE_URL}",
                name=name,
                url=url,
                revision=revision,
            )

    if force:
        probe = "（维护者已人工放行，跳过探测）"
    else:
        reachable, detail = check_reachable(url)
        if not reachable:
            return make_result(
                "unreachable",
                f"暂时没能收录 ⏳\n\n自动探测 `{url}` 失败：{detail}\n\n"
                "如果站点确实可以正常访问（可能是地域限制、反爬拦截或临时故障），"
                "请维护者在本 Issue 上添加 `accepted` 标签，工作流会跳过探测并重新收录。",
                name=name,
                url=url,
                revision=revision,
            )
        probe = detail

    entry: dict[str, object] = {
        "name": name,
        "url": url,
        "owner": owner,
        "description": description,
        "languages": languages,
        "region": region,
        "tags": tags,
    }
    if feed:
        entry["feed"] = feed

    insert_before_home(sites, entry)
    DATA.write_text(render(sites), encoding="utf-8")

    comment = (
        f"已收录 ✅ 感谢提交！\n\n「{name}」已加入目录，本次自动构建完成后即可在线看到。\n\n"
        f"- 站点：{url}\n"
        f"- 可用性探测：{probe}\n\n"
        f"线上浏览：{SITE_URL}\n\n"
        "若简介或标签需要调整，欢迎直接修改 `data/sites.json` 提交 PR。"
    )
    return make_result("accepted", comment, name=name, url=url, issue_number=issue_number, revision=revision)


# ---------------------------------------------------------------- 命令行入口

def write_github_output(path: str, payload: dict) -> None:
    """以 GitHub Actions 的 $GITHUB_OUTPUT 格式追加多行输出。"""
    with open(path, "a", encoding="utf-8") as handle:
        for key in ("status", "name", "url", "marker", "is_accepted", "commit_message"):
            handle.write(f"{key}={payload[key]}\n")
        handle.write("comment<<OPOS_COMMENT_EOF\n")
        handle.write(payload["comment"] + "\n")
        handle.write("OPOS_COMMENT_EOF\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="解析 Issue 提交并写入 data/sites.json")
    parser.add_argument("body_file", help="包含 Issue 表单正文的 Markdown 文件")
    parser.add_argument("--result", default="/tmp/ingest-result.json", help="结果 JSON 输出路径")
    parser.add_argument("--comment-file", default="", help="Issue 评论正文输出路径")
    parser.add_argument("--marker-file", default="", help="去重标记输出路径")
    parser.add_argument("--github-output", default="", help="$GITHUB_OUTPUT 输出路径")
    parser.add_argument("--issue-number", default="", help="Issue 编号，写入提交信息")
    parser.add_argument("--force", action="store_true", help="跳过可用性探测与排除清单（维护者人工放行）")
    args = parser.parse_args()

    body = Path(args.body_file).read_text(encoding="utf-8", errors="replace")
    payload = ingest(body, force=args.force, issue_number=args.issue_number)

    Path(args.result).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if args.comment_file:
        Path(args.comment_file).write_text(payload["comment"], encoding="utf-8")
    if args.marker_file:
        Path(args.marker_file).write_text(payload["marker"], encoding="utf-8")
    if args.github_output:
        write_github_output(args.github_output, payload)

    print(f"{payload['status']}: {payload['name'] or '-'} {payload['url'] or '-'}")


if __name__ == "__main__":
    main()
