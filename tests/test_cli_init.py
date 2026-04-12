# tests/test_cli_init.py
import tempfile
from pathlib import Path
from install_skills.cli import command_init
from install_skills.config import load_user_config


def _make_skill(skills_dir: Path, name: str) -> None:
    d = skills_dir / name
    d.mkdir()
    (d / "SKILL.md").write_text("test")


def test_init_creates_config():
    """ce init 应创建 ~/.ce/config.yaml"""
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        repo_root = Path(tmp) / "repo"
        repo_root.mkdir()

        skills_dir = repo_root / "skills"
        skills_dir.mkdir()
        _make_skill(skills_dir, "dev-tdd")

        def mock_input(prompt):
            if "Obsidian vault" in prompt:
                return ""
            return ""

        result = command_init(repo_root, home, _input_func=mock_input)

        assert result == 0
        config_path = home / ".ce" / "config.yaml"
        assert config_path.exists()

        config = load_user_config(config_path)
        assert config is not None
        assert "global" in config.groups
        assert "dev-tdd" in config.groups["global"].skills


def test_init_obsidian_group_classification():
    """life-ask 和 life-parse-knowledge 应归入 obsidian 组而非 global 组"""
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        repo_root = Path(tmp) / "repo"
        repo_root.mkdir()

        # 创建 obsidian vault 目录
        vault = home / "MyVault"
        vault.mkdir()
        (vault / ".obsidian").mkdir()

        skills_dir = repo_root / "skills"
        skills_dir.mkdir()
        _make_skill(skills_dir, "dev-tdd")
        _make_skill(skills_dir, "obsidian-markdown")
        _make_skill(skills_dir, "life-ask")
        _make_skill(skills_dir, "life-parse-knowledge")
        _make_skill(skills_dir, "life-ai-newsletters")

        answers = iter([str(vault)])

        def mock_input(prompt: str) -> str:
            return next(answers)

        result = command_init(repo_root, home, _input_func=mock_input)

        assert result == 0
        config = load_user_config(home / ".ce" / "config.yaml")
        assert config is not None
        assert "obsidian" in config.groups

        obsidian_skills = config.groups["obsidian"].skills
        global_skills = config.groups["global"].skills

        # life-ask 和 life-parse-knowledge 应在 obsidian 组
        assert "life-ask" in obsidian_skills
        assert "life-parse-knowledge" in obsidian_skills
        assert "life-ai-newsletters" in obsidian_skills
        assert "obsidian-markdown" in obsidian_skills

        # 不应在 global 组
        assert "life-ask" not in global_skills
        assert "life-parse-knowledge" not in global_skills
        assert "dev-tdd" in global_skills
