---
name: dev-git-worktrees
description: 开始需要与当前工作区隔离的功能工作前使用，或在执行实施计划前 - 创建隔离的 git worktree
---

# 使用 Git Worktrees

## 概述

Git worktrees 创建共享同一仓库的隔离工作区，允许同时工作在多个分支而无需切换。

**核心原则：** 固定全局目录 + 安全验证 = 可靠隔离。

**开始时宣布：** "我正在使用 git-worktrees skill 来设置隔离工作区。"

## 目录规则

所有 git worktree 一律创建在：

```bash
~/.agents/worktrees/<项目名称>/<分支名>
```

不要使用项目内的 `.worktrees/`、`worktrees/` 或任何其他自定义目录，也不要为路径选择再次询问用户。

## 安全验证

### 对于全局目录（`~/.agents/worktrees`）

不需要 .gitignore 验证 - 完全在项目外。

## 创建步骤

### 1. 检测项目名称

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
```

### 2. 创建 Worktree

```bash
# 确定完整路径
path="$HOME/.agents/worktrees/$project/$BRANCH_NAME"
mkdir -p "$(dirname "$path")"

# 用新分支创建 worktree
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

### 3. 复制 .env 文件（如果主分支存在）

如果主分支工作区有 `.env` 文件，自动复制到新 worktree：

```bash
# 获取主分支 worktree 路径
main_worktree=$(git worktree list --porcelain | grep -A 1 "worktree" | head -2 | grep "^worktree" | cut -d ' ' -f2)

# 如果主分支有 .env 且新 worktree 没有，则复制
if [ -f "$main_worktree/.env" ] && [ ! -f "$path/.env" ]; then
    cp "$main_worktree/.env" "$path/.env"
    echo "已复制 .env 从主分支"
fi
```

### 4. 运行项目设置

自动检测并运行适当设置：

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

### 5. 验证干净基线

运行测试确保 worktree 从干净开始：

```bash
# 示例 - 使用项目适当命令
npm test
cargo test
pytest
go test ./...
```

**如果测试失败：** 报告失败，询问是继续还是调查。

**如果测试通过：** 报告就绪。

### 6. 报告位置

```
Worktree 就绪于 <完整路径>
测试通过（<N> 测试，0 失败）
准备实现 <功能名称>
```

## 快速参考

| 情况 | 行动 |
|-----------|--------|
| 需要创建 worktree | 使用 `~/.agents/worktrees/<项目名称>/<分支名>` |
| 项目内已有 `.worktrees/` 或 `worktrees/` | 忽略，不作为新 worktree 位置 |
| 基线测试失败 | 报告失败 + 询问 |
| 无 package.json/Cargo.toml | 跳过依赖安装 |
| 主分支有 .env | 自动复制到新 worktree |

## 常见错误

### 假设目录位置

- **问题：** 创建不一致，违反项目约定
- **修复：** 始终使用 `~/.agents/worktrees/<项目名称>/<分支名>`

### 测试失败仍继续

- **问题：** 无法区分新 bug 和已有问题
- **修复：** 报告失败，获取明确许可才继续

### 硬编码设置命令

- **问题：** 在不同工具的项目上中断
- **修复：** 从项目文件自动检测（package.json 等）

## 集成

**被以下调用：**
- **dev-brainstorming**（阶段 4）- 设计批准且跟随实现时必需
- **dev-subagent-driven-development** - 执行任何任务前必需
- **dev-executing-plans** - 执行任何任务前必需
- 任何需要隔离工作区的 skill

**配对：**
- **dev-finishing-branch** - 工作完成后清理必需
