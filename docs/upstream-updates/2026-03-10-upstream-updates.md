# 上游仓库更新报告（2026-03-10）

## 更新范围

- 更新时间：2026-03-10
- 更新方式：`git submodule update --remote`，随后执行 `uv run .agents/skills/update-upstream-repos/scripts/switch_updated_submodules_to_main.py`
- 覆盖仓库：`upstream/everything-claude-code`、`upstream/superpowers`、`upstream/ui-ux-pro-max-skill`
- 未变化仓库：`upstream/humanizer-zh`、`upstream/obsidian-skills`
- 最终状态：本次有变化的 3 个 submodule 已切回本地 `main`，且 `HEAD == origin/main`
- 证据来源：根仓库 gitlink diff、各上游仓库 `git log` / `git diff --stat`、README、RELEASE-NOTES、具体 skill / rule / agent 文件

## 变更概览

| 仓库 | 旧 SHA | 新 SHA | commit 数 | 结论 |
|------|--------|--------|-----------|------|
| `upstream/everything-claude-code` | `2fea46e` | `af51fca` | 248 | 从 v1.5.0 后一路升级到 v1.8.x 修复线，研究优先、持续 agent loop、跨 harness 一致性明显增强 |
| `upstream/superpowers` | `e16d611` | `33e55e6` | 38 | 升级到 v5.0.0，spec / plan review loop、架构约束、指令优先级表达都更完整 |
| `upstream/ui-ux-pro-max-skill` | `6623f12` | `07f4ef3` | 19 | 从单体 UI/UX skill 扩成设计 skill 族，新增 design-system、ui-styling、slides、brand、banner-design |

## upstream/superpowers

### 本次更新包含什么

- `2026-03-09` `57b346d` 发布 `v5.0.0`
- `2026-03-08` `245d50e` 把 `AGENTS.md` 纳入指令优先级说明
- `2026-03-06` `7b99c39` / `6c274dc` 增加 plan review loop 和 reviewer prompt
- `2026-01-23` `ee14cae` 增加 spec reviewer prompt
- `2026-03-06` `daa3fb2` 把架构边界和能力分层前置到多个 workflow skill

### 具体变化

- 新增 spec / plan 文档审查闭环。
  - 证据：
    - `upstream/superpowers/skills/brainstorming/SKILL.md`
    - `upstream/superpowers/skills/writing-plans/SKILL.md`
  - 变化点：
    - spec 写完后必须进入 reviewer loop
    - plan 按 chunk 编写并逐段审查
    - 循环超过 5 次需要抛给人类决策

- 强化 brainstorming 阶段的边界控制。
  - 证据：
    - `upstream/superpowers/skills/brainstorming/SKILL.md`
  - 变化点：
    - 先看项目上下文，再问问题
    - 超大需求先拆子项目，而不是直接写一个大 spec
    - 明确强调单一职责、清晰接口、文件不要失控膨胀

- 强化指令优先级表达。
  - 证据：
    - `upstream/superpowers/skills/using-superpowers/SKILL.md`
  - 变化点：
    - 用户直接请求、`AGENTS.md`、`CLAUDE.md` 明确高于 skill 默认行为
    - skill 负责覆盖默认系统行为，但不能覆盖用户约束

- 执行侧更偏向 capable harness 的 subagent 路径。
  - 证据：
    - `upstream/superpowers/skills/writing-plans/SKILL.md`
    - commit `5e51c3e`
  - 变化点：
    - 支持 subagent 的环境默认走 `subagent-driven-development`
    - `executing-plans` 的批处理停顿模式被弱化

### 与本项目的关系

- 可以直接复用：
  - spec reviewer loop
  - plan reviewer loop
  - 用户请求 / `AGENTS.md` / skill 的优先级表达
- 需要手动适配：
  - 上游默认文档路径是 `docs/superpowers/specs/` 和 `docs/superpowers/plans/`
  - 可视化 brainstorming companion 不适合当前仓库作为默认路径
- 暂时无需跟进：
  - 浏览器 companion server
  - 某些平台安装和兼容性补丁

## upstream/everything-claude-code

### 本次更新包含什么

- `2026-03-05` `1797e79` 进入 `v1.8.0`
- `2026-02-27` `b3d3eac` 发布 `v1.7.0`
- `2026-02-20` `c9dc53e` 新增 `search-first`
- `2026-03-03` `cd129ed` / `2026-03-03` `912df24` 增强自动化 workflow 和项目识别
- `2026-03-09` `af51fca` 收口近期跨平台可移植性修复

### 具体变化

- 把 research-first 固化成正式 workflow。
  - 证据：
    - `upstream/everything-claude-code/rules/common/development-workflow.md`
    - `upstream/everything-claude-code/skills/search-first/SKILL.md`
  - 变化点：
    - 新实现前必须先做 GitHub / MCP / 包管理器检索
    - 在 adopt / extend / build 之间做显式决策
    - planner / architect 都被要求先做研究再写方案

- 持续 agent loop 命名和路线更稳定。
  - 证据：
    - `upstream/everything-claude-code/skills/continuous-agent-loop/SKILL.md`
    - `upstream/everything-claude-code/skills/autonomous-loops/SKILL.md`
  - 变化点：
    - `continuous-agent-loop` 成为 v1.8+ canonical 名称
    - 明确了 sequential / RFC DAG / quality gate / eval / recovery 的组合方式

- 跨工具一致性继续增强。
  - 证据：
    - `upstream/everything-claude-code/README.md`
    - commit `9b69dd0` / `61485f9`
  - 变化点：
    - README 明确强调 Claude Code、Codex、OpenCode、Antigravity 的一致体验
    - `install.sh` 增加 `--target antigravity`
    - hooks 和运行时控制进一步脚本化

- `architect` agent 仍然是稳定参考，而不是这次需要马上吸收的新增工作流。
  - 证据：
    - `upstream/everything-claude-code/agents/architect.md`
  - 判断：
    - 其核心仍是模块化、低耦合、清晰接口、权衡分析
    - 这次 update 没有看到它带来必须同步的新结构性规则

### 与本项目的关系

- 可以直接复用：
  - research-first / `search-first`
  - `continuous-agent-loop` 的分层命名和 recovery 结构
- 需要手动适配：
  - ECC 的 hooks、runtime control、multi-command 体系较重，不能整套平移
- 暂时无需跟进：
  - `chief-of-staff` 这类偏沟通协同 agent
  - Antigravity、Cowork 之类平台专属安装细节

## upstream/ui-ux-pro-max-skill

### 本次更新包含什么

- `2026-03-10` `4f78df8` 新增 `design-system`
- `2026-03-10` `1c2cb32` 新增 `ui-styling`
- `2026-03-10` `1cdf887` 新增 `slides`
- `2026-03-10` `e9e2e32` 新增 `banner-design`
- `2026-03-10` `6512820` / `ace7759` 新增 `brand` / `design`

### 具体变化

- 从一个 UI/UX skill 扩展成完整设计 skill 族。
  - 证据：
    - `upstream/ui-ux-pro-max-skill/.claude/skills/design/SKILL.md`
    - `upstream/ui-ux-pro-max-skill/README.md`
  - 变化点：
    - 统一路由 brand、tokens、UI、slides、banner、icons、social photos
    - 设计相关知识不再堆在一个大 skill 里

- `design-system` 明确三层 token 架构。
  - 证据：
    - `upstream/ui-ux-pro-max-skill/.claude/skills/design-system/SKILL.md`
  - 变化点：
    - `primitive -> semantic -> component`
    - 有配套 token 生成、校验、Tailwind 集成和组件状态定义

- `ui-styling` 把 shadcn/ui、Tailwind、可访问性、响应式和主题定制整合成一个实现导向 skill。
  - 证据：
    - `upstream/ui-ux-pro-max-skill/.claude/skills/ui-styling/SKILL.md`
  - 变化点：
    - 不是只谈视觉风格，而是把组件、样式、主题、可访问性放进一套操作面

- `slides` 和 `design-system` 之间形成了更强的资产复用。
  - 证据：
    - `upstream/ui-ux-pro-max-skill/.claude/skills/slides/SKILL.md`
    - `upstream/ui-ux-pro-max-skill/.claude/skills/design-system/SKILL.md`
  - 变化点：
    - slides 直接使用 token、Chart.js、策略 CSV、布局规则
    - 更像一个“小型设计知识库 + 脚本系统”

### 与本项目的关系

- 可以直接复用：
  - `design-system` 的 token 分层
  - `ui-styling` 的实现导向组织方式
- 需要手动适配：
  - 资源体量大，含大量数据、脚本、字体、模板，不能整仓镜像
  - 命名和元数据格式偏 Claude 生态，需要按当前 skill 规范转译
- 暂时无需跟进：
  - logo、CIP、banner、social photos 这一整条品牌设计生产链

## 推荐结论

### 必入

#### 1. `superpowers` 的 spec / plan review loop

- 证据：
  - `upstream/superpowers/skills/brainstorming/SKILL.md`
  - `upstream/superpowers/skills/writing-plans/SKILL.md`
- 为什么重要：
  - 这次更新里，对本项目核心 workflow 提升最大的一项
  - 它不是“多一个检查动作”，而是把设计阶段和计划阶段都变成可审查闭环
  - 不引入重型框架，只提升流程质量
- 建议动作：
  - 持续保持 `dev-brainstorming`、`dev-writing-plans` 与这套 reviewer loop 对齐

#### 2. `everything-claude-code` 的 research-first / `search-first`

- 证据：
  - `upstream/everything-claude-code/rules/common/development-workflow.md`
  - `upstream/everything-claude-code/skills/search-first/SKILL.md`
- 为什么重要：
  - 和本项目“工具优先于推理、禁止重复造轮子”的根规则高度一致
  - 这套内容已经从口号变成了可执行 workflow
- 建议动作：
  - 继续把 research-first 保持在 `dev-brainstorming` 和相关 workflow skill 的前置阶段

#### 3. `superpowers` 的指令优先级表达

- 证据：
  - `upstream/superpowers/skills/using-superpowers/SKILL.md`
  - commit `245d50e`
- 为什么重要：
  - 它把用户请求、`AGENTS.md`、skill 的关系写得更清楚
  - 能减少多 skill 并行时的解释歧义
- 建议动作：
  - 持续保持 `dev-using-skills` 与该优先级表达对齐

### 建议引入

#### 1. `ui-ux-pro-max-skill` 的 `design-system`

- 证据：
  - `upstream/ui-ux-pro-max-skill/.claude/skills/design-system/SKILL.md`
- 推荐原因：
  - token 分层清晰
  - references / scripts / assets 的知识组织方式可直接借鉴
- 建议动作：
  - 作为前端与设计类 skill 的稳定参考模板

#### 2. `ui-ux-pro-max-skill` 的 `ui-styling`

- 证据：
  - `upstream/ui-ux-pro-max-skill/.claude/skills/ui-styling/SKILL.md`
- 推荐原因：
  - 把组件、样式、主题、可访问性放进一个统一操作面，复用价值高
- 建议动作：
  - 作为 UI 类 skill 的结构参考，不整仓搬运资源

#### 3. `everything-claude-code` 的 `continuous-agent-loop`

- 证据：
  - `upstream/everything-claude-code/skills/continuous-agent-loop/SKILL.md`
  - `upstream/everything-claude-code/skills/autonomous-loops/SKILL.md`
- 推荐原因：
  - 对未来多 agent 自动化编排有价值
  - 但当前仓库还没有完整的配套命令体系
- 建议动作：
  - 先作为架构参考，按需吸收

### 观察即可

#### 1. `everything-claude-code` 的 Plankton 质量门

- 证据：
  - commit `cd129ed`
  - `upstream/everything-claude-code/README.md`
- 原因：
  - 需要 hooks、质量门、评测链路一起配合，当前仓库直接引入会偏重

#### 2. `everything-claude-code` 的 `architect` agent

- 证据：
  - `upstream/everything-claude-code/agents/architect.md`
- 原因：
  - 原则仍然有价值，但这次没有新增到必须同步的结构性变化

#### 3. `ui-ux-pro-max-skill` 的品牌设计生产链

- 证据：
  - `upstream/ui-ux-pro-max-skill/.claude/skills/design/SKILL.md`
- 原因：
  - 覆盖 logo、CIP、banner、social photos，范围过大
  - 当前仓库没有直接消费入口，容易变成低复用资产堆积

## 后续动作

- [ ] 评估是否继续把 `superpowers` 新增的 reviewer loop 细节同步回本仓库 workflow skill
- [ ] 评估是否需要把 `search-first` 再抽成更独立的通用说明或固定检查项
- [ ] 后续每次执行上游同步时，固定补跑 `switch_updated_submodules_to_main.py`，避免 submodule 留在 detached HEAD 或回退到旧的本地 `main`
- [ ] 如后续需要提交，先复查 `upstream/everything-claude-code/agents/architect.md` 是否有新的稳定规则值得同步
