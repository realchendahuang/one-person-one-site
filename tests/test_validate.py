#!/usr/bin/env python3
"""validate.py 的规则测试：合法数据通过，每类违规都要被拦住。

这些用例同时是「收录标准」的可执行说明——改规则时先改这里，
避免放宽限制后悄悄放进不符合标准的站点。

用法：
    python3 -m pytest tests/ -q
    python3 tests/test_validate.py          # 无需 pytest 也能跑
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate import (  # noqa: E402
    LANGUAGE_RE,
    MAX_DESCRIPTION,
    MAX_NAME,
    MAX_TAGS,
    MIN_DESCRIPTION,
    REQUIRED,
    TAG_RE,
    Invalid,
    validate,
)

VALID = {
    "name": "示例博客",
    "url": "https://example.com",
    "owner": "示例作者",
    "description": "一个用来演示数据格式的个人博客，长期记录技术与生活。",
    "languages": ["zh-CN"],
    "region": "China",
    "tags": ["blog", "developer"],
}


def site(**overrides):
    entry = copy.deepcopy(VALID)
    entry.update(overrides)
    for key, value in overrides.items():
        if value is None:
            entry.pop(key, None)
    return entry


def expect_invalid(entry, label):
    try:
        validate([entry])
    except Invalid:
        return True
    raise AssertionError(f"应当拒绝但通过了: {label}")


def test_valid_entry_passes():
    assert validate([site()]) == 1


def test_real_data_file_passes():
    sites = json.loads((ROOT / "data" / "sites.json").read_text(encoding="utf-8"))
    assert validate(sites) == len(sites)


def test_missing_required_field():
    expect_invalid(site(tags=None), "缺少 tags")
    expect_invalid(site(feed=None, url=None), "缺少 url")


def test_wrong_top_level_type():
    try:
        validate({"name": "x"})
    except Invalid:
        return
    raise AssertionError("顶层不是数组时应当拒绝")


def test_name_too_long():
    expect_invalid(site(name="长" * 41), "name 超过 40 字符")


def test_description_bounds():
    expect_invalid(site(description="太短"), "description 少于 15 字符")
    expect_invalid(site(description="长" * 241), "description 超过 240 字符")


def test_url_must_be_http():
    expect_invalid(site(url="ftp://example.com"), "非 http(s) 协议")
    expect_invalid(site(url="example.com"), "缺少协议")
    expect_invalid(site(url=""), "空 url")


def test_duplicate_url_is_rejected():
    try:
        validate([site(), site(url="https://example.com/")])
    except Invalid:
        return
    raise AssertionError("忽略结尾斜杠后重复的网址应当拒绝")


def test_language_format():
    expect_invalid(site(languages=["zh-cn"]), "语言代码需大写地区")
    expect_invalid(site(languages=["Chinese"]), "语言需用代码而非名称")
    expect_invalid(site(languages=[]), "语言不能为空")
    expect_invalid(site(languages=["en", "en"]), "语言不能重复")
    assert validate([site(languages=["zh-TW", "en", "ja"])]) == 1


def test_tag_format():
    expect_invalid(site(tags=["Blog"]), "标签必须小写")
    expect_invalid(site(tags=["indie hacker"]), "多词标签用中划线")
    expect_invalid(site(tags=["-blog"]), "标签不能以中划线开头")
    expect_invalid(site(tags=[]), "标签不能为空")
    expect_invalid(site(tags=[f"t{i}" for i in range(9)]), "标签最多 8 个")
    expect_invalid(site(tags=["blog", "blog"]), "标签不能重复")
    assert validate([site(tags=["indie-hacker", "ai", "web3"])]) == 1


def test_feed_optional_but_validated():
    assert validate([site()]) == 1
    assert validate([site(feed="https://example.com/rss.xml")]) == 1
    expect_invalid(site(feed="not-a-url"), "feed 必须是有效地址")


def test_unsupported_field():
    expect_invalid(site(star=5), "不支持的字段应当拒绝")


def test_non_string_owner():
    expect_invalid(site(owner=123), "owner 必须是字符串")
    expect_invalid(site(description="   "), "空白字符串不算有内容")


def test_schema_matches_validator():
    """schema/site.schema.json 与 validate.py 必须描述同一套规则。

    以前这个 schema 文件没有任何代码引用，贡献者却会以为提交被它校验过。
    现在它是可执行契约的一部分：任一侧改了限制而另一侧没跟上，测试就会失败。
    """
    schema = json.loads(
        (ROOT / "schema" / "site.schema.json").read_text(encoding="utf-8")
    )
    props = schema["properties"]

    assert schema["required"] == REQUIRED, "必填字段与校验器不一致"
    assert schema["additionalProperties"] is False, "应禁止未声明字段"

    assert props["name"]["maxLength"] == MAX_NAME
    assert props["description"]["minLength"] == MIN_DESCRIPTION
    assert props["description"]["maxLength"] == MAX_DESCRIPTION
    assert props["tags"]["maxItems"] == MAX_TAGS
    assert props["tags"]["uniqueItems"] is True
    assert props["languages"]["uniqueItems"] is True

    assert props["tags"]["items"]["pattern"] == TAG_RE.pattern
    assert props["languages"]["items"]["pattern"] == LANGUAGE_RE.pattern


def test_schema_patterns_agree_with_validator():
    """用同一批样例分别喂给 schema 正则与校验器，结果必须一致。"""
    schema = json.loads(
        (ROOT / "schema" / "site.schema.json").read_text(encoding="utf-8")
    )
    import re as _re

    tag_pattern = _re.compile(schema["properties"]["tags"]["items"]["pattern"])
    lang_pattern = _re.compile(schema["properties"]["languages"]["items"]["pattern"])

    for tag in ["blog", "indie-hacker", "ai", "Blog", "indie hacker", "-x", "a_b"]:
        assert bool(tag_pattern.match(tag)) == bool(TAG_RE.match(tag)), tag

    for lang in ["zh-CN", "en", "ja", "zh-TW", "zh-cn", "Chinese", "EN"]:
        assert bool(lang_pattern.match(lang)) == bool(LANGUAGE_RE.match(lang)), lang


def test_cli_exit_codes():
    ok = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate.py")],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert ok.returncode == 0, ok.stderr

    bad = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate.py"), "--data", "/nonexistent.json"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert bad.returncode == 1


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
