# tests/test_models.py
import pytest
from pathlib import Path
from install_skills.models import UserConfig, GroupConfig


def test_group_config_creation():
    """GroupConfig 应能正确创建"""
    group = GroupConfig(
        name="global",
        skills=["dev-brainstorming", "dev-tdd"],
        targets=[Path("~/.claude/skills").expanduser()]
    )
    assert group.name == "global"
    assert len(group.skills) == 2


def test_user_config_creation():
    """UserConfig 应包含版本和分组"""
    config = UserConfig(
        version=2,
        repo_root=Path("/home/user/coding-everything"),
        groups={}
    )
    assert config.version == 2
    assert config.repo_root == Path("/home/user/coding-everything")
