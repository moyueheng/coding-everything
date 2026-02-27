# Agent Skills 标准文档

> 本文档整合了 [Agent Skills 开放标准](https://agentskills.io/specification) 和 [Claude Code Skills 实现](https://code.claude.com/docs/en/skills) 的核心内容，并提供深度对比分析。

---

## 概述

**Agent Skills** 是包含指令、脚本和资源的文件夹，AI Agent 可以发现并使用它们来更准确、更高效地完成任务。

### 核心优势

| 角色 | 价值 |
|------|------|
| **Skill 作者** | 一次构建能力，部署到多个 Agent 产品 |
| **兼容 Agent** | 支持 skills 让终端用户开箱即用地赋予 Agent 新能力 |
| **团队/企业** | 将组织知识捕获为可移植、版本控制的包 |

### Skills 能做什么

- **领域专业知识**: 将专业领域知识打包为可复用指令（从法律审查流程到数据分析管道）
- **新能力**: 赋予 Agent 新能力（如创建演示文稿、构建 MCP 服务器、分析数据集）
- **可重复工作流**: 将多步骤任务转变为一致且可审计的工作流
- **互操作性**: 跨不同兼容 skills 的 Agent 产品复用相同 skill

### 两种标准的关系

Claude Code 明确声明：*"Claude Code skills follow the Agent Skills open standard... Claude Code extends the standard with additional features"*

| 维度 | Agent Skills 开放标准 | Claude Code Skills |
|------|----------------------|-------------------|
| **定位** | 跨平台通用标准 | Claude Code 专属实现 |
| **关系** | 基础标准 | 扩展实现 |
| **目标** | 互操作性、可移植性 | 用户体验、高级功能 |
| **约束** | 严格、最小化 | 灵活、功能丰富 |

---

## Skill 文件结构

每个 Skill 是一个目录，`SKILL.md` 是必需的入口文件。

### 标准结构（Agent Skills）

```
skill-name/
├── SKILL.md          # 必需
├── scripts/          # 可执行代码
├── references/       # 附加文档
│   ├── REFERENCE.md
│   ├── FORMS.md
│   └── domain-specific.md
└── assets/           # 静态资源
    ├── templates/
    ├── images/
    └── data/
```

**特点：**
- 标准化目录命名（`scripts/`, `references/`, `assets/`）
- 每个目录有明确的用途划分
- 强调资源类型的分离

### Claude Code 结构

```
my-skill/
├── SKILL.md           # 必需
├── template.md        # 模板
├── examples/          # 示例
│   └── sample.md
└── scripts/
    └── validate.sh
```

**特点：**
- 更灵活的命名
- 强调 `examples/` 和 `template.md`
- 没有强制的 `references/` 和 `assets/` 目录

### 支持文件说明

- `SKILL.md`: 包含主要指令，是必需的
- `template.md`: Claude 要填写的模板
- `examples/`: 显示预期格式的示例输出
- `scripts/`: 可执行脚本（Agent 决定支持的语言，常见 Python、Bash、JavaScript）
- `references/`: 详细参考文档（Agent Skills 标准）
- `assets/`: 静态资源如模板、图片、数据文件（Agent Skills 标准）

从 `SKILL.md` 中引用这些文件，以便 Agent 知道它们包含什么以及何时加载它们。

---

## SKILL.md 格式规范

### YAML Frontmatter（`---` 标记之间）

```yaml
---
name: my-skill
description: What this skill does and when to use it.
license: MIT
metadata:
  author: my-org
  version: "1.0"
---
```

#### Frontmatter 字段参考

| 字段 | Agent Skills | Claude Code | 说明 |
|------|-------------|-------------|------|
| `name` | **必填** | 可选 | Skill 显示名称，1-64字符，小写/数字/连字符 |
| `description` | **必填** | 推荐 | 功能描述+使用时机，1-1024字符 |
| `license` | 可选 | ❌ | 许可证声明 |
| `compatibility` | 可选 | ❌ | 环境要求（1-500字符）|
| `metadata` | 可选 | ❌ | 扩展元数据键值对 |
| `allowed-tools` | 实验性 | 支持 | 预批准工具列表 |
| `argument-hint` | ❌ | 支持 | 自动完成提示，如 `[issue-number]` |
| `disable-model-invocation` | ❌ | 支持 | 设为 `true` 禁止自动触发 |
| `user-invocable` | ❌ | 支持 | 设为 `false` 从 `/` 菜单隐藏 |
| `model` | ❌ | 支持 | Skill 激活时使用的模型 |
| `context` | ❌ | 支持 | 设为 `fork` 在 subagent 中运行 |
| `agent` | ❌ | 支持 | `context: fork` 时的 subagent 类型 |
| `hooks` | ❌ | 支持 | Skill 生命周期 hooks |

#### `name` 字段约束（Agent Skills 更严格）

**Agent Skills：**
- 1-64 字符
- 仅小写字母、数字、连字符
- **不能首尾连字符**
- **不能连续连字符** (`--`)
- **必须与父目录名完全匹配**

**Claude Code：**
- 最多 64 字符
- 小写字母、数字、连字符
- 省略则使用目录名

#### `description` 要求

**Agent Skills（强制）：**
```yaml
# 必须同时描述：做什么 + 何时使用
description: Extracts text from PDFs. Use when working with PDF documents or when user mentions PDFs.
```
- 1-1024 字符
- 必须描述**做什么**和**何时使用**
- 应包含帮助 Agent 识别任务的关键词

**Claude Code：**
- 推荐但不强制
- 省略则使用 markdown 第一段

#### 调用控制组合（Claude Code 特有）

| Frontmatter | 用户可调用 `/name` | Claude 可自动调用 | 描述是否在上下文中 |
|-------------|-------------------|------------------|-------------------|
| （默认）| ✓ | ✓ | 始终在上下文中 |
| `disable-model-invocation: true` | ✓ | ✗ | 不在上下文中，调用时加载 |
| `user-invocable: false` | ✗ | ✓ | 始终在上下文中 |

### Markdown 内容

Skill 的具体指令，Agent 在调用时遵循。

#### 内容类型

**参考内容（Reference）**: 添加 Agent 应用于当前工作的知识

```markdown
---
name: api-conventions
description: API design patterns for this codebase
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
- Include request validation
```

**任务内容（Task）**: 为 Agent 提供特定操作的分步说明

```markdown
---
name: deploy
description: Deploy the application to production
context: fork
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite
2. Build the application
3. Push to the deployment target
```

---

## 渐进式披露（Progressive Disclosure）

Agent Skills 推荐的内容加载策略：

| 层级 | 内容 | Token 预算 | 加载时机 |
|------|------|-----------|---------|
| **Metadata** | `name` + `description` | ~100 | 启动时，所有 skills |
| **Instructions** | `SKILL.md` body | < 5000 推荐 | Skill 激活时 |
| **Resources** | `scripts/`, `references/`, `assets/` | 按需 | 引用时 |

**约束：**
- 主 `SKILL.md` 建议 < 500 行
- 详细内容移至单独文件
- 保持文件引用一级深度

---

## 字符串替换变量

| 变量 | Agent Skills | Claude Code | 描述 |
|------|-------------|-------------|------|
| `$ARGUMENTS` | ✓ | ✓ | 调用时传递的所有参数 |
| `$ARGUMENTS[N]` | ✓ | ✓ | 按 0 基索引访问特定参数 |
| `$N` | ✓ | ✓ | `$ARGUMENTS[N]` 的简写 |
| `${CLAUDE_SESSION_ID}` | ❌ | ✓ | 当前会话 ID |

### 使用示例

```markdown
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit
```

运行 `/fix-issue 123` 时，`$ARGUMENTS` 被替换为 `123`。

---

## 存放位置

Skill 存储位置决定谁可以使用它（Claude Code 四级优先级）：

| 级别 | 路径 | 适用范围 |
|------|------|----------|
| Enterprise | 托管设置 | 组织所有用户 |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | 所有项目 |
| Project | `.claude/skills/<skill-name>/SKILL.md` | 仅当前项目 |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | 插件启用处 |

### 优先级规则

- 当 skills 在不同级别共享相同名称时，**更高优先级的位置获胜**: enterprise > personal > project
- Plugin skills 使用 `plugin-name:skill-name` 命名空间，避免与其他级别冲突
- `.claude/commands/` 中的文件工作方式相同，但 skill 与 command 同名时 skill 优先

### 嵌套目录自动发现

在子目录中处理文件时，Claude Code 自动从嵌套的 `.claude/skills/` 目录中发现 skills。例如，编辑 `packages/frontend/` 中的文件时，也会查找 `packages/frontend/.claude/skills/` 中的 skills。这支持 monorepo 设置。

---

## 高级特性（Claude Code 特有）

### 1. 动态上下文注入

使用 `` !`command`` `` 语法在 skill 内容发送给 Claude 前运行 shell 命令，输出替换占位符：

```markdown
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

执行流程：
1. 每个 `` !`command`` `` 立即执行（Claude 看到内容前）
2. 输出替换 skill 内容中的占位符
3. Claude 接收具有实际数据的完全渲染的提示

### 2. 在 Subagent 中运行

添加 `context: fork` 让 skill 在隔离中运行。skill 内容变成驱动 subagent 的 prompt，无法访问对话历史。

```markdown
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

执行流程：
1. 创建新的隔离上下文
2. Subagent 接收 skill 内容作为其提示
3. `agent` 字段确定执行环境（模型、工具、权限）
4. 结果被总结并返回到主对话

**Agent 类型：**

| Agent 类型 | 用途 |
|-----------|------|
| `Explore` | 代码库探索（只读工具）|
| `Plan` | 计划制定 |
| `general-purpose` | 通用任务（默认）|

### Skills 与 Subagents 的关系

| 方法 | 系统提示 | 任务 | 同时加载 |
|------|----------|------|----------|
| 带 `context: fork` 的 Skill | 来自 agent 类型 | SKILL.md 内容 | CLAUDE.md |
| 带 `skills` 字段的 Subagent | Subagent 的 markdown 正文 | Claude 的委派消息 | 预加载的 skills + CLAUDE.md |

---

## 平台支持

Agent Skills 开放标准被以下 AI 开发工具支持：

- **Claude Code** - Anthropic 的 AI 编程助手
- **Codex** - OpenAI 的 CLI 编程助手
- **Kimi CLI** - Moonshot AI 的命令行工具
- **OpenCode** - 开源 AI 编程助手

---

## 工具权限

### `allowed-tools` 字段

**Agent Skills（实验性）：**
```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```
- 空格分隔
- 支持工具名 + 参数模式
- 标注为实验性，支持度因实现而异

**Claude Code：**
```yaml
allowed-tools: Read, Grep, Glob
```
- 逗号分隔
- 实现更成熟
- 支持动态权限控制

---

## 验证工具（Agent Skills 特有）

```bash
skills-ref validate ./my-skill
```

- 检查 frontmatter 有效性
- 验证命名约定
- 标准提供的参考实现
- 建议在 CI/CD 中使用

---

## 最佳实践

### 命名规范

- 使用小写字母、数字、连字符
- 最大 64 字符
- 使用分类前缀便于区分：`dev-`, `life-`, `work-`, `tool-`, `learn-`
- **遵循 Agent Skills 标准**：`name` 必须与父目录名匹配

### 描述编写

- 包含用户会自然说的关键词
- 描述应具体，避免过于宽泛导致频繁触发
- **遵循 Agent Skills 标准**：同时说明"做什么"和"何时使用"
- 1-1024 字符

### 内容组织

- 保持 `SKILL.md` 专注要点（< 500 行）
- 大型参考文档放在单独文件，按需引用
- 复杂 skills 使用支持文件保持主 skill 简洁
- 详细内容放入 `references/`
- 可执行脚本放入 `scripts/`

### 工具限制

- 使用 `allowed-tools` 创建只读模式（`Read, Grep, Glob`）
- 谨慎授予 `Bash` 权限，尽量限制命令范围（`Bash(gh *)`）

---

## 混合策略（推荐）

编写兼容 Agent Skills 标准同时利用 Claude Code 扩展的 skill：

```yaml
---
# Agent Skills 标准字段（核心，确保跨平台兼容）
name: my-skill
description: Does something useful. Use when...
license: MIT
compatibility: Designed for Claude Code and compatible agents
metadata:
  author: my-org
  version: "1.0"

# Claude Code 扩展字段（可选增强）
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Bash
---
```

**原则：**
1. 核心字段（`name`, `description`）遵循 Agent Skills 标准
2. Claude 扩展字段（`disable-model-invocation`, `context` 等）作为可选增强
3. 使用 `metadata` 存储自定义数据
4. 使用 `license` 和 `compatibility` 声明元信息
5. 为跨平台兼容性做测试

---

## 故障排除

### Skill 未触发

1. 检查描述是否包含用户会自然说的关键词
2. 验证 skill 是否出现在 `What skills are available?`
3. 尝试重新表述请求以更接近描述
4. 使用 `/skill-name` 直接调用

### Skill 触发过于频繁

1. 使描述更具体
2. 添加 `disable-model-invocation: true` 仅手动调用

### Claude 看不到所有 Skills

- Skill 描述加载到上下文，过多可能超过字符预算
- 预算在上下文窗口的 2% 处动态缩放，回退为 16,000 字符
- 运行 `/context` 检查排除的 skills 警告
- 设置 `SLASH_COMMAND_TOOL_CHAR_BUDGET` 环境变量覆盖限制

---

## 选择建议

### 使用纯 Agent Skills 标准当：

- 需要**跨平台兼容**（Claude Code, Codex, Kimi, OpenCode）
- 需要**严格的验证**（`skills-ref validate`）
- 需要声明**许可证**和**兼容性**
- Skill 需要**长期维护**和**广泛分发**
- 遵循**最小化原则**

### 使用 Claude Code 扩展当：

- 仅在 **Claude Code** 中使用
- 需要**高级调用控制**（`disable-model-invocation`, `user-invocable`）
- 需要 **Subagent 执行**（`context: fork`）
- 需要**动态上下文注入**（`` !`command`` ``）
- 需要**会话级功能**（`${CLAUDE_SESSION_ID}`）

---

## 总结表

| 特性类别 | Agent Skills | Claude Code | 建议 |
|---------|-------------|-------------|------|
| **标准性质** | 开放标准 | 具体实现 | 核心遵循标准，扩展按需使用 |
| **必填字段** | `name`, `description` | 无 | 始终填写 `name` 和 `description` |
| `name` 约束 | 严格（匹配目录）| 宽松 | 遵循标准约束 |
| `description` | 强制 | 推荐 | 始终编写完整描述 |
| 许可证 | 支持 | ❌ | 开源 skill 建议添加 |
| 兼容性声明 | 支持 | ❌ | 跨平台 skill 建议添加 |
| 调用控制 | ❌ | 支持 | Claude 专用时使用 |
| Subagent | ❌ | 支持 | 需要隔离执行时使用 |
| 动态注入 | ❌ | 支持 | 需要实时数据时使用 |
| 验证工具 | `skills-ref` | ❌ | CI/CD 中验证标准合规性 |
| 目录命名 | 标准化 | 灵活 | 遵循标准目录结构 |

---

## 参考链接

- **Agent Skills Specification**: https://agentskills.io/specification
- **Agent Skills 官网**: https://agentskills.io/
- **Claude Code Skills 文档**: https://code.claude.com/docs/en/skills
- **Agent Skills GitHub**: https://github.com/anthropics/skills

---

*本文档基于 2025 年初的官方文档整理，标准可能持续演进*
