#!/usr/bin/env python3
"""
Switch upstream submodules back to their local main branch.

Default mode:
- Read all initialized upstream/* submodules from .gitmodules
- For each submodule, fast-forward local `main` to the current checkout commit

Explicit mode:
- Accept one or more --path values to limit which submodules are switched

Legacy mode:
- --changed-only limits switching to submodules whose gitlink differs from a base ref
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


def is_initialized_submodule(repo_root: Path, path: str) -> bool:
    return (repo_root / path / ".git").exists()


def parse_gitmodules_paths(repo_root: Path) -> list[str]:
    raw = run_git(["config", "--file", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$"], repo_root)
    paths: list[str] = []
    for line in raw.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        path = parts[1]
        if path.startswith("upstream/") and is_initialized_submodule(repo_root, path):
            paths.append(path)
    return paths


def parse_all_upstream_submodules(repo_root: Path) -> list[SubmoduleTarget]:
    return [
        SubmoduleTarget(path=path, target_sha=read_submodule_head(repo_root, path))
        for path in parse_gitmodules_paths(repo_root)
    ]


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
    try:
        run_git(["switch", "main"], submodule_dir)
    except subprocess.CalledProcessError:
        run_git(["switch", "--track", "origin/main"], submodule_dir)
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


def choose_targets(repo_root: Path, paths: list[str], changed_only: bool, base_ref: str) -> list[SubmoduleTarget]:
    if paths:
        return [
            SubmoduleTarget(path=path, target_sha=read_submodule_head(repo_root, path))
            for path in paths
        ]
    if changed_only:
        return parse_changed_submodules(repo_root, base_ref)
    return parse_all_upstream_submodules(repo_root)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Switch upstream submodules back to local main."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Root repository path. Defaults to current directory.",
    )
    parser.add_argument(
        "--base-ref",
        default="HEAD",
        help="Base ref for --changed-only detection. Defaults to HEAD.",
    )
    parser.add_argument(
        "--changed-only",
        action="store_true",
        help="Only switch submodules whose gitlink differs from --base-ref.",
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
        targets = choose_targets(repo_root, args.paths, args.changed_only, args.base_ref)
        if not targets:
            print("[OK] 当前没有检测到已初始化的 upstream submodule")
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
