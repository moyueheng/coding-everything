#!/usr/bin/env python3
"""
Generate a markdown summary for updated submodules in the current repository.

Default mode:
- Compare submodule gitlinks in the worktree against a base ref (default HEAD)
- Summarize changed submodules only

Explicit mode:
- Accept one or more --range entries in the form:
  upstream/superpowers:oldsha..newsha
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ChangeRange:
    path: str
    old_sha: str
    new_sha: str


def run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def read_gitlink_sha(repo_root: Path, ref: str, path: str) -> str:
    output = run_git(["ls-tree", ref, path], repo_root)
    if not output:
        raise ValueError(f"无法从 {ref} 读取 {path} 的 gitlink")
    parts = output.split()
    if len(parts) < 3 or parts[1] != "commit":
        raise ValueError(f"{ref}:{path} 不是 submodule gitlink")
    return parts[2]


def parse_changed_submodules(repo_root: Path, base_ref: str) -> list[ChangeRange]:
    raw = run_git(["diff", "--raw", base_ref, "--"], repo_root)
    changes: list[ChangeRange] = []
    for line in raw.splitlines():
        if not line.startswith(":160000 160000 "):
            continue
        _, path = line.split("\t", 1)
        old_sha = read_gitlink_sha(repo_root, base_ref, path)
        new_sha = run_git(["rev-parse", "HEAD"], repo_root / path)
        changes.append(ChangeRange(path=path, old_sha=old_sha, new_sha=new_sha))
    return changes


def parse_explicit_range(raw_value: str) -> ChangeRange:
    if ":" not in raw_value or ".." not in raw_value:
        raise ValueError(f"Invalid --range value: {raw_value}")
    path, rev_range = raw_value.split(":", 1)
    old_sha, new_sha = rev_range.split("..", 1)
    path = path.strip()
    old_sha = old_sha.strip()
    new_sha = new_sha.strip()
    if not path or not old_sha or not new_sha:
        raise ValueError(f"Invalid --range value: {raw_value}")
    return ChangeRange(path=path, old_sha=old_sha, new_sha=new_sha)


def collect_commits(submodule_dir: Path, old_sha: str, new_sha: str) -> list[str]:
    fmt = "%h%x09%ad%x09%s"
    output = run_git(
        ["log", "--date=short", f"--pretty=format:{fmt}", f"{old_sha}..{new_sha}"],
        submodule_dir,
    )
    return [line for line in output.splitlines() if line.strip()]


def collect_shortstat(submodule_dir: Path, old_sha: str, new_sha: str) -> str:
    output = run_git(["diff", "--shortstat", old_sha, new_sha], submodule_dir)
    return output or "无文件差异统计"


def format_markdown(changes: list[ChangeRange], repo_root: Path, base_ref: str) -> str:
    lines: list[str] = []
    lines.append("# 上游更新摘要")
    lines.append("")
    lines.append(f"- 基准引用：`{base_ref}`")
    lines.append(f"- 仓库根目录：`{repo_root}`")
    lines.append("")

    if not changes:
        lines.append("当前没有检测到 submodule gitlink 变化。")
        return "\n".join(lines) + "\n"

    lines.append("## 变更概览")
    lines.append("")
    lines.append("| 仓库 | 旧 SHA | 新 SHA | commit 数 |")
    lines.append("|------|--------|--------|-----------|")

    section_cache: list[tuple[ChangeRange, list[str], str]] = []
    for change in changes:
        submodule_dir = repo_root / change.path
        commits = collect_commits(submodule_dir, change.old_sha, change.new_sha)
        shortstat = collect_shortstat(submodule_dir, change.old_sha, change.new_sha)
        section_cache.append((change, commits, shortstat))
        lines.append(
            f"| `{change.path}` | `{change.old_sha[:7]}` | `{change.new_sha[:7]}` | {len(commits)} |"
        )

    for change, commits, shortstat in section_cache:
        lines.append("")
        lines.append(f"## {change.path}")
        lines.append("")
        lines.append(f"- 旧 SHA：`{change.old_sha}`")
        lines.append(f"- 新 SHA：`{change.new_sha}`")
        lines.append(f"- diff 统计：{shortstat}")
        lines.append("")
        lines.append("### Commit 列表")
        lines.append("")
        if commits:
            for commit in commits:
                sha, date, subject = commit.split("\t", 2)
                lines.append(f"- `{date}` `{sha}` {subject}")
        else:
            lines.append("- 该区间没有可列出的 commit。")

    return "\n".join(lines) + "\n"


def write_output(content: str, output: str | None) -> None:
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        print(f"[OK] 已写入 {output_path}")
        return
    print(content, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate upstream update markdown.")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Root repository path. Defaults to current directory.",
    )
    parser.add_argument(
        "--base-ref",
        default="HEAD",
        help="Base ref for changed submodule detection. Defaults to HEAD.",
    )
    parser.add_argument(
        "--range",
        action="append",
        default=[],
        dest="ranges",
        help="Explicit range in the form path:oldsha..newsha. Repeatable.",
    )
    parser.add_argument(
        "--output",
        help="Write markdown to a file instead of stdout.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if not (repo_root / ".git").exists():
        print(f"[ERROR] Not a git repository root: {repo_root}", file=sys.stderr)
        return 1

    try:
        if args.ranges:
            changes = [parse_explicit_range(item) for item in args.ranges]
        else:
            changes = parse_changed_submodules(repo_root, args.base_ref)
        content = format_markdown(changes, repo_root, args.base_ref)
        write_output(content, args.output)
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        print(f"[ERROR] Git command failed: {message}", file=sys.stderr)
        return exc.returncode or 1
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
