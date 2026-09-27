#!/usr/bin/env python3
"""check_health.py 的分类逻辑测试（不发网络请求）。

重点是 TLS 分支：早先这里对所有请求使用 CERT_NONE，等于放弃了对中间人的
防护 —— 被劫持的站点会返回 200，巡检会报「一切正常」。现在证书默认严格校验，
问题站点单独归为 tls，既不静默放行，也不会被误判成失效。

用法：
    python3 tests/test_health.py
"""
from __future__ import annotations

import socket
import ssl
import sys
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_health as ch  # noqa: E402


class FakeResponse:
    def __init__(self, status: int, url: str):
        self.status = status
        self._url = url

    def geturl(self) -> str:
        return self._url

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_default_context_verifies_certificates():
    """默认必须校验证书，不能再是 CERT_NONE。"""
    captured: list[ssl.SSLContext] = []

    def fake_urlopen(req, timeout=None, context=None):
        captured.append(context)
        return FakeResponse(200, "https://example.com/")

    original = ch.urllib.request.urlopen
    ch.urllib.request.urlopen = fake_urlopen
    try:
        ch.request("https://example.com/", "GET")
    finally:
        ch.urllib.request.urlopen = original

    ctx = captured[0]
    assert ctx.verify_mode == ssl.CERT_REQUIRED, "默认没有校验证书"
    assert ctx.check_hostname is True, "默认没有校验主机名"


def test_insecure_fallback_is_opt_in_only():
    """verify=False 才会关掉校验，且只用于补充探测。"""
    captured: list[ssl.SSLContext] = []

    def fake_urlopen(req, timeout=None, context=None):
        captured.append(context)
        return FakeResponse(200, "https://example.com/")

    original = ch.urllib.request.urlopen
    ch.urllib.request.urlopen = fake_urlopen
    try:
        ch.request("https://example.com/", "GET", verify=False)
    finally:
        ch.urllib.request.urlopen = original

    assert captured[0].verify_mode == ssl.CERT_NONE


def test_probe_classifies_tls_error_without_marking_gone():
    """证书失效的站点应归为 tls，而不是 gone。"""

    def fake_urlopen(req, timeout=None, context=None):
        if context.verify_mode == ssl.CERT_REQUIRED:
            raise urllib.error.URLError(
                ssl.SSLCertVerificationError("certificate has expired")
            )
        return FakeResponse(200, "https://example.com/")

    original = ch.urllib.request.urlopen
    ch.urllib.request.urlopen = fake_urlopen
    try:
        result = ch.probe("https://example.com/")
    finally:
        ch.urllib.request.urlopen = original

    assert result["status"] == "tls", result
    assert "过期" in result["detail"], result
    assert "仍可访问" in result["detail"], "站点其实活着，应当如实说明"


def test_probe_classifies_hostname_mismatch():
    def fake_urlopen(req, timeout=None, context=None):
        if context.verify_mode == ssl.CERT_REQUIRED:
            raise urllib.error.URLError(
                ssl.SSLCertVerificationError("hostname mismatch")
            )
        return FakeResponse(200, "https://example.com/")

    original = ch.urllib.request.urlopen
    ch.urllib.request.urlopen = fake_urlopen
    try:
        result = ch.probe("https://example.com/")
    finally:
        ch.urllib.request.urlopen = original

    assert result["status"] == "tls", result


def test_probe_still_reports_gone_for_dns_failure():
    """域名解析失败仍然是明确失效。"""

    def fake_urlopen(req, timeout=None, context=None):
        raise urllib.error.URLError(socket.gaierror("Name or service not known"))

    original = ch.urllib.request.urlopen
    ch.urllib.request.urlopen = fake_urlopen
    try:
        result = ch.probe("https://nope.invalid/")
    finally:
        ch.urllib.request.urlopen = original

    assert result["status"] == "gone", result
    assert "无法解析" in result["detail"]


def test_probe_keeps_403_as_uncertain():
    """反爬拦截不应被当成失效。"""

    def fake_urlopen(req, timeout=None, context=None):
        raise urllib.error.HTTPError("https://example.com/", 403, "Forbidden", {}, None)

    original = ch.urllib.request.urlopen
    ch.urllib.request.urlopen = fake_urlopen
    try:
        result = ch.probe("https://example.com/")
    finally:
        ch.urllib.request.urlopen = original

    assert result["status"] == "uncertain", result


def test_classify_covers_status_codes():
    assert ch.classify(404, "u", "u")["status"] == "gone"
    assert ch.classify(410, "u", "u")["status"] == "gone"
    assert ch.classify(429, "u", "u")["status"] == "uncertain"
    assert ch.classify(200, "https://a.com/", "https://a.com/")["status"] == "ok"
    # 跳转需要如实说明
    assert "跳转" in ch.classify(200, "https://b.com/", "https://a.com/")["detail"]


def test_report_mentions_tls_section_and_counts():
    """报告要单列证书问题，并说明不会因此下架。"""
    results = [
        {"name": "好的站", "url": "https://a.com/", "status": "ok", "code": 200, "detail": "HTTP 200"},
        {"name": "证书坏的站", "url": "https://b.com/", "status": "tls", "code": 0, "detail": "证书已过期（站点仍可访问）"},
    ]
    report = ch.build_report(results)
    assert "证书问题 1" in report, report
    assert "## 证书问题" in report, report
    assert "不会因此下架" in report, report
    # 证书问题必须在概览里被计入，且不属于「疑似失效」
    assert "疑似失效 0" in report, report


def test_report_all_ok_mentions_cert_verified():
    results = [
        {"name": "a", "url": "https://a.com/", "status": "ok", "code": 200, "detail": "HTTP 200"}
    ]
    assert "证书校验通过" in ch.build_report(results)


def test_main_helpers_importable():
    """健康检查脚本仍可作为 CLI 正常导入（防止改动破坏入口）。"""
    assert callable(ch.probe)
    assert callable(ch.check_all)
    assert callable(ch.build_report)


def main() -> None:
    tests = [
        (name, fn)
        for name, fn in sorted(globals().items())
        if name.startswith("test_") and callable(fn)
    ]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"ERROR {name}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
