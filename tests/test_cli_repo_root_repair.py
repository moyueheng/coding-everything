from __future__ import annotations

import io
import tempfile
from pathlib import Path

from install_skills.cli import _repair_config_repo_root_if_stale
from install_skills.config import load_user_config, save_user_config
from install_skills.models import GroupConfig, UserConfig


def _make_repo_root(path: Path) -> None:
    (path / "skills").mkdir(parents=True)
    (path / "install_skills").mkdir()
    (path / "pyproject.toml").write_text("[project]\nname = \"test\"\n")


def test_repair_config_repo_root_when_configured_path_is_missing():
    """仓库移动后，旧 repo_root 不存在时应自动更新到当前仓库。"""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        home = root / "home"
        repo_root = root / "01-Projects" / "coding-everything"
        stale_root = root / "Projects" / "coding-everything"
        _make_repo_root(repo_root)

        config_path = home / ".ce" / "config.yaml"
        save_user_config(
            config_path,
            UserConfig(
                version=2,
                repo_root=stale_root,
                groups={
                    "global": GroupConfig(
                        name="global",
                        skills=["dev-tdd"],
                        targets=[home / ".agents/skills"],
                    )
                },
            ),
        )

        stdout = io.StringIO()
        _repair_config_repo_root_if_stale(config_path, repo_root, stdout=stdout)

        config = load_user_config(config_path)
        assert config is not None
        assert config.repo_root == repo_root.resolve()
        assert "repo_root moved" in stdout.getvalue()


def test_repair_config_repo_root_keeps_existing_configured_path():
    """旧 repo_root 仍存在时不应静默改写配置。"""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        home = root / "home"
        repo_root = root / "01-Projects" / "coding-everything"
        configured_root = root / "Projects" / "coding-everything"
        _make_repo_root(repo_root)
        _make_repo_root(configured_root)

        config_path = home / ".ce" / "config.yaml"
        save_user_config(
            config_path,
            UserConfig(
                version=2,
                repo_root=configured_root,
                groups={},
            ),
        )

        stdout = io.StringIO()
        _repair_config_repo_root_if_stale(config_path, repo_root, stdout=stdout)

        config = load_user_config(config_path)
        assert config is not None
        assert config.repo_root == configured_root
        assert stdout.getvalue() == ""
