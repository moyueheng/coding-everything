# 上游仓库更新报告（2026-04-20）

## 更新范围

- 更新时间：2026-04-20
- 更新方式：`git submodule update --remote`
- 后续处理：已执行 `uv run .agents/skills/update-upstream-repos/scripts/switch_updated_submodules_to_main.py`
- 覆盖仓库：全部 `.gitmodules` 仓库；本次只有 `upstream/everything-claude-code` 与 `upstream/superpowers` 发生 gitlink 变化
- 最终状态：两个变化的 submodule 均已切回本地 `main`，且 `main...origin/main` 无 ahead/behind
- 证据来源：`git diff --submodule=short HEAD`、`generate_upstream_report.py`、对应 commit diff、`upstream/everything-claude-code/ecc2/README.md`、`upstream/superpowers/README.md`

## 变更概览

| 仓库 | 旧 SHA | 新 SHA | commit 数 | 结论 |
|------|--------|--------|-----------|------|
| `upstream/everything-claude-code` | `1a50145` | `8bdf88e` | 2 | ECC2 新增 board observability 原型，值得观察但暂不迁移 |
| `upstream/superpowers` | `c4bbe65` | `b557648` | 4 | README 安装说明更新，补充 Codex CLI / Codex App 插件路径 |

## upstream/everything-claude-code

### 本次更新包含什么

- `2026-04-18` `7992f8fc` `feat: integrate ecc2 board observability prototype`
- `2026-04-19` `8bdf88e5` 合并 `feat/ecc2-board-observability-integration`

### 具体变化

- 新增 `SessionBoardMeta`，字段覆盖 lane、project、feature、issue、row/column/stack 坐标、progress、status detail、activity note、handoff backlog、conflict signal。
- `ecc2/src/session/store.rs` 新增/扩展 `session_board` 表、索引、迁移列补齐、`list_session_board_meta()`、`refresh_session_board_meta()` 以及从 session 状态推导 board lane / progress / conflict signal 的逻辑。
- `ecc2/src/tui/dashboard.rs` 新增 `Pane::Board`、`board_meta_by_session` 缓存和 board pane 渲染入口，接入 dashboard 同步流程。

### 与本项目的关系

- 可以直接复用：暂无。当前项目没有 Rust ECC2 控制面，也没有对应本地安装/测试入口。
- 需要手动适配：如果未来吸收 ECC2，需要先评估 `session_board` 数据模型、TUI pane 交互和本项目现有 `dev-continuous-agent-loop` / subagent 工作流是否有边界重叠。
- 暂时无需跟进：这仍属于 `ecc2/` alpha。上游 README 明确该目录是可本地实验的控制面脚手架，不是完整 ECC2 产品。

## upstream/superpowers

### 本次更新包含什么

- `2026-04-16` `a5dd364` README updates for Codex, other cleanup
- `2026-04-16` `99e4c65` reorder installs
- `2026-04-16` `9f42444` formatting
- `2026-04-16` `b557648` formatting

### 具体变化

- `README.md` 将安装章节改为按平台列出。
- 新增 OpenAI Codex CLI 安装路径：通过 `/plugins` 搜索 Superpowers 并选择 `Install Plugin`。
- 新增 OpenAI Codex App 安装路径：侧边栏 Plugins 中 Coding 分类安装 Superpowers。
- Claude Code 官方 marketplace 与 Superpowers marketplace 的描述被拆开；Cursor、OpenCode、Copilot、Gemini 说明保留。
- 贡献说明强调上游通常不接受新增 skill，修改 skill 需要跨支持的 coding agents 可用。

### 与本项目的关系

- 可以直接复用：安装文档中关于 Codex CLI / Codex App 插件入口的描述，可作为后续更新本项目 Codex 相关说明的依据。
- 需要手动适配：本项目当前仍使用本地 `skills/` + `ce` CLI 管理共享 skill，不直接改用 Superpowers 插件安装。
- 暂时无需跟进：本次没有 superpowers skill 内容变化，不需要同步 `dev-brainstorming`、`dev-writing-plans` 等本地 skill。

## 值得关注

### 1. ECC2 board observability 原型

- 证据：`7992f8fc` 修改 `ecc2/src/session/mod.rs`、`ecc2/src/session/store.rs`、`ecc2/src/tui/dashboard.rs`，新增 `SessionBoardMeta`、`session_board` 存储和 dashboard Board pane。
- 为什么重要：它把多 agent/session 状态从列表推进到 board 视角，和本项目已有的长时间 agent loop、并行分发、review checkpoint 方向相关。
- 建议动作：观察，不立即迁移；等 ECC2 的 orchestration / packaging 更稳定后再评估是否抽取工作流思想到本项目 skill。

### 2. Superpowers 官方 Codex 插件入口

- 证据：`a5dd364` / `99e4c65` 更新 `upstream/superpowers/README.md`，新增 OpenAI Codex CLI 与 Codex App 的插件安装说明。
- 为什么重要：本项目支持 Codex，后续写安装文档时可引用上游插件入口作为替代路径。
- 建议动作：暂不改变 `ce` CLI；仅在需要面向 Codex 用户补充说明时引用。

## 后续动作

- [ ] 暂不迁移 ECC2 board 代码，保持观察
- [ ] 下次更新 superpowers 时继续检查是否有 skill 内容变化，而不只看 README
- [ ] 如补充 Codex 安装说明，应区分本项目 `ce` CLI 与 Superpowers 官方插件路径
- [ ] 提交前确认两个变化 submodule 保持在本地 `main`
