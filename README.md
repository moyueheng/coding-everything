# coding-everything

个人 AI 编程助手配置集合，支持 Kimi、OpenCode 等平台，跟踪多个上游优秀配置仓库。

## 这是什么项目？

本项目聚合了多个优秀的 AI 编程助手配置：

- **[obra/superpowers](https://github.com/obra/superpowers)** - AI 编程助手工作流框架（14 个核心技能）
- **[affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)** - Claude Code 完整配置（39 个技能）
- **[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)** - UI/UX Pro Max Skill

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

### 2. 安装 Kimi 技能

使用自动化脚本（推荐）：

```bash
# 进入项目目录后执行
/skill:setup
```

或手动创建软链接：

```bash
# 创建软链接到 Kimi 技能目录
mkdir -p ~/.agents
ln -sf "$(pwd)/kimi/skills" ~/.agents/skills

# Agent 配置（可选）
mkdir -p ~/.kimi/agents
ln -sf "$(pwd)/kimi/agents/superpower" ~/.kimi/agents/superpower
```

### 3. 验证安装

```bash
ls ~/.agents/skills/
```

应该能看到类似 `dev-using-skills`、`dev-tdd`、`dev-debugging` 等技能目录。

## 核心技能

### 开发工作流技能

| 技能 | 用途 | 触发场景 |
|------|------|----------|
| `dev-using-skills` | 技能入口 | 不知道用什么技能时先执行这个 |
| `dev-brainstorming` | 头脑风暴 | 开始任何新功能前 |
| `dev-writing-plans` | 编写计划 | 需要将任务分解为可执行步骤 |
| `dev-executing-plans` | 执行计划 | 按计划一步步实现 |
| `dev-tdd` | 测试驱动开发 | 写代码前先写测试 |
| `dev-debugging` | 调试 | 遇到 Bug 时 |
| `dev-verification` | 验证 | 完成任务前检查 |
| `dev-requesting-review` | 代码审查 | 需要审查代码时 |
| `dev-finishing-branch` | 完成分支 | 合并代码前 |
| `dev-git-worktrees` | Git 工作树 | 隔离多个任务 |

### 辅助技能

| 技能 | 用途 |
|------|------|
| `dev-writing-skills` | 编写新的技能 |
| `dev-code-cleanup` | 清理死代码 |
| `dev-update-codemaps` | 更新代码地图文档 |
| `dev-backend-patterns` | 后端架构模式 |
| `dev-frontend-patterns` | 前端架构模式 |

## 典型工作流

```
1. 头脑风暴 → 完善需求、边界条件
         ↓
2. 编写计划 → 拆分为 2-5 分钟任务
         ↓
3. 执行计划 → 按步骤实现
         ↓
4. TDD 开发 → RED → GREEN → REFACTOR
         ↓
5. 代码审查 → 检查清单验证
         ↓
6. 完成分支 → 验证并合并
```

**重要原则**：任何行动前先检查是否有适用的 skill。

## 常用命令

### Git Submodule 管理

```bash
# 更新所有子模块到最新
git submodule update --remote

# 更新特定子模块
cd upstream/superpowers && git pull origin main
```

### 查看技能

```bash
# 列出所有可用技能
ls ~/.agents/skills/

# 查看技能详情
cat ~/.agents/skills/dev-tdd/SKILL.md
```

## 项目结构

```
coding-everything/
├── kimi/                    # Kimi 配置
│   ├── agents/superpower/   # Agent 配置
│   └── skills/              # 14 个技能
├── opencode/                # OpenCode 配置（待完善）
├── upstream/                # 上游仓库（子模块）
│   ├── superpowers/         # superpowers 框架
│   └── everything-claude-code/  # Claude Code 配置
└── docs/                    # 文档
```

## 文档

详细文档请参考：

- **[AGENTS.md](./AGENTS.md)** - 完整项目文档，包含架构、约定、工作流等

## 上游仓库

| 仓库 | 说明 |
|------|------|
| [obra/superpowers](https://github.com/obra/superpowers) | AI 编程助手工作流框架 |
| [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | Claude Code 完整配置 |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | UI/UX Pro Max Skill |

## 许可证

各上游仓库遵循其原有许可证。个人配置采用 MIT 许可证。
