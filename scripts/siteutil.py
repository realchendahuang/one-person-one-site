#!/usr/bin/env python3
"""跨脚本共用的纯函数：URL 解析与文件名 slug。

这几个函数此前在 generate_site.py、fetch_favicons.py、ingest_issue.py 里各抄了
一份。generate_site.py 按 slug 找图标、fetch_favicons.py 按 slug 写图标，
两边一旦漂移，图标就会静默失效（构建不报错，只是全部退化成首字母色块），
所以收敛到一处，由测试保证行为一致。
"""
from __future__ import annotations

import re

# 模板占位符形状：__SITES_DATA__、__CARDS__ 等。
# 收录数据里如果出现同形状的文本，字符串替换会把用户内容当成占位符处理，
# 导致构建失败或内容错位，因此在校验阶段就当作非法输入拒绝。
PLACEHOLDER_RE = re.compile(r"__[A-Z][A-Z_]*__")


def domain_of(url: str) -> str:
    """取出 URL 的主机名（小写、不含端口）；无法解析时返回空串。"""
    match = re.match(r"^https?://([^/]+)", url or "", re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).split(":")[0].lower()


def slug_for(domain: str) -> str:
    """把域名转成稳定的文件名，例如 blackman99.github.io → blackman99-github-io。

    生成的路径只用于仓库内已知的两个目录（data/favicons/ 与 site/favicons/），
    拼接前会剥掉端口，因此不含 ".." 或 "/"。
    """
    return re.sub(r"[^a-z0-9]+", "-", (domain or "").lower()).strip("-") or "site"


def has_placeholder(text: str) -> bool:
    """文本里是否含有 __X__ 形状的模板占位符。"""
    return bool(PLACEHOLDER_RE.search(text or ""))
