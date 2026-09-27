#!/usr/bin/env python3
"""自动收录流水线的安全回归测试。

这里锁住两类曾经真实存在的漏洞，改动相关代码后必须仍然通过：

1. **命令注入**：站点名是不可信的 Issue 输入。它会一路流到 commit message，
   而 commit message 曾被 .github/workflows/ingest-issue.yml 直接插进
   `git commit -m "${{ ... }}"`。GitHub Actions 在 bash 解析脚本**之前**做
   文本替换，所以 `$(...)` 与反引号会被执行 —— 任何能开 Issue 的人都能在
   带 contents: write 的 runner 上执行任意命令。
   现在有两条独立的防线，两条都要测：
     - 工作流改用 env 传值，值不会被 shell 二次解析；
     - ingest_issue.py 主动剥掉 shell 元字符。

2. **模板占位符污染**：站点名里含 __CARDS__ 这类 token 时，构建期的
   字符串替换会把它当成占位符，导致整站构建失败（一个 PR 就能让站点下线）。
   现在 validate.py 在关卡拦下，生成器也改成单遍渲染不再二次扫描。

用法：
    python3 tests/test_ingest.py
    python3 -m pytest tests/ -q
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ingest_issue  # noqa: E402
from ingest_issue import ingest  # noqa: E402
from validate import Invalid, validate  # noqa: E402
from siteutil import domain_of, has_placeholder, slug_for  # noqa: E402


# 一份能通过全部校验的最小表单
GOOD_BODY = """### 网站名称

{name}

### 网站地址

https://example.com/

### 站长 / 创作者

tester

### 一句话介绍

this is a perfectly normal description for a personal blog

### 主要语言

en

### 地区

US

### 标签

blog

### 提交确认

- [x] 我确认这是真实个人长期维护的网站
- [x] 我确认该网站当前可以正常访问
"""


def body_with_name(name: str) -> str:
    return GOOD_BODY.format(name=name)


def run_ingest(name: str, data_file: Path) -> dict:
    """在临时数据文件上跑一次收录，返回结果字典。

    注意：ingest_issue.DATA 是模块导入时求值的常量，改环境变量对它无效
    （曾经因此把测试数据写进了真实的 data/sites.json），必须直接替换属性。
    """
    original = ingest_issue.DATA
    ingest_issue.DATA = data_file
    try:
        return ingest(body_with_name(name), force=True, issue_number="1")
    finally:
        ingest_issue.DATA = original


# ------------------------------------------------------------ 命令注入防线

def test_shell_metacharacters_stripped_from_name():
    """站点名里的 shell 元字符必须被剥掉（纵深防御层）。"""
    import os
    from ingest_issue import sanitize_label

    for payload in [
        "foo$(id)bar",
        "foo`id`bar",
        "foo;id",
        "foo|id",
        "foo&&id",
        "a\nb",
        "a\rb",
        "a\x00b",
    ]:
        cleaned = sanitize_label(payload)
        for char in "$`;|&()<>{}[]\\!*?~\"'":
            assert char not in cleaned, f"{payload!r} 清洗后仍含 {char!r}: {cleaned!r}"
        assert "\n" not in cleaned and "\r" not in cleaned
        assert "\x00" not in cleaned


def test_commit_message_is_shell_inert():
    """即使站点名带 $(...)，产出的 commit message 也不能触发命令执行。"""
    with tempfile.TemporaryDirectory() as tmp:
        data_file = Path(tmp) / "sites.json"
        data_file.write_text("[]\n", encoding="utf-8")
        result = run_ingest("evil$(touch /tmp/opos-should-not-exist)", data_file)

    message = result["commit_message"]
    assert "$(" not in message, f"commit message 仍含 $(: {message!r}"
    assert "`" not in message, f"commit message 仍含反引号: {message!r}"


def test_env_passed_commit_message_does_not_execute():
    """工作流那一侧：env 传进 shell 的值不会被二次解析。

    模拟 GitHub Actions 的文本替换语义 —— 旧写法把 ${{ }} 的值直接拼进
    脚本文本，bash 随后会解析其中的 $(...)；新写法只引用 $VAR。
    """
    marker = Path(tempfile.gettempdir()) / "opos-injection-canary"
    if marker.exists():
        marker.unlink()

    payload = f"feat: 收录新站点「x$(touch {marker})y」"

    # 新写法：值通过环境变量传入，脚本里只引用变量
    script = 'set -euo pipefail\nprintf "%s" "$COMMIT_MESSAGE" > /dev/null\n'
    result = subprocess.run(
        ["bash", "-c", script],
        env={"COMMIT_MESSAGE": payload, "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert not marker.exists(), "env 传值时 $() 被执行了，说明工作流写法退化了"

    # 对照：旧写法（表达式直接拼进脚本文本）确实会执行
    old_script = f'set -euo pipefail\nprintf "%s" "{payload}" > /dev/null\n'
    subprocess.run(["bash", "-c", old_script], capture_output=True, text=True)
    assert marker.exists(), (
        "对照组没有触发执行，说明本机 shell 语义与 CI 不同，测试失去意义"
    )
    marker.unlink()


def test_workflow_does_not_interpolate_untrusted_outputs():
    """工作流里不允许把 step output 直接插进 run: 块。

    这是第一道防线：即使 Python 侧被绕过或将来重构，env 写法也不会退化成
    可注入的表达式插值。
    """
    workflow = (ROOT / ".github" / "workflows" / "ingest-issue.yml").read_text(
        encoding="utf-8"
    )
    # git commit 必须走环境变量
    assert 'git commit -m "$COMMIT_MESSAGE"' in workflow, \
        "commit message 未通过 env 传递"

    # 逐个 run: 块检查：块内不得出现 steps.*.outputs.* 插值
    in_run = False
    block: list[str] = []
    for line in workflow.splitlines():
        stripped = line.strip()
        if stripped.startswith("- name:") or stripped.startswith("run:"):
            if in_run and block:
                joined = "\n".join(block)
                assert "${{ steps." not in joined, (
                    f"run: 块内直接插值了 step output:\n{joined}"
                )
            in_run = stripped.startswith("run:")
            block = []
            continue
        if in_run:
            block.append(line)
    if block:
        assert "${{ steps." not in "\n".join(block)


# ------------------------------------------------------- 模板占位符污染防线

def test_placeholder_in_name_rejected_by_validator():
    """__CARDS__ 这类 token 必须在关卡被拦下。"""
    for field, value in [
        ("name", "__CARDS__"),
        ("owner", "__MILESTONE_BAR__"),
        ("description", "正常简介，但里面有 __SITES_DATA__ 标记"),
    ]:
        site = {
            "name": "ok",
            "url": "https://example.com",
            "owner": "ok",
            "description": "a" * 30,
            "languages": ["en"],
            "region": "US",
            "tags": ["blog"],
        }
        site[field] = value
        try:
            validate([site])
        except Invalid:
            continue
        raise AssertionError(f"{field} 含占位符 token 时应当被拒绝: {value!r}")


def test_ingest_rejects_placeholder_name():
    """自动收录流水线自身也要拦下占位符 token，给出可操作的提示。"""
    with tempfile.TemporaryDirectory() as tmp:
        data_file = Path(tmp) / "sites.json"
        data_file.write_text("[]\n", encoding="utf-8")
        result = run_ingest("__CARDS__", data_file)

    assert result["status"] == "invalid", result
    assert "保留标记" in result["comment"] or "大写" in result["comment"]


def test_build_survives_placeholder_in_data():
    """即便坏数据绕过关卡，生成器也不能被它带崩。

    单遍渲染保证替换进去的内容不会被回头当成占位符解析。
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from generate_site import render_template

    template = "<p>__CARDS__</p><p>__COUNT__</p>"
    values = {"CARDS": "<div>__CARDS__</div>", "COUNT": "7"}
    out = render_template(template, values)
    # 用户内容原样保留，且不会把模板标记吃掉
    assert "<div>__CARDS__</div>" in out
    assert "<p>7</p>" in out


def test_has_placeholder_helper():
    assert has_placeholder("a __CARDS__ b")
    assert has_placeholder("__A__")
    assert not has_placeholder("normal text")
    assert not has_placeholder("__lower__")
    assert not has_placeholder("")
    assert not has_placeholder("a__b__c")  # 前后有字母，不构成占位符


def test_ingest_never_writes_real_data_file():
    """跑完整套收录用例后，真实 data/sites.json 必须一字未动。

    ingest_issue.DATA 在导入时求值，测试若误设环境变量而非替换属性，
    就会把测试数据写进仓库 —— 这条用例专门盯住这种事故。
    """
    real = ROOT / "data" / "sites.json"
    before = real.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        data_file = Path(tmp) / "sites.json"
        data_file.write_text("[]\n", encoding="utf-8")
        run_ingest("some benign site", data_file)
    assert real.read_text(encoding="utf-8") == before, \
        "测试污染了真实的 data/sites.json"


# ------------------------------------------------------------------ slug

def test_slug_and_domain_are_consistent():
    """generate_site.py 与 fetch_favicons.py 共用同一套 slug 逻辑。"""
    assert slug_for("blackman99.github.io") == "blackman99-github-io"
    assert slug_for("Blackman99.GitHub.io") == "blackman99-github-io"
    assert domain_of("https://Example.com:8443/path") == "example.com"
    assert domain_of("not-a-url") == ""
    # slug 只含安全字符，可直接拼进仓库内路径
    assert all(c.isalnum() or c == "-" for c in slug_for("../../etc/passwd"))


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
