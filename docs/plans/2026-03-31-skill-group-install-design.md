# Skill 分组安装设计

## 动机

当前安装器（`scripts/install_skills.py`）只支持全局安装，所有 skill symlink 到 `~/.agents/skills/` 和 `~/.claude/skills/`。部分 skill（如 obsidian-skills）只需在特定项目目录下生效，不应污染全局环境。

## 目标

- 支持将 skill 按"组"安装到不同目标目录（全局或项目级）
- 用声明式配置文件管理分组
- 安装器改造为 `ce` CLI 工具，通过 `uv tool install -e` 直接执行
- 迁移 upstream/obsidian-skills 作为第一个项目级分组

## 非目标

- 不支持 skill 安装到多个项目（每个组对应固定目标路径）
- 不自动同步上游 skill（仍手动 cp + 更新 UPSTREAM.md）
- 不改变 symlink 机制本身

---

## 设计

### 1. 分类配置文件 `skills-install.yaml`

仓库根目录，声明所有分组：

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

规则：
- `global` 组是特殊名称，承担 kimi agent、ks、MCP 的安装（额外职责）
- 非 `global` 组只做 skill symlink
- `targets` 支持 `~` 展开
- skill 列表显式声明，未在配置中出现的 skill 不安装
- 如果 `skills-install.yaml` 不存在，退化为现有行为（自动 discover + 全局安装），保持向后兼容

### 2. 工具入口

把安装器改造为 Python 包，通过 `pyproject.toml` 声明 CLI 入口：

```bash
uv tool install -e /path/to/coding-everything   # 一次性安装
ce install                                        # 安装所有组
ce install --group obsidian                       # 只安装 obsidian 组
ce update                                         # 更新所有组
ce update --group obsidian                        # 只更新 obsidian 组
ce uninstall                                      # 卸载所有组
ce uninstall --group obsidian                     # 只卸载 obsidian 组
ce status                                         # 显示所有组状态
ce status --group global                          # 只显示 global 组
```

`uv tool install -e` 以 editable 模式安装，仓库代码改动直接生效。

删除 Makefile，统一用 `ce` 命令。

### 3. 包结构

```
coding-everything/
├── pyproject.toml          # [project.scripts] ce = "install_skills.cli:main"
├── install_skills/         # Python 包（原 scripts/install_skills.py 拆分）
│   ├── __init__.py
│   ├── cli.py              # 命令行入口、参数解析
│   ├── config.py           # skills-install.yaml 加载与解析
│   ├── installer.py        # symlink / manifest / MCP 逻辑
│   └── models.py           # InstallTargets, InstallGroup 等数据结构
├── skills-install.yaml     # 分组配置
├── tests/
│   └── test_install_skills.py
└── ...
```

### 4. Manifest 分组

路径：`~/.ce/install-manifest.json`

```json
{
  "version": 2,
  "groups": {
    "global": {
      "repo_root": "/Users/moyueheng/Projects/moyueheng/coding-everything",
      "installed_at": "2026-03-31T12:00:00+00:00",
      "updated_at": "2026-03-31T12:00:00+00:00",
      "targets": [
        "/Users/moyueheng/.agents/skills",
        "/Users/moyueheng/.claude/skills"
      ],
      "skills": ["dev-tdd", "dev-debugging"],
      "mcp_servers": ["auggie-mcp", "zai-github-read"]
    },
    "obsidian": {
      "installed_at": "2026-03-31T12:00:00+00:00",
      "updated_at": "2026-03-31T12:00:00+00:00",
      "targets": [
        "/Users/moyueheng/Documents/ObsidianVault/.claude/skills",
        "/Users/moyueheng/Documents/ObsidianVault/.agents/skills"
      ],
      "skills": ["obsidian-markdown", "obsidian-bases"]
    }
  }
}
```

规则：
- 遇到无 `version` 字段的 v1 manifest，自动迁移为 v2 的 `global` 组
- `global` 组有 `repo_root` 和 `mcp_servers`，其他组没有
- 每组独立的 `targets`，卸载时只清理该组登记过的 symlink
- targets 存绝对路径，写入时展开 `~`

### 5. obsidian-skills 迁移

从 `upstream/obsidian-skills/skills/` 物理复制到 `skills/`：

```
skills/
├── obsidian-markdown/      # UPSTREAM.md 记录来源
├── obsidian-bases/
├── json-canvas/
├── obsidian-cli/
├── defuddle/
└── ...                     # 现有 skill
```

- 物理复制，和现有 skill 管理方式一致
- 每个 skill 目录下维护 `UPSTREAM.md`（来源仓库、分支、最后同步 SHA）
- 同步方式：手动 `cp -r upstream/obsidian-skills/skills/<name>/ skills/<name>/`

### 6. Status 输出

```bash
$ ce status
[global] installed=24 missing=0 drifted=0
  mcp: configured=auggie-mcp,zai-github-read,zai-web-reader,zai-web-search-prime
[obsidian] installed=5 missing=0 drifted=0
  targets: ~/Documents/ObsidianVault/.claude/skills, ~/Documents/ObsidianVault/.agents/skills

$ ce status --group global
[global] installed=24 missing=0 drifted=0
  mcp: configured=auggie-mcp,zai-github-read,zai-web-reader,zai-web-search-prime
```

按组分行，组名用方括号标注，每组显示 targets 路径。

---

## 验收标准

- [ ] `ce install` 安装所有组的 skill 到各自 targets
- [ ] `ce install --group obsidian` 只安装 obsidian 组
- [ ] `ce update` 更新所有组
- [ ] `ce uninstall --group obsidian` 只卸载 obsidian 组，不影响 global
- [ ] `ce status` 按组显示状态
- [ ] v1 manifest 自动迁移为 v2
- [ ] `skills-install.yaml` 不存在时退化为现有行为
- [ ] 旧版 `~/.local/share/coding-everything/install-manifest.json` 在迁移后被清理
- [ ] 测试覆盖率 >= 80%
- [ ] ruff check 全部通过
