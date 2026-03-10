# 上游仓库更新报告（2026-03-10）

## 更新范围

- 更新时间：2026-03-10
- 更新方式：`git submodule update --remote`
- 覆盖仓库：`upstream/everything-claude-code`、`upstream/superpowers`、`upstream/ui-ux-pro-max-skill`
- 未变化仓库：`upstream/humanizer-zh`、`upstream/obsidian-skills`
- 证据来源：根仓库 gitlink diff、各上游仓库 `git log` / `git diff`、README、RELEASE-NOTES、具体 skill / rule / agent 文件

## 变更概览

| 仓库 | 旧 SHA | 新 SHA | commit 数 | 结论 |
|------|--------|--------|-----------|------|
| `upstream/everything-claude-code` | `2fea46e` | `af51fca` | 248 | 从 v1.5.0 一路更新到 v1.8.0 之后的修复线，新增 research-first、持续 agent loop、Plankton 质量门、Chief of Staff agent，值得拆分吸收 |
| `upstream/superpowers` | `e16d611` | `33e55e6` | 38 | 升级到 v5.0.0，brainstorming / plans / subagent 流程显著增强，是本项目最值得优先跟进的一次更新 |
| `upstream/ui-ux-pro-max-skill` | `6623f12` | `07f4ef3` | 19 | 从单一 UI/UX skill 扩展为设计 skill 族，新增 design / slides / design-system / ui-styling / brand / banner-design，适合前端与品牌设计场景借鉴 |

## upstream/superpowers

### 本次更新包含什么

- `2026-03-09` `133a0a8` / `57b346d` 发布 `v5.0.0`
- `2026-02-21` `d2d6cf4` 发布 `v4.3.1`
- 关键文件：
  - `RELEASE-NOTES.md`
  - `skills/brainstorming/SKILL.md`
  - `skills/writing-plans/SKILL.md`
  - `skills/subagent-driven-development/`
  - `skills/using-superpowers/SKILL.md`
  - `lib/brainstorm-server/`

### 具体变化

- 新增可视化 brainstorming companion。
  - 证据：`RELEASE-NOTES.md` 的 `v5.0.0` 新特性；`skills/brainstorming/visual-companion.md`；`lib/brainstorm-server/`
- 新增 spec / plan 文档审查循环。
  - 证据：`skills/brainstorming/spec-document-reviewer-prompt.md`、`skills/writing-plans/plan-document-reviewer-prompt.md`
- 把架构隔离、文件尺寸控制、scope assessment 前移到 brainstorming / writing-plans / SDD 全链路。
  - 证据：`RELEASE-NOTES.md` 的 “Architecture guidance across the skill pipeline”；`skills/brainstorming/SKILL.md`
- plans 目录结构重构。
  - 证据：`RELEASE-NOTES.md` 指定默认输出从 `docs/plans/` 改为 `docs/superpowers/specs/` 与 `docs/superpowers/plans/`
- 在支持 subagent 的平台上，subagent-driven-development 变成默认必选路径；`executing-plans` 不再 3 步一停。
  - 证据：`RELEASE-NOTES.md` 的 “Subagent-driven development mandatory on capable harnesses” 与 “Executing-plans no longer batches”
- 增强指令优先级。
  - 证据：`RELEASE-NOTES.md` 的 “Instruction priority hierarchy”，明确用户指令 / `AGENTS.md` / `CLAUDE.md` 高于 skill 默认要求

### 与本项目的关系

- 可以直接复用：
  - `brainstorming` 的“先设计、后实现、可视化可选”流程
  - spec / plan review loop
  - 指令优先级与 `AGENTS.md` 优先原则
- 需要手动适配：
  - `docs/superpowers/specs/` 和 `docs/superpowers/plans/` 的目录约定，目前本项目 docs 结构不同
  - 可视化 companion 依赖浏览器与 server，不适合无图形场景默认启用
- 暂时无需跟进：
  - 某些平台兼容修复可记录为参考，但不必逐项镜像

## upstream/everything-claude-code

### 本次更新包含什么

- 区间很大：从 `v1.5.0-154-g2fea46e` 更新到 `af51fca`
- 关键里程碑：
  - `db27ba1` / `b3d3eac` / `1797e79` 对应 `v1.6.0`、`v1.7.0`、`v1.8.0`
  - `af51fca` 为近期可移植性修复
- 关键文件：
  - `README.md`
  - `rules/common/development-workflow.md`
  - `skills/search-first/SKILL.md`
  - `skills/autonomous-loops/SKILL.md`
  - `skills/continuous-agent-loop/SKILL.md`
  - `skills/plankton-code-quality/SKILL.md`
  - `agents/chief-of-staff.md`
  - `install.sh`

### 具体变化

- 强化 research-first 开发。
  - 证据：`rules/common/development-workflow.md` 在第 0 步强制“Research & Reuse”，要求先做 GitHub / 包管理器 / MCP 检索；`skills/search-first/SKILL.md` 给出 adopt / extend / build 决策矩阵
- 新增持续 agent loop 能力。
  - 证据：`skills/autonomous-loops/SKILL.md` 与 `skills/continuous-agent-loop/SKILL.md`
- 引入 Plankton 质量门。
  - 证据：`skills/plankton-code-quality/SKILL.md`；`README.md` 对 Plankton 三阶段质量钩子做了明确说明
- 跨平台支持继续扩展。
  - 证据：`README.md` 写明已覆盖 Windows/macOS/Linux，并紧密集成 Cursor、OpenCode、Codex、Antigravity；`install.sh` 新增 `--target antigravity`
- 新增 `chief-of-staff` agent。
  - 证据：`agents/chief-of-staff.md`
- 继续补强 Codex / AGENTS.md 体系。
  - 证据：`README.md` 中关于 AGENTS.md、Codex 支持和跨工具共享上下文的章节

### 与本项目的关系

- 可以直接复用：
  - `search-first` 的“先搜索、再决定 adopt / extend / build”思路，和本项目“工具优先于推理、禁止重复造轮子”完全一致
  - `continuous-agent-loop` / `autonomous-loops` 作为将来多 agent 自动化编排的参考
- 需要手动适配：
  - Plankton 偏重写时质量钩子与多语言 lint 生态，落地前要评估是否过重
  - `chief-of-staff` 是沟通工作流 agent，与当前仓库主目标不直接相关
- 暂时无需跟进：
  - Antigravity、部分 Claude/Cursor/OpenCode 专项安装与 hook 细节，可先保留为知识储备

## upstream/ui-ux-pro-max-skill

### 本次更新包含什么

- `2026-03-09` `07f4ef3` 对应 `v2.5.0`
- 关键变化主要集中在 `.claude/skills/` 扩展与设计数据集增厚
- 关键文件：
  - `.claude/skills/design/SKILL.md`
  - `.claude/skills/design-system/SKILL.md`
  - `.claude/skills/ui-styling/SKILL.md`
  - `.claude/skills/slides/SKILL.md`
  - `.claude/skills/brand/SKILL.md`
  - `.claude/skills/banner-design/SKILL.md`
  - `README.md`

### 具体变化

- 从单体 UI/UX skill 拆成设计 skill 族。
  - 证据：新增 `.claude/skills/design/`、`design-system/`、`ui-styling/`、`slides/`、`brand/`、`banner-design/`
- 新增 design-system token 架构与 slide 生成链路。
  - 证据：`design-system/SKILL.md` 描述 primitive → semantic → component 三层 token，并内置 slide CSV 决策系统和生成脚本
- 新增 `ui-styling`，把 shadcn/ui、Tailwind、canvas 设计整合为一个 UI 实现 skill。
  - 证据：`ui-styling/SKILL.md`
- 新增 `design` 总路由 skill。
  - 证据：`design/SKILL.md`，统一路由 brand / token / UI / logo / CIP / slides / banner / social photos / icon
- 设计数据进一步系统化。
  - 证据：新增 `design.csv`、`google-fonts.csv`、`app-interface.csv`，以及大量字体与模板资源

### 与本项目的关系

- 可以直接复用：
  - `design-system` 的 token 分层思路
  - `slides` 与 `banner-design` 的资料组织方式
  - `ui-styling` 对 shadcn/ui + Tailwind + 视觉规范的整合方式
- 需要手动适配：
  - 这个仓库资源体量明显变大，包含字体、图片、脚本、数据集，迁入时不能无差别全量复制
  - 命名与元数据格式偏 Claude 生态，需要按当前仓库的 skill 标准做转换
- 暂时无需跟进：
  - 品牌、CIP、社媒图片等偏设计生产链路的内容，当前仓库没有直接消费入口

## 值得关注

## 推荐结论

### 必入

#### 1. `superpowers` 的 spec / plan review loop

- 来源：
  - `upstream/superpowers/skills/brainstorming/spec-document-reviewer-prompt.md`
  - `upstream/superpowers/skills/writing-plans/plan-document-reviewer-prompt.md`
  - `upstream/superpowers/RELEASE-NOTES.md`
- 推荐原因：
  - 这是这次更新里最贴近本项目核心工作流的增强
  - 它直接提升复杂任务的稳定性，能减少“计划写了但质量不稳”“设计文档缺口没人兜底”的问题
  - 与本项目强调的 workflow 约束完全同向，不需要额外引入重型框架
- 建议采纳方式：
  - 优先把 reviewer loop 思路吸收到 `kimi/skills/dev-brainstorming` 与 `kimi/skills/dev-writing-plans`

#### 2. `everything-claude-code` 的 research-first / `search-first`

- 来源：
  - `upstream/everything-claude-code/rules/common/development-workflow.md`
  - `upstream/everything-claude-code/skills/search-first/SKILL.md`
- 推荐原因：
  - 和本项目“工具优先于推理”“禁止重复造轮子”完全一致
  - 它已经不是口号，而是 rule + skill 的可执行组合
  - 这个能力对所有后续 skill 开发、上游同步、脚本开发都有普适收益
- 建议采纳方式：
  - 新增一个本项目风格的 research-first / search-first skill，或把这套决策矩阵固化进现有开发 workflow skill

#### 3. `superpowers` 的指令优先级表达

- 来源：
  - `upstream/superpowers/RELEASE-NOTES.md`
  - `upstream/superpowers/skills/using-superpowers/SKILL.md`
- 推荐原因：
  - 它把“用户指令 / AGENTS.md / CLAUDE.md 高于 skill 默认要求”说得更清楚
  - 这和本项目已经在做的事情一致，但上游这次把它整理成更稳定的规则表达
- 建议采纳方式：
  - 把这套优先级描述补进相关 workflow skill，减少多 skill 并行时的歧义

### 建议引入

#### 1. `ui-ux-pro-max-skill` 的 `design-system`

- 来源：
  - `upstream/ui-ux-pro-max-skill/.claude/skills/design-system/SKILL.md`
- 推荐原因：
  - 三层 token 架构清晰，可作为本项目未来前端 / 设计类 skill 的参考骨架
  - 对“可复用知识库 + 脚本 + 数据”这种 skill 组织方式有直接借鉴价值
- 建议采纳方式：
  - 借鉴 token 分层与 references/scripts 结构，不建议整仓照搬

#### 2. `ui-ux-pro-max-skill` 的 `ui-styling`

- 来源：
  - `upstream/ui-ux-pro-max-skill/.claude/skills/ui-styling/SKILL.md`
- 推荐原因：
  - 它把 shadcn/ui、Tailwind、视觉设计规范整合成一个技能面
  - 对后续前端 UI 类 skill 设计有帮助
- 建议采纳方式：
  - 只借鉴组织方式和决策维度，不直接引入其全部资源文件

#### 3. `everything-claude-code` 的 continuous agent loop

- 来源：
  - `upstream/everything-claude-code/skills/autonomous-loops/SKILL.md`
  - `upstream/everything-claude-code/skills/continuous-agent-loop/SKILL.md`
- 推荐原因：
  - 对将来多 agent 自动化执行、持续迭代、并行任务分发有参考价值
  - 但当前仓库还没有稳定的配套命令体系，直接引入收益不会立刻兑现
- 建议采纳方式：
  - 先保留为架构参考，后续在有明确自动化编排需求时再落地

### 观察即可

#### 1. `everything-claude-code` 的 Plankton 质量门

- 来源：
  - `upstream/everything-claude-code/skills/plankton-code-quality/SKILL.md`
  - `upstream/everything-claude-code/README.md`
- 暂不必入原因：
  - 依赖、hook、lint 生态都偏重
  - 当前仓库还没有对应的多语言质量门基础设施，直接引入会放大维护成本

#### 2. `everything-claude-code` 的 `chief-of-staff` agent

- 来源：
  - `upstream/everything-claude-code/agents/chief-of-staff.md`
- 暂不必入原因：
  - 它面向多渠道沟通管理，不属于本仓库当前主线

#### 3. `ui-ux-pro-max-skill` 的品牌 / CIP / 社媒图片链路

- 来源：
  - `upstream/ui-ux-pro-max-skill/.claude/skills/design/SKILL.md`
- 暂不必入原因：
  - 资源体量大，当前仓库没有直接消费入口
  - 引入后容易形成大而全但低复用的内容堆积

### 1. `superpowers` v5.0.0 的文档评审循环与架构前置约束

- 证据：
  - `upstream/superpowers/RELEASE-NOTES.md`
  - `upstream/superpowers/skills/brainstorming/spec-document-reviewer-prompt.md`
  - `upstream/superpowers/skills/writing-plans/plan-document-reviewer-prompt.md`
- 为什么重要：
  - 这套更新正好补强本项目最关注的“流程约束”和“不要一上来就写代码”
  - spec / plan review loop 可以直接提升复杂任务的稳定性
- 建议动作：
  - 优先评估是否把 spec / plan reviewer 思路吸收到 `kimi/skills/` 体系

### 2. `everything-claude-code` 的 research-first 与 `search-first`

- 证据：
  - `upstream/everything-claude-code/rules/common/development-workflow.md`
  - `upstream/everything-claude-code/skills/search-first/SKILL.md`
- 为什么重要：
  - 与本项目现有“工具优先于推理”“禁止重复造轮子”高度一致
  - 这不是单一句子，而是已经被写成 rule + skill 的可执行工作流
- 建议动作：
  - 评估是否新增一个本项目风格的 research-first / update-upstream 衍生 skill，而不是只保留口头约束

### 3. `everything-claude-code` 的 continuous agent loop 与 Plankton

- 证据：
  - `upstream/everything-claude-code/skills/autonomous-loops/SKILL.md`
  - `upstream/everything-claude-code/skills/plankton-code-quality/SKILL.md`
  - `upstream/everything-claude-code/README.md`
- 为什么重要：
  - 一个解决持续多 agent 编排，一个解决写时质量门
  - 都是“可复用流程资产”，不是单纯文档
- 建议动作：
  - `continuous-agent-loop` 可作为未来自动化实验参考
  - Plankton 先观察，不建议现在直接引入，原因是依赖和 hook 复杂度偏高

### 4. `ui-ux-pro-max-skill` 的设计 skill 家族化

- 证据：
  - `upstream/ui-ux-pro-max-skill/.claude/skills/design/SKILL.md`
  - `upstream/ui-ux-pro-max-skill/.claude/skills/design-system/SKILL.md`
  - `upstream/ui-ux-pro-max-skill/.claude/skills/ui-styling/SKILL.md`
- 为什么重要：
  - 它不再只是“一个 UI/UX skill”，而是可拆分、可路由、带脚本和数据的设计知识库
  - 对后续前端、品牌、演示稿方向的 skill 设计很有参考价值
- 建议动作：
  - 只按需挑选 `design-system` / `ui-styling` / `slides` 思路，不要整仓复制

## 后续动作

- [ ] 评估是否把 `superpowers` 的 spec / plan review loop 引入 `kimi/skills/`
- [ ] 评估是否从 `everything-claude-code` 引入 research-first / search-first 工作流
- [ ] 评估是否单独提炼 `ui-ux-pro-max-skill` 的 `design-system` / `ui-styling` / `slides` 能力
- [ ] 如果后续目录结构或固定脚本入口再变化，再同步更新 `AGENTS.md` / `README.md`
