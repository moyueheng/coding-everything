#!/usr/bin/env python3
"""Create CLAUDE.md -> AGENTS.md symlinks next to AGENTS.md files."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or repair CLAUDE.md symlinks pointing to AGENTS.md."
    )
    parser.add_argument("directories", nargs="+", help="Directories that contain AGENTS.md")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing CLAUDE.md file or symlink after AGENTS.md is present.",
    )
    return parser.parse_args()


def ensure_link(directory: Path, force: bool) -> str:
    target = directory / "AGENTS.md"
    link = directory / "CLAUDE.md"

    if not directory.is_dir():
        raise FileNotFoundError(f"not a directory: {directory}")
    if not target.is_file():
        raise FileNotFoundError(f"missing AGENTS.md: {target}")

    if link.is_symlink():
        current = os.readlink(link)
        if current == "AGENTS.md":
            return f"ok: {link} -> AGENTS.md"
        if not force:
            raise FileExistsError(f"{link} points to {current!r}; use --force to replace")
        link.unlink()
    elif link.exists():
        if not force:
            raise FileExistsError(f"{link} exists and is not a symlink; use --force to replace")
        link.unlink()

    link.symlink_to("AGENTS.md")
    return f"created: {link} -> AGENTS.md"


def main() -> int:
    args = parse_args()
    for raw_directory in args.directories:
        print(ensure_link(Path(raw_directory).resolve(), args.force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
