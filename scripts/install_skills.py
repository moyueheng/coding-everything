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


MANIFEST_RELATIVE_PATH = Path(".local/share/coding-everything/install-manifest.json")
AGENTS_SKILLS_RELATIVE_DIR = Path(".agents/skills")
CLAUDE_SKILLS_RELATIVE_DIR = Path(".claude/skills")
KIMI_AGENT_RELATIVE_PATH = Path(".kimi/agents/superpower")
KS_RELATIVE_PATH = Path(".local/bin/ks")


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


def merge_mcp_config(home: Path, repo_root: Path) -> list[str]:
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

    for name, server_def in template["mcpServers"].items():
        clean_def = _deep_copy_without_internal_keys(server_def)

        needs_zai_key = PLACEHOLDER_ZAI_API_KEY in json.dumps(clean_def)
        if needs_zai_key and zai_api_key is None:
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

    return sorted(installed)


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
    dst.parent.mkdir(parents=True, exist_ok=True)
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


def write_manifest(
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
    targets.manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def load_manifest(targets: InstallTargets) -> dict | None:
    if not targets.manifest_path.exists():
        return None
    return json.loads(targets.manifest_path.read_text(encoding="utf-8"))


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
    mcp_installed = merge_mcp_config(home, repo_root)
    installed_at = None
    existing = load_manifest(targets)
    if existing:
        installed_at = existing.get("installed_at")
    write_manifest(
        repo_root,
        targets,
        skills,
        installed_at=installed_at,
        mcp_servers=mcp_installed,
    )
    print(f"installed {len(skills)} skills", file=stdout)
    print("mcp_servers=" + ",".join(mcp_installed), file=stdout)
    return 0


def command_update(repo_root: Path, home: Path, stdout: TextIO = sys.stdout) -> int:
    targets = build_targets(home)
    manifest = load_manifest(targets)
    if manifest is None:
        print("manifest missing; running install", file=stdout)
        return command_install(repo_root, home, stdout=stdout)

    ensure_parent_dirs(targets)
    skills = discover_skills(repo_root)
    install_skill_links(repo_root, targets, skills)
    install_kimi_agent_and_ks(repo_root, targets)
    mcp_installed = merge_mcp_config(home, repo_root)
    write_manifest(
        repo_root,
        targets,
        skills,
        installed_at=manifest.get("installed_at"),
        mcp_servers=mcp_installed,
    )
    print(f"updated {len(skills)} skills", file=stdout)
    print("mcp_servers=" + ",".join(mcp_installed), file=stdout)
    return 0


def collect_status(repo_root: Path, home: Path) -> tuple[dict | None, dict]:
    targets = build_targets(home)
    manifest = load_manifest(targets)
    current_skills = discover_skills(repo_root)
    state = {
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
                state["missing"].append(f"{dst}")
            elif not dst.is_symlink() or dst.resolve() != expected_src.resolve():
                state["drifted"].append(f"{dst}")
            else:
                state["installed"].append(f"{dst}")

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

    for key in ("installed", "missing", "drifted", "untracked_new_skills"):
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
    manifest = load_manifest(targets)
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


if __name__ == "__main__":
    raise SystemExit(main())
