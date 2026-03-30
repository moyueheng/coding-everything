---
name: setup
description: 安装 coding-everything 配置到系统，支持 Kimi/Claude Code/Codex/OpenCode 多平台。当用户需要安装 skills、初始化配置或运行 setup 时使用。
license: MIT
---

现在开始安装 coding-everything 的共享 skills 与 Kimi 默认配置。当用户需要安装 skills、初始化配置或运行 setup 时使用。

# Setup: 安装 Coding Everything 配置

安装个人 AI 编程助手配置到系统。默认采用逐项 symlink 的方式，把本仓库的共享 `skills/` 合并安装到用户已有目录中，并同时安装 Kimi agent 与 `ks`。

**兼容性：**
- **Kimi CLI**: 使用 `~/.kimi/agents/superpower` 和 `ks`
- **Claude Code**: 使用 `~/.claude/skills/`
- **共享 skills**: 同时写入 `~/.agents/skills/` 与 `~/.claude/skills/`

## 参考文档

- [Agent Skills 标准](references/skill-standard.md) - Skill 格式规范与多平台兼容性说明
- [安装重构设计](../../../docs/plans/2026-03-31-setup-install-refactor-design.md) - 安装模型、manifest 与边界说明

## 安装入口

推荐使用仓库根目录的短入口：

```bash
make install
make update
make uninstall
make status
```

其中：

- `make install` 安装共享 `skills/`、`~/.kimi/agents/superpower` 和 `ks`
- `make update` 只更新本仓库受管内容
- `make uninstall` 只删除 manifest 登记的内容
- `make status` 查看安装状态

## 安装模型

共享 `skills/` 的安装行为是逐项合并安装，而不是整目录接管。

```text
repo/skills/<skill-name>
  -> ~/.agents/skills/<skill-name>
  -> ~/.claude/skills/<skill-name>
```

默认语义等同强制覆盖：

- 同名 skill 会被替换为本仓库版本
- 不会扫描并删除用户其他无关 skill
- uninstall/update/status 依赖 manifest 只管理本仓库安装过的项

Kimi 默认安装项：

```text
kimi/agents/superpower
ks
```

## 安装流程

### 1. 检查源目录

确认项目目录结构完整：
- `skills/` - 跨平台共享 skill 目录
- `kimi/agents/superpower/` - Kimi Agent 配置（仅 Kimi 需要）

### 2. 创建目标目录

```bash
mkdir -p ~/.agents
mkdir -p ~/.claude
mkdir -p ~/.kimi/agents
mkdir -p ~/.local/bin
```

### 3. 安装共享 skills

逐项将 `skills/` 中的 skill 安装到两个目标目录：

```bash
make install
```

### 4. 验证安装

检查所有组件是否正确安装：
```bash
ls -la ~/.agents/skills
ls -la ~/.claude/skills
ls -la ~/.kimi/agents/superpower
which ks
```

### 5. 输出结果

显示安装状态：
- Skills 数量
- Agent 配置状态
- 各平台使用方法

## 使用方式

### 快速启动（推荐）

```bash
ks                    # YOLO 模式启动 Kimi + Superpower Agent
ks -w /path/to/project # 指定工作目录
```

### 各平台命令

| 平台 | 命令 | 说明 |
|------|------|------|
| **Kimi CLI** | `kimi --agent-file ~/.kimi/agents/superpower/agent.yaml` | 带 Agent 配置启动 |
| **Claude Code** | `claude` | 自动加载 `~/.claude/skills/` |
| **Codex** | `codex` | 自动加载 `~/.agents/skills/` |
| **OpenCode** | `opencode` | 自动加载 `~/.agents/skills/` |

## 平台兼容性

**Skills 目录结构**遵循 [Agent Skills 开放标准](references/skill-standard.md)：
- 路径：`~/.agents/skills/<skill-name>/SKILL.md` 或 `~/.claude/skills/<skill-name>/SKILL.md`
- 格式：YAML frontmatter + Markdown 内容
- 兼容：Claude Code、Codex、Kimi CLI、OpenCode
- 安装器使用 manifest 跟踪本仓库受管项，避免误删用户自行安装的其他 skill

## 实时同步

由于采用逐项 symlink，修改项目中的 skill 文件会立即生效：

```bash
vim skills/dev-tdd/SKILL.md  # 修改后立即生效
```

## 卸载

如需卸载，删除 manifest 记录的受管项即可：

```bash
make uninstall
```
