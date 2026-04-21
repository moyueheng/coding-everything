# install_skills 模块

`ce` CLI 的核心实现，负责将 `skills/` 目录下的 skill 以 symlink 方式安装到多个目标位置，并管理 MCP 配置合并和 manifest 追踪。

## 文件结构

| 文件 | 职责 |
|------|------|
| `__init__.py` | 包入口，声明 `__version__` |
| `models.py` | 不可变数据结构（frozen dataclass） |
| `config.py` | 用户配置 `~/.ce/config.yaml` 的加载与持久化 |
| `cli.py` | argparse 命令路由，交互式 init，add-skill/add-target |
| `installer.py` | 核心安装逻辑：symlink、manifest、MCP 合并、v1→v2 迁移 |

## 数据流

```
~/.ce/config.yaml          (用户配置，定义 groups/skills/targets)
        │
        ▼
cli.py main()               解析命令行参数，路由到对应 command_* 函数
        │
        ▼
installer.py                读取配置 → discover_skills → force_symlink → 写 manifest
        │
        ├─► ~/.agents/skills/<skill>     symlink
        ├─► ~/.claude/skills/<skill>     symlink
        ├─► ~/.kimi/agents/superpower    symlink  (仅 global 组)
        ├─► ~/.local/bin/ks              symlink  (仅 global 组)
        ├─► ~/.claude.json               MCP 配置合并 (仅 global 组)
        └─► ~/.ce/install-manifest.json  v2 manifest
```

## 两种配置模式

### 模式 A：UserConfig（推荐）

存在 `~/.ce/config.yaml` 时优先使用。由 `ce init` 交互式生成。

```yaml
version: 2
repo_root: /path/to/coding-everything
groups:
  global:
    skills: [dev-tdd, dev-debugging, ...]
    targets:
      - ~/.agents/skills
      - ~/.claude/skills
  obsidian:
    skills: [obsidian-markdown, obsidian-cli, ...]
    targets:
      - ~/Documents/ObsidianVault/.claude/skills
      - ~/Documents/ObsidianVault/.agents/skills
```

路由函数：`command_install_from_config`、`command_uninstall_from_config`、`command_status_from_config`、`command_doctor_from_config`。

### 模式 B：Legacy（向后兼容）

`~/.ce/config.yaml` 不存在时，回退到仓库根的 `skills-install.yaml`。

路由函数：`command_install_grouped`、`command_uninstall_grouped`、`command_status_grouped`、`command_doctor`。

再往下退化为无分组模式（`command_install`、`command_update` 等）。

## 关键数据结构（models.py）

所有 dataclass 均 `frozen=True`，通过 `dataclasses.replace()` 创建新实例。

| 结构 | 用途 |
|------|------|
| `SkillGroup` | YAML 分组（legacy 模式） |
| `GroupManifest` | Manifest 中一个组的安装记录 |
| `ManifestV2` | v2 manifest 顶层结构 |
| `GroupConfig` | 用户配置中一个组的定义 |
| `UserConfig` | `~/.ce/config.yaml` 的内存表示 |

## Manifest（v2）

路径：`~/.ce/install-manifest.json`

```json
{
  "version": 2,
  "groups": {
    "global": {
      "installed_at": "2026-...",
      "updated_at": "2026-...",
      "targets": ["~/.agents/skills", "~/.claude/skills"],
      "skills": ["dev-tdd", ...],
      "mcp_servers": ["auggie-mcp", ...],
      "repo_root": "/path/to/coding-everything"
    },
    "obsidian": { ... }
  }
}
```

卸载时以 manifest 为准，只删除 manifest 中记录的条目。

## MCP 配置合并

`installer.py` 中的 `merge_mcp_config()` 负责：

1. 从 `mcp-configs/required.json` 加载模板
2. 解析已有的 `~/.claude.json` 获取现有配置
3. 从现有配置或环境变量中提取 `ZAI_API_KEY`
4. 将 `{{ZAI_API_KEY}}` 占位符替换为真实值
5. 合并到 `~/.claude.json` 的 `mcpServers` 字段

## v1→v2 迁移

`_migrate_v1_manifest()` 在每次安装时自动检查：

- 旧路径：`~/.local/share/coding-everything/install-manifest.json`（无 `version` 字段）
- 新路径：`~/.ce/install-manifest.json`（`version: 2`）
- 迁移后将扁平结构包装为分组结构，删除旧文件

## CLI 命令

| 命令 | 说明 |
|------|------|
| `ce init` | 交互式初始化配置（扫描 skills、询问 Obsidian 路径） |
| `ce install [--group NAME]` | 安装指定组或全部组 |
| `ce update [--group NAME]` | 同 install（幂等） |
| `ce uninstall [--group NAME]` | 卸载并清理 manifest |
| `ce status [--group NAME]` | 检查 symlink 状态（installed/missing/drifted） |
| `ce doctor` | 诊断损坏的 symlink 等环境问题 |
| `ce add-skill SKILL --group GROUP` | 向配置中的组添加 skill |
| `ce add-target PATH --group GROUP` | 向配置中的组添加 target 目录 |
| `ce sync [--group NAME]` | 对齐实际安装与 config（安装缺失 + 清理多余） |

## Repo Root 自愈

存在 `~/.ce/config.yaml` 时，`ce install/update/status/sync/doctor/uninstall` 会先检查配置中的 `repo_root`。如果旧 `repo_root` 已不存在，且当前运行路径看起来是本项目仓库根目录（包含 `skills/`、`install_skills/`、`pyproject.toml`），CLI 会自动把 `repo_root` 更新到当前仓库路径。这样用户把 `Projects` 改名为 `01-Projects` 后，只需在新仓库路径运行 `ce update`，即可重建 symlink 并刷新 manifest。

## 依赖

- Python >= 3.12
- pyyaml >= 6.0（唯一外部依赖）
- 入口点定义在 `pyproject.toml`：`ce = "install_skills.cli:main"`
