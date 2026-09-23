#!/usr/bin/env python3
"""巡检已收录站点的可用性，产出报告供人工复核。

设计原则：**只报告，不删数据**。

自动删掉一个站点看起来省事，但误判代价很高——很多正常站点会对脚本请求
返回 403/429、拒绝 HEAD、按地域限流，或只是临时宕机。因此本脚本：

- 先用 HEAD，失败再退回 GET（大量站点不接受 HEAD）；
- 带浏览器 UA，避免被当作爬虫直接拒绝；
- 区分「明确失效」（404/410，域名不存在）与「无法确认」（403/429/超时/证书问题）；
- 只有连续多次巡检都明确失效的站点才建议下架，且仍由维护者决定。

用法：
    python3 scripts/check_health.py                  # 输出报告
    python3 scripts/check_health.py --json out.json  # 附带机器可读结果
    python3 scripts/check_health.py --issue-body body.md
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import socket
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "sites.json"

TIMEOUT = 20
WORKERS = 8
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

# 明确的失效信号：这些状态码意味着页面确实不在了
GONE_STATUS = {404, 410, 451}

# 无法确认的信号：站点可能正常，只是不欢迎脚本访问
UNCERTAIN_STATUS = {401, 403, 405, 406, 418, 429, 503}


def request(url: str, method: str) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "User-Agent": BROWSER_UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    )
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=context) as response:
        return response.status, response.geturl()


def probe(url: str) -> dict:
    """探测单个站点，返回 {status, code, detail}。"""
    last_error = ""
    for method in ("HEAD", "GET"):
        try:
            status, final_url = request(url, method)
            if status in GONE_STATUS:
                return {"status": "gone", "code": status, "detail": f"HTTP {status}"}
            if status in UNCERTAIN_STATUS:
                return {"status": "uncertain", "code": status, "detail": f"HTTP {status}"}
            if 200 <= status < 400:
                redirected = "" if final_url.rstrip("/") == url.rstrip("/") else f"（跳转到 {final_url}）"
                return {"status": "ok", "code": status, "detail": f"HTTP {status}{redirected}"}
            return {"status": "uncertain", "code": status, "detail": f"HTTP {status}"}
        except urllib.error.HTTPError as exc:
            if exc.code in GONE_STATUS:
                return {"status": "gone", "code": exc.code, "detail": f"HTTP {exc.code}"}
            last_error = f"HTTP {exc.code}"
        except urllib.error.URLError as exc:
            reason = exc.reason
            if isinstance(reason, socket.gaierror):
                return {"status": "gone", "code": 0, "detail": "域名无法解析"}
            last_error = f"连接失败（{type(reason).__name__}）"
        except (TimeoutError, socket.timeout):
            last_error = "请求超时"
        except (ssl.SSLError, OSError) as exc:
            last_error = f"{type(exc).__name__}"

    # 两种方法都没能确认状态：归入「无法确认」，交给人工判断
    return {"status": "uncertain", "code": 0, "detail": last_error or "无法确认"}


def check_all(sites: list[dict]) -> list[dict]:
    results: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(probe, s["url"]): s for s in sites}
        for future in concurrent.futures.as_completed(futures):
            site = futures[future]
            try:
                outcome = future.result()
            except Exception as exc:  # noqa: BLE001
                outcome = {"status": "uncertain", "code": 0, "detail": type(exc).__name__}
            results.append({"name": site.get("name", ""), "url": site["url"], **outcome})
    return sorted(results, key=lambda r: (r["status"] != "gone", r["name"].lower()))


def build_report(results: list[dict]) -> str:
    gone = [r for r in results if r["status"] == "gone"]
    uncertain = [r for r in results if r["status"] == "uncertain"]
    ok = [r for r in results if r["status"] == "ok"]

    lines = [
        f"巡检完成：共 {len(results)} 个站点，正常 {len(ok)}，"
        f"疑似失效 {len(gone)}，无法确认 {len(uncertain)}。",
        "",
    ]

    if gone:
        lines += [
            "## 疑似失效（建议人工复核）",
            "",
            "| 站点 | 地址 | 结果 |",
            "|---|---|---|",
        ]
        lines += [f"| {r['name']} | {r['url']} | {r['detail']} |" for r in gone]
        lines += [
            "",
            "> 这些站点返回了明确的失效信号。请先手动打开确认；",
            "> 确实无法访问时再从 `data/sites.json` 中移除。",
            "",
        ]

    if uncertain:
        lines += [
            "## 无法确认（多数属于正常站点）",
            "",
            "常见原因是拒绝脚本访问、限流或按地域拦截，不代表站点有问题。",
            "",
            "| 站点 | 地址 | 结果 |",
            "|---|---|---|",
        ]
        lines += [f"| {r['name']} | {r['url']} | {r['detail']} |" for r in uncertain]
        lines += [""]

    if not gone and not uncertain:
        lines += ["所有站点均可正常访问。", ""]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="巡检收录站点可用性")
    parser.add_argument("--data", default=str(DEFAULT_DATA))
    parser.add_argument("--json", dest="json_out", default="")
    parser.add_argument("--issue-body", default="")
    parser.add_argument(
        "--fail-on-gone",
        action="store_true",
        help="存在疑似失效站点时以非零退出（默认只报告）",
    )
    args = parser.parse_args()

    sites = json.loads(Path(args.data).read_text(encoding="utf-8"))
    results = check_all(sites)
    report = build_report(results)

    print(report)

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    if args.issue_body:
        Path(args.issue_body).write_text(report, encoding="utf-8")

    gone = [r for r in results if r["status"] == "gone"]
    if args.fail_on_gone and gone:
        sys.exit(1)


if __name__ == "__main__":
    main()
