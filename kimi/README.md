# Kimi Configuration

基于 [superpowers](https://github.com/obra/superpowers) 框架的 Kimi Code CLI 配置。

## 目录

- [快速开始](#快速开始)
  - [使用 Makefile（推荐）](#使用-makefile推荐)
  - [直接使用脚本](#直接使用脚本)
- [包含内容](#包含内容)
  - [Skills (11 个)](#skills-11-个)
  - [Agent](#agent)
- [安装脚本](#安装脚本)
- [测试](#测试)
- [安装路径](#安装路径)
- [使用方法](#使用方法)
  - [方式1: 使用生成的启动脚本（推荐）](#方式1-使用生成的启动脚本推荐)
  - [方式2: 直接指定 agent-file](#方式2-直接指定-agent-file)
  - [方式3: 创建别名](#方式3-创建别名)
- [目录结构](#目录结构)
- [核心工作流](#核心工作流)
- [相关链接](#相关链接)

---

## 快速开始

### 使用 Makefile（推荐）

```bash
# 查看所有可用命令
make help

# 安装配置
make install

# 更新配置
make update

# 查看状态
make status

# 运行测试
make test
```

### 直接使用脚本

```bash
# 安装配置
./scripts/install.sh

# 启动 Kimi
./kimi-superpower
```

## 包含内容

### Skills (15 个)

#### 核心 workflow skill（严格类型）

| Skill | 用途 |
|-------|------|
| `dev-using-skills` | skill 入口 |
| `dev-brainstorming` | 编码前苏格拉底式对话 |
| `dev-debugging` | 四阶段调试流程 |
| `dev-tdd` | 测试驱动开发 |
| `dev-writing-plans` | 编写实施计划 |
| `dev-executing-plans` | 执行计划 |
| `dev-git-worktrees` | Git 工作树管理 |
| `dev-requesting-review` | 代码审查请求 |
| `dev-verification` | 完成前验证 |
| `dev-finishing-branch` | 分支完成工作流 |
| `dev-writing-skills` | 编写新 skill |
| `dev-code-cleanup` | 代码清理和死代码删除 |

#### 辅助 skill（灵活类型）

| Skill | 用途 |
|-------|------|
| `dev-update-codemaps` | 分析代码库结构并生成架构文档 |
| `dev-backend-patterns` | 后端架构模式与最佳实践 |
| `dev-frontend-patterns` | 前端架构模式与最佳实践 |

### Agent

- `superpower/` - 基于 superpowers 框架的 agent 配置

## 安装脚本

单文件脚本：`scripts/install.sh`

```bash
# 安装（默认）
./scripts/install.sh
./scripts/install.sh install

# 强制安装（覆盖）
./scripts/install.sh install -f

# 更新配置
./scripts/install.sh update

# 卸载配置
./scripts/install.sh uninstall

# 查看状态
./scripts/install.sh status

# 帮助
./scripts/install.sh --help
```

## 测试

```bash
# 运行测试
./tests/test_install.sh
```

## 安装路径

统一安装路径：
- Skills: `~/.agents/skills/`（所有 Agent 工具共享）
- Agent: `~/.kimi/agents/superpower/`（仅 Kimi）

## 使用方法

### 方式1: 使用生成的启动脚本（推荐）

```bash
# 安装后会在项目根目录生成 kimi-superpower 脚本
./kimi-superpower
```

### 方式2: 直接指定 agent-file

```bash
kimi --agent-file ~/.kimi/agents/superpower/agent.yaml
```

### 方式3: 创建别名

添加到 `~/.bashrc` 或 `~/.zshrc`:

```bash
alias kimi-superpower='kimi --agent-file ~/.kimi/agents/superpower/agent.yaml'
```

## 目录结构

```
kimi/
├── README.md                    # 本文件
├── agents/
│   └── superpower/              # Agent 配置
│       ├── agent.yaml           # Agent 定义
│       ├── system.md            # 系统提示词
│       └── README.md
└── skills/                      # Skills 目录（15 个）
    ├── dev-using-skills/
    ├── dev-brainstorming/
    ├── dev-debugging/
    ├── dev-tdd/
    ├── dev-writing-plans/
    ├── dev-executing-plans/
    ├── dev-git-worktrees/
    ├── dev-requesting-review/
    ├── dev-verification/
    ├── dev-finishing-branch/
    ├── dev-writing-skills/
    ├── dev-code-cleanup/
    ├── dev-update-codemaps/
    ├── dev-backend-patterns/
    └── dev-frontend-patterns/
```

## 核心工作流

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

## 相关链接

- [Kimi Code CLI 文档](https://moonshotai.github.io/kimi-cli/)
- [superpowers 框架](https://github.com/obra/superpowers)
- [Agent Skills 规范](https://agentskills.io/)
