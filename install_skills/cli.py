from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from install_skills import installer


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ce",
        description="Manage coding-everything skill installation",
    )
    parser.add_argument(
        "command",
        choices=("install", "update", "uninstall", "status"),
    )
    parser.add_argument(
        "--group",
        default=None,
        help="Only operate on the specified group",
    )
    return parser.parse_args(argv)


def main(
    argv: list[str] | None = None,
    *,
    repo_root: Path | None = None,
    home: Path | None = None,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    resolved_repo_root = repo_root or Path(__file__).resolve().parents[1]
    resolved_home = home or Path.home()

    config_path = resolved_repo_root / "skills-install.yaml"
    use_grouped = config_path.is_file()

    if use_grouped:
        if args.command == "install":
            return installer.command_install_grouped(
                resolved_repo_root,
                resolved_home,
                config_path,
                group=args.group,
                stdout=stdout,
            )
        if args.command == "update":
            return installer.command_install_grouped(
                resolved_repo_root,
                resolved_home,
                config_path,
                group=args.group,
                stdout=stdout,
            )
        if args.command == "uninstall":
            return installer.command_uninstall_grouped(
                resolved_repo_root,
                resolved_home,
                config_path,
                group=args.group,
                stdout=stdout,
                stderr=stderr,
            )
        return installer.command_status_grouped(
            resolved_repo_root,
            resolved_home,
            config_path,
            group=args.group,
            stdout=stdout,
        )

    if args.command == "install":
        return installer.command_install(
            resolved_repo_root, resolved_home, stdout=stdout
        )
    if args.command == "update":
        return installer.command_update(
            resolved_repo_root, resolved_home, stdout=stdout
        )
    if args.command == "uninstall":
        return installer.command_uninstall(
            resolved_repo_root, resolved_home, stdout=stdout, stderr=stderr
        )
    return installer.command_status(resolved_repo_root, resolved_home, stdout=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
