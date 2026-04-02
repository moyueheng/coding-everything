# tests/test_cli_init.py
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from install_skills.cli import command_init
from install_skills.config import load_user_config


def test_init_creates_config():
    """ce init 应创建 ~/.ce/config.yaml"""
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        repo_root = Path(tmp) / "repo"
        repo_root.mkdir()

        # 创建模拟 skills 目录
        skills_dir = repo_root / "skills"
        skills_dir.mkdir()
        (skills_dir / "dev-tdd").mkdir()
        (skills_dir / "dev-tdd" / "SKILL.md").write_text("test")

        # 模拟用户输入：obsidian 路径
        def mock_input(prompt):
            if "Obsidian vault" in prompt:
                return ""  # 跳过 obsidian
            return ""

        result = command_init(
            repo_root,
            home,
            _input_func=mock_input
        )

        assert result == 0
        config_path = home / ".ce" / "config.yaml"
        assert config_path.exists()

        # 验证配置内容
        config = load_user_config(config_path)
        assert config is not None
        assert "global" in config.groups
        assert "dev-tdd" in config.groups["global"].skills
