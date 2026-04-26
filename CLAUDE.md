# coding-everything 项目文档

## 目录

- [共享 Skills 架构图](./docs/skills-architecture.md) - 技能关系图和调用流程可视化
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

### 个人配置

| 平台 | 路径 | 状态 |
|------|------|------|
| **共享 skills** | `skills/` | ✅ 已配置（46 个共享 skill；其中 5 个 Obsidian 编辑类 skill 可单独分组安装） |
| **Kimi** | `kimi/` | ✅ 已配置（agent/config） |
| **Claude Code** | 通过 `ce` CLI 写入 `~/.claude/skills/` 或项目级 `.claude/skills/`，并合并 `mcp-configs/required.json` | ✅ 已兼容 |

---

## 项目结构

```
coding-everything/
├── README.md                   # 项目简介
├── AGENTS.md                   # 本文档
├── CLAUDE.md                   # Claude/Codex 共享项目文档
├── .gitmodules                 # Git submodule 配置
├── .agents/
│   └── skills/                 # 系统级 skills
│       ├── setup/              # 安装 skill
│       ├── update-upstream-repos/ # 上游更新与报告生成 skill
│       └── dev-creating-subagents/ # 创建和管理 subagent
│
├── skills/                     # 跨平台共享 skills
│   ├── dev-*/                  # 开发 workflow / 模式类 skill（21 个）
│   ├── life-*/                 # OrbitOS 派生 workflow（9 个）
│   ├── work-*/                 # 产品 / 研究 workflow（6 个）
│   ├── obsidian-*/             # Obsidian 编辑 skill（3 个）
│   ├── json-canvas/            # JSON Canvas 文件编辑
│   ├── defuddle/               # 网页提取为干净 markdown
│   ├── tool-*/                 # 工具类 skill
│   ├── learn-*/                # 学习 / 研究类 skill（2 个）
│   └── agent-browser/          # 单独镜像跟踪的外部浏览器自动化 skill
├── install_skills/             # ce CLI 工具 Python 包
│   ├── __init__.py
│   ├── cli.py                  # 命令行入口
│   ├── config.py               # `~/.ce/config.yaml` 读写
│   ├── installer.py            # symlink / manifest / MCP 逻辑
│   └── models.py               # 配置与 manifest 数据结构
├── pyproject.toml              # Python 包定义（ce CLI 入口）
├── ks                          # Kimi Superpower 启动脚本
├── mcp-configs/                # MCP 服务器配置模板
│   └── required.json           # Auggie + ZAI + Context7
├── scripts/                    # 本地同步脚本
│   └── sync-agent-browser-skill.sh # 同步 vercel-labs/agent-browser skill
├── tests/                      # ce CLI / 安装逻辑测试
│
├── kimi/                       # Kimi 专属配置
│   ├── README.md
│   └── agents/
│       └── superpower/         # agent 配置
│           ├── agent.yaml
│           ├── system.md
│           └── README.md
│
├── docs/                       # 文档
│   ├── CODEMAPS/               # token-lean 架构索引
│   ├── plans/                  # 计划与调研文档
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
    ├── orbitos/                # AI 驱动的 Obsidian 个人生产力系统
        ├── README.md
        └── EN/                 # 英文版 vault 模板与 AI workflow
    │
    ├── karpathy-llm-wiki/      # Karpathy 风格 LLM Wiki 构建工具
    │   ├── SKILL.md
    │   ├── README.md
    │   └── references/
    │
    └── karpathy-skills/        # Karpathy 编码行为指南 skill
```

---

## 上游仓库详情

### 1. superpowers

**简介**: 为 AI 编程助手设计的综合软件开发工作流框架

**当前跟踪版本**: `b557648`（位于 `v5.0.7` 之后 23 个提交，2026-04-24 同步）

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
- ✅ 当前 gitlink 已前进到 `b557648`，本轮上游重点在 Codex plugin 镜像工具链与 README / 安装表述整理

### 2. everything-claude-code

**简介**: 完整的 Claude Code 配置集合

**内容**:
- `.claude/` - Claude 专属配置
- `.cursor/` - Cursor 编辑器配置
- `.opencode/` - OpenCode 配置
- `skills/` - 183 个 skill
- `agents/` - 48 个 agent 配置
- `commands/` - 79 个 legacy command shim
- `hooks/` - 会话钩子
- `docs/zh-CN/skills/` - 116 个简体中文条目
- `ecc2/` - ECC 2.0 Rust TUI 脚手架（开发中）

**本次同步观察**:
- `4e66b288` 把 Continuous Learning v2、Cursor 原生 hook / MCP、Windows hook wrapper 等安装链路继续收敛
- 上游 README 当前公开面已对齐到 `48 agents / 183 skills / 79 legacy command shims`
- 这次不直接引入 ECC 新表面，但本仓库文档应同步它的真实体量和插件安装边界

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
- ✅ 已迁移 9 个 OrbitOS workflow skill 到 `skills/`：`life-start-my-day`、`life-kickoff`、`life-research`、`life-brainstorm`、`life-parse-knowledge`、`life-archive`、`life-ask`、`life-ai-newsletters`、`life-ai-products`
- ✅ 当前仓库另含 6 个 `work-*` workflow：`work-jobs-to-be-done`、`work-market-research`、`work-problem-statement`、`work-user-story`、`work-user-story-mapping`、`work-user-story-splitting`
- ✅ 已新增 `learn-llm-wiki`，来源于 `upstream/karpathy-llm-wiki/`
- ✅ `ce init` 默认只把 5 个 Obsidian 编辑类 skill 归入可选 `obsidian` 组；OrbitOS workflow 会随 `global` 组安装
- ✅ 本地适配统一使用 `20_Project/`，不保留 `20_Projects/` 兼容层

---

## 个人 Kimi 配置

共享 skill 基于 Agent Skills 标准组织；`kimi/` 目录仅保留 Kimi Code CLI 专属 agent/config。当前仓库共有 46 个共享 skill，按前缀分类如下：

### skill列表

| 前缀 / 组 | 数量 | 说明 |
|------|------|------|
| `dev-*` | 21 | 开发 workflow、模式与安装配套，包括 `dev-mcp-patterns` |
| `life-*` | 9 | OrbitOS 派生的个人 workflow |
| `work-*` | 6 | 产品、研究与需求分析 workflow |
| `obsidian-*` | 3 | Obsidian 编辑 skill |
| `json-canvas` + `defuddle` | 2 | Obsidian 相关辅助 skill |
| `tool-*` | 2 | 工具类 skill |
| `learn-*` | 2 | 深度研究类 skill，含 `learn-llm-wiki` |
| `agent-browser` | 1 | 浏览器自动化 skill |

分组规则：
- `ce init` 会把 `obsidian-*`、`json-canvas`、`defuddle` 识别为可选 `obsidian` 组
- 其余共享 skill 默认进入 `global` 组

### 快速安装

通过 `uv tool install -e` 安装 `ce` CLI 工具（一次性）：

```bash
cd coding-everything
uv tool install -e .
```

先初始化用户配置：

```bash
ce init
```

初始化会把分组配置写入 `~/.ce/config.yaml`。随后再安装：

```bash
ce install
```

默认分组行为：
- `global` 组：skill symlink 到 `~/.agents/skills/` 和 `~/.claude/skills/`，安装 `~/.kimi/agents/superpower`、`~/.local/bin/ks`，并把 `mcp-configs/required.json` 合并到 `~/.claude.json`
- `obsidian` 组：仅在 `ce init` 时提供 vault 路径后创建，安装到对应 vault 的 `.claude/skills/` 与 `.agents/skills/`

单组操作：

```bash
ce install --group obsidian     # 只安装 obsidian 组
ce update --group global        # 只更新 global 组
ce uninstall --group obsidian   # 只卸载 obsidian 组
ce status                       # 查看所有组状态
ce status --group global        # 只查看 global 组
ce doctor                       # 检查并修复常见安装问题
ce add-skill learn-llm-wiki --group global
ce add-target /Users/moyueheng/00-life/myhron-os/.claude/skills --group obsidian
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
5. 当前主流程通过 `~/.ce/config.yaml` 管理分组；如新增 skill，需要通过 `ce init` / `ce add-skill` / `ce add-target` 进入目标组

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
