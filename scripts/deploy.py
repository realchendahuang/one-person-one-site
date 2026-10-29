#!/usr/bin/env python3
"""本地构建并把 site/ 发布到 gh-pages 分支。

CI 已移除，部署完全本地：先重新生成静态站，再把 site/ 的内容作为一个
新提交写入 gh-pages 分支并推送。GitHub Pages 配置为「从 gh-pages 分支
（root 目录）部署」，push 完成后 Pages 自动更新，全程不依赖 Actions。

实现走 git plumbing（临时 index → write-tree → commit-tree → update-ref），
不改工作区、不动 main 的暂存区，也不需要 worktree。

用法：
    python3 scripts/deploy.py                 # 构建 + 发布 + 推送
    python3 scripts/deploy.py --no-push       # 只更新本地 gh-pages 分支
    python3 scripts/deploy.py --skip-build    # 跳过重新生成，直接发布现有 site/
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PAGES_BRANCH = "gh-pages"
PAGES_URL = "https://realchendahuang.github.io/one-person-one-site/"

# Jekyll 会忽略下划线开头的路径并重新处理静态文件；一个空的 .nojekyll
# 让 Pages 原样发布构建产物。
NOJEKYLL = ".nojekyll"


def run(args: list[str], env: dict | None = None, cwd: Path | None = None) -> str:
    result = subprocess.run(
        args, cwd=cwd or ROOT, env=env, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"命令失败 ({result.returncode}): {' '.join(args)}\n{result.stderr.strip()}"
        )
    return result.stdout.strip()


def git_env(extra: dict[str, str] | None = None) -> dict:
    env = dict(os.environ)
    if extra:
        env.update(extra)
    return env


def build() -> None:
    print("构建静态站 …")
    run([sys.executable, str(ROOT / "scripts" / "generate_site.py")])
    print("构建完成")


def stage_tree() -> str:
    """把 site/ 的内容 + .nojekyll 写进临时 index，返回 tree 的 sha。

    tree 的根必须直接是产物（index.html 在根上）：在仓库里直接
    `git add site` 会把 `site/` 前缀带进 index，发布出去就是
    根目录下多一层 site/，Pages 找不到 index.html 返回 404。
    所以复制到临时目录后用 GIT_WORK_TREE 指过去再 add。
    """
    if not (SITE / "index.html").exists():
        raise SystemExit(f"{SITE} 里没有 index.html，请先构建")

    with tempfile.TemporaryDirectory(prefix="opos-deploy-") as tmp:
        work = Path(tmp) / "pub"
        shutil.copytree(SITE, work)
        # .nojekyll 不属于构建产物，发布时补上
        (work / NOJEKYLL).write_text("", encoding="utf-8")

        with tempfile.NamedTemporaryFile(prefix="opos-index-", delete=False) as handle:
            index_path = handle.name
        env = git_env({
            "GIT_INDEX_FILE": index_path,
            "GIT_DIR": str(ROOT / ".git"),
            "GIT_WORK_TREE": str(work),
        })
        try:
            run(["git", "read-tree", "--empty"], env=env, cwd=work)
            run(["git", "add", "--force", "--all", "."], env=env, cwd=work)
            tree = run(["git", "write-tree"], env=env, cwd=work)
        finally:
            Path(index_path).unlink(missing_ok=True)
    return tree


def make_commit(tree: str) -> str:
    parent = ""
    for ref in (f"refs/heads/{PAGES_BRANCH}", f"refs/remotes/origin/{PAGES_BRANCH}"):
        try:
            parent = run(["git", "rev-parse", "--verify", ref])
            break
        except RuntimeError:
            continue

    head = run(["git", "rev-parse", "--short", "HEAD"])
    count = run(["git", "show", "--format=%h", "--no-patch", "HEAD"])
    message = f"deploy: 发布 main@{head} 的构建产物"
    args = ["git", "commit-tree", tree, "-m", message]
    if parent:
        args += ["-p", parent]
    commit = run(args)
    return commit


def deploy(push: bool = True) -> None:
    tree = stage_tree()
    commit = make_commit(tree)
    run(["git", "update-ref", f"refs/heads/{PAGES_BRANCH}", commit])
    try:
        base = run(["git", "rev-parse", "--short", f"{PAGES_BRANCH}~1"])
    except RuntimeError:
        base = "（首个提交）"
    files = len(run(["git", "ls-tree", "-r", "--name-only", PAGES_BRANCH]).splitlines())
    print(f"已写入 {PAGES_BRANCH}@{commit[:7]}（{files} 个文件，基于 {base}）")

    if not push:
        print("--no-push：未推送，如需上线请手动 git push origin gh-pages")
        return
    run(["git", "push", "origin", f"{PAGES_BRANCH}:{PAGES_BRANCH}"])
    print(f"已推送。Pages 构建完成后可访问：{PAGES_URL}")


def main() -> None:
    parser = argparse.ArgumentParser(description="本地构建并发布到 gh-pages 分支")
    parser.add_argument("--no-push", action="store_true", help="只更新本地 gh-pages，不推送")
    parser.add_argument("--skip-build", action="store_true", help="跳过 generate_site.py，直接发布现有 site/")
    args = parser.parse_args()

    if not args.skip_build:
        build()
    deploy(push=not args.no_push)


if __name__ == "__main__":
    main()
