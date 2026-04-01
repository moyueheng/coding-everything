from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SkillGroup:
    """YAML 配置中的一个分组。"""

    name: str
    skills: list[str]
    targets: list[Path]


@dataclass(frozen=True)
class GroupManifest:
    """Manifest 中一个组的记录。"""

    installed_at: str
    updated_at: str
    targets: list[Path]
    skills: list[str]
    mcp_servers: list[str] = field(default_factory=list)
    repo_root: Path | None = None


@dataclass(frozen=True)
class ManifestV2:
    """v2 manifest 结构。"""

    groups: dict[str, GroupManifest]
