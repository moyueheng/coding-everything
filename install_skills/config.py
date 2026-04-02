from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

from install_skills.models import UserConfig, GroupConfig, SkillGroup


CE_DIR = Path(".ce")
CONFIG_FILENAME = "config.yaml"


def expand_path(p: str | Path) -> Path:
    """展开 ~ 为绝对路径。"""
    return Path(p).expanduser()


def get_default_config_path(home: Path | None = None) -> Path:
    """返回默认配置文件路径 ~/.ce/config.yaml"""
    home = home or Path.home()
    return home / CE_DIR / CONFIG_FILENAME


def _group_to_dict(group: GroupConfig) -> dict[str, Any]:
    """将 GroupConfig 转为字典"""
    return {
        "skills": list(group.skills),
        "targets": [str(t) for t in group.targets],
    }


def _group_from_dict(name: str, data: dict[str, Any]) -> GroupConfig:
    """从字典创建 GroupConfig"""
    return GroupConfig(
        name=name,
        skills=list(data.get("skills", [])),
        targets=[expand_path(t) for t in data.get("targets", [])],
    )


def load_user_config(config_path: Path) -> UserConfig | None:
    """从 YAML 加载用户配置。如果不存在返回 None。"""
    if not config_path.exists():
        return None

    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if data is None:
        return None

    groups: dict[str, GroupConfig] = {}
    for name, group_data in data.get("groups", {}).items():
        groups[name] = _group_from_dict(name, group_data)

    repo_root = data.get("repo_root")

    return UserConfig(
        version=data.get("version", 2),
        repo_root=Path(repo_root) if repo_root else None,
        groups=groups,
    )


def save_user_config(config_path: Path, config: UserConfig) -> None:
    """保存用户配置到 YAML。"""
    config_path.parent.mkdir(parents=True, exist_ok=True)

    data: dict[str, Any] = {
        "version": config.version,
    }

    if config.repo_root:
        data["repo_root"] = str(config.repo_root)

    data["groups"] = {
        name: _group_to_dict(group)
        for name, group in config.groups.items()
    }

    config_path.write_text(
        yaml.safe_dump(data, default_flow_style=False, allow_unicode=True),
        encoding="utf-8"
    )


def load_install_config(config_path: Path) -> dict[str, SkillGroup]:
    """【已废弃】保留以兼容旧代码，实际不再使用。"""
    return {}
