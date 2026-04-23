# coding-everything Roadmap

最后更新：2026-04-24

## 文档目的

这份文档专门记录 `coding-everything` 的项目规划，用来回答四个问题：

- 这个项目接下来要演进成什么
- 当前处于什么阶段
- 接下来几个阶段分别做什么
- 哪些事情现在明确不做

它不是实现计划，不替代 `docs/plans/` 里的执行级文档。

## 项目愿景

把 `coding-everything` 从“个人维护的一组 AI 助手配置和 skill 集合”，逐步演进成一个更清晰的、可扩展的、跨工具的 skill 平台。

目标不是做一个重型平台，也不是做一个 GUI 壳，而是把下面几层能力打稳：

```text
skills content
    ->
installation and distribution
    ->
tool adapters and workspace scopes
    ->
verification, discovery, and sync policy
    ->
source management and trust
```

长期看，这个仓库应该同时承担三种角色：

1. 共享 skill 仓库
2. 多工具安装与分发系统
3. 上游生态吸收、本地化和沉淀的中枢

## 当前阶段判断

截至 2026-04-24，项目更接近：

```text
skill repository
  + installer
  + upstream sync
  + partial workspace conventions
```

已经具备的基础：

- 共享 `skills/` 目录已经成型
- `ce` CLI 已经能做基础安装、更新、卸载、状态检查
- manifest 模型已经存在
- 已有多工作区 agent context 模板
- 已有上游 submodule + 迁移 + 文档化工作流

当前主要短板：

- tool 适配规则分散在文档和安装逻辑里，缺少显式 registry
- scope 还没有统一建模成 `user / workspace / project / vault`
- skill discovery 还偏“固定目录结构”，对多层布局兼容不够系统
- sync 策略偏 symlink 优先，缺少更明确的 fallback 模式
- source、trust、安全治理还没进入正式设计

## 规划原则

后续 roadmap 统一遵循这些原则：

1. 先做抽象，再做壳
2. 优先增强 CLI 和数据模型，不优先做重型 GUI
3. 优先兼容真实 skill 仓库布局，不要求外部世界适配我们
4. 避免隐式耦合，tool 适配规则必须显式化
5. 先把本地单机能力做扎实，再讨论账号、云同步、市场

## 阶段路线

## Phase 1: Skill Manager Core

目标：把现在的安装器升级成更清晰的 skill manager core。

### 1. Tool Adapter Registry

建立显式的 tool 适配层，把每个工具的路径、能力和限制从散落逻辑里抽出来。

建议最小模型：

```text
ToolAdapter
  - id
  - display_name
  - supported_scopes
  - global_skill_paths
  - project_skill_paths
  - supports_symlink
  - preferred_sync_mode
  - discovery_notes
```

阶段完成标志：

- 新增一个工具时，不需要把路径规则写散到多个文件
- `ce` 能基于 registry 输出兼容矩阵

### 2. Scope Model 统一化

把现在分散存在的安装目标，统一收敛成显式 scope：

```text
user
workspace
project
vault
```

阶段完成标志：

- `ce install/status/update` 可以显式按 scope 工作
- 文档、模板、安装逻辑使用同一套 scope 术语

### 3. Skill Discovery Engine

从“只认一种目录结构”升级到“支持常见 skill 仓库布局”的发现器。

至少支持：

- `skills/<skill>/SKILL.md`
- `skills/<group>/<skill>/SKILL.md`
- `<repo-root>/SKILL.md`
- 被 vendor / upstream 引入的多层目录

阶段完成标志：

- discovery 能输出 found / skipped / duplicate 报告
- 对 `superpowers` 这类多层 skill 布局有明确兼容策略

### 4. Sync Policy 抽象

把同步策略从“基本等于 symlink”升级为显式可配置：

```text
symlink
copy
mirror
```

短期先实现 `symlink` 和 `copy`。

阶段完成标志：

- tool 可以声明默认 sync mode
- 用户可以覆盖 sync mode
- `ce status` 能区分“已安装但漂移”和“安装策略不兼容”

## Phase 2: Management Layer

目标：从“能安装”升级到“能管理”。

### 1. Group 和 Batch 管理增强

把已有 group 概念提升为真正的一等公民。

建议能力：

- group enable / disable
- group diff
- group export / import
- group sync to targets
- batch apply / batch verify

阶段完成标志：

- group 不只是配置文件里的字段，而是 CLI 的稳定能力
- 常见批量操作不再依赖手工拼命令

### 2. Verification 和 Drift Detection

把“安装状态”从存在性检查，升级为更可信的状态校验。

建议能力：

- target 是否存在
- link / copy 是否符合预期
- 目标是否漂移
- manifest 是否过期
- tool 目录是否仍然可读

阶段完成标志：

- `ce status` 能解释“为什么不一致”
- `ce verify` 能输出可执行修复建议

### 3. 文档自动生成

用 registry + discovery 数据反向生成一部分稳定文档。

适合自动生成的内容：

- 支持的 tool 列表
- 各 tool 的 global/project 路径
- compatibility matrix
- scope 与 target 说明

阶段完成标志：

- 关键兼容信息不再只能靠手写 README 维护

## Phase 3: Source Layer

目标：把 skill 的来源和输入边界做清楚。

### 1. Source Abstraction

不要把 source 设计成只支持 GitHub。

建议模型：

```text
SkillSource
  - local_path
  - git_https
  - git_ssh
  - github_repo
  - private_git
  - archive_file
```

阶段完成标志：

- 可以统一描述本地目录、公开 Git 仓库、私有 Git 源
- 后续接 marketplace / registry 时不用推翻模型

### 2. Upstream Intake Workflow

把“发现一个外部 skill 仓库并吸收进来”的过程进一步模板化。

建议沉淀的步骤：

1. discovery
2. license check
3. layout compatibility check
4. local adaptation
5. `UPSTREAM.md` 记录
6. install target 声明

阶段完成标志：

- 新引入一个上游 skill 仓库时，有稳定入口和固定检查项

## Phase 4: Trust Layer

目标：让 skill 的安装和分发更可信。

### 1. Trust Metadata

为 source 或 skill 记录最低限度的信任信息：

- 来源
- 作者
- license
- upstream URL
- hash / revision
- 本地适配状态

### 2. 安全治理基础

短期不做复杂扫描平台，但至少做最基本的风险提示机制。

可考虑：

- install 前提示 source 类型
- 未知来源提示
- 仅白名单源安装
- 对高风险脚本型 skill 给出显式 warning

阶段完成标志：

- “这个 skill 从哪来、能不能信”不再完全靠人工记忆

## Phase 5: Optional Product Surface

目标：只在 core 足够稳定之后，再考虑更高层产品形态。

可评估但不承诺当前周期投入：

- 轻量 marketplace / registry
- profile sharing
- team preset
- 远期云同步
- 远期桌面应用或 Web 控制台

这里要明确：

```text
core first
distribution second
cloud last
GUI optional
```

## 明确不优先做的事

当前 roadmap 明确不优先：

- 新引入重型 GUI 框架
- 先做账号系统再补 core 抽象
- 在没有 source / trust 模型前做 marketplace
- 为单一工具写大量特判而不抽象公共 adapter
- 把文档模板和安装逻辑继续分叉演进

## 未来 3 个里程碑

### M1: Core 抽象稳定

范围：

- Tool Adapter Registry
- Scope Model
- Skill Discovery Engine
- Sync Policy v1

完成后项目状态应变成：

```text
skill repository
  + configurable manager core
```

### M2: 管理能力完整

范围：

- Group / Batch 管理
- Verify / Drift Detection
- Compatibility 文档自动生成

完成后项目状态应变成：

```text
skill repository
  + manager core
  + operational management layer
```

### M3: 来源与信任成型

范围：

- Source Abstraction
- Upstream Intake Workflow
- Trust Metadata

完成后项目状态应变成：

```text
skill platform
  = content + distribution + source + trust
```

## 和现有调研文档的关系

这份 roadmap 主要吸收并固化了：

- [Skills-Manager 架构调研](./2026-04-23-skills-manager-architecture-research.md)
- 现有 `ce` CLI / manifest / 安装流程现状
- 多工作区 agent context 方案

如果后面继续调研别的项目，这份 roadmap 应该继续更新，但保持结构稳定，不要每次重写。

## 维护规则

更新这份 roadmap 时，优先修改：

- 当前阶段判断
- 阶段目标
- 完成标志
- 非优先项

不要把它写成流水账或周报。它应该始终保持：

- 稳定
- 高信息密度
- 可作为项目方向判断依据
