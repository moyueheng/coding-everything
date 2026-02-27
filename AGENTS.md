# coding-everything 项目文档

## 项目概述

本项目 (`coding-everything`) 是个人 AI 编程助手配置集合，通过 Git Submodule 跟踪多个上游配置仓库，并维护自己的专属配置。

### 跟踪的上游仓库

| 仓库 | 用途 | 路径 |
|------|------|------|
| [obra/superpowers](https://github.com/obra/superpowers.git) | AI 编程助手工作流框架 | `upstream/superpowers/` |
| [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code.git) | Claude Code 完整配置 | `upstream/everything-claude-code/` |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git) | UI/UX Pro Max Skill | `upstream/ui-ux-pro-max-skill/` |

### 个人配置

| 平台 | 路径 | 状态 |
|------|------|------|
| **Kimi** | `kimi/` | ✅ 已配置（11 个技能 + 安装脚本） |
| **Codex** | `codex/` | ✅ 已配置（11 个技能 + 安装脚本） |
| **OpenCode** | `opencode/` | 🏗️ 目录结构 |

---

## 项目结构

```
coding-everything/
├── README.md                   # 项目简介
├── AGENTS.md                   # 本文档
├── Makefile                    # 常用命令
├── .gitmodules                 # Git submodule 配置
│
├── kimi/                       # Kimi 配置
│   ├── README.md
│   ├── agents/
│   │   └── superpower/         # 智能体配置
│   │       ├── agent.yaml
│   │       ├── system.md
│   │       └── README.md
│   └── skills/                 # 11 个技能
│       ├── dev-using-skills/
│       ├── dev-brainstorming/
│       ├── dev-debugging/
│       ├── dev-tdd/
│       ├── dev-writing-plans/
│       ├── dev-executing-plans/
│       ├── dev-git-worktrees/
│       ├── dev-requesting-review/
│       ├── dev-verification/
│       ├── dev-finishing-branch/
│       └── dev-writing-skills/
│
├── codex/                      # Codex 配置
│   ├── README.md
│   └── skills/                 # 11 个技能（从 kimi 迁移）
│       ├── dev-using-skills/
│       ├── dev-brainstorming/
│       ├── dev-debugging/
│       ├── dev-tdd/
│       ├── dev-writing-plans/
│       ├── dev-executing-plans/
│       ├── dev-git-worktrees/
│       ├── dev-requesting-review/
│       ├── dev-verification/
│       ├── dev-finishing-branch/
│       └── dev-writing-skills/
│
├── opencode/                   # OpenCode 配置
│   ├── README.md
│   ├── plugins/                # 插件目录
│   └── skills/                 # 技能目录（待填充）
│
├── scripts/                    # 工具脚本
│   └── install.sh              # 配置安装脚本 (TDD, 支持 kimi/codex)
│
├── tests/                      # 测试
│   └── test_install.sh         # install.sh 的测试（27 个用例，覆盖 kimi/codex）
│
├── docs/                       # 文档
│
└── upstream/                   # 上游仓库（git submodules）
    ├── superpowers/            # superpowers 框架
    │   ├── skills/             # 14 个核心技能
    │   ├── .opencode/          # OpenCode 集成
    │   └── ...
    │
    └── everything-claude-code/ # everything-claude-code 配置
        ├── .claude/            # Claude 配置
        ├── .cursor/            # Cursor 编辑器配置
        ├── .opencode/          # OpenCode 配置
        ├── skills/             # 39 个技能
        ├── agents/             # 智能体配置
        └── ...
```

---

## 上游仓库详情

### 1. superpowers

**简介**: 为 AI 编程助手设计的综合软件开发工作流框架

**核心技能**:
- `using-superpowers` - 技能使用入口
- `brainstorming` - 编码前设计完善
- `test-driven-development` - TDD 循环
- `systematic-debugging` - 系统化调试
- `writing-plans` / `executing-plans` - 计划编写与执行
- `finishing-a-development-branch` - 分支完成工作流
- 等等（共 14 个）

**支持平台**: Claude Code, Codex, OpenCode

### 2. everything-claude-code

**简介**: 完整的 Claude Code 配置集合

**内容**:
- `.claude/` - Claude 专属配置
- `.cursor/` - Cursor 编辑器配置
- `.opencode/` - OpenCode 配置
- `skills/` - 39 个技能
- `agents/` - 智能体配置
- `commands/` - 预定义命令
- `hooks/` - 会话钩子

---

## 个人 Kimi 配置

基于 superpowers 框架改写，适配 Kimi Code CLI 使用。

### 技能列表

| 技能 | 用途 | 类型 |
|------|------|------|
| `dev-using-skills` | 入口点 - 技能使用方法 | 严格 |
| `dev-brainstorming` | 编码前苏格拉底式对话 | 严格 |
| `dev-debugging` | 四阶段调试流程 | 严格 |
| `dev-tdd` | 测试驱动开发 | 严格 |
| `dev-writing-plans` | 编写实施计划 | 严格 |
| `dev-executing-plans` | 执行计划 | 严格 |
| `dev-git-worktrees` | Git 工作树管理 | 严格 |
| `dev-requesting-review` | 代码审查请求 | 严格 |
| `dev-verification` | 完成前验证 | 严格 |
| `dev-finishing-branch` | 分支完成工作流 | 严格 |
| `dev-writing-skills` | 编写新技能 | 严格 |

### 快速安装

使用 Makefile（推荐）：

```bash
# 查看所有可用命令
make help

# 安装配置到 ~/.kimi/
make install

# 更新配置
make update

# 查看状态
make status

# 运行测试
make test
```

或使用脚本直接安装：

```bash
# 安装配置
./scripts/install.sh

# 启动 Kimi
./kimi-superpower
```

### 安装脚本功能

`scripts/install.sh` 使用 TDD 开发，支持 Kimi 和 Codex 双平台：

```bash
# 命令格式
./scripts/install.sh [platform] [command] [options]

# Platform: kimi (默认) | codex
# Command: install | update | uninstall | status
```

| 命令 | 说明 |
|------|------|
| `install` | 安装配置（默认 kimi） |
| `kimi install` | 安装 Kimi 配置到 `~/.kimi/` |
| `codex install` | 安装 Codex 配置到 `~/.codex/` |
| `install -f` | 强制安装，覆盖现有配置 |
| `update` | 更新已安装的配置 |
| `uninstall` | 卸载配置 |
| `status` | 查看安装状态 |

**Kimi 安装路径：**
- Skills: `~/.kimi/skills/`（11 个 dev-* skills）
- Agent: `~/.kimi/agents/superpower/`
- 启动脚本: `./kimi-superpower`

**Codex 安装路径：**
- Skills: `~/.agents/skills/`（11 个 dev-* skills，符合 Codex 官方规范）
- 直接使用 `codex` 命令启动，skills 自动加载

### 测试

```bash
# 运行所有测试
make test

# 或直接运行
./tests/test_install.sh
```

测试覆盖：
- install: 创建目录、复制 skills/agent、创建启动脚本
- install -f: 覆盖现有配置
- update: 更新配置、未安装时报错
- uninstall: 删除配置和启动脚本
- status: 显示安装状态
- 边界情况: 无效命令、源文件缺失等

---

## 个人 Codex 配置

基于 superpowers 框架改写，适配 Codex CLI 使用。技能与 Kimi 配置相同。

### 技能列表

与 Kimi 配置相同的 11 个技能：

| 技能 | 用途 | 类型 |
|------|------|------|
| `dev-using-skills` | 入口点 - 技能使用方法 | 严格 |
| `dev-brainstorming` | 编码前苏格拉底式对话 | 严格 |
| `dev-debugging` | 四阶段调试流程 | 严格 |
| `dev-tdd` | 测试驱动开发 | 严格 |
| `dev-writing-plans` | 编写实施计划 | 严格 |
| `dev-executing-plans` | 执行计划 | 严格 |
| `dev-git-worktrees` | Git 工作树管理 | 严格 |
| `dev-requesting-review` | 代码审查请求 | 严格 |
| `dev-verification` | 完成前验证 | 严格 |
| `dev-finishing-branch` | 分支完成工作流 | 严格 |
| `dev-writing-skills` | 编写新技能 | 严格 |

### 快速安装

使用 Makefile：

```bash
# 查看所有可用命令
make help

# 安装 codex skills 到 ~/.agents/skills/
make install-codex

# 更新配置
make update-codex

# 查看状态
make status-codex

# 运行测试
make test
```

或使用脚本直接安装：

```bash
# 安装 codex skills
./scripts/install.sh codex install

# 启动 Codex（skills 会自动加载）
codex
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

**关键规则**: 在执行任何任务之前，先检查并调用相关技能。

---

## 开发约定

### 使用技能时

1. **始终先调用技能** —— 任何回应或行动前检查技能
2. **遵循技能类型** —— 严格技能完全遵循，灵活技能按需调整
3. **技能优先级** —— 流程技能优先于实现技能
4. **指令是 WHAT 不是 HOW** —— 不要跳过工作流

### 技能开发

1. 遵循 `dev-writing-skills` 技能指南
2. 每个技能包含：
   - `SKILL.md` 带 YAML frontmatter
   - `<EXTREMELY-IMPORTANT>` 强制规则
   - 流程图（Graphviz dot）
   - 检查清单（如适用）
3. **Skill 标准**：本项目的 skills 遵循 [Agent Skills 开放标准](https://agentskills.io/)，与 Claude Code、Codex 等平台兼容

### 脚本开发

1. 使用 TDD 开发重要脚本
2. 测试文件放在 `tests/` 目录
3. 使用 `make test` 运行测试
4. 保持脚本 POSIX 兼容（优先使用 bash）

### 文档同步（AGENTS/CLAUDE）

1. 开始任务先运行：`find . -type f \( -name 'AGENTS.md' -o -name 'CLAUDE.md' \)`，识别可受影响文档
2. 只要变更触及目录结构、架构边界、工作流、安装步骤、测试入口等高信息密度事实，必须同步更新相关文档
3. 更新内容禁止流水账，优先写稳定、可执行、可复用的约束与结构信息

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
---

## 资源链接

### 上游仓库

- **superpowers**: https://github.com/obra/superpowers
- **everything-claude-code**: https://github.com/affaan-m/everything-claude-code

### 平台文档

- **本项目**: https://github.com/moyueheng/coding-everything
- **Kimi CLI 文档**: https://moonshotai.github.io/kimi-cli/
- **Codex CLI 文档**: https://github.com/openai/codex

### Skill 标准

- **Agent Skills 开放标准**: https://agentskills.io/ - 跨平台 AI 技能标准
- **Claude Code Skills 文档**: https://code.claude.com/docs/en/skills - Claude Code 技能开发指南

---

## 许可证

各上游仓库遵循其原有许可证。个人配置采用 MIT 许可证。
