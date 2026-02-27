---
name: setup
description: 安装 coding-everything 配置到系统。当用户需要安装 skills、初始化配置或运行 setup 时使用。
license: MIT
---

# Setup: 安装 Coding Everything 配置

安装个人 AI 编程助手配置到系统，使用 symlink 模式实现实时同步。

## 安装流程

### 1. 检查源目录

确认项目目录结构完整：
- `kimi/skills/` - 技能目录
- `kimi/agents/superpower/` - Kimi Agent 配置

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
- 使用方法

## 使用方式

安装完成后：

**Kimi CLI:**
```bash
kimi --agent-file ~/.kimi/agents/superpower/agent.yaml
```

**Codex:**
```bash
codex
```

**OpenCode:**
```bash
opencode
```

## 实时同步

由于使用 symlink，修改项目中的技能文件会立即生效：

```bash
vim kimi/skills/dev-tdd/SKILL.md  # 修改后立即生效
```

## 卸载

如需卸载，删除 symlink 即可：

```bash
rm ~/.agents/skills
rm -rf ~/.kimi/agents/superpower
```
