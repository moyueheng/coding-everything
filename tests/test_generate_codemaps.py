"""Tests for scripts/generate_codemaps.py — codemap 生成器测试套件。"""

from __future__ import annotations

import textwrap
from pathlib import Path

from generate_codemaps import (
    AreaInfo,
    SkillMeta,
    SubmoduleEntry,
    classify_file,
    compute_diff_ratio,
    count_lines,
    estimate_tokens,
    extract_skill_metas,
    generate_cli_codemap,
    generate_generic_codemap,
    generate_index,
    generate_skills_codemap,
    parse_skill_frontmatter,
    parse_submodules,
    walk_files,
)


# ---------------------------------------------------------------------------
# walk_files
# ---------------------------------------------------------------------------


class TestWalkFiles:
    """walk_files() 应正确遍历目录并跳过噪音目录。"""

    def test_empty_dir(self, tmp_path: Path) -> None:
        assert walk_files(tmp_path) == []

    def test_finds_regular_files(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("pass")
        (tmp_path / "b.md").write_text("# hi")
        result = walk_files(tmp_path)
        assert len(result) == 2
        names = {p.name for p in result}
        assert names == {"a.py", "b.md"}

    def test_recursive(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "c.py").write_text("pass")
        result = walk_files(tmp_path)
        assert len(result) == 1
        assert result[0].name == "c.py"

    def test_skips_noise_dirs(self, tmp_path: Path) -> None:
        for noise in (".git", "node_modules", "__pycache__", ".venv", "dist"):
            (tmp_path / noise).mkdir()
            (tmp_path / noise / "x.py").write_text("pass")
        (tmp_path / "keep.py").write_text("pass")
        result = walk_files(tmp_path)
        assert len(result) == 1
        assert result[0].name == "keep.py"

    def test_skips_upstream_dir(self, tmp_path: Path) -> None:
        (tmp_path / "upstream").mkdir()
        (tmp_path / "upstream" / "foo.py").write_text("pass")
        (tmp_path / "real.py").write_text("pass")
        result = walk_files(tmp_path)
        assert len(result) == 1
        assert result[0].name == "real.py"


# ---------------------------------------------------------------------------
# classify_file
# ---------------------------------------------------------------------------


class TestClassifyFile:
    """classify_file() 根据相对路径前缀将文件映射到区域键。"""

    def test_skills_dir(self) -> None:
        assert classify_file(Path("skills/dev-tdd/SKILL.md")) == "skills"

    def test_install_skills_dir(self) -> None:
        assert classify_file(Path("install_skills/cli.py")) == "cli"

    def test_tests_dir(self) -> None:
        assert classify_file(Path("tests/test_foo.py")) == "cli"

    def test_pyproject(self) -> None:
        assert classify_file(Path("pyproject.toml")) == "cli"

    def test_mcp_configs(self) -> None:
        assert classify_file(Path("mcp-configs/required.json")) == "cli"

    def test_kimi_dir(self) -> None:
        assert classify_file(Path("kimi/agents/superpower/agent.yaml")) == "agents"

    def test_agents_skills_dir(self) -> None:
        assert classify_file(Path(".agents/skills/setup/SKILL.md")) == "agents"

    def test_opencode_dir(self) -> None:
        assert classify_file(Path("opencode/skills/foo.md")) == "agents"

    def test_docs_dir(self) -> None:
        assert classify_file(Path("docs/ROADMAP.md")) == "docs"

    def test_root_claude_md(self) -> None:
        assert classify_file(Path("CLAUDE.md")) == "docs"

    def test_root_agents_md(self) -> None:
        assert classify_file(Path("AGENTS.md")) == "docs"

    def test_root_readme(self) -> None:
        assert classify_file(Path("README.md")) == "docs"

    def test_scripts_dir(self) -> None:
        assert classify_file(Path("scripts/sync.sh")) == "scripts"

    def test_agents_subdir_scripts(self) -> None:
        assert classify_file(Path(".agents/skills/foo/scripts/bar.py")) == "scripts"

    def test_unknown_returns_none(self) -> None:
        assert classify_file(Path("random.bin")) is None

    def test_upstream_excluded(self) -> None:
        assert classify_file(Path("upstream/foo/bar.py")) is None


# ---------------------------------------------------------------------------
# parse_skill_frontmatter
# ---------------------------------------------------------------------------


class TestParseSkillFrontmatter:
    """parse_skill_frontmatter() 从 SKILL.md 内容提取 name 和 description。"""

    def test_standard_frontmatter(self) -> None:
        content = textwrap.dedent("""\
            ---
            name: dev-tdd
            description: 测试驱动开发
            ---
            # 正文
        """)
        meta = parse_skill_frontmatter(content)
        assert meta is not None
        assert meta.name == "dev-tdd"
        assert meta.description == "测试驱动开发"

    def test_extra_fields(self) -> None:
        content = textwrap.dedent("""\
            ---
            name: agent-browser
            description: 浏览器自动化
            allowed-tools: Bash(foo)
            ---
            # 正文
        """)
        meta = parse_skill_frontmatter(content)
        assert meta is not None
        assert meta.name == "agent-browser"
        assert meta.description == "浏览器自动化"

    def test_no_frontmatter(self) -> None:
        meta = parse_skill_frontmatter("# No frontmatter\nJust text")
        assert meta is None

    def test_empty_frontmatter(self) -> None:
        meta = parse_skill_frontmatter("---\n---\n# Empty")
        assert meta is None

    def test_missing_name(self) -> None:
        content = "---\ndescription: only desc\n---\n# Text"
        meta = parse_skill_frontmatter(content)
        assert meta is None

    def test_multiline_description(self) -> None:
        content = textwrap.dedent("""\
            ---
            name: foo
            description: 这是一段很长的描述
              跨越多行
            ---
        """)
        meta = parse_skill_frontmatter(content)
        assert meta is not None
        assert "跨越多行" in meta.description


# ---------------------------------------------------------------------------
# extract_skill_metas
# ---------------------------------------------------------------------------


class TestExtractSkillMetas:
    """extract_skill_metas() 从 skills/ 目录收集所有 SKILL.md 元数据。"""

    def test_extracts_all_skills(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        for name in ("dev-tdd", "dev-debug", "work-research"):
            skill_dir = skills_dir / name
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: desc for {name}\n---\n# {name}"
            )
        metas = extract_skill_metas(skills_dir)
        assert len(metas) == 3
        names = {m.name for m in metas}
        assert names == {"dev-tdd", "dev-debug", "work-research"}

    def test_skips_dirs_without_skill_md(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        (skills_dir / "no-skill").mkdir(parents=True)
        metas = extract_skill_metas(skills_dir)
        assert metas == []

    def test_handles_broken_frontmatter(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skill_dir = skills_dir / "broken"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("No frontmatter here")
        metas = extract_skill_metas(skills_dir)
        assert metas == []


# ---------------------------------------------------------------------------
# parse_submodules
# ---------------------------------------------------------------------------


class TestParseSubmodules:
    """parse_submodules() 从 .gitmodules 文件提取 submodule 列表。"""

    def test_parses_gitmodules(self, tmp_path: Path) -> None:
        content = textwrap.dedent("""\
            [submodule "upstream/superpowers"]
            \tpath = upstream/superpowers
            \turl = https://github.com/obra/superpowers.git
            \tbranch = main
            [submodule "upstream/everything-claude-code"]
            \tpath = upstream/everything-claude-code
            \turl = https://github.com/affaan-m/everything-claude-code.git
            \tbranch = main
        """)
        gitmodules = tmp_path / ".gitmodules"
        gitmodules.write_text(content)
        entries = parse_submodules(gitmodules)
        assert len(entries) == 2
        assert entries[0].name == "upstream/superpowers"
        assert entries[0].url == "https://github.com/obra/superpowers.git"
        assert entries[1].name == "upstream/everything-claude-code"

    def test_empty_file(self, tmp_path: Path) -> None:
        gitmodules = tmp_path / ".gitmodules"
        gitmodules.write_text("")
        entries = parse_submodules(gitmodules)
        assert entries == []

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        entries = parse_submodules(tmp_path / "nonexistent")
        assert entries == []


# ---------------------------------------------------------------------------
# estimate_tokens / count_lines
# ---------------------------------------------------------------------------


class TestEstimateTokens:
    """estimate_tokens() 粗略估算文本的 token 数。"""

    def test_empty_string(self) -> None:
        assert estimate_tokens("") == 0

    def test_short_text(self) -> None:
        # 中文字符每个约 1 token，英文约 4 字符 1 token
        text = "hello world"
        tokens = estimate_tokens(text)
        assert tokens > 0

    def test_chinese_text(self) -> None:
        text = "这是一段中文测试"
        tokens = estimate_tokens(text)
        assert tokens > 0


class TestCountLines:
    """count_lines() 统计文件行数。"""

    def test_normal_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.py"
        f.write_text("line1\nline2\nline3\n")
        assert count_lines(f) == 3  # splitlines() returns 3 lines

    def test_empty_file(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.py"
        f.write_text("")
        assert count_lines(f) == 1  # split("") gives [""]

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        assert count_lines(tmp_path / "nope") == 0


# ---------------------------------------------------------------------------
# compute_diff_ratio
# ---------------------------------------------------------------------------


class TestComputeDiffRatio:
    """compute_diff_ratio() 计算两个文本的差异比例。"""

    def test_identical_texts(self) -> None:
        assert compute_diff_ratio("hello\nworld\n", "hello\nworld\n") == 0.0

    def test_completely_different(self) -> None:
        assert compute_diff_ratio("aaa\n", "bbb\n") > 0.0

    def test_partially_different(self) -> None:
        old = "line1\nline2\nline3\nline4\n"
        new = "line1\nchanged\nline3\nline4\n"
        ratio = compute_diff_ratio(old, new)
        assert 0.0 < ratio < 1.0


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------


class TestGenerateIndex:
    """generate_index() 生成 INDEX.md。"""

    def test_basic_structure(self) -> None:
        areas = {
            "skills": AreaInfo(
                name="Skills",
                files=[Path("skills/dev-tdd/SKILL.md")],
                directories=["skills"],
                entry_points=[],
            ),
        }
        result = generate_index(
            areas=areas,
            all_files=[Path("skills/dev-tdd/SKILL.md")],
            submodules=[],
            total_tokens=100,
        )
        assert "# Codemap Index" in result
        assert "生成时间:" in result
        assert "扫描文件: 1" in result
        assert "Token 估算:" in result

    def test_contains_submodule_list(self) -> None:
        submodules = [
            SubmoduleEntry(
                name="upstream/foo", path="upstream/foo", url="https://example.com"
            ),
        ]
        result = generate_index(
            areas={}, all_files=[], submodules=submodules, total_tokens=50
        )
        assert "upstream/foo" in result
        assert "https://example.com" in result


class TestGenerateSkillsCodemap:
    """generate_skills_codemap() 生成 skills.md。"""

    def test_groups_by_prefix(self) -> None:
        metas = [
            SkillMeta(
                name="dev-tdd", description="TDD", path=Path("skills/dev-tdd/SKILL.md")
            ),
            SkillMeta(
                name="dev-debug",
                description="Debug",
                path=Path("skills/dev-debug/SKILL.md"),
            ),
            SkillMeta(
                name="work-research",
                description="Research",
                path=Path("skills/work-research/SKILL.md"),
            ),
        ]
        result = generate_skills_codemap(metas)
        assert "# Skills Codemap" in result
        assert "dev-" in result
        assert "work-" in result

    def test_empty_metas(self) -> None:
        result = generate_skills_codemap([])
        assert "# Skills Codemap" in result


class TestGenerateCliCodemap:
    """generate_cli_codemap() 生成 cli.md。"""

    def test_basic_structure(self) -> None:
        area = AreaInfo(
            name="CLI",
            files=[Path("install_skills/cli.py"), Path("install_skills/models.py")],
            directories=["install_skills"],
            entry_points=["install_skills/cli.py"],
        )
        result = generate_cli_codemap(area)
        assert "# CLI Codemap" in result
        assert "install_skills" in result


class TestGenerateGenericCodemap:
    """generate_generic_codemap() 生成通用区域 codemap。"""

    def test_basic_structure(self) -> None:
        area = AreaInfo(
            name="Docs",
            files=[Path("docs/ROADMAP.md"), Path("docs/guide.md")],
            directories=["docs"],
            entry_points=[],
        )
        # 无 root 时只显示文件名
        result = generate_generic_codemap("docs", area)
        assert "# Docs Codemap" in result
        assert "ROADMAP.md" in result

    def test_empty_area(self) -> None:
        area = AreaInfo(name="Empty", files=[], directories=[], entry_points=[])
        result = generate_generic_codemap("empty", area)
        assert "# Empty Codemap" in result


# ---------------------------------------------------------------------------
# Integration: dry-run (不写文件)
# ---------------------------------------------------------------------------


class TestDryRun:
    """集成测试：--dry-run 不应写入文件系统。"""

    def test_dry_run_no_files_written(self, tmp_path: Path) -> None:
        # 创建最小项目结构
        (tmp_path / "skills" / "dev-tdd").mkdir(parents=True)
        (tmp_path / "skills" / "dev-tdd" / "SKILL.md").write_text(
            "---\nname: dev-tdd\ndescription: TDD\n---\n# TDD"
        )
        (tmp_path / ".gitmodules").write_text("")
        (tmp_path / "install_skills").mkdir()
        (tmp_path / "install_skills" / "cli.py").write_text("pass")
        (tmp_path / "docs").mkdir()
        (tmp_path / "CLAUDE.md").write_text("# project")

        from generate_codemaps import run_scan

        result = run_scan(tmp_path)
        assert "index" in result.markdowns
        assert "skills" in result.markdowns
        assert "cli" in result.markdowns
        # 不应写入文件
        codemaps_dir = tmp_path / "docs" / "CODEMAPS"
        assert not codemaps_dir.exists()
