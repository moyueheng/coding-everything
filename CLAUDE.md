# coding-everything 项目文档

## 目录

- [共享 Skills 架构图](./docs/skills-architecture.md) - 技能关系图和调用流程可视化
- [CODEMAPS](./docs/CODEMAPS/INDEX.md) - 面向 AI 上下文的 token-lean 架构索引（由 `scripts/generate_codemaps.py` 自动生成）
- [Agent 上下文加载机制](./docs/agent-context-loading.md) - Codex、Claude Code、Kimi CLI 与 OpenCode 在嵌套 Git 工作区中的 `AGENTS.md`、`CLAUDE.md` 和 skill 加载边界对比
- [Agent Context 模板](./docs/templates/agent-context/) - 全局、开发、生活、Obsidian 多工作区 agent context 模板和 Kimi/OpenCode wrapper 示例
- [项目 Roadmap](./docs/ROADMAP.md) - 项目分阶段规划、能力边界、非目标与里程碑
- [Skills-Manager 架构调研](./docs/2026-04-23-skills-manager-architecture-research.md) - `jiweiyeah/Skills-Manager` 的公开能力边界、架构推断与对本仓库 roadmap 的启发
- [PM Skills 迁移待办](./docs/product-manager-skills-migration-backlog.md) - Product Manager Skills 分批迁移清单
- [项目概述](#项目概述)
  - [跟踪的上游仓库](#跟踪的上游仓库)
  - [个人配置](#个人配置)
- [项目结构](#项目结构)
- [上游仓库详情](#上游仓库详情)
  - [superpowers](#1-superpowers)
  - [everything-claude-code](#2-everything-claude-code)
  - [obsidian-skills](#3-obsidian-skills)
- [个人 Kimi 配置](#个人-kimi-配置)
  - [skill列表](#skill列表)
  - [快速安装](#快速安装)
- [Git Submodule 管理](#git-submodule-管理)
  - [克隆包含 submodules 的项目](#克隆包含-submodules-的项目)
  - [初始化 submodules](#初始化-submodules如果已克隆但没有-submodules)
  - [更新所有 submodules](#更新所有-submodules-到最新)
  - [更新特定 submodule](#更新特定-submodule)
  - [添加新的 submodule](#添加新的-submodule)
- [核心工作流](#核心工作流)
- [开发约定](#开发约定)
  - [使用skill时](#使用skill时)
  - [skill开发](#skill开发)
  - [脚本开发](#脚本开发)
  - [文档同步（AGENTS/CLAUDE）](#文档同步agentsclaude)
  - [多工具嵌套工作区](#多工具嵌套工作区)
  - [命名规范](#命名规范)
- [资源链接](#资源链接)
  - [上游仓库](#上游仓库)
  - [平台文档](#平台文档)
  - [Skill 标准](#skill-标准)
- [许可证](#许可证)

---

## 项目概述

本项目 (`coding-everything`) 是个人 AI 编程助手配置集合，通过 Git Submodule 跟踪多个上游配置仓库，并维护自己的专属配置。

### 跟踪的上游仓库

| 仓库 | 用途 | 路径 |
|------|------|------|
| [obra/superpowers](https://github.com/obra/superpowers.git) | AI 编程助手工作流框架 | `upstream/superpowers/` |
| [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code.git) | Claude Code 完整配置 | `upstream/everything-claude-code/` |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git) | UI/UX Pro Max Skill | `upstream/ui-ux-pro-max-skill/` |
| [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh.git) | AI 写作去痕工具（中文版） | `upstream/humanizer-zh/` |
| [deanpeters/Product-Manager-Skills](https://github.com/deanpeters/Product-Manager-Skills.git) | Product Manager 相关 skill 集合 | `upstream/product-manager-skills/` |
| [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills.git) | Obsidian agent skills 仓库 | `upstream/obsidian-skills/` |
| [MarsWang42/OrbitOS](https://github.com/MarsWang42/OrbitOS.git) | AI 驱动的 Obsidian 个人生产力系统 | `upstream/orbitos/` |
| [Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki.git) | Karpathy 风格 LLM Wiki 构建工具 | `upstream/karpathy-llm-wiki/` |
| [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills.git) | Karpathy 编码行为指南 skill | `upstream/karpathy-skills/` |

### 个人配置

| 平台 | 路径 | 状态 |
|------|------|------|
| **共享 skills** | `skills/` | ✅ 已配置（46 个含 `SKILL.md` 的 skill） |
| **Kimi** | `kimi/` | ✅ 已配置（agent/config） |
| **Claude Code** | 通过 `ce` CLI 写入 `~/.claude/skills/` 或项目级 `.claude/skills/` | ✅ 已兼容 |
| **OpenCode** | `opencode/` | 🏗️ 开发中（12 个skill目录，1 个已完成） |

---

## 项目结构

```
coding-everything/
├── README.md                   # 项目简介
├── AGENTS.md                   # 本文档
├── .gitmodules                 # Git submodule 配置
├── .agents/
│   └── skills/                 # 系统级 skills
│       ├── setup/              # 安装 skill
│       ├── update-upstream-repos/ # 上游更新与报告生成 skill
│       └── dev-creating-subagents/ # 创建和管理 subagent
│
├── skills/                     # 跨平台共享 skills
│   ├── agent-browser/          # 单独镜像跟踪的外部浏览器自动化 skill
│   ├── obsidian-markdown/      # Obsidian Flavored Markdown 编辑（从上游迁移）
│   ├── obsidian-bases/         # Obsidian Bases 语法编辑
│   ├── json-canvas/            # JSON Canvas 文件编辑
│   ├── obsidian-cli/           # Obsidian CLI 与 vault 交互
│   ├── defuddle/               # 网页提取为干净 markdown
│   ├── dev-using-skills/
│   ├── dev-brainstorming/
│   ├── dev-debugging/
│   ├── dev-tdd/
│   ├── dev-writing-plans/
│   ├── dev-executing-plans/
│   ├── dev-git-worktrees/
│   ├── dev-requesting-review/
│   ├── dev-verification/
│   ├── dev-finishing-branch/
│   ├── dev-writing-skills/
│   ├── dev-code-cleanup/
│   ├── dev-update-codemaps/
│   ├── dev-search-first/
│   ├── dev-backend-patterns/
│   ├── dev-frontend-patterns/
│   ├── dev-design-system/
│   ├── dev-ui-styling/
│   ├── dev-continuous-agent-loop/
│   ├── dev-e2e-testing/
│   ├── learn-deep-research/
│   ├── learn-llm-wiki/ # Karpathy 风格 LLM Wiki 构建与维护
│   ├── work-market-research/
│   ├── tool-humanizer-zh/
│   └── tool-macos-hidpi/
├── install_skills/             # ce CLI 工具 Python 包
│   ├── __init__.py
│   ├── cli.py                  # 命令行入口
│   ├── config.py               # 用户级 ~/.ce/config.yaml 加载
│   ├── installer.py            # symlink / manifest / MCP 逻辑
│   └── models.py               # 数据结构
├── pyproject.toml              # Python 包定义（ce CLI 入口）
├── mcp-configs/                # MCP 服务器配置模板
│   └── required.json           # 必装 MCP 定义（auggie-mcp / zai / context7）
├── scripts/                    # 本地同步与工具脚本
│   ├── sync-agent-browser-skill.sh # 同步 vercel-labs/agent-browser skill
│   └── generate_codemaps.py    # codemap 生成器（扫描仓库 → docs/CODEMAPS/）
│
├── tests/                      # 测试
│   ├── conftest.py             # 将 scripts/ 加入 sys.path
│   └── test_generate_codemaps.py # codemap 生成器测试
│
├── kimi/                       # Kimi 专属配置
│   ├── README.md
│   └── agents/
│       └── superpower/         # agent 配置
│           ├── agent.yaml
│           ├── system.md
│           └── README.md
│
├── opencode/                   # OpenCode 配置
│   ├── README.md
│   ├── plugins/                # 插件目录
│   └── skills/                 # skill目录（待填充）
│
├── docs/                       # 文档
│   ├── CODEMAPS/               # token-lean 架构索引，由 scripts/generate_codemaps.py 自动生成
│   ├── agent-context-loading.md # 多工具指令文件与 skill 加载机制对比
│   ├── templates/agent-context/ # 多工作区 agent context 模板
│   └── upstream-updates/       # 上游更新报告
│
└── upstream/                   # 上游仓库（git submodules）
    ├── superpowers/            # superpowers 框架
    │   ├── skills/             # 14 个核心skill
    │   ├── .opencode/          # OpenCode 集成
    │   └── ...
    │
    ├── everything-claude-code/ # everything-claude-code 配置
    │   ├── .claude/            # Claude 配置
    │   ├── .cursor/            # Cursor 编辑器配置
    │   ├── .opencode/          # OpenCode 配置
    │   └── ...
    │
    ├── ui-ux-pro-max-skill/    # UI/UX Pro Max Skill
    │   └── ...
    │
    ├── humanizer-zh/           # AI 写作去痕工具（中文版）
    │   ├── SKILL.md
    │   └── README.md
    │
    ├── product-manager-skills/ # Product Manager skill 集合
    │   ├── README.md
    │   └── skills/             # PM 工作流相关 skill
    │
    ├── obsidian-skills/        # Obsidian agent skills
    │   ├── README.md
    │   └── skills/             # Obsidian / Bases / Canvas / CLI 等 skill
    │
    └── orbitos/                # AI 驱动的 Obsidian 个人生产力系统
        ├── README.md
        └── EN/                 # 英文版 vault 模板与 AI workflow

    └── karpathy-llm-wiki/      # Karpathy 风格 LLM Wiki 构建工具
        ├── SKILL.md
        ├── README.md
        └── references/         # 文章/索引/归档模板

    └── karpathy-skills/        # Karpathy 编码行为指南
        ├── skills/karpathy-guidelines/  # 单 skill：编码行为准则
        ├── CLAUDE.md           # 同内容可作为 CLAUDE.md 注入
        └── CURSOR.md           # Cursor 编辑器版本
```

---

## 上游仓库详情

### 1. superpowers

**简介**: 为 AI 编程助手设计的综合软件开发工作流框架

**当前跟踪版本**: `b557648`（2026-04-16，post-v5.0.7）

**核心skill**:
- `using-superpowers` - skill使用入口
- `brainstorming` - 编码前设计完善（v5.0.6 已同步内联自审模式）
- `test-driven-development` - TDD 循环
- `systematic-debugging` - 系统化调试
- `writing-plans` / `executing-plans` - 计划编写与执行（v5.0.6 已同步内联自审模式）
- `finishing-a-development-branch` - 分支完成工作流
- 等等（共 14 个）

**支持平台**: Claude Code, Codex, OpenCode

**同步状态**: 
- ✅ `dev-brainstorming` 已同步 v5.0.6 内联自审模式（替代 subagent review loop）
- ✅ `dev-writing-plans` 已同步 v5.0.6 内联自审模式（替代 subagent review loop）
- ✅ 当前跟踪到 `b557648`，README 已补充 OpenAI Codex CLI / Codex App 插件安装入口；本地 skill 内容本次无变化

### 2. everything-claude-code

**简介**: 完整的 Claude Code 配置集合

**内容**:
- `.claude/` - Claude 专属配置
- `.cursor/` - Cursor 编辑器配置
- `.opencode/` - OpenCode 配置
- `skills/` - 69+ 个skill（持续增长）
- `agents/` - 28+ 个 agent 配置
- `commands/` - 58+ 个预定义命令
- `hooks/` - 会话钩子
- `docs/zh-CN/skills/` - **32 个简体中文skill**（引入时无需翻译）
- `ecc2/` - ECC 2.0 Rust TUI 脚手架（alpha），近期新增 board observability 原型（`session_board` 元数据 + dashboard Board pane）

**值得关注的 skill（尚未引入）**:
| skill | 用途 | 引入障碍 |
|-------|------|----------|
| `ck` (context-keeper) | 持久化项目记忆，跨会话恢复上下文 | 需要 Node.js + Claude Code hook 系统，Kimi 不完全兼容 |
| `git-workflow` | Git 工作流最佳实践（分支策略、提交规范、PR 流程） | 与 `dev-git-worktrees` 互补，可考虑整合 |
| `rules-distill` | 规则提炼与整理 | 待评估 |
| `architecture-decision-records` | 架构决策记录管理 | 待评估 |

### 3. obsidian-skills

**简介**: 面向 Obsidian 的 agent skills 仓库，遵循 Agent Skills 开放标准，可供 Claude Code、Codex CLI、OpenCode 等兼容环境使用

**迁移状态**: ✅ 已迁移到 `skills/` 目录（obsidian-markdown, obsidian-bases, json-canvas, obsidian-cli, defuddle），每个目录含 `UPSTREAM.md` 跟踪来源

**内容**:
- `skills/obsidian-markdown/` - Obsidian Flavored Markdown 编辑
- `skills/obsidian-bases/` - Obsidian Bases 语法编辑
- `skills/json-canvas/` - JSON Canvas 文件编辑
- `skills/obsidian-cli/` - Obsidian CLI 与 vault 交互
- `skills/defuddle/` - 网页提取为干净 markdown

### 4. orbitos

**简介**: AI 驱动的 Obsidian 个人生产力系统，通过自然语言与 AI 助手管理知识库和日常任务规划

**内容**:
- `EN/` - 英文版 vault 模板，包含完整的文件夹结构、Prompts、Templates
- `99_System/Prompts/` - AI persona 提示词（Claude Code / Gemini CLI 可用）
- `99_System/Templates/` - Markdown 模板（Daily、Project、Research、Wiki 等）
- 核心 workflow 命令：`/start-my-day`、`/kickoff`、`/research`、`/ask`、`/brainstorm`、`/parse-knowledge`、`/archive`

**迁移状态**:
- ✅ 已迁移 9 个 workflow skill 到 `skills/`：`life-start-my-day`、`life-kickoff`、`life-research`、`life-brainstorm`、`life-ask`、`life-parse-knowledge`、`life-archive`、`life-ai-newsletters`、`life-ai-products`
- ✅ obsidian 组互斥规则：`learn-llm-wiki`、`life-ask`、`life-parse-knowledge`、`life-start-my-day` 等只归入 obsidian 组，不重复安装到 global
- ✅ 本地适配统一使用 `20_Project/`，不保留 `20_Projects/` 兼容层

### 5. karpathy-skills

**简介**: 基于 Andrej Karpathy 观察总结的 LLM 编码行为指南，遵循 Agent Skills 开放标准

**内容**:
- `skills/karpathy-guidelines/` - 编码行为准则 skill（Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution）
- `CLAUDE.md` - 同内容可注入项目级 CLAUDE.md
- `CURSOR.md` - Cursor 编辑器版本
- `EXAMPLES.md` - 使用示例

**核心原则**:
1. **Think Before Coding** — 不假设、不隐藏困惑、呈现权衡
2. **Simplicity First** — 最小代码解决问题，不做推测性设计
3. **Surgical Changes** — 只改必须改的，只清理自己制造的遗留
4. **Goal-Driven Execution** — 定义可验证的成功标准，循环直到确认通过

**迁移状态**: 📋 待评估是否引入到 `skills/`

---

## 个人 Kimi 配置

共享 skill 基于 Agent Skills 标准组织；`kimi/` 目录仅保留 Kimi Code CLI 专属 agent/config。

### skill列表

| skill | 用途 | 类型 |
|------|------|------|
| `dev-using-skills` | 入口点 - skill使用方法与指令优先级 | 严格 |
| `dev-brainstorming` | 编码前苏格拉底式对话与设计审查闭环（审查清单外置） | 严格 |
| `dev-debugging` | 四阶段调试流程 | 严格 |
| `dev-tdd` | 测试驱动开发 | 严格 |
| `dev-writing-plans` | 编写实施计划与分段审查收口（审查清单外置） | 严格 |
| `dev-executing-plans` | 执行计划 | 严格 |
| `dev-git-worktrees` | Git 工作树管理 | 严格 |
| `dev-requesting-review` | 代码审查请求 | 严格 |
| `dev-verification` | 完成前验证 | 严格 |
| `dev-finishing-branch` | 分支完成工作流 | 严格 |
| `dev-writing-skills` | 编写新skill | 严格 |
| `dev-code-cleanup` | 代码清理和死代码删除 | 严格 |
| `dev-update-codemaps` | 分析代码库结构并生成架构文档 | 灵活 |
| `dev-search-first` | 编码前先检索仓库、依赖、MCP、公开 skill 与 GitHub 方案，再决定 Adopt / Extend / Build | 严格 |
| `dev-backend-patterns` | 后端架构模式与最佳实践 | 灵活 |
| `dev-frontend-patterns` | 前端架构模式与最佳实践 | 灵活 |
| `dev-design-system` | 设计 token、语义层与组件状态的设计系统模式 | 灵活 |
| `dev-ui-styling` | 组件样式、响应式布局、主题与可访问性的 UI 实现模式 | 灵活 |
| `dev-continuous-agent-loop` | 顺序流水线、并行分发和持续 agent 循环的自动化执行模式 | 灵活 |
| `dev-e2e-testing` | Playwright Python 端到端测试模式 | 灵活 |
| `learn-deep-research` | 正式研究报告、技术调研、行业综述与结构化证据追踪 | 灵活 |
| `learn-llm-wiki` | Karpathy 风格 LLM Wiki 构建与维护（导入/查询/质量检查） | 灵活 |
| `work-market-research` | 市场规模、竞品、价格带、区域机会与进入策略调研 | 灵活 |
| `tool-humanizer-zh` | 去除文本中的 AI 生成痕迹 | 灵活 |
| `tool-macos-hidpi` | 为 macOS 新增或验证 HiDPI/标准分辨率 | 灵活 |
| `dev-creating-subagents` | 创建和管理 subagent（Kimi CLI/Codex 双平台指南） | 灵活 |
| `agent-browser` | 浏览器自动化 CLI 使用、页面交互、抓取与截图 workflow | 灵活 |
| `obsidian-markdown` | Obsidian Flavored Markdown 编辑（项目级安装到 Obsidian vault） | 灵活 |
| `obsidian-bases` | Obsidian Bases 语法编辑（项目级安装到 Obsidian vault） | 灵活 |
| `json-canvas` | JSON Canvas 文件编辑（项目级安装到 Obsidian vault） | 灵活 |
| `obsidian-cli` | Obsidian CLI 与 vault 交互（项目级安装到 Obsidian vault） | 灵活 |
| `defuddle` | 网页提取为干净 markdown（项目级安装到 Obsidian vault） | 灵活 |

### 快速安装

通过 `uv tool install -e` 安装 `ce` CLI 工具（一次性）：

```bash
cd coding-everything
uv tool install -e .
```

安装所有组的 skill：

```bash
ce install
```

默认会按 `~/.ce/config.yaml` 分组安装：
- `global` 组：skill symlink 到 `~/.agents/skills/` 和 `~/.claude/skills/`，安装 `~/.kimi/agents/superpower`、`~/.local/bin/ks`，合并 MCP 配置
- `obsidian` 组：skill symlink 到 Obsidian vault 下的 `.claude/skills/` 和 `.agents/skills/`；与 global 组互斥，同一 skill 只归属一个组

`ce init` 中 obsidian 组的分类规则（`cli.py` `_obsidian_names`）：
- 前缀匹配：`obsidian-*`、`defuddle`、`json-canvas`
- 显式名称：`learn-llm-wiki`、`life-ai-newsletters`、`life-ai-products`、`life-ask`、`life-parse-knowledge`、`life-start-my-day`
- 其余 skill 归入 global 组

单组操作：

```bash
ce install --group obsidian     # 只安装 obsidian 组
ce update --group global        # 只更新 global 组
ce uninstall --group obsidian   # 只卸载 obsidian 组
ce status                       # 查看所有组状态
ce status --group global        # 只查看 global 组
```

---

## Git Submodule 管理

### 克隆包含 submodules 的项目

```bash
git clone --recursive https://github.com/moyueheng/coding-everything.git
```

### 初始化 submodules（如果已克隆但没有 submodules）

```bash
git submodule update --init --recursive
```

### 更新所有 submodules 到最新

```bash
git submodule update --remote
```

约束：
- 所有 `upstream/` submodule 必须显式跟踪 `main` 分支，禁止依赖远端默认分支隐式漂移
- 更新 submodule 后，先检查 gitlink 是否沿 `main` 前进，再决定是否写报告或提交
- `git submodule update --remote` 后，必须把本次有变化的 submodule 切回本地 `main`，不要把工作树停在 detached HEAD
- 固定入口：

```bash
uv run .agents/skills/update-upstream-repos/scripts/switch_updated_submodules_to_main.py
```

### 更新特定 submodule

```bash
cd upstream/superpowers
git pull origin main
cd ../..
git add upstream/superpowers
git commit -m "Update superpowers submodule"
```

### 添加新的 submodule

```bash
git submodule add <仓库URL> upstream/<名称>
```

### 生成上游更新报告

更新 submodule 后，使用系统级 skill 附带脚本整理真实 commit 变化：

```bash
uv run .agents/skills/update-upstream-repos/scripts/generate_upstream_report.py
```

推荐将报告写入：

```bash
docs/upstream-updates/YYYY-MM-DD-upstream-updates.md
```

---

## 核心工作流

基于 superpowers 框架的开发工作流：

```
1. 头脑风暴 → 通过提问完善想法
         ↓
2. 编写计划 → 将工作分解为 2-5 分钟任务
         ↓
3. 执行计划 → 按步骤实现
         ↓
4. TDD 开发 → RED → GREEN → REFACTOR
         ↓
5. 代码审查 → 检查清单
         ↓
6. 完成分支 → 验证并合并
```

**关键规则**: 在执行任何任务之前，先检查并调用相关skill。

---

## 开发约定

### 使用skill时

1. **始终先调用skill** —— 任何回应或行动前检查skill
2. **遵循skill类型** —— 严格skill完全遵循，灵活skill按需调整
3. **skill优先级** —— 流程skill优先于实现skill
4. **指令是 WHAT 不是 HOW** —— 不要跳过工作流
5. `dev-brainstorming` 与 `dev-writing-plans` 的审查标准已拆到各自目录下的 checklist 文件，修改主流程时要同步检查旁边的 checklist

### skill开发

1. 遵循 `dev-writing-skills` skill指南
2. 每个skill包含：
   - `SKILL.md` 带 YAML frontmatter
   - `<EXTREMELY-IMPORTANT>` 强制规则
   - 流程图（Graphviz dot）
   - 检查清单（如适用）
3. **Skill 标准**：本项目的 skills 遵循 [Agent Skills 开放标准](https://agentskills.io/)，与 Claude Code、Codex 等平台兼容
4. 安装与卸载边界以 manifest 为准（`~/.ce/install-manifest.json`），`update/uninstall/status` 只能处理本仓库登记过的项
5. 新增 skill 必须在 `skills-install.yaml` 中声明所属组和 targets，否则不会被安装

### 脚本开发

1. 使用 TDD 开发重要脚本
2. 测试文件放在 `tests/` 目录
3. 保持脚本 POSIX 兼容（优先使用 bash）
4. 外部单 skill 同步脚本放在仓库根 `scripts/`，并与被跟踪目录内的 `UPSTREAM.md` 一起维护来源、分支、SHA 与同步命令

### 文档同步（AGENTS/CLAUDE）

1. 开始任务先运行：`find . -type f \( -name 'AGENTS.md' -o -name 'CLAUDE.md' \)`，识别可受影响文档
2. 只要变更触及目录结构、架构边界、工作流、安装步骤、测试入口等高信息密度事实，必须同步更新相关文档
3. 更新内容禁止流水账，优先写稳定、可执行、可复用的约束与结构信息
4. 每次 commit 前检查 `upstream/everything-claude-code/agents/architect.md` 是否需要同步到当前仓库的相关 skills 或文档

### 多工具嵌套工作区

1. 多 Git 仓库共享父级规则时，先查阅 `docs/agent-context-loading.md`，确认 Codex、Claude Code、Kimi CLI、OpenCode 的指令文件和 skill 发现边界
2. Codex 多仓库工作区优先使用 `.codex-root` + `project_root_markers = [".codex-root"]`，不要同时依赖 `.git` 和 `.codex-root` 作为等价 marker
3. Kimi CLI 和 OpenCode 在嵌套 Git 仓库中不会稳定继承父级项目级 rules/skills；需要跨仓库共享时优先使用用户级 skill 目录、symlink、或显式配置/启动函数注入

### Git Worktree 约束

1. 新建 git worktree 时，统一使用 `~/.agents/worktrees/<项目名称>/<分支名>`
2. 不要在仓库内创建或复用 `.worktrees/`、`worktrees/` 等项目本地目录作为新 worktree 位置

### 命名规范

#### Skill 分类前缀

所有 Skills 使用分类前缀，便于区分用途：

| 前缀 | 类别 | 示例 |
|------|------|------|
| `dev-` | 开发相关 | `dev-plan`, `dev-tdd`, `dev-review-py` |
| `life-` | 生活相关 | `life-notes`, `life-daily` |
| `work-` | 工作相关 | `work-meeting`, `work-project` |
| `tool-` | 工具相关 | `tool-mcp-builder`, `tool-sshfs-mount` |
| `learn-` | 学习相关 | `learn-paper`, `learn-research` |

命名前缀规范适用于 Agents/Commands/Skills 及其 frontmatter `name` 字段，按用途选择前缀。

#### 术语约定

| 术语 | 约定 | 说明 |
|------|------|------|
| skill | 不翻译 | 统一使用英文 "skill"，不用"技能" |
| agent | 不翻译 | 统一使用英文 "agent"，不用"智能体" |

**示例**：
- ❌ "核心技能" → ✅ "核心 skill"
- ❌ "技能列表" → ✅ "skill 列表"
- ❌ "使用技能" → ✅ "使用 skill"

---

## 资源链接

### 上游仓库

- **superpowers**: https://github.com/obra/superpowers
- **everything-claude-code**: https://github.com/affaan-m/everything-claude-code
- **ui-ux-pro-max-skill**: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **humanizer-zh**: https://github.com/op7418/Humanizer-zh
- **product-manager-skills**: https://github.com/deanpeters/Product-Manager-Skills
- **obsidian-skills**: https://github.com/kepano/obsidian-skills
- **orbitos**: https://github.com/MarsWang42/OrbitOS
- **karpathy-llm-wiki**: https://github.com/Astro-Han/karpathy-llm-wiki
- **karpathy-skills**: https://github.com/forrestchang/andrej-karpathy-skills

### 平台文档

- **本项目**: https://github.com/moyueheng/coding-everything
- **Kimi CLI 文档**: https://moonshotai.github.io/kimi-cli/
- **Codex CLI 文档**: https://github.com/openai/codex

### Skill 标准

- **Agent Skills 开放标准**: https://agentskills.io/ - 跨平台 AI skill标准
- **Claude Code Skills 文档**: https://code.claude.com/docs/en/skills - Claude Code skill开发指南

---

## 许可证

各上游仓库遵循其原有许可证。个人配置采用 MIT 许可证。
