# Skill 分组安装实施计划

> **给 Agent：** 必需子 skill：使用 `dev-executing-plans` 逐个任务实施此计划。

**目标：** 将现有 Python 安装器改造为分组安装 CLI 工具 `ce`，支持 skill 按组安装到全局或项目级目录。

**架构：** 现有单文件 `scripts/install_skills.py`（428 行）拆分为 `install_skills/` Python 包，新增 YAML 分组配置，manifest 从 v1 扁平结构升级为 v2 按组结构。通过 `pyproject.toml` + `[project.scripts]` 声明 `ce` CLI 入口，`uv tool install -e` 安装后直接可用。

**技术栈：** Python 3.12+、pyyaml、argparse、unittest、uv

---

## 文件变更规划

| 文件 | 操作 | 职责 |
|------|------|------|
| `install_skills/__init__.py` | 创建 | 包入口，导出版本号 |
| `install_skills/models.py` | 创建 | 数据结构：`SkillGroup`、`ManifestV2`、`GroupManifest` |
| `install_skills/config.py` | 创建 | 加载 `skills-install.yaml`，解析分组配置 |
| `install_skills/installer.py` | 创建 | symlink / manifest / MCP 逻辑（从旧脚本迁移） |
| `install_skills/cli.py` | 创建 | 命令行入口、参数解析 |
| `pyproject.toml` | 创建 | 包定义，`[project.scripts] ce = "install_skills.cli:main"` |
| `skills-install.yaml` | 创建 | 分组配置文件 |
| `tests/test_install_skills.py` | 修改 | 适配新包结构，新增分组相关测试 |
| `Makefile` | 删除 | 被 `ce` 命令替代 |
| `scripts/install_skills.py` | 删除 | 已拆分到 `install_skills/` 包 |
| `skills/obsidian-markdown/` | 创建 | 从 upstream 迁移 |
| `skills/obsidian-bases/` | 创建 | 从 upstream 迁移 |
| `skills/json-canvas/` | 创建 | 从 upstream 迁移 |
| `skills/obsidian-cli/` | 创建 | 从 upstream 迁移 |
| `skills/defuddle/` | 创建 | 从 upstream 迁移 |
| `CLAUDE.md` | 修改 | 更新安装说明、目录结构 |

---

## 任务 1：创建 pyproject.toml 和包骨架

**文件：**
- 创建：`pyproject.toml`
- 创建：`install_skills/__init__.py`
- 创建：`install_skills/models.py`
- 创建：`install_skills/config.py`
- 创建：`install_skills/installer.py`
- 创建：`install_skills/cli.py`

> 此任务为纯配置/骨架，不需要 TDD。

**步骤 1：创建 pyproject.toml**

```toml
[project]
name = "coding-everything"
version = "0.2.0"
description = "Personal AI coding assistant configuration manager"
requires-python = ">=3.12"
dependencies = [
    "pyyaml>=6.0",
]

[project.scripts]
ce = "install_skills.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**步骤 2：创建包骨架**

`install_skills/__init__.py`：
```python
"""coding-everything skill installer."""

__version__ = "0.2.0"
```

`install_skills/models.py`：
```python
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
```

`install_skills/config.py`：
```python
from __future__ import annotations

from pathlib import Path

import yaml

from install_skills.models import SkillGroup


def expand_path(p: str) -> Path:
    """展开 ~ 为绝对路径。"""
    return Path(p).expanduser()


def load_install_config(config_path: Path) -> dict[str, SkillGroup]:
    """加载 skills-install.yaml，返回 {name: SkillGroup}。

    如果配置文件不存在返回空 dict（退化模式）。
    """
    if not config_path.is_file():
        return {}

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if raw is None or "groups" not in raw:
        return {}

    result: dict[str, SkillGroup] = {}
    for name, group_data in raw["groups"].items():
        targets = [expand_path(t) for t in group_data.get("targets", [])]
        result[name] = SkillGroup(
            name=name,
            skills=list(group_data.get("skills", [])),
            targets=targets,
        )
    return result
```

`install_skills/installer.py`：创建空文件，仅 `"""Installer logic."""` 占位。

`install_skills/cli.py`：创建空文件，仅 `"""CLI entry point."""` 占位。

**步骤 3：验证包可以被 import**

运行：`uv run python -c "from install_skills.models import SkillGroup; print('ok')"`
预期：输出 `ok`

**步骤 4：提交**

```bash
git add pyproject.toml install_skills/
git commit -m "feat: create install_skills package skeleton with models and config"
```

---

## 任务 2：迁移 installer 核心逻辑

**文件：**
- 修改：`install_skills/installer.py`
- 修改：`tests/test_install_skills.py`

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

这是最大的任务。将 `scripts/install_skills.py` 中的所有函数迁移到 `install_skills/installer.py`，保持原有行为不变。

**步骤 1：RED - 迁移现有测试文件引用**

修改 `tests/test_install_skills.py` 的 import：
```python
# 旧：from scripts import install_skills
# 新：
from install_skills import installer
```

运行：`uv run python -m unittest tests.test_install_skills -v`
预期：全部 FAIL（因为 installer.py 是空的）

**步骤 2：GREEN - 迁移所有函数到 installer.py**

从 `scripts/install_skills.py` 复制以下函数到 `install_skills/installer.py`，调整函数签名保持兼容：

```python
from __future__ import annotations

import json
import os as _os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, TextIO

from install_skills.models import ManifestV2, GroupManifest

# 常量
MANIFEST_DIR_NAME = ".ce"
MANIFEST_FILENAME = "install-manifest.json"
LEGACY_MANIFEST_RELATIVE_PATH = Path(".local/share/coding-everything/install-manifest.json")
AGENTS_SKILLS_RELATIVE_DIR = Path(".agents/skills")
CLAUDE_SKILLS_RELATIVE_DIR = Path(".claude/skills")
KIMI_AGENT_RELATIVE_PATH = Path(".kimi/agents/superpower")
KS_RELATIVE_PATH = Path(".local/bin/ks")
MCP_CONFIG_RELATIVE_PATH = Path("mcp-configs/required.json")
ZAI_MCP_NAMES = ("zai-github-read", "zai-web-reader", "zai-web-search-prime")
CLAUDE_JSON_FILENAME = ".claude.json"
PLACEHOLDER_ZAI_API_KEY = "{{ZAI_API_KEY}}"


def now_iso() -> str: ...
def build_targets(home: Path) -> dict: ...  # 保持旧接口
def discover_skills(repo_root: Path) -> list[str]: ...
def load_mcp_template(repo_root: Path) -> dict: ...
def resolve_zai_api_key(claude_config: dict) -> str | None: ...
def _deep_copy_without_internal_keys(data: dict) -> dict: ...
def merge_mcp_config(home: Path, repo_root: Path) -> list[str]: ...
def remove_managed_mcps(home: Path, managed_names: list[str]) -> None: ...
def collect_mcp_status(home: Path, repo_root: Path) -> dict: ...
def remove_existing(path: Path) -> None: ...
def force_symlink(src: Path, dst: Path) -> None: ...
def ensure_parent_dirs(targets) -> None: ...
def manifest_payload(...) -> dict: ...
def write_manifest(...) -> None: ...
def load_manifest(path: Path) -> dict | None: ...
def install_skill_links(repo_root: Path, targets, skills: Iterable[str]) -> None: ...
def install_kimi_agent_and_ks(repo_root: Path, targets) -> None: ...
def command_install(repo_root: Path, home: Path, stdout: TextIO) -> int: ...
def command_update(repo_root: Path, home: Path, stdout: TextIO) -> int: ...
def collect_status(repo_root: Path, home: Path) -> tuple: ...
def command_status(repo_root: Path, home: Path, stdout: TextIO) -> int: ...
def command_uninstall(repo_root: Path, home: Path, stdout: TextIO, stderr: TextIO) -> int: ...
```

函数体完全从旧文件复制，只改：
1. `load_manifest(targets)` → `load_manifest(path: Path)` 接受 manifest 文件路径
2. `write_manifest(targets, ...)` → `write_manifest(path: Path, ...)` 接受 manifest 文件路径
3. manifest 路径常量新增 `CE_DIR = home / ".ce"`、`CE_MANIFEST = CE_DIR / "install-manifest.json"`
4. 保持旧版 `InstallTargets` dataclass 以兼容现有测试

**步骤 3：更新测试文件引用**

```python
# 所有 install_skills.xxx 改为 installer.xxx
from install_skills import installer

# 例如
install_skills.discover_skills(...) → installer.discover_skills(...)
install_skills.main(...) → installer.main(...)
```

注意：测试中的 `manifest_path()` 需要暂时保持返回旧路径（因为旧测试测的就是旧路径），后续任务会更新。

**步骤 4：验证 GREEN**

运行：`uv run python -m unittest tests.test_install_skills -v`
预期：全部 PASS

**步骤 5：REFACTOR - 清理旧文件**

- 删除 `scripts/install_skills.py`（所有逻辑已迁移）
- ruff check：`uv run ruff check install_skills/`

**步骤 6：提交**

```bash
git add install_skills/installer.py tests/test_install_skills.py
git rm scripts/install_skills.py
git commit -m "refactor: migrate installer logic from scripts/ to install_skills package"
```

---

## 任务 3：CLI 入口点

**文件：**
- 修改：`install_skills/cli.py`
- 修改：`tests/test_install_skills.py`

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1：RED - 编写 CLI 测试**

在 `tests/test_install_skills.py` 末尾新增：

```python
from install_skills import cli


class CliArgParseTest(unittest.TestCase):
    def test_parse_install_command(self) -> None:
        args = cli.parse_args(["install"])
        self.assertEqual(args.command, "install")
        self.assertIsNone(args.group)

    def test_parse_install_with_group(self) -> None:
        args = cli.parse_args(["install", "--group", "obsidian"])
        self.assertEqual(args.command, "install")
        self.assertEqual(args.group, "obsidian")

    def test_parse_status(self) -> None:
        args = cli.parse_args(["status"])
        self.assertEqual(args.command, "status")

    def test_parse_update_with_group(self) -> None:
        args = cli.parse_args(["update", "--group", "global"])
        self.assertEqual(args.command, "update")
        self.assertEqual(args.group, "global")

    def test_parse_uninstall(self) -> None:
        args = cli.parse_args(["uninstall"])
        self.assertEqual(args.command, "uninstall")
        self.assertIsNone(args.group)
```

运行：`uv run python -m unittest tests.test_install_skills.CliArgParseTest -v`
预期：FAIL（`cli.parse_args` 不存在）

**步骤 2：GREEN - 实现 CLI**

`install_skills/cli.py`：

```python
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from install_skills import installer


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ce",
        description="Manage coding-everything skill installation",
    )
    parser.add_argument(
        "command",
        choices=("install", "update", "uninstall", "status"),
    )
    parser.add_argument(
        "--group",
        default=None,
        help="Only operate on the specified group",
    )
    return parser.parse_args(argv)


def main(
    argv: list[str] | None = None,
    *,
    repo_root: Path | None = None,
    home: Path | None = None,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    resolved_repo_root = repo_root or Path(__file__).resolve().parents[1]
    resolved_home = home or Path.home()

    kwargs = {"stdout": stdout}
    if args.command == "uninstall":
        kwargs["stderr"] = stderr

    handler = getattr(installer, f"command_{args.command}")
    return handler(resolved_repo_root, resolved_home, **kwargs)


if __name__ == "__main__":
    raise SystemExit(main())
```

运行：`uv run python -m unittest tests.test_install_skills.CliArgParseTest -v`
预期：全部 PASS

**步骤 3：提交**

```bash
git add install_skills/cli.py tests/test_install_skills.py
git commit -m "feat: add ce CLI entry point with --group argument"
```

---

## 任务 4：分组安装逻辑

**文件：**
- 修改：`install_skills/installer.py`
- 修改：`tests/test_install_skills.py`

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

这是核心任务——让 installer 支持分组安装。

**步骤 1：RED - 编写分组安装测试**

在测试文件中新增：

```python
from install_skills.config import load_install_config
from install_skills.models import SkillGroup


class GroupInstallTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.repo_root = root / "repo"
        self.home = root / "home"
        self.skills_dir = self.repo_root / "skills"
        self.skills_dir.mkdir(parents=True)

        # 创建 global skill
        for skill in ("dev-tdd", "dev-debug"):
            d = self.skills_dir / skill
            d.mkdir()
            (d / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")

        # 创建 obsidian skill
        for skill in ("obsidian-markdown", "obsidian-bases"):
            d = self.skills_dir / skill
            d.mkdir()
            (d / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")

        # 创建 kimi agent + ks
        kimi = self.repo_root / "kimi/agents/superpower"
        kimi.mkdir(parents=True)
        (kimi / "agent.yaml").write_text("name: superpower\n", encoding="utf-8")
        (self.repo_root / "ks").write_text("#!/bin/bash\n", encoding="utf-8")
        self._create_mcp_required_json()

        # 创建 YAML 配置
        self.config_path = self.repo_root / "skills-install.yaml"
        self.config_path.write_text(
            "groups:\n"
            "  global:\n"
            "    skills: [dev-tdd, dev-debug]\n"
            "    targets:\n"
            "      - ~/.agents/skills\n"
            "      - ~/.claude/skills\n"
            "  obsidian:\n"
            "    skills: [obsidian-markdown, obsidian-bases]\n"
            "    targets:\n"
            f"      - {self.home}/vault/.claude/skills\n"
            f"      - {self.home}/vault/.agents/skills\n",
            encoding="utf-8",
        )

        self.stdout = io.StringIO()
        self.stderr = io.StringIO()

    def _create_mcp_required_json(self) -> None:
        mcp_dir = self.repo_root / "mcp-configs"
        mcp_dir.mkdir(parents=True, exist_ok=True)
        (mcp_dir / "required.json").write_text(
            json.dumps({"mcpServers": {"auggie-mcp": {"command": "auggie", "type": "stdio"}}}),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def manifest_path(self) -> Path:
        return self.home / ".ce" / "install-manifest.json"

    def test_install_all_groups(self) -> None:
        """ce install 安装所有组。"""
        code = installer.command_install_grouped(
            self.repo_root, self.home, self.config_path, stdout=self.stdout,
        )
        self.assertEqual(code, 0)

        # global skills 在全局 targets
        for skill in ("dev-tdd", "dev-debug"):
            self.assertTrue((self.home / ".agents/skills" / skill).is_symlink())
            self.assertTrue((self.home / ".claude/skills" / skill).is_symlink())

        # obsidian skills 在项目 targets
        for skill in ("obsidian-markdown", "obsidian-bases"):
            self.assertTrue((self.home / "vault/.claude/skills" / skill).is_symlink())
            self.assertTrue((self.home / "vault/.agents/skills" / skill).is_symlink())

        # kimi + ks 也被安装（global 组的额外职责）
        self.assertTrue((self.home / ".kimi/agents/superpower").is_symlink())
        self.assertTrue((self.home / ".local/bin/ks").is_symlink())

    def test_install_single_group(self) -> None:
        """ce install --group obsidian 只安装 obsidian 组。"""
        code = installer.command_install_grouped(
            self.repo_root, self.home, self.config_path,
            group="obsidian", stdout=self.stdout,
        )
        self.assertEqual(code, 0)

        # obsidian skills 已安装
        for skill in ("obsidian-markdown", "obsidian-bases"):
            self.assertTrue((self.home / "vault/.claude/skills" / skill).is_symlink())

        # global skills 未安装
        self.assertFalse((self.home / ".agents/skills" / "dev-tdd").exists())

    def test_install_writes_v2_manifest(self) -> None:
        """安装后写入 v2 格式 manifest。"""
        installer.command_install_grouped(
            self.repo_root, self.home, self.config_path, stdout=self.stdout,
        )
        manifest = json.loads(self.manifest_path().read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], 2)
        self.assertIn("groups", manifest)
        self.assertIn("global", manifest["groups"])
        self.assertIn("obsidian", manifest["groups"])

    def test_uninstall_single_group(self) -> None:
        """ce uninstall --group obsidian 只卸载 obsidian 组。"""
        installer.command_install_grouped(
            self.repo_root, self.home, self.config_path, stdout=self.stdout,
        )

        code = installer.command_uninstall_grouped(
            self.repo_root, self.home, self.config_path,
            group="obsidian", stdout=self.stdout, stderr=self.stderr,
        )
        self.assertEqual(code, 0)

        # obsidian skills 已移除
        self.assertFalse((self.home / "vault/.claude/skills" / "obsidian-markdown").exists())

        # global skills 仍在
        self.assertTrue((self.home / ".agents/skills" / "dev-tdd").is_symlink())

        # manifest 仍存在，但 obsidian 组已移除
        manifest = json.loads(self.manifest_path().read_text(encoding="utf-8"))
        self.assertNotIn("obsidian", manifest["groups"])
        self.assertIn("global", manifest["groups"])

    def test_status_shows_all_groups(self) -> None:
        """ce status 显示所有组的状态。"""
        installer.command_install_grouped(
            self.repo_root, self.home, self.config_path, stdout=self.stdout,
        )
        self.stdout = io.StringIO()
        code = installer.command_status_grouped(
            self.repo_root, self.home, self.config_path, stdout=self.stdout,
        )
        self.assertEqual(code, 0)
        output = self.stdout.getvalue()
        self.assertIn("[global]", output)
        self.assertIn("[obsidian]", output)

    def test_status_single_group(self) -> None:
        """ce status --group global 只显示 global 组。"""
        installer.command_install_grouped(
            self.repo_root, self.home, self.config_path, stdout=self.stdout,
        )
        self.stdout = io.StringIO()
        code = installer.command_status_grouped(
            self.repo_root, self.home, self.config_path,
            group="global", stdout=self.stdout,
        )
        self.assertEqual(code, 0)
        output = self.stdout.getvalue()
        self.assertIn("[global]", output)
        self.assertNotIn("[obsidian]", output)

    def test_install_no_config_falls_back_to_legacy(self) -> None:
        """skills-install.yaml 不存在时退化为旧版行为。"""
        config_path = self.repo_root / "nonexistent.yaml"
        code = installer.command_install_grouped(
            self.repo_root, self.home, config_path, stdout=self.stdout,
        )
        self.assertEqual(code, 0)
        # 全部 skills 安装到默认全局 targets
        for skill in ("dev-tdd", "dev-debug", "obsidian-markdown", "obsidian-bases"):
            self.assertTrue((self.home / ".agents/skills" / skill).is_symlink())
```

运行：`uv run python -m unittest tests.test_install_skills.GroupInstallTest -v`
预期：全部 FAIL

**步骤 2：GREEN - 实现分组安装函数**

在 `install_skills/installer.py` 中新增以下函数：

```python
from install_skills.config import load_install_config
from install_skills.models import SkillGroup


def _ce_manifest_path(home: Path) -> Path:
    """新 manifest 路径：~/.ce/install-manifest.json"""
    return home / ".ce" / "install-manifest.json"


def _legacy_manifest_path(home: Path) -> Path:
    """旧 manifest 路径：~/.local/share/coding-everything/install-manifest.json"""
    return home / ".local/share/coding-everything/install-manifest.json"


def _migrate_v1_manifest(home: Path) -> None:
    """将 v1 manifest 迁移为 v2 并删除旧文件。"""
    legacy = _legacy_manifest_path(home)
    if not legacy.is_file():
        return
    v1 = json.loads(legacy.read_text(encoding="utf-8"))
    if "version" in v1:
        return  # 已经是 v2

    v2 = {
        "version": 2,
        "groups": {
            "global": {**v1},
        },
    }
    new_path = _ce_manifest_path(home)
    new_path.parent.mkdir(parents=True, exist_ok=True)
    new_path.write_text(
        json.dumps(v2, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    legacy.unlink()


def load_v2_manifest(home: Path) -> dict | None:
    path = _ce_manifest_path(home)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_v2_manifest(home: Path, data: dict) -> None:
    path = _ce_manifest_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _install_group(
    repo_root: Path,
    home: Path,
    group: SkillGroup,
    manifest_data: dict,
) -> dict:
    """安装单个组的 skills，返回更新后的 manifest_data。"""
    timestamp = now_iso()
    targets = group.targets

    # 确保 target 目录存在
    for target in targets:
        target.mkdir(parents=True, exist_ok=True)

    # symlink 每个 skill
    for skill in group.skills:
        src = repo_root / "skills" / skill
        for target in targets:
            force_symlink(src, target / skill)

    # global 组的额外职责
    mcp_servers: list[str] = []
    existing_group = manifest_data.get("groups", {}).get(group.name, {})
    installed_at = existing_group.get("installed_at", timestamp)

    if group.name == "global":
        # kimi agent + ks
        kimi_dir = home / KIMI_AGENT_RELATIVE_PATH
        ks_path = home / KS_RELATIVE_PATH
        kimi_dir.parent.mkdir(parents=True, exist_ok=True)
        ks_path.parent.mkdir(parents=True, exist_ok=True)
        force_symlink(repo_root / "kimi/agents/superpower", kimi_dir)
        force_symlink(repo_root / "ks", ks_path)
        # MCP
        mcp_servers = merge_mcp_config(home, repo_root)

    group_entry = {
        "installed_at": installed_at,
        "updated_at": timestamp,
        "targets": [str(t) for t in targets],
        "skills": list(group.skills),
        **({"mcp_servers": mcp_servers} if group.name == "global" else {}),
        **({"repo_root": str(repo_root)} if group.name == "global" else {}),
    }

    groups = {**manifest_data.get("groups", {}), group.name: group_entry}
    return {**manifest_data, "groups": groups}


def command_install_grouped(
    repo_root: Path,
    home: Path,
    config_path: Path,
    *,
    group: str | None = None,
    stdout: TextIO = sys.stdout,
) -> int:
    config = load_install_config(config_path)

    if not config:
        # 退化模式：无配置文件时走旧版行为
        return command_install(repo_root, home, stdout=stdout)

    _migrate_v1_manifest(home)
    manifest_data = load_v2_manifest(home) or {"version": 2, "groups": {}}

    groups_to_install = (
        {group: config[group]} if group else config
    )

    for g_name, g in groups_to_install.items():
        manifest_data = _install_group(repo_root, home, g, manifest_data)
        print(f"[{g_name}] installed {len(g.skills)} skills", file=stdout)

    if "global" in groups_to_install and groups_to_install["global"].name == "global":
        mcp = manifest_data["groups"]["global"].get("mcp_servers", [])
        print("mcp_servers=" + ",".join(mcp), file=stdout)

    write_v2_manifest(home, manifest_data)
    return 0


def command_uninstall_grouped(
    repo_root: Path,
    home: Path,
    config_path: Path,
    *,
    group: str | None = None,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    manifest_data = load_v2_manifest(home)
    if manifest_data is None:
        print("manifest missing; refusing uninstall", file=stderr)
        return 1

    if group:
        # 只卸载指定组
        group_entry = manifest_data.get("groups", {}).get(group)
        if group_entry is None:
            print(f"group '{group}' not found in manifest", file=stderr)
            return 1
        for skill in group_entry.get("skills", []):
            for target_str in group_entry.get("targets", []):
                target = Path(target_str)
                remove_existing(target / skill)
        if group == "global":
            remove_existing(home / KIMI_AGENT_RELATIVE_PATH)
            remove_existing(home / KS_RELATIVE_PATH)
            mcp_names = group_entry.get("mcp_servers", [])
            if mcp_names:
                remove_managed_mcps(home, mcp_names)
        groups = {k: v for k, v in manifest_data["groups"].items() if k != group}
        manifest_data = {**manifest_data, "groups": groups}
        if groups:
            write_v2_manifest(home, manifest_data)
        else:
            p = _ce_manifest_path(home)
            if p.exists():
                p.unlink()
        print(f"[{group}] uninstalled", file=stdout)
    else:
        # 卸载所有组
        for g_name, g_entry in manifest_data.get("groups", {}).items():
            for skill in g_entry.get("skills", []):
                for target_str in g_entry.get("targets", []):
                    remove_existing(Path(target_str) / skill)
            if g_name == "global":
                remove_existing(home / KIMI_AGENT_RELATIVE_PATH)
                remove_existing(home / KS_RELATIVE_PATH)
                mcp_names = g_entry.get("mcp_servers", [])
                if mcp_names:
                    remove_managed_mcps(home, mcp_names)
        p = _ce_manifest_path(home)
        if p.exists():
            p.unlink()
        print("uninstalled all groups", file=stdout)
    return 0


def command_status_grouped(
    repo_root: Path,
    home: Path,
    config_path: Path,
    *,
    group: str | None = None,
    stdout: TextIO = sys.stdout,
) -> int:
    config = load_install_config(config_path)
    if not config:
        return command_status(repo_root, home, stdout=stdout)

    manifest_data = load_v2_manifest(home)

    groups_to_show = (
        {group: config[group]} if group and group in config else
        {group: config[group]} if group else config
    )

    for g_name, g in groups_to_show.items():
        group_entry = (manifest_data or {}).get("groups", {}).get(g_name)
        if group_entry is None:
            print(f"[{g_name}] state=unmanaged", file=stdout)
            continue

        skills_in_manifest = set(group_entry.get("skills", []))
        targets = [Path(t) for t in group_entry.get("targets", [])]
        installed = 0
        missing = 0
        drifted = 0
        for skill in skills_in_manifest:
            expected_src = repo_root / "skills" / skill
            for target in targets:
                dst = target / skill
                if not dst.exists() and not dst.is_symlink():
                    missing += 1
                elif not dst.is_symlink() or dst.resolve() != expected_src.resolve():
                    drifted += 1
                else:
                    installed += 1
        print(f"[{g_name}] installed={installed} missing={missing} drifted={drifted}", file=stdout)

        if g_name == "global":
            mcp_status = collect_mcp_status(home, repo_root)
            mcp_conf = ",".join(mcp_status["configured"])
            mcp_miss = ",".join(mcp_status["missing"])
            print(f"  mcp: configured={mcp_conf} missing={mcp_miss}", file=stdout)
        else:
            targets_str = ", ".join(str(t) for t in targets)
            print(f"  targets: {targets_str}", file=stdout)

    return 0
```

运行：`uv run python -m unittest tests.test_install_skills.GroupInstallTest -v`
预期：全部 PASS

**步骤 3：REFACTOR - 连接 CLI 到分组函数**

修改 `install_skills/cli.py` 的 `main()` 函数，让它根据是否有 `skills-install.yaml` 来决定走分组还是旧版路径：

```python
def main(
    argv: list[str] | None = None,
    *,
    repo_root: Path | None = None,
    home: Path | None = None,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    resolved_repo_root = repo_root or Path(__file__).resolve().parents[1]
    resolved_home = home or Path.home()
    config_path = resolved_repo_root / "skills-install.yaml"

    if config_path.is_file():
        if args.command == "install":
            return installer.command_install_grouped(
                resolved_repo_root, resolved_home, config_path,
                group=args.group, stdout=stdout,
            )
        if args.command == "update":
            return installer.command_install_grouped(
                resolved_repo_root, resolved_home, config_path,
                group=args.group, stdout=stdout,
            )
        if args.command == "uninstall":
            return installer.command_uninstall_grouped(
                resolved_repo_root, resolved_home, config_path,
                group=args.group, stdout=stdout, stderr=stderr,
            )
        return installer.command_status_grouped(
            resolved_repo_root, resolved_home, config_path,
            group=args.group, stdout=stdout,
        )

    # 无配置文件时走旧版
    if args.command == "install":
        return installer.command_install(resolved_repo_root, resolved_home, stdout=stdout)
    if args.command == "update":
        return installer.command_update(resolved_repo_root, resolved_home, stdout=stdout)
    if args.command == "uninstall":
        return installer.command_uninstall(
            resolved_repo_root, resolved_home, stdout=stdout, stderr=stderr,
        )
    return installer.command_status(resolved_repo_root, resolved_home, stdout=stdout)
```

运行：`uv run python -m unittest tests.test_install_skills -v`
预期：全部 PASS（新旧测试都通过）

**步骤 4：提交**

```bash
git add install_skills/ tests/test_install_skills.py
git commit -m "feat: add grouped install/uninstall/status with YAML config"
```

---

## 任务 5：创建 skills-install.yaml

**文件：**
- 创建：`skills-install.yaml`

> 此任务为纯配置，不需要 TDD。

**步骤 1：创建配置文件**

```yaml
groups:
  global:
    skills:
      - dev-brainstorming
      - dev-debugging
      - dev-tdd
      - dev-writing-plans
      - dev-executing-plans
      - dev-git-worktrees
      - dev-requesting-review
      - dev-verification
      - dev-finishing-branch
      - dev-writing-skills
      - dev-code-cleanup
      - dev-update-codemaps
      - dev-search-first
      - dev-using-skills
      - dev-backend-patterns
      - dev-frontend-patterns
      - dev-design-system
      - dev-ui-styling
      - dev-continuous-agent-loop
      - dev-e2e-testing
      - learn-deep-research
      - work-market-research
      - tool-humanizer-zh
      - tool-macos-hidpi
      - agent-browser
    targets:
      - ~/.agents/skills
      - ~/.claude/skills

  obsidian:
    skills:
      - obsidian-markdown
      - obsidian-bases
      - json-canvas
      - obsidian-cli
      - defuddle
    targets:
      - ~/Documents/ObsidianVault/.claude/skills
      - ~/Documents/ObsidianVault/.agents/skills
```

**步骤 2：提交**

```bash
git add skills-install.yaml
git commit -m "feat: add skills-install.yaml with global and obsidian groups"
```

---

## 任务 6：迁移 obsidian-skills

**文件：**
- 创建：`skills/obsidian-markdown/`（含 SKILL.md + UPSTREAM.md）
- 创建：`skills/obsidian-bases/`
- 创建：`skills/json-canvas/`
- 创建：`skills/obsidian-cli/`
- 创建：`skills/defuddle/`

> 此任务为文件复制 + 元数据，不需要 TDD。

**步骤 1：复制上游 skill 目录**

```bash
for skill in obsidian-markdown obsidian-bases json-canvas obsidian-cli defuddle; do
  cp -r upstream/obsidian-skills/skills/$skill/ skills/$skill/
done
```

**步骤 2：为每个 skill 创建 UPSTREAM.md**

每个 UPSTREAM.md 内容：

```markdown
# <skill-name> 来源信息

- 来源仓库：https://github.com/kepano/obsidian-skills
- 跟踪路径：`skills/<skill-name>/`
- 跟踪分支：`main`
- 当前同步 SHA：`bb9ec95e1b59c3471bd6fd77a78a4042430bfac3`
- 最近同步日期：`2026-03-31`

## 同步命令

```bash
cp -r upstream/obsidian-skills/skills/<skill-name>/ skills/<skill-name>/
```
```

**步骤 3：提交**

```bash
git add skills/obsidian-markdown/ skills/obsidian-bases/ skills/json-canvas/ skills/obsidian-cli/ skills/defuddle/
git commit -m "feat: migrate obsidian-skills from upstream with UPSTREAM.md tracking"
```

---

## 任务 7：删除 Makefile

**文件：**
- 删除：`Makefile`

> 此任务为纯清理，不需要 TDD。

**步骤 1：删除 Makefile**

```bash
git rm Makefile
```

**步骤 2：提交**

```bash
git commit -m "chore: remove Makefile, replaced by ce CLI"
```

---

## 任务 8：更新文档

**文件：**
- 修改：`CLAUDE.md`

> 此任务为文档更新，不需要 TDD。

**步骤 1：更新 CLAUDE.md 中的安装说明**

需要更新的部分：

1. **快速安装**：`make install` → `uv tool install -e . && ce install`
2. **项目结构**：新增 `install_skills/` 包、`skills-install.yaml`，删除 `Makefile`
3. **skill 列表**：新增 obsidian 组的 5 个 skill
4. **上游 obsidian-skills**：更新同步状态为"已迁移到 skills/ 目录"
5. **验收标准关联**：确保文档反映新的 CLI 入口

具体修改：
- 将 `make install/update/uninstall/status` 替换为对应的 `ce` 命令
- 在 skill 列表表格中新增 obsidian 组
- 更新项目结构图

**步骤 2：提交**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for ce CLI and obsidian group"
```

---

## 任务 9：端到端验证

**文件：** 无新文件

> 此任务为验证，不需要 TDD。

**步骤 1：ruff check**

```bash
uv run ruff check install_skills/ tests/
```
预期：全部通过，无 warning

**步骤 2：运行全部测试**

```bash
uv run python -m unittest tests.test_install_skills -v
```
预期：全部 PASS

**步骤 3：安装 ce 命令**

```bash
uv tool install -e .
```

**步骤 4：验证 ce 命令可用**

```bash
ce status
```
预期：显示当前安装状态（可能显示 unmanaged 如果没有旧 manifest）

**步骤 5：验证分组安装**

```bash
ce install --group global
ce status
```
预期：`[global] installed=N missing=0 drifted=0`

---

## 任务 10：最终提交整理

**文件：** 无新文件

如果任务 1-9 中有未提交的改动，统一检查并提交。确保 git 状态干净。

```bash
git status
git log --oneline -10
```

确认：
- 所有新文件已提交
- 旧文件（`scripts/install_skills.py`、`Makefile`）已删除
- 测试全部通过
- ruff check 全部通过
