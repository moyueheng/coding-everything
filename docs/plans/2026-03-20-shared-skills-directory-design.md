# 共享 skill 顶层化重构设计

日期：2026-03-20

## 背景

当前仓库将跨平台共享的 skill 主资产放在 `kimi/skills/` 下，但这些 skill 实际同时面向 Kimi、Codex、OpenCode，以及通过兼容路径供 Claude Code 使用。

这导致两个问题：

1. 目录语义失真。`kimi/skills/` 看起来像 Kimi 专属配置，实际却是跨平台共享资产。
2. 结构约束被历史命名污染。安装说明、架构图、setup 文档和后续扩展都默认把共享 skill 与 Kimi 绑定。

与此同时，参考文档 `.agents/skills/setup/references/skill-standard.md` 已明确说明这些平台兼容同一套 Agent Skills 标准，因此共享 skill 不应继续挂在单一平台目录下。

## 目标

将共享 skill 从平台目录中剥离，提升为仓库顶层资产；平台目录只保留各平台专属的 agent、配置和入口文件。

本次重构只处理目录语义、仓库路径和安装说明，不主动改变用户侧的技能发现行为。

## 非目标

- 不重写现有 skill 内容
- 不改变 Kimi agent 的行为和提示词逻辑
- 不在本次重构中引入新的平台启动器或新的安装机制
- 不将所有平台目录改成点目录，例如 `.kimi/`

## 设计原则

### 1. 共享能力与平台适配分离

共享资产使用能力导向命名，放在顶层：

```text
skills/
```

平台专属内容继续按平台组织，例如：

```text
kimi/
codex/
opencode/
```

### 2. 借鉴 superpowers 的分层原则，不机械照搬命名

参考 `upstream/superpowers`：

- 顶层 `skills/` 承载共享能力
- 平台相关目录承载平台分发或集成入口

本仓库应借鉴其“共享能力 vs 平台适配”的边界划分，但不要求把 Kimi 仓库目录改成 `.kimi/`。仓库内部目录首先服务可维护性，其次才是平台自动发现约定。

### 3. 优先纠正仓库语义，保守处理运行时兼容

本次先纠正仓库内主资产路径和文档表达。安装后的用户侧目标路径维持现状，以降低行为回归风险。

## 目标结构

```text
coding-everything/
├── skills/                 # 跨平台共享 skill
├── kimi/                   # Kimi 专属 agent/config
├── codex/                  # Codex 专属 config
├── opencode/               # OpenCode 专属 config
├── .agents/skills/         # 系统级 meta skills
└── upstream/
```

### 目录职责

- `skills/`
  - 当前 `kimi/skills/` 的继承者
  - 承载跨平台共享的主 skill 资产
- `kimi/`
  - 仅保留 Kimi 专属 agent/config，例如 `kimi/agents/superpower/`
- `codex/`
  - 仅保留 Codex 专属配置
- `opencode/`
  - 仅保留 OpenCode 专属配置
- `.agents/skills/`
  - 保留系统级 meta skills，例如 setup、update-upstream-repos
  - 不与业务/开发共享 skill 混合

## 迁移方案

### 第一阶段：主资产迁移

1. 将 `kimi/skills/` 整体迁移为 `skills/`
2. 保持 `kimi/agents/superpower/` 不动
3. 更新所有仓库内对 `kimi/skills` 的直接引用

这一阶段的目标是完成语义纠偏，并让仓库主结构稳定下来。

### 第二阶段：文档与安装收口

更新以下内容，使其统一以 `skills/` 作为共享来源：

- `README.md`
- `AGENTS.md`
- `.agents/skills/setup/SKILL.md`
- `.agents/skills/setup/references/skill-standard.md` 中与本仓库示例耦合的描述
- `docs/kimi-skills-architecture.md`
- 其他设计文档、计划文档、脚本注释、说明文本

### 第三阶段：兼容层清理

短期可以保留兼容层，例如：

```text
kimi/skills -> ../skills
```

兼容层只作为过渡，不作为长期结构。待仓库内路径引用清理完成后移除。

## 安装与运行时兼容策略

本次重构不改变用户侧安装目标路径，只改变仓库中的源路径。

### 保持不变

- 共享 skill 仍安装到 `~/.agents/skills`
- Claude Code 兼容路径仍可安装到 `~/.claude/skills`
- Kimi 专属 agent 仍安装到 `~/.kimi/agents/superpower`
- `ks` 仍作为 Kimi 启动入口

### 发生变化

- setup、README 和相关脚本中的 `SKILLS_SOURCE` 或说明文本，改为引用仓库顶层 `skills/`

## 命名决策

### 为什么不用 `shared/skills/`

`skills/` 更接近上游 `superpowers` 的共享能力表达，也更符合 Agent Skills 仓库的通用预期。`shared/skills/` 会增加一层没有必要的抽象。

### 为什么不用 `.kimi/`

`.kimi/` 更像平台自动发现入口，不适合作为仓库中的主要人工维护目录。隐藏目录会降低结构可见性，但不能带来足够的收益。本仓库当前更需要清晰的资产边界，而不是隐藏化。

## 风险与缓解

### 风险 1：旧文档或脚本仍引用 `kimi/skills`

缓解：

- 第一轮迁移后统一全文检索并修正
- 过渡期保留兼容 symlink

### 风险 2：setup 或安装说明出现断链

缓解：

- 优先更新 `.agents/skills/setup/SKILL.md`
- 验证 symlink 目标是否改为 `$(pwd)/skills`

### 风险 3：架构文档继续把共享 skill 误称为 Kimi skill

缓解：

- 更新 `docs/kimi-skills-architecture.md` 的标题、描述和结构图
- 将“共享 skill”与“Kimi 专属 agent”分开描述

## 实施顺序

1. 迁移目录：`kimi/skills` -> `skills`
2. 更新安装与文档引用
3. 视情况添加短期兼容 symlink
4. 验证仓库内已无关键引用残留

## 验收标准

- 仓库中共享 skill 的主路径为 `skills/`
- `kimi/` 下不再承载共享 skill 主资产
- 文档与 setup 不再把共享 skill 描述为 “Kimi/Codex/OpenCode 共享的 `kimi/skills`”
- Kimi 专属 agent 路径保持稳定
- 用户侧安装目标路径与现有行为保持兼容
