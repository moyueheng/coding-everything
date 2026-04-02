#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os as _os
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, TextIO

from install_skills.models import SkillGroup


MANIFEST_RELATIVE_PATH = Path(".local/share/coding-everything/install-manifest.json")
AGENTS_SKILLS_RELATIVE_DIR = Path(".agents/skills")
CLAUDE_SKILLS_RELATIVE_DIR = Path(".claude/skills")
KIMI_AGENT_RELATIVE_PATH = Path(".kimi/agents/superpower")
KS_RELATIVE_PATH = Path(".local/bin/ks")

CE_DIR = Path(".ce")
CE_MANIFEST = Path(".ce/install-manifest.json")


@dataclass(frozen=True)
class InstallTargets:
    agents_skills_dir: Path
    claude_skills_dir: Path
    kimi_agent_dir: Path
    ks_path: Path
    manifest_path: Path


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_targets(home: Path) -> InstallTargets:
    return InstallTargets(
        agents_skills_dir=home / AGENTS_SKILLS_RELATIVE_DIR,
        claude_skills_dir=home / CLAUDE_SKILLS_RELATIVE_DIR,
        kimi_agent_dir=home / KIMI_AGENT_RELATIVE_PATH,
        ks_path=home / KS_RELATIVE_PATH,
        manifest_path=home / MANIFEST_RELATIVE_PATH,
    )


def discover_skills(repo_root: Path) -> list[str]:
    skills_dir = repo_root / "skills"
    if not skills_dir.is_dir():
        raise FileNotFoundError(f"skills directory not found: {skills_dir}")
    discovered = []
    for path in skills_dir.iterdir():
        if not path.is_dir():
            continue
        if path.is_symlink() and path.resolve() == skills_dir.resolve():
            continue
        if not (path / "SKILL.md").is_file():
            continue
        discovered.append(path.name)
    return sorted(discovered)


MCP_CONFIG_RELATIVE_PATH = Path("mcp-configs/required.json")
ZAI_MCP_NAMES = ("zai-github-read", "zai-web-reader", "zai-web-search-prime")
CLAUDE_JSON_FILENAME = ".claude.json"
PLACEHOLDER_ZAI_API_KEY = "{{ZAI_API_KEY}}"


def load_mcp_template(repo_root: Path) -> dict:
    path = repo_root / MCP_CONFIG_RELATIVE_PATH
    if not path.is_file():
        raise FileNotFoundError(f"MCP config not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_zai_api_key(claude_config: dict) -> str | None:
    for name in ZAI_MCP_NAMES:
        server = claude_config.get("mcpServers", {}).get(name, {})
        auth = server.get("headers", {}).get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[len("Bearer ") :]
    env_key = _os.environ.get("ZAI_API_KEY")
    if env_key:
        return env_key
    return None


def _deep_copy_without_internal_keys(data: dict) -> dict:
    return {k: v for k, v in data.items() if not k.startswith("_")}


def merge_mcp_config(home: Path, repo_root: Path) -> tuple[list[str], list[str]]:
    """合并 MCP 配置到 ~/.claude.json。

    Returns:
        (installed, skipped) 元组，分别表示已安装和因缺少 ZAI_API_KEY 而跳过的 MCP 名称
    """
    template = load_mcp_template(repo_root)
    claude_json_path = home / CLAUDE_JSON_FILENAME

    if claude_json_path.exists():
        claude_config = json.loads(claude_json_path.read_text(encoding="utf-8"))
    else:
        claude_config = {}

    if "mcpServers" not in claude_config:
        claude_config = {**claude_config, "mcpServers": {}}

    zai_api_key = resolve_zai_api_key(claude_config)
    installed: list[str] = []
    skipped: list[str] = []

    for name, server_def in template["mcpServers"].items():
        clean_def = _deep_copy_without_internal_keys(server_def)

        needs_zai_key = PLACEHOLDER_ZAI_API_KEY in json.dumps(clean_def)
        if needs_zai_key and zai_api_key is None:
            skipped.append(name)
            continue

        if needs_zai_key:
            serialized = json.dumps(clean_def)
            serialized = serialized.replace(PLACEHOLDER_ZAI_API_KEY, zai_api_key)
            clean_def = json.loads(serialized)

        claude_config["mcpServers"] = {
            **claude_config["mcpServers"],
            name: clean_def,
        }
        installed.append(name)

    claude_json_path.parent.mkdir(parents=True, exist_ok=True)
    claude_json_path.write_text(
        json.dumps(claude_config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return sorted(installed), sorted(skipped)


def remove_managed_mcps(home: Path, managed_names: list[str]) -> None:
    claude_json_path = home / CLAUDE_JSON_FILENAME
    if not claude_json_path.exists():
        return

    claude_config = json.loads(claude_json_path.read_text(encoding="utf-8"))
    servers = claude_config.get("mcpServers", {})

    managed_set = set(managed_names)
    updated_servers = {k: v for k, v in servers.items() if k not in managed_set}

    claude_config = {**claude_config, "mcpServers": updated_servers}
    claude_json_path.write_text(
        json.dumps(claude_config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def collect_mcp_status(home: Path, repo_root: Path) -> dict:
    template = load_mcp_template(repo_root)
    claude_json_path = home / CLAUDE_JSON_FILENAME

    if claude_json_path.exists():
        claude_config = json.loads(claude_json_path.read_text(encoding="utf-8"))
        existing = set(claude_config.get("mcpServers", {}).keys())
    else:
        existing = set()

    configured: list[str] = []
    missing: list[str] = []

    for name in sorted(template["mcpServers"].keys()):
        if name in existing:
            configured.append(name)
        else:
            missing.append(name)

    return {"configured": configured, "missing": missing}


def remove_existing(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    shutil.rmtree(path)


def force_symlink(src: Path, dst: Path) -> None:
    # 检查并修复损坏的父目录链接
    parent = dst.parent
    if parent.is_symlink() and not parent.exists():
        # 父目录是损坏的符号链接，删除它
        parent.unlink()
    parent.mkdir(parents=True, exist_ok=True)
    # 如果解析后 dst 等于 src，创建 symlink 会变成自引用（循环）
    # 例如：当 ~/.claude/skills 是 repo/skills 的 symlink 时，
    # ~/.claude/skills/foo -> repo/skills/foo 实际指向自身
    try:
        if src.resolve() == (dst.parent.resolve() / dst.name):
            return
    except (OSError, FileNotFoundError):
        # 解析失败时继续执行
        pass
    remove_existing(dst)
    dst.symlink_to(src)


def ensure_parent_dirs(targets: InstallTargets) -> None:
    for directory in (
        targets.agents_skills_dir,
        targets.claude_skills_dir,
        targets.kimi_agent_dir.parent,
        targets.ks_path.parent,
        targets.manifest_path.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def manifest_payload(
    repo_root: Path,
    targets: InstallTargets,
    skills: Iterable[str],
    installed_at: str | None = None,
    mcp_servers: list[str] | None = None,
) -> dict:
    timestamp = now_iso()
    return {
        "repo_root": str(repo_root),
        "installed_at": installed_at or timestamp,
        "updated_at": timestamp,
        "targets": {
            "agents_skills_dir": str(targets.agents_skills_dir),
            "claude_skills_dir": str(targets.claude_skills_dir),
            "kimi_agent_dir": str(targets.kimi_agent_dir),
            "ks_path": str(targets.ks_path),
        },
        "skills": list(skills),
        "mcp_servers": list(mcp_servers) if mcp_servers is not None else [],
    }


def load_manifest(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(
    path: Path,
    repo_root: Path,
    targets: InstallTargets,
    skills: Iterable[str],
    installed_at: str | None = None,
    mcp_servers: list[str] | None = None,
) -> None:
    payload = manifest_payload(
        repo_root,
        targets,
        skills,
        installed_at=installed_at,
        mcp_servers=mcp_servers,
    )
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def install_skill_links(
    repo_root: Path, targets: InstallTargets, skills: Iterable[str]
) -> None:
    for skill in skills:
        src = repo_root / "skills" / skill
        force_symlink(src, targets.agents_skills_dir / skill)
        force_symlink(src, targets.claude_skills_dir / skill)


def install_kimi_agent_and_ks(repo_root: Path, targets: InstallTargets) -> None:
    force_symlink(repo_root / "kimi/agents/superpower", targets.kimi_agent_dir)
    force_symlink(repo_root / "ks", targets.ks_path)


def command_install(repo_root: Path, home: Path, stdout: TextIO = sys.stdout) -> int:
    targets = build_targets(home)
    ensure_parent_dirs(targets)
    skills = discover_skills(repo_root)
    install_skill_links(repo_root, targets, skills)
    install_kimi_agent_and_ks(repo_root, targets)
    mcp_installed, mcp_skipped = merge_mcp_config(home, repo_root)
    installed_at = None
    manifest_path = build_targets(home).manifest_path
    existing = load_manifest(manifest_path)
    if existing:
        installed_at = existing.get("installed_at")
    write_manifest(
        manifest_path,
        repo_root,
        targets,
        skills,
        installed_at=installed_at,
        mcp_servers=mcp_installed,
    )
    print(f"installed {len(skills)} skills", file=stdout)
    print("mcp_servers=" + ",".join(mcp_installed), file=stdout)
    if mcp_skipped:
        print(f"mcp_skipped=" + ",".join(mcp_skipped), file=stdout)
        print(f"warning: ZAI_API_KEY not set; {len(mcp_skipped)} MCP servers skipped", file=stdout)
        print("hint: set ZAI_API_KEY environment variable or add to ~/.claude.json", file=stdout)
    return 0


def command_update(repo_root: Path, home: Path, stdout: TextIO = sys.stdout) -> int:
    targets = build_targets(home)
    manifest_path = build_targets(home).manifest_path
    manifest = load_manifest(manifest_path)
    if manifest is None:
        print("manifest missing; running install", file=stdout)
        return command_install(repo_root, home, stdout=stdout)

    ensure_parent_dirs(targets)
    skills = discover_skills(repo_root)
    install_skill_links(repo_root, targets, skills)
    install_kimi_agent_and_ks(repo_root, targets)
    mcp_installed, mcp_skipped = merge_mcp_config(home, repo_root)
    write_manifest(
        manifest_path,
        repo_root,
        targets,
        skills,
        installed_at=manifest.get("installed_at"),
        mcp_servers=mcp_installed,
    )
    print(f"updated {len(skills)} skills", file=stdout)
    print("mcp_servers=" + ",".join(mcp_installed), file=stdout)
    if mcp_skipped:
        print(f"mcp_skipped=" + ",".join(mcp_skipped), file=stdout)
        print(f"warning: ZAI_API_KEY not set; {len(mcp_skipped)} MCP servers skipped", file=stdout)
        print("hint: set ZAI_API_KEY environment variable or add to ~/.claude.json", file=stdout)
    return 0


def collect_status(repo_root: Path, home: Path) -> tuple[dict | None, dict]:
    targets = build_targets(home)
    manifest_path = build_targets(home).manifest_path
    manifest = load_manifest(manifest_path)
    current_skills = discover_skills(repo_root)
    state: dict[str, list[str]] = {
        "installed": [],
        "missing": [],
        "drifted": [],
        "untracked_new_skills": [],
    }
    if manifest is None:
        state["untracked_new_skills"] = current_skills
        return None, state

    managed = manifest.get("skills", [])
    for skill in managed:
        expected_src = repo_root / "skills" / skill
        for base_dir in (targets.agents_skills_dir, targets.claude_skills_dir):
            dst = base_dir / skill
            if not dst.exists() and not dst.is_symlink():
                if skill not in state["missing"]:
                    state["missing"].append(skill)
            elif not dst.is_symlink() or dst.resolve() != expected_src.resolve():
                if skill not in state["drifted"]:
                    state["drifted"].append(skill)
            else:
                if skill not in state["installed"]:
                    state["installed"].append(skill)

    managed_set = set(managed)
    for skill in current_skills:
        if skill not in managed_set:
            state["untracked_new_skills"].append(skill)

    return manifest, state


def command_status(repo_root: Path, home: Path, stdout: TextIO = sys.stdout) -> int:
    manifest, state = collect_status(repo_root, home)
    if manifest is None:
        print("state=unmanaged", file=stdout)
        if state["untracked_new_skills"]:
            print(
                "untracked_new_skills=" + ",".join(state["untracked_new_skills"]),
                file=stdout,
            )
        return 0

    installed_count = len(state["installed"])
    print(f"installed={installed_count}", file=stdout)

    for key in ("missing", "drifted", "untracked_new_skills"):
        values = state[key]
        if values:
            print(f"{key}=" + ",".join(values), file=stdout)
        else:
            print(f"{key}=", file=stdout)

    mcp_status = collect_mcp_status(home, repo_root)
    print("mcp_configured=" + ",".join(mcp_status["configured"]), file=stdout)
    print("mcp_missing=" + ",".join(mcp_status["missing"]), file=stdout)
    return 0


def command_uninstall(
    repo_root: Path,
    home: Path,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    targets = build_targets(home)
    manifest_path = build_targets(home).manifest_path
    manifest = load_manifest(manifest_path)
    if manifest is None:
        print("manifest missing; refusing uninstall", file=stderr)
        return 1

    for skill in manifest.get("skills", []):
        remove_existing(targets.agents_skills_dir / skill)
        remove_existing(targets.claude_skills_dir / skill)
    remove_existing(targets.kimi_agent_dir)
    remove_existing(targets.ks_path)
    managed_mcp_names = manifest.get("mcp_servers", [])
    if managed_mcp_names:
        remove_managed_mcps(home, managed_mcp_names)
    remove_existing(targets.manifest_path)
    print("uninstalled managed entries", file=stdout)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manage coding-everything skill installation"
    )
    parser.add_argument("command", choices=("install", "update", "uninstall", "status"))
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

    if args.command == "install":
        return command_install(resolved_repo_root, resolved_home, stdout=stdout)
    if args.command == "update":
        return command_update(resolved_repo_root, resolved_home, stdout=stdout)
    if args.command == "uninstall":
        return command_uninstall(
            resolved_repo_root, resolved_home, stdout=stdout, stderr=stderr
        )
    return command_status(resolved_repo_root, resolved_home, stdout=stdout)


def _ce_manifest_path(home: Path) -> Path:
    """返回 ~/.ce/install-manifest.json 路径。"""
    return home / CE_MANIFEST


def _legacy_manifest_path(home: Path) -> Path:
    """返回旧版 manifest 路径。"""
    return home / MANIFEST_RELATIVE_PATH


def _migrate_v1_manifest(home: Path) -> None:
    """如果旧路径存在 v1 manifest（无 version 字段），迁移为 v2 到新路径并删除旧文件。"""
    legacy_path = _legacy_manifest_path(home)
    if not legacy_path.exists():
        return

    old_data = load_manifest(legacy_path)
    if old_data is None:
        return

    # 已经是 v2 格式则跳过
    if old_data.get("version") == 2:
        return

    # 迁移：将 v1 扁平结构包装为 v2 分组结构
    skills = old_data.get("skills", [])
    targets_map = old_data.get("targets", {})
    target_paths = list(targets_map.values()) if targets_map else []

    v2_groups: dict[str, dict] = {
        "global": {
            "installed_at": old_data.get("installed_at", now_iso()),
            "updated_at": now_iso(),
            "targets": target_paths,
            "skills": skills,
            "mcp_servers": old_data.get("mcp_servers", []),
            "repo_root": old_data.get("repo_root"),
        }
    }

    v2_data = {
        "version": 2,
        "groups": v2_groups,
    }

    new_path = _ce_manifest_path(home)
    new_path.parent.mkdir(parents=True, exist_ok=True)
    new_path.write_text(
        json.dumps(v2_data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    legacy_path.unlink()


def load_v2_manifest(home: Path) -> dict | None:
    """从 ~/.ce/install-manifest.json 加载 v2 manifest。"""
    path = _ce_manifest_path(home)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_v2_manifest(home: Path, data: dict) -> None:
    """写入 ~/.ce/install-manifest.json。"""
    path = _ce_manifest_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _install_group(
    repo_root: Path,
    home: Path,
    group: SkillGroup,
    manifest_data: dict,
) -> dict:
    """安装单个组的 skills 到该组的 targets。

    如果组名是 "global"，额外处理 kimi agent、ks、MCP。
    返回更新后的 manifest_data。
    """
    # 为每个 target 创建目录并 symlink 每个 skill
    for skill_name in group.skills:
        src = repo_root / "skills" / skill_name
        for target in group.targets:
            force_symlink(src, target / skill_name)

    timestamp = now_iso()
    mcp_servers: list[str] = []

    # global 组额外处理 kimi agent、ks、MCP
    if group.name == "global":
        targets = build_targets(home)
        ensure_parent_dirs(targets)
        install_kimi_agent_and_ks(repo_root, targets)
        mcp_installed, mcp_skipped = merge_mcp_config(home, repo_root)
        mcp_servers = mcp_installed

    group_record = manifest_data.get("groups", {}).get(group.name, {})
    manifest_data.setdefault("groups", {})[group.name] = {
        "installed_at": group_record.get("installed_at", timestamp),
        "updated_at": timestamp,
        "targets": [str(t) for t in group.targets],
        "skills": list(group.skills),
        "mcp_servers": mcp_servers,
        "repo_root": str(repo_root),
    }

    return manifest_data


def command_install_grouped(
    repo_root: Path,
    home: Path,
    config_path: Path,
    *,
    group: str | None = None,
    stdout: TextIO = sys.stdout,
) -> int:
    """分组安装入口。如果配置为空，退化为 command_install。"""
    from install_skills.config import load_install_config

    groups = load_install_config(config_path)
    if not groups:
        return command_install(repo_root, home, stdout=stdout)

    # 迁移 v1 manifest
    _migrate_v1_manifest(home)

    manifest_data: dict = load_v2_manifest(home) or {"version": 2, "groups": {}}
    manifest_data["version"] = 2

    groups_to_install = {group: groups[group]} if group else groups

    for group_name, grp in groups_to_install.items():
        manifest_data = _install_group(repo_root, home, grp, manifest_data)
        skill_count = len(grp.skills)
        print(f"[{group_name}] installed {skill_count} skills", file=stdout)

        # global 组额外显示 MCP 安装情况
        if group_name == "global":
            group_record = manifest_data.get("groups", {}).get(group_name, {})
            mcp_servers = group_record.get("mcp_servers", [])
            if mcp_servers:
                print(f"[{group_name}] mcp installed: {','.join(mcp_servers)}", file=stdout)
            else:
                print(f"[{group_name}] mcp installed: (none)", file=stdout)
            # 检查是否有因缺少 ZAI_API_KEY 而跳过的 MCP
            template = load_mcp_template(repo_root)
            all_zai_mcps = {
                name for name, def_ in template["mcpServers"].items()
                if PLACEHOLDER_ZAI_API_KEY in json.dumps(def_)
            }
            installed_set = set(mcp_servers)
            skipped_mcps = sorted(all_zai_mcps - installed_set)
            if skipped_mcps:
                print(f"[{group_name}] mcp skipped: {','.join(skipped_mcps)}", file=stdout)
                print(f"[{group_name}] warning: ZAI_API_KEY not set; {len(skipped_mcps)} MCP servers skipped", file=stdout)
                print(f"[{group_name}] hint: set ZAI_API_KEY environment variable or add to ~/.claude.json", file=stdout)

    write_v2_manifest(home, manifest_data)
    return 0


def command_uninstall_grouped(
    repo_root: Path,
    home: Path,
    config_path: Path,
    *,
    group: str | None = None,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    """分组卸载：从 v2 manifest 读取，如果指定 group 只卸载该组。"""
    manifest_data = load_v2_manifest(home)
    if manifest_data is None:
        print("manifest missing; refusing uninstall", file=stderr)
        return 1

    all_groups = manifest_data.get("groups", {})
    if not all_groups:
        print("no groups in manifest", file=stderr)
        return 1

    from install_skills.config import load_install_config

    load_install_config(config_path)  # 验证配置可用
    groups_to_uninstall = {group: all_groups[group]} if group else dict(all_groups)

    for group_name, group_record in groups_to_uninstall.items():
        if group_name not in all_groups:
            print(f"[{group_name}] not found in manifest", file=stderr)
            continue

        targets = [Path(t) for t in group_record.get("targets", [])]
        for skill_name in group_record.get("skills", []):
            for target in targets:
                remove_existing(target / skill_name)

        # global 组额外清理 kimi/ks/MCP
        if group_name == "global":
            targets_obj = build_targets(home)
            remove_existing(targets_obj.kimi_agent_dir)
            remove_existing(targets_obj.ks_path)
            managed_mcp = group_record.get("mcp_servers", [])
            if managed_mcp:
                remove_managed_mcps(home, managed_mcp)

        print(f"[{group_name}] uninstalled", file=stdout)
        del manifest_data["groups"][group_name]

    # 如果还有组剩余，更新 manifest；否则删除
    if manifest_data["groups"]:
        write_v2_manifest(home, manifest_data)
    else:
        manifest_path = _ce_manifest_path(home)
        remove_existing(manifest_path)

    return 0


def command_status_grouped(
    repo_root: Path,
    home: Path,
    config_path: Path,
    *,
    group: str | None = None,
    stdout: TextIO = sys.stdout,
) -> int:
    """分组状态：检查每个 skill 在每个 target 的 symlink 状态。"""
    from install_skills.config import load_install_config

    groups = load_install_config(config_path)
    if not groups:
        return command_status(repo_root, home, stdout=stdout)

    load_v2_manifest(home)  # 预加载（用于后续状态对比）

    groups_to_check = {group: groups[group]} if group else groups

    for group_name, grp in groups_to_check.items():
        installed_count = 0
        missing_count = 0
        drifted_count = 0

        for skill_name in grp.skills:
            src = repo_root / "skills" / skill_name
            for target in grp.targets:
                dst = target / skill_name
                if not dst.exists() and not dst.is_symlink():
                    missing_count += 1
                elif not dst.is_symlink() or dst.resolve() != src.resolve():
                    drifted_count += 1
                else:
                    installed_count += 1

        print(
            f"[{group_name}] installed={installed_count} missing={missing_count} drifted={drifted_count}",
            file=stdout,
        )

        # global 组额外显示 MCP 状态
        if group_name == "global":
            mcp_status = collect_mcp_status(home, repo_root)
            if mcp_status["configured"]:
                print(
                    "  mcp_configured=" + ",".join(mcp_status["configured"]),
                    file=stdout,
                )
            if mcp_status["missing"]:
                print(
                    "  mcp_missing=" + ",".join(mcp_status["missing"]),
                    file=stdout,
                )
        else:
            # 非 global 组显示 targets 路径
            for t in grp.targets:
                # 显示相对于 home 的路径
                try:
                    rel = t.relative_to(home)
                    print(f"  target=~/{rel}", file=stdout)
                except ValueError:
                    print(f"  target={t}", file=stdout)

    return 0


def command_doctor(
    repo_root: Path,
    home: Path,
    config_path: Path,
    *,
    stdout: TextIO = sys.stdout,
) -> int:
    """诊断安装环境问题并尝试修复。"""
    from install_skills.config import load_install_config

    groups = load_install_config(config_path)
    issues_found = []
    issues_fixed = []

    def check_path(path: Path, description: str) -> None:
        """检查路径是否存在问题。"""
        if path.is_symlink() and not path.exists():
            issues_found.append(f"{description}: {path} (损坏的符号链接 -> {path.readlink()})")
            try:
                path.unlink()
                issues_fixed.append(f"{description}: 已删除损坏的符号链接")
            except OSError as e:
                issues_found.append(f"{description}: 无法删除 - {e}")
        elif path.is_symlink() and path.is_dir():
            # 目录是符号链接（可能是用户手动设置的）
            issues_found.append(f"{description}: {path} 是符号链接而非目录")

    # 检查 global 组的 targets
    if groups and "global" in groups:
        for target_str in groups["global"].targets:
            target = Path(target_str).expanduser()
            check_path(target, f"global target '{target}'")

    # 检查 obsidian 组的 targets
    if groups and "obsidian" in groups:
        for target_str in groups["obsidian"].targets:
            target = Path(target_str).expanduser()
            # 检查父目录是否存在损坏链接
            check_path(target.parent, f"obsidian parent '{target.parent}'")
            check_path(target, f"obsidian target '{target}'")

    # 输出结果
    if not issues_found:
        print("✓ 未发现问题，环境健康", file=stdout)
        return 0

    print(f"发现 {len(issues_found)} 个问题:", file=stdout)
    for issue in issues_found:
        print(f"  • {issue}", file=stdout)

    if issues_fixed:
        print(f"\n已自动修复 {len(issues_fixed)} 个问题:", file=stdout)
        for fix in issues_fixed:
            print(f"  ✓ {fix}", file=stdout)

    remaining = len(issues_found) - len(issues_fixed)
    if remaining > 0:
        print(f"\n还有 {remaining} 个问题需要手动修复", file=stdout)
        return 1

    print("\n✓ 所有问题已修复，可以运行 'ce install'", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
