# tests/test_installer_v2.py
import pytest
import tempfile
from pathlib import Path
from install_skills.installer import command_install_from_config
from install_skills.config import save_user_config
from install_skills.models import UserConfig, GroupConfig


def test_install_reads_from_user_config():
    """install 应从 ~/.ce/config.yaml 读取配置"""
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        repo_root = Path(tmp) / "repo"
        repo_root.mkdir()

        # 创建 skills 目录
        skills_dir = repo_root / "skills"
        skills_dir.mkdir()
        (skills_dir / "test-skill").mkdir()
        (skills_dir / "test-skill" / "SKILL.md").write_text("test")

        # 创建用户配置
        config = UserConfig(
            version=2,
            repo_root=repo_root,
            groups={
                "test": GroupConfig(
                    name="test",
                    skills=["test-skill"],
                    targets=[home / ".claude/skills"]
                )
            }
        )
        save_user_config(home / ".ce" / "config.yaml", config)

        # 运行安装
        result = command_install_from_config(
            repo_root, home
        )

        assert result == 0
        # 验证 symlink 已创建
        assert (home / ".claude/skills" / "test-skill").is_symlink()
