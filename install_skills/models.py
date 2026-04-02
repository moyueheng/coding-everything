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


@dataclass(frozen=True)
class GroupConfig:
    """用户配置中的分组定义"""

    name: str
    skills: list[str] = field(default_factory=list)
    targets: list[Path] = field(default_factory=list)


@dataclass(frozen=True)
class UserConfig:
    """用户级配置文件 ~/.ce/config.yaml 的内存表示"""

    version: int = 2
    repo_root: Path | None = None
    groups: dict[str, GroupConfig] = field(default_factory=dict)
