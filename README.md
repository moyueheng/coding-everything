# coding-everything

个人 AI 编程助手配置集合，支持 Kimi、OpenCode 等平台，跟踪多个上游优秀配置仓库。

## 这是什么项目？

本项目聚合了多个优秀的 AI 编程助手配置：

- **[obra/superpowers](https://github.com/obra/superpowers)** - AI 编程助手工作流框架（14 个核心skill）
- **[affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)** - Claude Code 完整配置（39 个skill）
- **[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)** - UI/UX Pro Max Skill
- **[kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)** - Obsidian agent skills 仓库
- **[vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)** - 单独镜像跟踪 `agent-browser` skill

## 快速开始

### 1. 克隆项目

```bash
git clone --recursive https://github.com/moyueheng/coding-everything.git
cd coding-everything
```

如果没有使用 `--recursive` 参数，请手动初始化子模块：

```bash
git submodule update --init --recursive
```

### 2. 安装共享 skill

使用自动化脚本（推荐）：

```bash
# 进入项目目录后执行
kimi # 让kimi自行安装, 会同时安装到kimi和codex
/skill:setup
```

或手动创建软链接：

```bash
# 创建软链接到共享 skill 目录
mkdir -p ~/.agents
ln -sf "$(pwd)/skills" ~/.agents/skills

# Agent 配置（可选）
mkdir -p ~/.kimi/agents
ln -sf "$(pwd)/kimi/agents/superpower" ~/.kimi/agents/superpower
```

### 3. 验证安装

```bash
ls ~/.agents/skills/
```

应该能看到类似 `dev-using-skills`、`dev-search-first`、`learn-deep-research` 等 skill 目录。

## 核心skill

### 开发工作流skill

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

### 辅助skill

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

### 系统级 skill

| skill | 用途 |
|------|------|
| `setup` | 安装本项目 skills 和 Kimi agent 配置 |
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

## 常用命令

### Git Submodule 管理

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

### 查看skill

```bash
# 列出所有可用skill
ls ~/.agents/skills/

# 查看skill详情
cat ~/.agents/skills/dev-tdd/SKILL.md

# 更新单独跟踪的 agent-browser skill
./scripts/sync-agent-browser-skill.sh
```

## 项目结构

```
coding-everything/
├── .agents/skills/          # 系统级 skills
│   ├── setup/               # 安装入口
│   └── update-upstream-repos/ # 上游更新与报告生成
├── skills/                  # 跨平台共享 skills
│   ├── dev-design-system/
│   ├── dev-search-first/
│   ├── dev-ui-styling/
│   ├── dev-continuous-agent-loop/
│   ├── agent-browser/         # 单独镜像跟踪的外部 skill
│   ├── learn-deep-research/
│   └── work-market-research/
├── scripts/                  # 本地同步脚本
│   └── sync-agent-browser-skill.sh
├── kimi/                    # Kimi 专属配置
│   └── agents/superpower/   # Agent 配置
├── opencode/                # OpenCode 配置（待完善）
├── upstream/                # 上游仓库（子模块）
│   ├── superpowers/         # superpowers 框架
│   ├── everything-claude-code/  # Claude Code 配置
│   ├── ui-ux-pro-max-skill/     # UI/UX Pro Max Skill
│   ├── humanizer-zh/            # 中文去痕工具
│   └── obsidian-skills/         # Obsidian agent skills
└── docs/                    # 文档
    └── upstream-updates/    # 上游更新报告
```

## 文档

详细文档请参考：

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

## 许可证

各上游仓库遵循其原有许可证。个人配置采用 MIT 许可证。
