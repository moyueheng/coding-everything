# Skills-Manager 架构调研与对本仓库的 roadmap 启发

调研日期：2026-04-23

调研对象：[jiweiyeah/Skills-Manager](https://github.com/jiweiyeah/Skills-Manager/tree/main)

## 结论摘要

`jiweiyeah/Skills-Manager` 值得参考的核心，不是它用了 `Tauri + React + Rust` 这一套桌面技术栈，而是它围绕“多 AI 工具下的统一 skill 管理”建立了一个更完整的产品抽象：

- 单一 skill 源目录，统一向多个 AI 工具分发
- 以软链接同步为主，避免多份拷贝漂移
- 有“工具适配层”概念，而不是把所有工具路径写死成一次性脚本
- 已经走到“项目级 skill”“skill 分组”“批量管理”“市场”“云同步”的产品化路线

对我们来说，最值得纳入 roadmap 的是这些抽象和能力边界；最不值得直接照搬的是“桌面 GUI 壳”本身。

## 调研边界

这次调研有一个非常关键的现实约束：

- 公开仓库 `main` 分支当前只包含 `README.md`、`README_CN.md`、`PRIVACY*.md`、`LICENSE`
- 公开仓库里**没有前端源码**、**没有 Rust 源码**、**没有 `src/` / `src-tauri/`**
- 因此无法做“基于源码的真实模块图”分析

所以本文严格区分三层：

- `事实`：README、Releases、Issues 中能直接证实的内容
- `推断`：基于已公开功能边界，对其内部架构做出的低风险推断
- `建议`：哪些能力值得我们吸收进后续 roadmap

## 事实层：这个项目公开暴露了什么能力

### 1. 产品定位是“统一的多工具 skill 管理器”

README 明确写了它是一个统一管理 AI coding assistant skills 的桌面应用，目标工具包括 Claude Code、Codex、Opencode 等。

来源：

- README: [GitHub README](https://github.com/jiweiyeah/Skills-Manager/tree/main)

### 2. 同步机制以软链接为核心

README 明确写了它使用 symlink synchronization mechanism，让一份 skill 可以被多个工具即时复用，而不是复制多份。

这说明它的核心数据模型大概率不是“每个工具自己维护一份 skill 副本”，而是：

```text
central skills store
      |
      +--> tool A target dir (symlink)
      +--> tool B target dir (symlink)
      `--> tool C target dir (symlink)
```

### 3. 它已经有“项目级 skills”“分组管理”“批量管理”

从最新 release `v2.0.2` 可直接确认：

- Support for adding project-level skills
- Support for skill group management
- Support for batch management

这几点很重要，因为它说明这个产品已经从“单纯同步器”演进成“部署与编排器”。

来源：

- Releases: [v2.0.2](https://github.com/jiweiyeah/Skills-Manager/releases)

### 4. 它在 `v2.0.0` 已经引入云同步与登录

`v2.0.0` release note 直接写了：

- Added cloud sync for skills and general settings
- Added Google and GitHub login functionality

这意味着它的产品路线已经从“本地单机管理”进入：

```text
local skill management
    -> account system
    -> cloud-backed settings
    -> possibly marketplace / distribution
```

### 5. 它正在走向 Marketplace / 社区分发

README roadmap 明确提到：

- Community Hub
- Cloud synchronization
- Plugin system
- Integrated AI chat interface

而 issue 侧也能看到用户已经开始围绕 market/private repo/security 提需求：

- `#32` 私有仓库 / 企业级使用诉求
- `#33` skill 安全扫描机制
- `#38` 市场技能 404
- `#85` 建议增加对 skills 市场和 clawhub 的重视

### 6. 它暴露出几个真实的能力缺口

公开 issues 能直接说明它目前的一些架构局限：

- `#39` 不支持 `superpowers` 这种嵌套 skill 目录
- `#35` 某些工具（Kiro）读取不到 symlink
- `#32` Marketplace 当前仅支持 GitHub，企业私有仓库场景不足
- `#33` 用户已经明确提出安全扫描诉求

这四类问题非常有代表性，几乎就是一个 skill manager 从“个人工具”走向“团队工具”时必然遇到的四堵墙：

```text
discovery wall   -> 嵌套目录 / 多种 repo 布局
compat wall      -> 某些 agent 不认 symlink
source wall      -> GitHub 之外的私有源 / 企业源
trust wall       -> skill 安全扫描 / 来源可信度
```

来源：

- Issues: [#39](https://github.com/jiweiyeah/Skills-Manager/issues/39), [#35](https://github.com/jiweiyeah/Skills-Manager/issues/35), [#32](https://github.com/jiweiyeah/Skills-Manager/issues/32), [#33](https://github.com/jiweiyeah/Skills-Manager/issues/33)

## 推断层：它大概率是什么架构

由于公开仓库没有源码，下面是**基于已公开功能边界的低风险推断**，不是源码事实。

### 推断 1：内部至少分成 4 个核心子系统

如果一个应用要支持：

- 多工具检测
- 中央 skill 仓库
- symlink 同步
- 分组 / 批量管理
- 项目级 / 全局级安装
- 市场 / 云同步 / 登录

那内部大概率至少有下面四层：

```text
+--------------------------------------------------+
| UI Layer                                         |
| React screens / settings / list / marketplace    |
+--------------------------------------------------+
| App Service Layer                                |
| state, batch ops, group ops, project/global mode |
+--------------------------------------------------+
| Domain Layer                                     |
| skill model, tool adapter, source model, sync    |
+--------------------------------------------------+
| System Layer                                     |
| fs, symlink/copy, OS detection, auth, network    |
+--------------------------------------------------+
```

### 推断 2：它应该有“工具适配器注册表”

README 既然强调：

- Multi-Tool Support
- Custom Tools
- extensible to others

那内部很可能不是散落的 `if tool == xxx`，而是至少存在一种“tool definition / adapter registry”：

```text
ToolAdapter
  - id
  - display_name
  - global_skill_path
  - project_skill_path
  - supports_symlink
  - detection_strategy
  - icon
```

否则很难同时支撑：

- 自动检测工具
- 自定义添加 tool
- 后续 plugin system

### 推断 3：它的“同步引擎”应该已经不仅仅是 `ln -s`

从 issue 可以看到：

- Windows junction 创建失败
- 某些工具不支持 symlink
- 迁移时旧链接清理不完整

这意味着真正需要的同步引擎不是：

```text
for each skill:
  ln -s source target
```

而是：

```text
discover source
validate layout
decide transport:
  symlink | junction | copy
apply target state
reconcile stale links
report per-tool result
```

也就是说，架构重点应是“状态收敛引擎”，不是“创建链接”这一条命令本身。

## 和我们当前仓库的对照

我们当前仓库已经具备一部分基础能力：

- `ce` CLI 已有按组安装与目标目录分发能力
- `install_skills/installer.py` 已有 symlink 安装、manifest、MCP 合并
- `install_skills/models.py` 已有 `GroupConfig` / `GroupManifest` / `ManifestV2`
- 当前整体仍然偏“安装器 / 分发器”，还不是“完整 skill manager”

粗略对照：

| 维度 | 我们当前状态 | Skills-Manager 暴露的方向 |
| --- | --- | --- |
| 中央 skill 源 | 已有，仓库 `skills/` | 已有 |
| 分组安装 | 已有基础模型 | 已产品化 |
| 项目级 skill | 有部分工作区方案，但未产品化成统一 UX | 已支持 |
| 批量管理 | 主要靠 CLI 组合操作 | 已作为显式功能 |
| 多工具适配层 | 有，但分散在 install 逻辑和文档里 | 更像显式产品概念 |
| 市场 / 社区分发 | 暂无 | 已作为 roadmap / 部分能力 |
| 云同步 / 账号 | 暂无 | 已上线 |
| 安全治理 | 暂无 | 用户已强烈提出 |
| 嵌套 skill 布局兼容 | 当前有意识，但未系统化抽象 | 公开 issue 说明仍有缺口 |

## 值得纳入我们后续 roadmap 的部分

下面按“建议吸收程度”排序。

### A. 强烈建议纳入

#### 1. 显式的 Tool Adapter Registry

把“支持哪些工具、每个工具的 global/project skill 路径、是否支持 symlink、需要什么桥接目录”从脚本逻辑里抽出来，变成明确的数据模型。

建议目标形态：

```text
tool_registry/
  claude-code
  codex
  opencode
  kimi
  opencode
  ...
```

每个 tool 描述：

- 用户级安装路径
- 项目级安装路径
- 是否原生读取 `.agents/skills`
- 是否需要桥接目录
- 是否支持 symlink
- 不支持 symlink 时的 fallback 策略

为什么值得做：

- 这会把“安装器”升级成“可扩展平台层”
- 后续新增工具不必继续改硬编码逻辑
- 也能支撑文档自动生成和兼容矩阵

#### 2. 嵌套目录 / 多 repo 布局发现器

Issue `#39` 很值得警惕：真实世界里的 skill 仓库并不总是 `skills/<skill>/SKILL.md` 单层布局。

建议 roadmap 直接支持：

- `skills/<skill>/SKILL.md`
- `skills/<group>/<skill>/SKILL.md`
- `<repo-root>/SKILL.md`
- 外层 bundle / monorepo / upstream vendor 目录

同时输出“发现报告”：

```text
found:
  - dev-brainstorming
  - superpowers/test-driven-development
skipped:
  - xxx (missing SKILL.md)
  - yyy (duplicate name)
```

这是很高 ROI 的能力，因为它直接决定我们能不能吸收更多上游 skill 生态。

#### 3. 同步策略从“仅 symlink”升级为“symlink / copy / mirror”三态

Issue `#35` 说明不是所有工具都可靠支持 symlink。

所以我们的 roadmap 不应继续默认“symlink = 唯一正确答案”，而应抽象为：

```text
sync_mode:
  - symlink   # 默认
  - copy      # tool 不支持 symlink 时
  - mirror    # 未来可做校验型复制
```

最少先做：

- tool 级默认策略
- 用户覆盖策略
- 安装后验证
- 漂移检测

#### 4. 项目级 / 用户级统一安装模型

`Skills-Manager` 在 `v2.0.2` 把“project-level skills”单独做成了 release point，这个判断是对的。

我们现在已经有：

- 用户级安装
- 多工作区 context 模板
- Obsidian 场景

下一步值得做的是把这几个概念统一成：

```text
scope:
  - user
  - workspace
  - vault
  - project
```

这样后续：

- `ce install --scope user`
- `ce install --scope project`
- `ce status --scope workspace`

就会更清晰。

### B. 建议进入中期 roadmap

#### 5. Skill Group / Batch Ops 的一等公民化

虽然我们已有 group 概念，但更像配置层，不是完整的“批量运维层”。

值得补强的方向：

- group enable/disable
- group diff
- group sync
- group export/import
- group apply to target set

这会让我们从“安装”走向“持续管理”。

#### 6. 私有源 / 企业源抽象

Issue `#32` 提到的不是边角需求，而是一个非常典型的企业落地门槛。

如果未来我们也做 market / install source，建议一开始就不要把 source 抽象成只有 GitHub：

```text
SkillSource
  - local_path
  - git_https
  - git_ssh
  - github_repo
  - private_git
  - archive_file
```

这样后面要接：

- GitHub
- 私有 GitLab / Gitea
- 本地 zip / `.skill`
- 内网共享目录

都不会推翻前面的模型。

#### 7. 安全与信任元数据

Issue `#33` 虽然没写展开，但方向是对的。skill 一旦进入：

- 市场
- 团队共享
- 自动安装

安全治理就不是锦上添花，而是门槛能力。

建议中期 roadmap 至少规划：

- 来源信息
- 作者信息
- hash / 校验
- 权限提示
- install 前风险提示
- “仅信任白名单源”

### C. 可以观察，但不建议现在投入

#### 8. 桌面 GUI 应用本身

这个项目的桌面形态是产品选择，不是我们当前仓库的必选项。

对我们来说，短期不建议引入新的重型 GUI 框架，原因很直接：

- 当前仓库主轴是 skill 内容、安装器、跨平台配置
- GUI 会显著拉高维护面
- 公开仓库没有源码，无法直接复用其实现

所以：

- 可以吸收其“产品能力抽象”
- 不建议现在复制其 “Tauri + React + Rust 桌面壳”

#### 9. 云同步 / 登录

这是很重的能力，牵涉：

- 账号系统
- 远端状态存储
- 隐私边界
- 冲突解决

我们可以把它列入远期 roadmap，但不建议在“适配层、发现器、同步模式、安全元数据”完成前就先做。

## 建议转成我们的 roadmap 版本

建议按三阶段推进。

### Phase 1: 把安装器升级成可扩展的 skill manager core

- 建 Tool Adapter Registry
- 建多布局 skill discovery
- 建 `sync_mode = symlink | copy`
- 统一 `scope = user | project | workspace | vault`
- 增强 status / diff / verify

### Phase 2: 把管理能力产品化

- group / batch 操作增强
- tool compatibility matrix
- per-target install policy
- source abstraction
- import/export profile

### Phase 3: 把生态与治理补齐

- 私有源 / 企业源
- 安全扫描 / 信任元数据
- 轻量 market / registry
- 远期再评估云同步

## 最终判断

### 值得参考的

- 单一 skill 源 + 多工具分发
- 工具适配层
- 项目级 / 用户级并存
- group / batch 管理
- source 与 market 的产品化方向
- 对 symlink 限制和兼容性的显式处理

### 不值得直接照搬的

- 桌面 GUI 技术栈本身
- 在基础模型还没稳定前就先做账号 / 云同步

### 对我们最有价值的一句话总结

这个项目给我们的最大启发不是“做一个桌面版 ce”，而是：

```text
把技能安装脚本
升级成
有 discovery / adapter / sync / source / trust 五层抽象的 skill manager
```

## 证据索引

- 仓库首页 / README:
  - [Skills-Manager README](https://github.com/jiweiyeah/Skills-Manager/tree/main)
- Releases:
  - [Releases](https://github.com/jiweiyeah/Skills-Manager/releases)
- 关键 issues:
  - [#39 对于 Superpowers 这种多层文件夹的 skill，似乎无法管理](https://github.com/jiweiyeah/Skills-Manager/issues/39)
  - [#35 Kiro似乎读取不到这种软链接的文件](https://github.com/jiweiyeah/Skills-Manager/issues/35)
  - [#32 Marketplace 目前仅支持 GitHub，能否支持企业级使用，例如私有仓库？](https://github.com/jiweiyeah/Skills-Manager/issues/32)
  - [#33 建议增加skill安全扫描机制](https://github.com/jiweiyeah/Skills-Manager/issues/33)
