#!/usr/bin/env python3
"""
Switch updated upstream submodules back to their local main branch.

Default mode:
- Detect submodules whose gitlink differs from a base ref (default HEAD)
- For each changed submodule, fast-forward local `main` to the updated commit

Explicit mode:
- Accept one or more --path values to limit which submodules are switched
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SubmoduleTarget:
    path: str
    target_sha: str


def run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def read_submodule_head(repo_root: Path, path: str) -> str:
    return run_git(["rev-parse", "HEAD"], repo_root / path)


def parse_changed_submodules(repo_root: Path, base_ref: str) -> list[SubmoduleTarget]:
    raw = run_git(["diff", "--raw", base_ref, "--"], repo_root)
    targets: list[SubmoduleTarget] = []
    for line in raw.splitlines():
        if not line.startswith(":160000 160000 "):
            continue
        _, path = line.split("\t", 1)
        targets.append(SubmoduleTarget(path=path, target_sha=read_submodule_head(repo_root, path)))
    return targets


def switch_to_main(repo_root: Path, target: SubmoduleTarget) -> str:
    submodule_dir = repo_root / target.path
    run_git(["switch", "main"], submodule_dir)
    run_git(["merge", "--ff-only", target.target_sha], submodule_dir)
    head = run_git(["rev-parse", "--abbrev-ref", "HEAD"], submodule_dir)
    if head != "main":
        raise ValueError(f"{target.path} 切换后仍不在 main 分支: {head}")
    current_sha = run_git(["rev-parse", "HEAD"], submodule_dir)
    if current_sha != target.target_sha:
        raise ValueError(
            f"{target.path} 的 main 没有前进到目标提交: {current_sha} != {target.target_sha}"
        )
    return head


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Switch updated upstream submodules back to local main."
    )
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
        "--path",
        action="append",
        default=[],
        dest="paths",
        help="Explicit submodule path to switch. Repeatable.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if not (repo_root / ".git").exists():
        print(f"[ERROR] Not a git repository root: {repo_root}", file=sys.stderr)
        return 1

    try:
        targets = (
            [SubmoduleTarget(path=path, target_sha=read_submodule_head(repo_root, path)) for path in args.paths]
            if args.paths
            else parse_changed_submodules(repo_root, args.base_ref)
        )
        if not targets:
            print("[OK] 当前没有检测到需要切回 main 的 submodule")
            return 0
        for target in targets:
            switch_to_main(repo_root, target)
            print(f"[OK] {target.path} -> main @ {target.target_sha[:7]}")
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
