from __future__ import annotations

from pathlib import Path

import yaml

from install_skills.models import SkillGroup


def expand_path(p: str) -> Path:
    """展开 ~ 为绝对路径。"""
    return Path(p).expanduser()


def load_install_config(config_path: Path) -> dict[str, SkillGroup]:
    """加载 skills-install.yaml，返回 {name: SkillGroup}。

    如果配置文件不存在返回空 dict（退化模式）。
    """
    if not config_path.is_file():
        return {}

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if raw is None or "groups" not in raw:
        return {}

    result: dict[str, SkillGroup] = {}
    for name, group_data in raw["groups"].items():
        targets = [expand_path(t) for t in group_data.get("targets", [])]
        result[name] = SkillGroup(
            name=name,
            skills=list(group_data.get("skills", [])),
            targets=targets,
        )
    return result
