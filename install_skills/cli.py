from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from install_skills import installer
from install_skills.config import (
    get_default_config_path,
    load_user_config,
    save_user_config,
)
from install_skills.models import UserConfig, GroupConfig


def _ask_obsidian_path(_input_func=input) -> Path | None:
    """交互式询问 Obsidian vault 路径"""
    print("\n是否安装 Obsidian 相关 skills?")
    print("这些 skills 需要安装到你的 Obsidian vault 目录中。")

    while True:
        answer = _input_func(
            "输入 Obsidian vault 路径 (例如 ~/00-life/ob-note)，或留空跳过: "
        ).strip()

        if not answer:
            return None

        path = Path(answer).expanduser()

        # 检查是否存在
        if not path.exists():
            print(f"❌ 路径不存在: {path}")
            retry = _input_func("是否重新输入? [Y/n]: ").strip().lower()
            if retry in ("", "y", "yes"):
                continue
            return None

        # 检查是否是 vault（有 .obsidian 目录）
        if not (path / ".obsidian").exists():
            print(f"⚠️  警告: {path} 似乎不是 Obsidian vault（缺少 .obsidian 目录）")
            confirm = _input_func("仍然继续? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
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

    print("初始化 ce CLI 配置...")
    print(f"仓库根目录: {repo_root}")

    # 扫描可用 skills
    from install_skills.installer import discover_skills

    available_skills = discover_skills(repo_root)

    # 分类 skills
    _obsidian_prefixes = ("obsidian-", "defuddle", "json-canvas")
    _obsidian_names = {
        "learn-llm-wiki",
        "life-ai-newsletters",
        "life-ai-products",
        "life-ask",
        "life-parse-knowledge",
        "life-start-my-day",
    }
    obsidian_skills = [
        s
        for s in available_skills
        if s.startswith(_obsidian_prefixes) or s in _obsidian_names
    ]
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
            ],
        )
    }

    if obsidian_path and obsidian_skills:
        groups["obsidian"] = GroupConfig(
            name="obsidian",
            skills=obsidian_skills,
            targets=[
                obsidian_path / ".claude/skills",
                obsidian_path / ".agents/skills",
            ],
        )

    config = UserConfig(
        version=2,
        repo_root=repo_root,
        groups=groups,
    )

    # 保存
    save_user_config(config_path, config)

    print(f"\n✓ 配置已保存: {config_path}")
    print("\n现在可以运行: ce install")

    return 0


def command_add_skill(
    skill_name: str,
    group_name: str,
    home: Path,
    *,
    stdout=None,
) -> int:
    """添加 skill 到指定组。"""
    config_path = get_default_config_path(home)
    config = load_user_config(config_path)

    if config is None:
        print("配置未找到，请先运行: ce init")
        return 1

    if group_name not in config.groups:
        print(f"组 '{group_name}' 不存在")
        return 1

    group = config.groups[group_name]

    if skill_name in group.skills:
        print(f"skill '{skill_name}' 已在组 '{group_name}' 中")
        return 0

    # 创建新的 GroupConfig（frozen dataclass 不能直接修改）
    from dataclasses import replace

    new_group = replace(group, skills=group.skills + [skill_name])

    # 更新 config
    new_groups = dict(config.groups)
    new_groups[group_name] = new_group

    new_config = replace(config, groups=new_groups)

    save_user_config(config_path, new_config)
    print(f"✓ 已添加 '{skill_name}' 到组 '{group_name}'")
    return 0


def command_add_target(
    target_path: str,
    group_name: str,
    home: Path,
    *,
    stdout=None,
) -> int:
    """添加 target 到指定组。"""
    config_path = get_default_config_path(home)
    config = load_user_config(config_path)

    if config is None:
        print("配置未找到，请先运行: ce init")
        return 1

    if group_name not in config.groups:
        print(f"组 '{group_name}' 不存在")
        return 1

    group = config.groups[group_name]
    target = Path(target_path).expanduser()

    if target in group.targets:
        print(f"target '{target}' 已在组 '{group_name}' 中")
        return 0

    # 创建新的 GroupConfig
    from dataclasses import replace

    new_group = replace(group, targets=group.targets + [target])

    # 更新 config
    new_groups = dict(config.groups)
    new_groups[group_name] = new_group

    new_config = replace(config, groups=new_groups)

    save_user_config(config_path, new_config)
    print(f"✓ 已添加 '{target}' 到组 '{group_name}'")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ce",
        description="Manage coding-everything skill installation",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    subparsers.add_parser("init", help="Initialize configuration interactively")

    # install
    install_parser = subparsers.add_parser("install", help="Install skills")
    install_parser.add_argument("--group", help="Only install specified group")

    # update
    update_parser = subparsers.add_parser("update", help="Update installed skills")
    update_parser.add_argument("--group", help="Only update specified group")

    # uninstall
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall skills")
    uninstall_parser.add_argument("--group", help="Only uninstall specified group")

    # status
    status_parser = subparsers.add_parser("status", help="Show installation status")
    status_parser.add_argument("--group", help="Only show specified group")

    # doctor
    subparsers.add_parser("doctor", help="Diagnose and fix installation issues")

    # add-skill
    add_skill_parser = subparsers.add_parser("add-skill", help="Add a skill to a group")
    add_skill_parser.add_argument("skill", help="Skill name to add")
    add_skill_parser.add_argument("--group", required=True, help="Target group")

    # add-target
    add_target_parser = subparsers.add_parser(
        "add-target", help="Add a target directory to a group"
    )
    add_target_parser.add_argument("target", help="Target directory path")
    add_target_parser.add_argument("--group", required=True, help="Target group")

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

    if args.command == "add-skill":
        return command_add_skill(args.skill, args.group, resolved_home, stdout=stdout)

    if args.command == "add-target":
        return command_add_target(args.target, args.group, resolved_home, stdout=stdout)

    # 检查是否存在用户级配置 ~/.ce/config.yaml
    user_config_path = get_default_config_path(resolved_home)
    if user_config_path.exists():
        # 使用新的 UserConfig 模式
        if args.command == "install":
            return installer.command_install_from_config(
                resolved_repo_root, resolved_home, group=args.group, stdout=stdout
            )
        if args.command == "update":
            return installer.command_install_from_config(
                resolved_repo_root, resolved_home, group=args.group, stdout=stdout
            )
        if args.command == "uninstall":
            return installer.command_uninstall_from_config(
                resolved_repo_root,
                resolved_home,
                group=args.group,
                stdout=stdout,
                stderr=stderr,
            )
        if args.command == "doctor":
            return installer.command_doctor_from_config(
                resolved_repo_root, resolved_home, stdout=stdout
            )
        if args.command == "status":
            return installer.command_status_from_config(
                resolved_repo_root, resolved_home, group=args.group, stdout=stdout
            )

    # 退回到旧版逻辑（向后兼容）
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
