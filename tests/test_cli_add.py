# tests/test_cli_add.py
import pytest
import tempfile
from pathlib import Path
from install_skills.cli import command_add_skill, command_add_target
from install_skills.config import load_user_config, save_user_config
from install_skills.models import UserConfig, GroupConfig


def test_add_skill_to_group():
    """add-skill 应添加 skill 到指定组"""
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)

        # 创建初始配置
        config = UserConfig(
            version=2,
            repo_root=Path("/repo"),
            groups={
                "global": GroupConfig(
                    name="global",
                    skills=["dev-tdd"],
                    targets=[home / ".claude/skills"]
                )
            }
        )
        save_user_config(home / ".ce" / "config.yaml", config)

        # 添加新 skill
        result = command_add_skill("dev-debugging", "global", home)

        assert result == 0

        # 验证配置已更新
        loaded = load_user_config(home / ".ce" / "config.yaml")
        assert "dev-debugging" in loaded.groups["global"].skills
        assert "dev-tdd" in loaded.groups["global"].skills  # 原有 skill 保留


def test_add_target_to_group():
    """add-target 应添加 target 到指定组"""
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)

        # 创建初始配置
        config = UserConfig(
            version=2,
            repo_root=Path("/repo"),
            groups={
                "global": GroupConfig(
                    name="global",
                    skills=["dev-tdd"],
                    targets=[home / ".claude/skills"]
                )
            }
        )
        save_user_config(home / ".ce" / "config.yaml", config)

        # 添加新 target
        new_target = home / ".agents/skills"
        result = command_add_target(str(new_target), "global", home)

        assert result == 0

        # 验证配置已更新
        loaded = load_user_config(home / ".ce" / "config.yaml")
        assert new_target in loaded.groups["global"].targets
