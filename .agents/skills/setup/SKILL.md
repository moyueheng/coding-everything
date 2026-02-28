---
name: setup
description: 安装 coding-everything 配置到系统，支持 Kimi/Codex/OpenCode 多平台。当用户需要安装 skills、初始化配置或运行 setup 时使用。
license: MIT
---

# Setup: 安装 Coding Everything 配置

安装个人 AI 编程助手配置到系统，使用 symlink 模式实现实时同步。

**兼容性：** Kimi CLI、Codex、OpenCode 均支持 `~/.agents/skills/` 路径。

## 参考文档

- [Agent Skills 标准](references/skill-standard.md) - Skill 格式规范与多平台兼容性说明

## 安装流程

### 1. 检查源目录

确认项目目录结构完整：
- `kimi/skills/` - skill 目录（Kimi/Codex/OpenCode 共享）
- `kimi/agents/superpower/` - Kimi Agent 配置（仅 Kimi 需要）

### 2. 创建目标目录

```bash
mkdir -p ~/.agents
mkdir -p ~/.kimi/agents
```

### 3. 创建 Symlink

**Skills（所有 Agent 工具共享）：**
```bash
ln -sf "$(pwd)/kimi/skills" ~/.agents/skills
```

**Agent 配置（仅 Kimi）：**
```bash
ln -sf "$(pwd)/kimi/agents/superpower" ~/.kimi/agents/superpower
```

### 4. 验证安装

检查 symlink 是否正确创建：
```bash
ls -la ~/.agents/skills
ls -la ~/.kimi/agents/superpower
```

### 5. 输出结果

显示安装状态：
- Skills 数量
- Agent 配置状态
- 各平台使用方法

## 使用方式

安装完成后，各平台均可使用：

| 平台 | 命令 | 说明 |
|------|------|------|
| **Kimi CLI** | `kimi --agent-file ~/.kimi/agents/superpower/agent.yaml` | 带 Agent 配置启动 |
| **Codex** | `codex` | 自动加载 `~/.agents/skills/` |
| **OpenCode** | `opencode` | 自动加载 `~/.agents/skills/` |

## 平台兼容性

**Skills 目录结构**遵循 [Agent Skills 开放标准](references/skill-standard.md)：
- 路径：`~/.agents/skills/<skill-name>/SKILL.md`
- 格式：YAML frontmatter + Markdown 内容
- 兼容：Claude Code、Codex、Kimi CLI、OpenCode

## 实时同步

由于使用 symlink，修改项目中的 skill 文件会立即生效：

```bash
vim kimi/skills/dev-tdd/SKILL.md  # 修改后立即生效
```

## 卸载

如需卸载，删除 symlink 即可：

```bash
rm ~/.agents/skills
rm -rf ~/.kimi/agents/superpower
```
