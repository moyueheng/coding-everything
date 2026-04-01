# 上游仓库更新报告（2026-04-01）

## 更新范围

- 更新时间：2026-04-01
- 更新方式：`git submodule update --remote`
- 后续步骤：执行 `uv run .agents/skills/update-upstream-repos/scripts/switch_updated_submodules_to_main.py`
- 覆盖仓库：`upstream/everything-claude-code`、`upstream/superpowers`
- 最终状态：两个已变化 submodule 都已切回本地 `main`，且 `HEAD == origin/main`
- 证据来源：根仓库 `git diff --submodule=short HEAD`、上游 `git log` / `git show` / `README.md` / `CLAUDE.md`

## 变更概览

| 仓库 | 旧 SHA | 新 SHA | commit 数 | 结论 |
|------|--------|--------|-----------|------|
| `upstream/everything-claude-code` | `a4d4b1d` | `1abeff9` | 56 | 新增多组可复用 workflow，OpenCode 与 Gemini 安装面继续扩展，值得按需筛选吸收 |
| `upstream/superpowers` | `eafe962` | `dd23728` | 9 | 发布 `v5.0.7`，核心是 Copilot CLI 支持和 OpenCode 修复，应同步认知但暂不必改本仓库流程 |

## upstream/everything-claude-code

### 本次更新包含什么

- `2026-04-01` `1abeff9` `feat: add connected operator workflow skills`
- `2026-03-31` `477d23a` `feat(agents,skills): add opensource-pipeline — 3-agent workflow for safe public releases`
- `2026-03-31` `99a44f6` `feat(commands): add santa-loop adversarial review command`
- `2026-03-31` `9b611f1` `feat: add hexagonal architecture SKILL.`
- `2026-03-31` `1744e1e` `feat: add gemini install target`
- `2026-03-31` `f90f269` `feat(opencode): complete OpenCode agent setup - add 10 missing agent prompts`
- `2026-04-01` `f3db349` `docs: shift repo guidance to skills-first workflows`
- `2026-04-01` `e134e49` `docs: close bundle drift and sync plugin guidance`

### 具体变化

- 新增：
  - 4 个 connected operator workflow skill：`skills/customer-billing-ops/SKILL.md`、`skills/google-workspace-ops/SKILL.md`、`skills/project-flow-ops/SKILL.md`、`skills/workspace-surface-audit/SKILL.md`
  - `skills/opensource-pipeline/SKILL.md` 与 3 个配套 agent，用于公开发布前的 secret 清理、独立审计和打包文档生成
  - `skills/hexagonal-architecture/SKILL.md`
  - Gemini 项目安装目标：`.gemini/GEMINI.md` 与安装 registry 入口
  - OpenCode `changed-files` 工具与多组 agent prompt，补齐 `.opencode/opencode.json` 注册项
- 调整：
  - README、AGENTS、WORKING-CONTEXT 进一步把仓库定位从 legacy commands 转向 skills-first workflow
  - 安装 manifest 扩展了新的 components / modules / profiles
- 修复：
  - hook 去重、install planning、catalog sync、Codex hook regression 等若干稳定性问题
  - 曾引入的 `orch-runtime`、`claude-hud`、`evalview-agent-testing` 有增删和回滚，说明该段功能仍在快速变动，不适合直接照搬

### 与本项目的关系

- 可以直接复用：
  - `hexagonal-architecture` 可作为 `dev-backend-patterns` / `dev-writing-plans` 的补充参考
  - `opensource-pipeline` 对本仓库未来开源清理流程有参考价值，尤其是 secret 扫描与文档补齐分工
- 需要手动适配：
  - connected operator workflow skill 偏运营域，不适合直接纳入当前开发型 skill 集
  - Gemini 安装目标与 OpenCode agent 扩展如果要吸收，需要先评估本仓库现有 `ce` 安装模型和 `opencode/` 目录边界
- 暂时无需跟进：
  - `santa-loop` 目前仍是 command 形态，不符合本仓库优先用 skill 的方向
  - 快速变动中的 orchestration / plugin 相关项先观察，不宜直接同步

## upstream/superpowers

### 本次更新包含什么

- `2026-03-31` `1f20bef` `Release v5.0.7: Copilot CLI support, OpenCode fixes`
- `2026-03-25` `8b16692` `feat: add Copilot CLI tool mapping, docs, and install instructions`
- `2026-03-25` `2d942f3` `fix(opencode): align skills path across bootstrap, runtime, and tests`
- `2026-03-25` `0a1124b` `fix(opencode): inject bootstrap as user message instead of system message`
- `2026-03-31` `c0b417e` `Add contributor guidelines to reduce agentic slop PRs`
- `2026-03-31` `dd23728` `Add agent-facing guardrails to contributor guidelines`

### 具体变化

- 新增：
  - Copilot CLI 安装指引和工具映射：`skills/using-superpowers/references/copilot-tools.md`
  - 版本发布脚本：`scripts/bump-version.sh`
- 调整：
  - README 新增 GitHub Copilot CLI 安装说明
  - contributor 指南在 `CLAUDE.md` 顶部增加面向 agent 的 guardrail，强调提交前自检、避免低质量 PR、允许对模糊指令提出异议
- 修复：
  - OpenCode bootstrap 从 system message 改为首条 user message 前置，避免重复注入和部分模型兼容性问题
  - OpenCode skills 路径在 bootstrap、runtime、tests 三处统一，减少路径漂移

### 与本项目的关系

- 可以直接复用：
  - OpenCode bootstrap/user message 修复与路径统一，能作为本仓库后续补齐 `opencode/` 配置时的实现参考
  - contributor guardrail 的方向与本仓库现有高约束 AGENTS 规则一致
- 需要手动适配：
  - Copilot CLI 支持目前不是本仓库的目标平台，需要时再评估是否引入
- 暂时无需跟进：
  - `v5.0.7` 未改变本仓库当前已同步的 `dev-brainstorming` / `dev-writing-plans` 内联自审模式，因此无需立即修改对应 skill

## 值得关注

### 1. `everything-claude-code` 的 `opensource-pipeline`

- 证据：`477d23a`，新增 `skills/opensource-pipeline/SKILL.md` 与 `agents/opensource-*`
- 为什么重要：这套流程直接覆盖“私有仓库对外发布前的脱敏、审计、打包”三段工作，和本仓库维护多平台配置、公开分发 skill 的场景相邻
- 建议动作：后续单独评估其 secret 规则与文档产物是否值得迁移为本仓库 skill

### 2. `everything-claude-code` 持续扩展 OpenCode / Gemini 安装面

- 证据：`1744e1e`、`f90f269`、`.gemini/GEMINI.md`、`.opencode/opencode.json`
- 为什么重要：本仓库已有 `opencode/` 目录且仍在开发中，这些更新提供了可参考的目标结构和 agent 覆盖面
- 建议动作：下次处理 `opencode/` 时，以这些提交为证据重新审视缺失能力，不要凭印象补目录

### 3. `superpowers` 的 OpenCode 修复值得保留为实现约束

- 证据：`0a1124b`、`2d942f3`
- 为什么重要：这两处修复直接说明 bootstrap 注入方式和 skills 路径一致性会影响 token 用量、模型兼容性和测试可靠性
- 建议动作：后续修改本仓库 OpenCode 集成时，把“user message 注入优于 system message”“单一 skills path 真值源”作为硬约束

## 后续动作

- [ ] 评估是否把 `opensource-pipeline` 或其部分检查逻辑迁移为本仓库独立 skill
- [ ] 处理 `opencode/` 时，对照 `everything-claude-code` 新增的 Gemini / OpenCode 安装与 agent 覆盖面做一次差异清单
- [ ] 后续继续沿用 `git submodule update --remote` 后补跑 `switch_updated_submodules_to_main.py`
- [x] 本次已同步 `AGENTS.md` / `CLAUDE.md` 中 `superpowers` 跟踪版本信息
