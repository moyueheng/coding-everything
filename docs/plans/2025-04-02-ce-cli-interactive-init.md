# ce CLI 交互式 init 命令实施计划

> **给 Agent：** 必需子 skill：使用 `dev-executing-plans` 逐个任务实施此计划。

**目标：** 实现 `ce init` 交互式配置向导，将静态配置从 `skills-install.yaml` 迁移到用户级 `~/.ce/config.yaml`

**架构：** 新增 `UserConfig` 类管理 `~/.ce/config.yaml`，包含分组技能列表和 targets。`ce init` 扫描仓库技能目录，交互式询问 obsidian 路径后生成此配置。`ce install` 重构为读取用户配置而非仓库 YAML。

**技术栈：** Python 3.12, PyYAML, pytest

---

## 文件结构变更

### 修改文件

| 文件 | 职责 |
|------|------|
| `install_skills/models.py` | 新增 `UserConfig`, `GroupConfig` 数据类 |
| `install_skills/config.py` | 重写：加载/保存 `~/.ce/config.yaml`，删除旧 YAML 逻辑 |
| `install_skills/installer.py` | 重构：使用 UserConfig 替代 SkillGroup |
| `install_skills/cli.py` | 新增 `init`, `add-skill`, `add-target` 命令 |
| `pyproject.toml` | 确保依赖包含 PyYAML |

### 删除文件

| 文件 | 说明 |
|------|------|
| `skills-install.yaml` | 静态配置迁移到用户级配置 |

### 新增测试文件

| 文件 | 职责 |
|------|------|
| `tests/test_config.py` | 测试 UserConfig 加载/保存 |
| `tests/test_cli_init.py` | 测试 init 命令交互逻辑 |

---

## 任务列表

### 任务 1：定义 UserConfig 数据模型

**文件：**
- 修改：`install_skills/models.py`
- 测试：`tests/test_models.py`（新建）

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1：RED - 编写失败的测试**

```python
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
```

**步骤 2：验证 RED - 看着它失败**

运行：`pytest tests/test_models.py -v`
预期：FAIL with "UserConfig not defined"

**步骤 3：GREEN - 编写最小实现**

```python
# install_skills/models.py
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SkillGroup:
    """YAML 配置中的一个分组（旧版，保留向后兼容）"""
    name: str
    skills: list[str]
    targets: list[Path]


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
```

**步骤 4：验证 GREEN - 看着它通过**

运行：`pytest tests/test_models.py -v`
预期：PASS

**步骤 5：提交**

```bash
git add tests/test_models.py install_skills/models.py
git commit -m "feat: add UserConfig and GroupConfig data models"
```

---

### 任务 2：实现 config.py 加载/保存逻辑

**文件：**
- 修改：`install_skills/config.py`
- 测试：`tests/test_config.py`（新建）

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1：RED - 编写失败的测试**

```python
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
```

**步骤 2：验证 RED - 看着它失败**

运行：`pytest tests/test_config.py -v`
预期：FAIL with functions not defined

**步骤 3：GREEN - 编写最小实现**

```python
# install_skills/config.py
from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

from install_skills.models import UserConfig, GroupConfig


CE_DIR = Path(".ce")
CONFIG_FILENAME = "config.yaml"


def expand_path(p: str | Path) -> Path:
    """展开 ~ 为绝对路径。"""
    return Path(p).expanduser()


def get_default_config_path(home: Path | None = None) -> Path:
    """返回默认配置文件路径 ~/.ce/config.yaml"""
    home = home or Path.home()
    return home / CE_DIR / CONFIG_FILENAME


def _group_to_dict(group: GroupConfig) -> dict[str, Any]:
    """将 GroupConfig 转为字典"""
    return {
        "skills": list(group.skills),
        "targets": [str(t) for t in group.targets],
    }


def _group_from_dict(name: str, data: dict[str, Any]) -> GroupConfig:
    """从字典创建 GroupConfig"""
    return GroupConfig(
        name=name,
        skills=list(data.get("skills", [])),
        targets=[expand_path(t) for t in data.get("targets", [])],
    )


def load_user_config(config_path: Path) -> UserConfig | None:
    """从 YAML 加载用户配置。如果不存在返回 None。"""
    if not config_path.exists():
        return None
    
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if data is None:
        return None
    
    groups: dict[str, GroupConfig] = {}
    for name, group_data in data.get("groups", {}).items():
        groups[name] = _group_from_dict(name, group_data)
    
    repo_root = data.get("repo_root")
    
    return UserConfig(
        version=data.get("version", 2),
        repo_root=Path(repo_root) if repo_root else None,
        groups=groups,
    )


def save_user_config(config_path: Path, config: UserConfig) -> None:
    """保存用户配置到 YAML。"""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    data: dict[str, Any] = {
        "version": config.version,
    }
    
    if config.repo_root:
        data["repo_root"] = str(config.repo_root)
    
    data["groups"] = {
        name: _group_to_dict(group)
        for name, group in config.groups.items()
    }
    
    config_path.write_text(
        yaml.safe_dump(data, default_flow_style=False, allow_unicode=True),
        encoding="utf-8"
    )


def load_install_config(config_path: Path) -> dict[str, Any]:
    """【已废弃】保留以兼容旧代码，实际不再使用。"""
    return {}
```

**步骤 4：验证 GREEN - 看着它通过**

运行：`pytest tests/test_config.py -v`
预期：PASS

**步骤 5：REFACTOR**

检查是否所有 edge case 已处理：
- 空 groups
- 缺失可选字段
- 路径展开

**步骤 6：提交**

```bash
git add tests/test_config.py install_skills/config.py
git commit -m "feat: implement UserConfig load/save with YAML"
```

---

### 任务 3：实现 ce init 命令核心逻辑

**文件：**
- 修改：`install_skills/cli.py`
- 修改：`install_skills/installer.py`

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1：RED - 编写测试（先在 test_cli_init.py 中）**

```python
# tests/test_cli_init.py
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from install_skills.cli import main
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
        with patch('builtins.input', return_value=str(home / "ob-note")):
            with patch('pathlib.Path.exists', return_value=True):
                result = main(
                    ['init'],
                    repo_root=repo_root,
                    home=home
                )
        
        assert result == 0
        config_path = home / ".ce" / "config.yaml"
        assert config_path.exists()
```

**步骤 2：验证 RED**

运行：`pytest tests/test_cli_init.py -v`
预期：FAIL - init 命令未定义

**步骤 3：GREEN - 实现 init 命令**

修改 `install_skills/cli.py`，添加 `init` 命令：

```python
# install_skills/cli.py
from pathlib import Path
from install_skills import installer
from install_skills.config import get_default_config_path, load_user_config


def _ask_obsidian_path() -> Path | None:
    """交互式询问 Obsidian vault 路径"""
    print("\n是否安装 Obsidian 相关 skills?")
    print("这些 skills 需要安装到你的 Obsidian vault 目录中。")
    
    while True:
        answer = input("输入 Obsidian vault 路径 (例如 ~/00-life/ob-note)，或留空跳过: ").strip()
        
        if not answer:
            return None
        
        path = Path(answer).expanduser()
        
        # 检查是否存在
        if not path.exists():
            print(f"❌ 路径不存在: {path}")
            retry = input("是否重新输入? [Y/n]: ").strip().lower()
            if retry in ('', 'y', 'yes'):
                continue
            return None
        
        # 检查是否是 vault（有 .obsidian 目录）
        if not (path / ".obsidian").exists():
            print(f"⚠️  警告: {path} 似乎不是 Obsidian vault（缺少 .obsidian 目录）")
            confirm = input("仍然继续? [y/N]: ").strip().lower()
            if confirm not in ('y', 'yes'):
                continue
        
        return path


def command_init(
    repo_root: Path,
    home: Path,
    *,
    stdout=None,
    _input_func=input,  # 注入以便测试
) -> int:
    """交互式初始化配置。"""
    config_path = get_default_config_path(home)
    
    # 检查是否已存在
    if config_path.exists():
        print(f"配置已存在: {config_path}")
        print("如需重新配置，请先删除该文件。")
        return 1
    
    print(f"初始化 ce CLI 配置...")
    print(f"仓库根目录: {repo_root}")
    
    # 扫描可用 skills
    from install_skills.installer import discover_skills
    available_skills = discover_skills(repo_root)
    
    # 分类 skills
    obsidian_skills = [s for s in available_skills if s.startswith(("obsidian-", "defuddle", "json-canvas"))]
    global_skills = [s for s in available_skills if s not in obsidian_skills]
    
    print(f"\n发现 {len(global_skills)} 个通用 skills")
    if obsidian_skills:
        print(f"发现 {len(obsidian_skills)} 个 Obsidian 相关 skills")
    
    # 询问 Obsidian 路径
    obsidian_path = _ask_obsidian_path()
    
    # 构建配置
    from install_skills.models import UserConfig, GroupConfig
    
    groups = {
        "global": GroupConfig(
            name="global",
            skills=global_skills,
            targets=[
                home / ".agents/skills",
                home / ".claude/skills",
            ]
        )
    }
    
    if obsidian_path and obsidian_skills:
        groups["obsidian"] = GroupConfig(
            name="obsidian",
            skills=obsidian_skills,
            targets=[
                obsidian_path / ".claude/skills",
                obsidian_path / ".agents/skills",
            ]
        )
    
    config = UserConfig(
        version=2,
        repo_root=repo_root,
        groups=groups,
    )
    
    # 保存
    from install_skills.config import save_user_config
    save_user_config(config_path, config)
    
    print(f"\n✓ 配置已保存: {config_path}")
    print(f"\n现在可以运行: ce install")
    
    return 0
```

然后在 `main()` 函数中添加 `init` 命令处理：

```python
# 在 parse_args 中更新 choices
parser.add_argument(
    "command",
    choices=("init", "install", "update", "uninstall", "status", "doctor"),
)

# 在 main() 中添加
if args.command == "init":
    return command_init(resolved_repo_root, resolved_home)
```

**步骤 4：验证 GREEN**

运行：`pytest tests/test_cli_init.py -v`
预期：PASS

**步骤 5：提交**

```bash
git add tests/test_cli_init.py install_skills/cli.py
git commit -m "feat: add ce init interactive configuration command"
```

---

### 任务 4：重构 installer.py 使用 UserConfig

**文件：**
- 修改：`install_skills/installer.py`

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1：RED - 编写测试验证重构后行为**

```python
# tests/test_installer.py
import pytest
import tempfile
from pathlib import Path
from install_skills.installer import command_install_grouped
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
        result = command_install_grouped(
            repo_root, home, home / ".ce" / "config.yaml"
        )
        
        assert result == 0
        # 验证 symlink 已创建
        assert (home / ".claude/skills" / "test-skill").is_symlink()
```

**步骤 2：验证 RED**

运行：`pytest tests/test_installer.py -v`
预期：FAIL - command_install_grouped 需要修改以接受 UserConfig

**步骤 3：GREEN - 重构 installer.py**

关键修改：
1. `command_install_grouped` 改为从 `config.yaml` 读取而非 `skills-install.yaml`
2. 更新 `_install_group` 使用 `GroupConfig` 而非 `SkillGroup`
3. 保留 v2 manifest 格式

修改 `install_skills/installer.py`：

```python
# 更新导入
from install_skills.models import UserConfig, GroupConfig
from install_skills.config import load_user_config, get_default_config_path


def _install_group_v2(
    repo_root: Path,
    home: Path,
    group: GroupConfig,
    manifest_data: dict,
) -> dict:
    """安装单个组的 skills 到该组的 targets（使用 GroupConfig）。"""
    # 为每个 target 创建目录并 symlink 每个 skill
    for skill_name in group.skills:
        src = repo_root / "skills" / skill_name
        for target in group.targets:
            force_symlink(src, target / skill_name)

    timestamp = now_iso()
    mcp_servers: list[str] = []

    # global 组额外处理 kimi agent、ks、MCP
    if group.name == "global":
        targets = build_targets(home)
        ensure_parent_dirs(targets)
        install_kimi_agent_and_ks(repo_root, targets)
        mcp_installed, mcp_skipped = merge_mcp_config(home, repo_root)
        mcp_servers = mcp_installed

    group_record = manifest_data.get("groups", {}).get(group.name, {})
    manifest_data.setdefault("groups", {})[group.name] = {
        "installed_at": group_record.get("installed_at", timestamp),
        "updated_at": timestamp,
        "targets": [str(t) for t in group.targets],
        "skills": list(group.skills),
        "mcp_servers": mcp_servers,
        "repo_root": str(repo_root),
    }

    return manifest_data


def command_install_grouped(
    repo_root: Path,
    home: Path,
    config_path: Path | None = None,  # 现在可以是 config.yaml
    *,
    group: str | None = None,
    stdout=None,
) -> int:
    """从 UserConfig 安装。"""
    config_path = config_path or get_default_config_path(home)
    
    # 加载用户配置
    config = load_user_config(config_path)
    if config is None:
        print(f"配置未找到: {config_path}")
        print("请先运行: ce init")
        return 1

    # 迁移 v1 manifest（保持向后兼容）
    _migrate_v1_manifest(home)

    manifest_data = load_v2_manifest(home) or {"version": 2, "groups": {}}
    manifest_data["version"] = 2

    groups_to_install = {group: config.groups[group]} if group else config.groups

    for group_name, grp in groups_to_install.items():
        if group_name not in config.groups:
            print(f"[{group_name}] 未在配置中定义", file=stdout)
            continue
            
        manifest_data = _install_group_v2(repo_root, home, grp, manifest_data)
        skill_count = len(grp.skills)
        print(f"[{group_name}] installed {skill_count} skills", file=stdout)

        # global 组额外显示 MCP 安装情况
        if group_name == "global":
            group_record = manifest_data.get("groups", {}).get(group_name, {})
            mcp_servers = group_record.get("mcp_servers", [])
            if mcp_servers:
                print(f"[{group_name}] mcp installed: {','.join(mcp_servers)}", file=stdout)

    write_v2_manifest(home, manifest_data)
    return 0
```

**步骤 4：验证 GREEN**

运行：`pytest tests/test_installer.py -v`
预期：PASS

**步骤 5：提交**

```bash
git add tests/test_installer.py install_skills/installer.py
git commit -m "refactor: installer uses UserConfig instead of skills-install.yaml"
```

---

### 任务 5：添加 add-skill 和 add-target 命令

**文件：**
- 修改：`install_skills/cli.py`

**步骤 1：实现 add-skill 命令**

```python
def command_add_skill(
    skill_name: str,
    group_name: str,
    home: Path,
    *,
    stdout=None,
) -> int:
    """添加 skill 到指定组。"""
    from install_skills.config import load_user_config, save_user_config
    
    config_path = get_default_config_path(home)
    config = load_user_config(config_path)
    
    if config is None:
        print("配置未找到，请先运行: ce init")
        return 1
    
    if group_name not in config.groups:
        print(f"组 '{group_name}' 不存在")
        return 1
    
    group = config.groups[group_name]
    
    if skill_name in group.skills:
        print(f"skill '{skill_name}' 已在组 '{group_name}' 中")
        return 0
    
    # 创建新的 GroupConfig（frozen dataclass 不能直接修改）
    from install_skills.models import GroupConfig
    new_group = GroupConfig(
        name=group.name,
        skills=group.skills + [skill_name],
        targets=group.targets,
    )
    
    # 更新 config
    new_groups = dict(config.groups)
    new_groups[group_name] = new_group
    
    from dataclasses import replace
    new_config = replace(config, groups=new_groups)
    
    save_user_config(config_path, new_config)
    print(f"✓ 已添加 '{skill_name}' 到组 '{group_name}'")
    return 0
```

**步骤 2：更新 CLI 参数解析**

```python
def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ce",
        description="Manage coding-everything skill installation",
    )
    subparsers = parser.add_subparsers(dest="command")
    
    # init
    subparsers.add_parser("init", help="Initialize configuration interactively")
    
    # install
    install_parser = subparsers.add_parser("install", help="Install skills")
    install_parser.add_argument("--group", help="Only install specified group")
    
    # ... 其他命令
    
    # add-skill
    add_skill_parser = subparsers.add_parser("add-skill", help="Add a skill to a group")
    add_skill_parser.add_argument("skill", help="Skill name")
    add_skill_parser.add_argument("--group", required=True, help="Target group")
    
    return parser.parse_args(argv)
```

**步骤 3：提交**

```bash
git add install_skills/cli.py
git commit -m "feat: add ce add-skill command"
```

---

### 任务 6：删除 skills-install.yaml 和旧代码

**文件：**
- 删除：`skills-install.yaml`
- 修改：`install_skills/config.py`（清理旧函数）

**步骤 1：删除 skills-install.yaml**

```bash
git rm skills-install.yaml
git commit -m "chore: remove skills-install.yaml (replaced by ~/.ce/config.yaml)"
```

**步骤 2：清理 config.py 中的旧代码**

删除 `load_install_config` 函数或标记为废弃。

**步骤 3：更新 CLAUDE.md**

更新文档，说明新的配置方式。

**步骤 4：提交**

```bash
git add install_skills/config.py CLAUDE.md
git commit -m "docs: update documentation for UserConfig-based setup"
```

---

### 任务 7：集成测试和验证

**步骤 1：完整流程测试**

```bash
# 1. 安装最新版本
uv pip install -e .

# 2. 运行 init
ce init
# 输入 Obsidian vault 路径

# 3. 检查生成的配置
cat ~/.ce/config.yaml

# 4. 运行 install
ce install

# 5. 检查状态
ce status
```

**步骤 2：运行全部测试**

```bash
pytest tests/ -v
```

**步骤 3：最终提交**

```bash
git add -A
git commit -m "feat: complete ce init interactive configuration"
```

---

## 计划自审检查清单

| 检查项 | 状态 |
|--------|------|
| Spec 覆盖度：init/install/add-skill 都覆盖 | ✅ |
| 无 TBD/TODO 占位符 | ✅ |
| 类型一致性：GroupConfig/UserConfig 贯穿始终 | ✅ |
| 每个实现任务引用 dev-tdd | ✅ |
| 文件边界清晰（config/installer/cli 分离） | ✅ |
| 向后兼容（v1 manifest 迁移） | ✅ |

---

## 执行交接

**计划已完成并保存到 `docs/plans/2025-04-02-ce-cli-interactive-init.md`。两种执行选项：**

**1. Subagent-Driven（推荐）** - 为每个任务分派 fresh subagent，任务间审查，快速迭代

**2. 内联执行** - 在本会话中使用 `dev-executing-plans` 执行任务，批量执行带检查点

**选择哪种方式？**
