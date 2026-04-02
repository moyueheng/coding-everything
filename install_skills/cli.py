from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from install_skills import installer
from install_skills.config import get_default_config_path, load_user_config, save_user_config
from install_skills.models import UserConfig, GroupConfig


def _ask_obsidian_path(_input_func=input) -> Path | None:
    """交互式询问 Obsidian vault 路径"""
    print("\n是否安装 Obsidian 相关 skills?")
    print("这些 skills 需要安装到你的 Obsidian vault 目录中。")

    while True:
        answer = _input_func("输入 Obsidian vault 路径 (例如 ~/00-life/ob-note)，或留空跳过: ").strip()

        if not answer:
            return None

        path = Path(answer).expanduser()

        # 检查是否存在
        if not path.exists():
            print(f"❌ 路径不存在: {path}")
            retry = _input_func("是否重新输入? [Y/n]: ").strip().lower()
            if retry in ('', 'y', 'yes'):
                continue
            return None

        # 检查是否是 vault（有 .obsidian 目录）
        if not (path / ".obsidian").exists():
            print(f"⚠️  警告: {path} 似乎不是 Obsidian vault（缺少 .obsidian 目录）")
            confirm = _input_func("仍然继续? [y/N]: ").strip().lower()
            if confirm not in ('y', 'yes'):
                continue

        return path


def command_init(
    repo_root: Path,
    home: Path,
    *,
    stdout=None,
    _input_func=input,
) -> int:
    """交互式初始化配置。"""
    config_path = get_default_config_path(home)

    # 检查是否已存在
    if config_path.exists():
        print(f"配置已存在: {config_path}")
        print("如需重新配置，请先删除该文件。")
        return 1

    print(f"初始化 ce CLI 配置...")
    print(f"仓库根目录: {repo_root}")

    # 扫描可用 skills
    from install_skills.installer import discover_skills
    available_skills = discover_skills(repo_root)

    # 分类 skills
    obsidian_skills = [s for s in available_skills if s.startswith(("obsidian-", "defuddle", "json-canvas"))]
    global_skills = [s for s in available_skills if s not in obsidian_skills]

    print(f"\n发现 {len(global_skills)} 个通用 skills")
    if obsidian_skills:
        print(f"发现 {len(obsidian_skills)} 个 Obsidian 相关 skills")

    # 询问 Obsidian 路径
    obsidian_path = _ask_obsidian_path(_input_func)

    # 构建配置
    groups = {
        "global": GroupConfig(
            name="global",
            skills=global_skills,
            targets=[
                home / ".agents/skills",
                home / ".claude/skills",
            ]
        )
    }

    if obsidian_path and obsidian_skills:
        groups["obsidian"] = GroupConfig(
            name="obsidian",
            skills=obsidian_skills,
            targets=[
                obsidian_path / ".claude/skills",
                obsidian_path / ".agents/skills",
            ]
        )

    config = UserConfig(
        version=2,
        repo_root=repo_root,
        groups=groups,
    )

    # 保存
    save_user_config(config_path, config)

    print(f"\n✓ 配置已保存: {config_path}")
    print(f"\n现在可以运行: ce install")

    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ce",
        description="Manage coding-everything skill installation",
    )
    parser.add_argument(
        "command",
        choices=("init", "install", "update", "uninstall", "status", "doctor"),
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

    if args.command == "init":
        return command_init(resolved_repo_root, resolved_home, stdout=stdout)

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
        if args.command == "doctor":
            return installer.command_doctor(
                resolved_repo_root,
                resolved_home,
                config_path,
                stdout=stdout,
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
