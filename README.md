# coding-everything

个人 AI 编程助手配置集合，支持 Claude Code、Codex/OpenCode、Kimi 等平台，跟踪多个上游优秀配置仓库。

## 这是什么项目？

本项目聚合了多个优秀的 AI 编程助手配置：

- **[obra/superpowers](https://github.com/obra/superpowers)** - AI 编程助手工作流框架（14 个核心skill）
- **[affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)** - Claude Code 完整配置（39 个skill）
- **[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)** - UI/UX Pro Max Skill
- **[kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)** - Obsidian agent skills 仓库
- **[MarsWang42/OrbitOS](https://github.com/MarsWang42/OrbitOS)** - AI 驱动的 Obsidian 个人生产力系统
- **[vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)** - 单独镜像跟踪 `agent-browser` skill

## 快速开始

### 前置条件

- [uv](https://docs.astral.sh/uv/) — Python 包管理器
- Python >= 3.12

### 1. 克隆项目

```bash
git clone --recursive https://github.com/moyueheng/coding-everything.git
cd coding-everything
```

如果没有使用 `--recursive` 参数，请手动初始化子模块：

```bash
git submodule update --init --recursive
```

### 2. 安装 ce 命令

```bash
uv tool install -e .
```

这会注册一个 `ce` 命令到 PATH 中，可全局直接使用。`-e` 表示 editable 模式，仓库代码改动后无需重新安装。

### 3. 安装 skill

```bash
# 安装所有组
ce install
```

默认安装两组 skill：

| 组 | 安装位置 | 内容 |
|------|------|------|
| `global` | `~/.agents/skills/` + `~/.claude/skills/` | 开发工作流 skill、Kimi agent、ks 命令、MCP 配置 |
| `obsidian` | `~/00-Life/ob-note/.claude/skills/` + `.agents/skills/` | Obsidian 编辑相关 skill（只在 vault 内生效） |

### 4. 验证安装

```bash
ce status
```

输出示例：

```
[global] installed=25 missing=0 drifted=0
  mcp: configured=auggie-mcp,...
[obsidian] installed=5 missing=0 drifted=0
  targets: ~/00-Life/ob-note/.claude/skills, ~/00-Life/ob-note/.agents/skills
```

## 常用命令

```bash
ce install                        # 安装所有组
ce install --group obsidian       # 只安装 obsidian 组
ce update                         # 更新所有组
ce update --group global          # 只更新 global 组
ce uninstall                      # 卸载所有组
ce uninstall --group obsidian     # 只卸载 obsidian 组
ce status                         # 查看所有组状态
ce status --group global          # 只查看 global 组
```

## 分组安装机制

skill 通过 `skills-install.yaml` 配置文件分组管理：

```yaml
groups:
  global:
    skills: [dev-tdd, dev-debugging, ...]
    targets:
      - ~/.agents/skills
      - ~/.claude/skills

  obsidian:
    skills: [obsidian-markdown, obsidian-bases, ...]
    targets:
      - ~/00-Life/ob-note/.claude/skills
      - ~/00-Life/ob-note/.agents/skills
```

- **global 组**：额外处理 kimi agent、ks 命令、MCP 服务器配置
- **非 global 组**：只做 skill symlink，安装到项目级目录
- 安装状态记录在 `~/.ce/install-manifest.json`
- 每组可独立安装、更新、卸载，互不影响

### 新增项目级分组

1. 把 skill 目录放到 `skills/` 下
2. 在 `skills-install.yaml` 中添加新组和 targets
3. 运行 `ce install --group <新组名>`

## 核心 skill

### 开发工作流 skill

| skill | 用途 | 触发场景 |
|------|------|----------|
| `dev-using-skills` | skill入口 | 不知道用什么skill时先执行这个，并明确用户请求 / AGENTS.md / skill 的优先关系 |
| `dev-brainstorming` | 头脑风暴 | 开始任何新功能前，先做设计并完成设计审查闭环 |
| `dev-writing-plans` | 编写计划 | 需要将任务分解为可执行步骤，并对计划做分段审查收口 |
| `dev-executing-plans` | 执行计划 | 按计划一步步实现 |
| `dev-tdd` | 测试驱动开发 | 写代码前先写测试 |
| `dev-debugging` | 调试 | 遇到 Bug 时 |
| `dev-verification` | 验证 | 完成任务前检查 |
| `dev-requesting-review` | 代码审查 | 需要审查代码时 |
| `dev-finishing-branch` | 完成分支 | 合并代码前 |
| `dev-git-worktrees` | Git 工作树 | 隔离多个任务 |

### 辅助 skill

| skill | 用途 |
|------|------|
| `dev-writing-skills` | 编写新的skill |
| `dev-code-cleanup` | 清理死代码 |
| `dev-update-codemaps` | 更新代码地图文档 |
| `dev-search-first` | 编码前先检索现成方案 |
| `dev-backend-patterns` | 后端架构模式 |
| `dev-frontend-patterns` | 前端架构模式 |
| `dev-design-system` | 设计 token、语义层和组件状态模式 |
| `dev-ui-styling` | 高质量 UI 样式实现与可访问性约束 |
| `dev-continuous-agent-loop` | 持续 agent 循环与自动化执行模式 |
| `learn-deep-research` | 通用深度调研与正式研究报告 |
| `work-market-research` | 市场、竞品、价格与区域机会调研 |
| `agent-browser` | 浏览器自动化 CLI 使用与网页交互 workflow |

### Obsidian skill（项目级安装）

| skill | 用途 |
|------|------|
| `obsidian-markdown` | Obsidian Flavored Markdown 编辑 |
| `obsidian-bases` | Obsidian Bases 语法编辑 |
| `json-canvas` | JSON Canvas 文件编辑 |
| `obsidian-cli` | Obsidian CLI 与 vault 交互 |
| `defuddle` | 网页提取为干净 markdown |

### 系统级 skill

| skill | 用途 |
|------|------|
| `setup` | 安装本项目共享 skills、Kimi agent 和 `ks` |
| `update-upstream-repos` | 更新 `upstream/` submodule、整理 commit 变化并生成 `docs/` 报告 |

## 典型工作流

```
1. dev-brainstorming → 完善需求、边界条件
              ↓
2. dev-writing-plans → 拆分为 2-5 分钟任务
              ↓
3. dev-executing-plans → 按步骤实现
              ↓
4. dev-tdd → RED → GREEN → REFACTOR
              ↓
5. dev-requesting-review → 检查清单验证
              ↓
6. dev-finishing-branch → 验证并合并
```

**重要原则**：任何行动前先检查是否有适用的 skill。

## Git Submodule 管理

```bash
# 更新所有子模块到最新
git submodule update --remote

# 将本次有变化的子模块切回本地 main，避免停在 detached HEAD
uv run .agents/skills/update-upstream-repos/scripts/switch_updated_submodules_to_main.py

# 更新特定子模块
cd upstream/superpowers && git pull origin main

# 生成上游更新摘要
uv run .agents/skills/update-upstream-repos/scripts/generate_upstream_report.py
```

约束：所有 `upstream/` 子模块都显式跟踪 `main` 分支，避免因远端默认分支变化导致漂移。执行 `git submodule update --remote` 后，还要把已变化的子模块切回本地 `main`，否则 Git 常会把工作树留在 detached HEAD。

## 项目结构

```
coding-everything/
├── install_skills/             # ce CLI 工具 Python 包
│   ├── cli.py                  # 命令行入口
│   ├── config.py               # skills-install.yaml 加载
│   ├── installer.py            # symlink / manifest / MCP 逻辑
│   └── models.py               # 数据结构
├── pyproject.toml              # Python 包定义（ce CLI 入口）
├── skills-install.yaml         # skill 分组安装配置
├── skills/                     # 跨平台共享 skills
│   ├── dev-tdd/
│   ├── dev-brainstorming/
│   ├── obsidian-markdown/      # 从上游迁移的 Obsidian skill
│   ├── agent-browser/          # 单独镜像跟踪的外部 skill
│   └── ...
├── .agents/skills/             # 系统级 skills
│   ├── setup/                  # 安装入口
│   └── update-upstream-repos/  # 上游更新与报告生成
├── kimi/                       # Kimi 专属配置
│   └── agents/superpower/      # Agent 配置
├── scripts/                    # 同步脚本
├── mcp-configs/                # MCP 服务器配置模板
├── upstream/                   # 上游仓库（子模块）
└── docs/                       # 文档
```

## 文档

- **[AGENTS.md](./AGENTS.md)** - 完整项目文档，包含架构、约定、工作流等
- **[docs/kimi-skills-architecture.md](./docs/kimi-skills-architecture.md)** - 共享 skill 架构全景图和调用关系
- `docs/upstream-updates/YYYY-MM-DD-upstream-updates.md` - 使用 `update-upstream-repos` skill 生成和维护的上游更新报告

## 上游仓库

| 仓库 | 说明 |
|------|------|
| [obra/superpowers](https://github.com/obra/superpowers) | AI 编程助手工作流框架 |
| [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | Claude Code 完整配置 |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | UI/UX Pro Max Skill |
| [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) | Obsidian agent skills 仓库 |
| [MarsWang42/OrbitOS](https://github.com/MarsWang42/OrbitOS) | AI 驱动的 Obsidian 个人生产力系统 |

## 许可证

各上游仓库遵循其原有许可证。个人配置采用 MIT 许可证。
