# coding-everything 项目文档

## 项目概述

本项目 (`coding-everything`) 是一个 Git submodule 包装器，包含了 **Superpowers** 项目 —— 一个为 AI 编程助手设计的综合软件开发工作流框架。Superpowers 提供了一系列可组合的 "技能"（skills），引导 AI 助手通过系统化、有纪律的软件开发工作流程。

**上游仓库**: https://github.com/obra/superpowers.git

### 什么是 Superpowers？

Superpowers 是一个专为 AI 编程助手（Claude Code、Codex、OpenCode）设计的工作流框架。它确保 AI 助手：

1. **不要立即开始编码** —— 而是先进行头脑风暴并完善需求规格
2. **遵循系统化流程** —— TDD、结构化调试、代码审查工作流
3. **自动使用技能** —— 每个技能在相关任务触发时自动激活

核心理念强调：
- **测试驱动开发 (TDD)** —— 始终先编写测试
- **系统化而非临时性** —— 流程胜于猜测
- **降低复杂度** —— 简洁是首要目标
- **证据胜于声明** —— 在宣布成功之前先验证

## 项目结构

```
coding-everything/
├── README.md                 # 项目标题
├── .gitmodules              # Git submodule 配置
├── AGENTS.md                # 本文件
└── upstream/
    └── superpowers/         # Git submodule: 实际的 superpowers 项目
        ├── .claude-plugin/  # Claude Code 插件配置
        ├── .codex/          # Codex 集成文件
        ├── .opencode/       # OpenCode 集成文件
        ├── .github/         # GitHub 配置 (FUNDING.yml)
        ├── agents/          # 智能体配置文件
        │   └── code-reviewer.md
        ├── commands/        # 预定义命令模板
        │   ├── brainstorm.md
        │   ├── execute-plan.md
        │   └── write-plan.md
        ├── docs/            # 文档
        │   ├── testing.md           # 测试指南
        │   ├── README.codex.md      # Codex 安装说明
        │   ├── README.opencode.md   # OpenCode 安装说明
        │   ├── plans/               # 示例实现计划
        │   └── windows/             # Windows 特定文档
        ├── hooks/           # 会话钩子
        │   ├── hooks.json
        │   └── session-start.sh     # 会话开始时注入 superpowers 上下文
        ├── lib/             # 核心库代码
        │   └── skills-core.js       # 技能解析和管理工具
        ├── skills/          # **核心技能库 (见下文)**
        └── tests/           # 测试套件
            ├── claude-code/         # Claude Code 集成测试
            ├── explicit-skill-requests/  # 技能请求测试
            ├── opencode/            # OpenCode 测试
            ├── skill-triggering/    # 技能自动触发测试
            └── subagent-driven-dev/ # 子智能体开发测试
```

## 技术栈

- **主要语言**: 
  - Shell 脚本 (Bash) —— 用于钩子和自动化
  - JavaScript (Node.js) —— 用于核心库和插件
  - Python —— 用于测试工具和分析
  
- **配置格式**: JSON、YAML frontmatter 技能文件

- **支持平台**:
  - **Claude Code** —— 通过插件市场 (`obra/superpowers-marketplace`)
  - **Codex** —— 通过技能发现 `~/.agents/skills/superpowers/`
  - **OpenCode** —— 通过插件系统

- **插件版本**: 4.3.0 (截至 2026-02-12)

## 技能库

所有技能位于 `upstream/superpowers/skills/`。每个技能是一个目录，至少包含一个带有 YAML frontmatter 的 `SKILL.md` 文件。

### 技能格式

```yaml
---
name: skill-name
description: Use when [condition] - [what it does]
---

<EXTREMELY-IMPORTANT>
必须遵循的关键指令
</EXTREMELY-IMPORTANT>

## 技能内容，包括图表、指南等
```

### 可用技能

| 技能 | 用途 | 类型 |
|------|------|------|
| `using-superpowers` | 入口点 —— 教你如何查找和使用技能 | 严格 |
| `brainstorming` | 编码前通过苏格拉底式对话完善设计 | 严格 |
| `using-git-worktrees` | 在新分支上创建隔离工作区 | 严格 |
| `writing-plans` | 创建详细的实现计划 | 严格 |
| `executing-plans` | 批量执行，带人工检查点 | 严格 |
| `subagent-driven-development` | 快速迭代，两阶段审查 | 严格 |
| `test-driven-development` | RED-GREEN-REFACTOR 循环 | 严格 |
| `systematic-debugging` | 四阶段根本原因分析 | 严格 |
| `verification-before-completion` | 确保修复确实有效 | 严格 |
| `requesting-code-review` | 审查前检查清单 | 严格 |
| `receiving-code-review` | 回应反馈 | 灵活 |
| `finishing-a-development-branch` | 合并/PR 决策工作流 | 严格 |
| `dispatching-parallel-agents` | 并行子智能体工作流 | 严格 |
| `writing-skills` | 遵循最佳实践创建新技能 | 严格 |

**技能类型**:
- **严格 (Rigid)**: 完全遵循。不要偏离纪律（TDD、调试）
- **灵活 (Flexible)**: 根据上下文调整原则（模式、某些工作流）

## 核心工作流

Superpowers 框架强制执行以下开发工作流：

```
1. 头脑风暴 → 通过提问完善想法，保存设计文档
         ↓
2. 使用 Git Worktrees → 创建隔离工作区，验证测试通过
         ↓
3. 编写计划 → 将工作分解为 2-5 分钟的任务，带验证步骤
         ↓
4. 执行计划 / 子智能体驱动开发 → 带审查的实现
         ↓
5. 测试驱动开发 → RED (失败测试) → GREEN (通过) → REFACTOR
         ↓
6. 请求代码审查 → 对照计划审查，按严重程度报告问题
         ↓
7. 完成开发分支 → 验证测试，呈现合并选项
```

**关键规则**: 智能体在执行任何任务之前检查相关技能。强制性工作流，不是建议。

## 开发约定

### 使用技能时

1. **始终先调用技能** —— 在任何回应或行动之前，检查是否有技能适用（即使有 1% 的可能性）
2. **遵循技能类型**:
   - 严格技能: 完全遵循，不要调整
   - 灵活技能: 根据上下文应用原则
3. **技能优先级**: 流程技能（头脑风暴、调试）优先于实现技能
4. **用户指令说明 WHAT，不是 HOW** —— "添加 X" 不代表跳过工作流

### 技能开发

创建或修改技能：

1. 遵循 `writing-skills` 技能（它包含完整指南）
2. 每个技能需要：
   - 带 YAML frontmatter 的 `SKILL.md`（名称、描述）
   - 清晰的 `<EXTREMELY-IMPORTANT>` 部分，说明强制规则
   - 流程图（Graphviz dot 格式）
   - 适用时的检查清单
3. 技能可以包含支持文件（脚本、示例、模板）

### 代码风格

- **Shell 脚本**: 使用 `set -euo pipefail`，包含错误处理
- **JavaScript**: ES 模块，清晰的导出，JSDoc 注释
- **文档**: Markdown，清晰的章节，好坏示例对比

## 测试

### 测试结构

位于 `upstream/superpowers/tests/`：

```
tests/
├── claude-code/                    # Claude Code 集成测试
│   ├── test-helpers.sh
│   ├── test-subagent-driven-development.sh
│   ├── test-subagent-driven-development-integration.sh
│   ├── analyze-token-usage.py
│   └── run-skill-tests.sh
├── opencode/                       # OpenCode 特定测试
│   ├── test-plugin-loading.sh
│   ├── test-skills-core.sh
│   └── test-tools.sh
├── explicit-skill-requests/        # 显式技能调用测试
├── skill-triggering/              # 自动触发验证
└── subagent-driven-dev/           # 子智能体工作流测试
```

### 运行测试

**集成测试** (需要安装 Claude Code)：
```bash
cd upstream/superpowers/tests/claude-code
./test-subagent-driven-development-integration.sh
```

**要求**：
- 从 superpowers 插件目录运行（非临时目录）
- Claude Code 必须可作为 `claude` 命令使用
- 开发测试时：`~/.claude/settings.json` 中设置 `"superpowers@superpowers-dev": true`

**测试时长**: 集成测试可能需要 10-30 分钟，因为它们执行真实的实现计划并使用多个子智能体。

### 测试覆盖

测试验证：
- 技能工具调用
- 子智能体分派（Task 工具）
- TodoWrite 用于跟踪
- 实现文件创建
- 测试通过
- Git 提交工作流合规性

## 关键配置文件

### `.claude-plugin/plugin.json`
Claude Code 市场的插件元数据。

### `hooks/hooks.json`
定义 SessionStart 钩子，注入 superpowers 上下文。

### `lib/skills-core.js`
核心工具：
- 从技能中提取 YAML frontmatter
- 在目录中查找技能
- 解析技能路径（个人技能覆盖 superpowers）
- 检查更新

## 安全注意事项

1. **钩子执行**: SessionStart 钩子运行 shell 脚本 —— 仔细审查
2. **技能内容**: 技能可以包含 shell 命令 —— 执行前验证
3. **Git 操作**: 技能执行 Git 操作（分支、提交）— 确保用户知晓
4. **子智能体分派**: 子智能体拥有与父智能体相同的权限 —— 尽可能沙盒化

## 更新 Submodule

更新 superpowers submodule 到最新上游：

```bash
cd upstream/superpowers
git fetch origin
git checkout main  # 或特定版本标签
cd ../..
git add upstream/superpowers
git commit -m "Update superpowers to vX.Y.Z"
```

## 许可证

MIT 许可证 —— 见 `upstream/superpowers/LICENSE`

## 资源

- **上游仓库**: https://github.com/obra/superpowers
- **市场**: https://github.com/obra/superpowers-marketplace
- **问题**: https://github.com/obra/superpowers/issues
- **博客文章**: https://blog.fsck.com/2025/10/09/superpowers/
