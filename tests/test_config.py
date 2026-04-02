# tests/test_config.py
import pytest
import tempfile
from pathlib import Path
from install_skills.config import (
    load_user_config,
    save_user_config,
    get_default_config_path,
    expand_path,
)
from install_skills.models import UserConfig, GroupConfig


def test_expand_path():
    """路径展开应正确处理 ~"""
    assert expand_path("~/test").name == "test"


def test_load_user_config_not_exists():
    """配置不存在时返回 None"""
    result = load_user_config(Path("/nonexistent/config.yaml"))
    assert result is None


def test_save_and_load_user_config():
    """保存后应能正确加载"""
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "config.yaml"
        config = UserConfig(
            version=2,
            repo_root=Path("/home/user/repo"),
            groups={
                "global": GroupConfig(
                    name="global",
                    skills=["dev-tdd"],
                    targets=[Path("~/.claude/skills")]
                )
            }
        )
        save_user_config(config_path, config)

        loaded = load_user_config(config_path)
        assert loaded is not None
        assert loaded.version == 2
        assert loaded.repo_root == Path("/home/user/repo")
        assert "global" in loaded.groups
