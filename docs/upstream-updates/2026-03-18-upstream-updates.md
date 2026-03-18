# 上游仓库更新报告（2026-03-18）

## 更新范围

- 更新时间：2026-03-18
- 更新方式：`git submodule update --init --remote`
- 覆盖仓库：全部 6 个上游仓库
- 最终状态：
  - 3 个仓库有更新（everything-claude-code、product-manager-skills、superpowers）
  - 已执行 `switch_updated_submodules_to_main.py`，所有变更 submodule 已切回本地 `main`
  - `HEAD == origin/main` 验证通过
- 证据来源：git diff、git log、RELEASE-NOTES.md、上游 skills 目录

## 变更概览

| 仓库 | 旧 SHA | 新 SHA | commit 数 | 结论 |
|------|--------|--------|-----------|------|
| `upstream/everything-claude-code` | `af51fca` | `4bdbf57` | 183 | 新增多个 skills/agents，108 skills 里程碑 |
| `upstream/product-manager-skills` | `1e8ff62` | `0c59857` | 10 | 新增命令层和 Streamlit skill 查找器 |
| `upstream/superpowers` | `33e55e6` | `7e51643` | 69 | v5.0.1-v5.0.5，零依赖 brainstorm server |

## upstream/superpowers

### 本次更新包含什么

**v5.0.5 (2026-03-17)**
- `3128a2c` fix: resolve ESM/CommonJS module conflict in brainstorming server
- `f34ee47` fix: Windows brainstorm server lifecycle, restore execution choice

**v5.0.4 (2026-03-16)**
- `2c6a8a3` Tone down review loops: single-pass plan review, raise issue bar
- `f4b54a1` Auto-register skills from plugin, simplify OpenCode install to one line
- `4e7c084` feat: add Cursor-compatible hooks and fix platform detection

**v5.0.2 (2026-03-11)**
- `7619570` Remove vendored node_modules, swap to zero-dep server.js
- `9ccce3b` Add context isolation principle to all delegation skills

**v5.0.1 (2026-03-10)**
- `419889b` Move brainstorm-server into skill directory per agentskills spec
- `715e18e` Load Gemini tool mapping via GEMINI.md @import

### 具体变化

- **新增**：
  - Cursor 兼容的 hooks (`hooks-cursor.json`)
  - Gemini CLI 扩展支持
  - OpenCode 一键安装（通过 `config` hook 自动注册 skills）
- **调整**：
  - Brainstorm server 从零依赖 Node.js 实现（移除 ~1200 行 vendored 代码）
  - Review loop 精简：单遍整体 plan review、3 轮最大迭代、检查清单简化
  - 所有委派 skills 增加上下文隔离原则
- **修复**：
  - ESM/CommonJS 模块冲突（Node.js 22+）
  - Bash 5.3+ hook hang、POSIX 安全脚本、可移植 shebang
  - Windows 下 brainstorm server 生命周期

### 与本项目的关系

- **可以直接复用**：
  - `skills/writing-plans/` 的精简 review loop 逻辑
  - `skills/brainstorming/scripts/server.cjs` 零依赖服务器
  - `hooks/hooks-cursor.json` 用于 Cursor 集成
- **需要手动适配**：
  - OpenCode 一键安装模式（本项目使用 symlink 方式）
  - Gemini CLI 扩展（本项目主要使用 Kimi CLI）
- **暂时无需跟进**：
  - Windows 特定修复（本项目主要 macOS 开发）

## upstream/everything-claude-code

### 本次更新包含什么

**新增 Skills/Agents (2026-03)**
- `93a78f1` feat: add documentation-lookup, bun-runtime, nextjs-turbopack; add rust-reviewer agent
- `ac53fbc` Add Claude DevFleet multi-agent orchestration skill
- `e4cb5a1` feat: add data-scraper-agent
- `8676d3a` feat: add team-builder skill
- `c2f2f95` feat: add ai-regression-testing skill
- `cd82517` feat: add mcp-server-patterns skill
- `678ee7d` feat: add blueprint skill for multi-session construction planning

**语言支持扩展**
- `7cf07ca` feat: add java-build-resolver for Maven/Gradle
- `b659597` feat: add C++ language support
- `ebd8c8c` feat: add Rust language support
- `f10d638` feat: add Kotlin, Android, and KMP rules
- `113119d` feat: add laravel skills

**基础设施**
- `5bd183f` feat: add Codex CLI customization scripts
- `609a0f4` fix: add 62 missing skills to install manifests — full profile now covers all 105 skills

### 具体变化

- **新增**：105+ skills、25 agents、57 commands
- **调整**：安装流程强化，skill catalog 完整性校验
- **修复**：observer memory explosion、orchestrator 循环、install pipeline 测试失败

### 与本项目的关系

- **值得关注**：
  - `skills/mcp-server-patterns/` — MCP server 开发模式
  - `skills/ai-regression-testing/` — AI 回归测试
  - `skills/blueprint/` — 多会话构建规划
  - `agents/rust-reviewer/` / `java-build-resolver/` — 新增语言 reviewer
- **需要手动适配**：
  - Codex CLI 定制脚本（本项目使用 Kimi CLI）
  - 安装清单（本项目使用自定义 setup skill）

## upstream/product-manager-skills

### 本次更新包含什么

**v0.75 (2026-03-17)**
- `5a423ed` Release v0.75: restore pedagogic and equally-tasked mission
- `0dae925` Add Streamlit skill finder and refresh v0.7 messaging

**v0.65 (2026-03-08)**
- `db99db1` Release v0.65 onboarding and integration guides
- `6f1911c` Add command layer and navigation UX for v0.6

### 具体变化

- **新增**：Streamlit skill 查找器、命令层、导航 UX
- **调整**：治理文档强化（pedagogic protection rules）
- **修复**：CLAUDE.md 完整 v0.75 说明

### 与本项目的关系

- **可以直接复用**：Streamlit skill finder 模式
- **建议关注**：PM skills 的迁移进度（参见 `docs/product-manager-skills-migration-backlog.md`）

## 值得关注

### 1. superpowers v5.0.x 的 Review Loop 精简

- **证据**：`2c6a8a3` 及 RELEASE-NOTES.md v5.0.4 章节
- **为什么重要**：大幅降低 token 消耗，加快 spec/plan 审查速度
  - 单遍整体 plan review（替代分块审查）
  - 最大迭代次数从 5 降到 3
  - 检查清单从 7 项精简到 4-5 项
- **建议动作**：
  - [ ] 同步 `dev-writing-plans` 和 `dev-brainstorming` 的审查逻辑
  - [ ] 更新 checklist 文件，移除格式化类检查项

### 2. everything-claude-code 的 MCP Server Patterns

- **证据**：`cd82517` feat(skills): add mcp-server-patterns
- **为什么重要**：MCP (Model Context Protocol) 是标准化工具集成的趋势
- **建议动作**：
  - [ ] 阅读 `upstream/everything-claude-code/skills/mcp-server-patterns/SKILL.md`
  - [ ] 评估是否创建 `dev-mcp-patterns` skill

### 3. superpowers 的 Cursor/Gemini CLI 支持

- **证据**：`4e7c084` (Cursor hooks)、`715e18e` (Gemini CLI)
- **为什么重要**：本项目未来可能扩展到多平台（Kimi + Cursor + Gemini）
- **建议动作**：
  - [ ] 保留观察，暂不实施
  - [ ] 如未来需要 Cursor 支持，直接复用 `hooks-cursor.json`

### 4. product-manager-skills v0.75

- **证据**：`5a423ed` Release v0.75
- **为什么重要**：PM skills 是本项目的迁移目标之一
- **建议动作**：
  - [ ] 参考 `docs/product-manager-skills-migration-backlog.md` 继续迁移

## 后续动作

- [ ] **是否同步到 `kimi/`**：
  - `dev-writing-plans`：同步精简 review loop
  - `dev-brainstorming`：同步 spec review 校准逻辑
- [ ] **是否新增 skills**：
  - 评估 `mcp-server-patterns` 是否值得创建 `dev-mcp-patterns`
  - 评估 `ai-regression-testing` 是否创建 `dev-ai-testing`
- [ ] **验证命令**：
  - `uv run .agents/skills/update-upstream-repos/scripts/validate_skill.py`
- [ ] **下次同步**：继续执行 `switch_updated_submodules_to_main.py` 切回 main
- [ ] **文档更新**：本次无目录结构变化，AGENTS.md 无需更新

---
*报告生成时间：2026-03-18*
*脚本：`uv run .agents/skills/update-upstream-repos/scripts/generate_upstream_report.py`*
