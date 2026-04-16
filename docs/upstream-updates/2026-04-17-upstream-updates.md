# 上游仓库更新报告（2026-04-17）

## 更新范围

- 更新时间：2026-04-17
- 更新方式：`git submodule update --remote`，随后执行 `uv run .agents/skills/update-upstream-repos/scripts/switch_updated_submodules_to_main.py`
- 覆盖仓库：`upstream/everything-claude-code`、`upstream/karpathy-llm-wiki`、`upstream/superpowers`
- 最终状态：3 个 submodule 均已切回本地 `main`，`HEAD == origin/main`
- 证据来源：git diff、git log、上游 README/docs/具体文件

## 变更概览

| 仓库 | 旧 SHA | 新 SHA | commit 数 | 结论 |
|------|--------|--------|-----------|------|
| `upstream/everything-claude-code` | `5df943e` | `1a50145` | 372 | ecc2 TUI 大规模开发 + 新增 accessibility/frontend-design 等 skill，ecc2 对本项目暂无直接影响 |
| `upstream/karpathy-llm-wiki` | `5a3acdc` | `9e8c4f4` | 9 | README SEO/GEO 优化 + 示例文件翻译为英文，skill 逻辑无变化 |
| `upstream/superpowers` | `b7a8f76` | `c4bbe65` | 14 | 新增 `sync-to-codex-plugin.sh` 脚本 + Discord 链接修复 + CHANGELOG 清理 |

## upstream/superpowers

### 本次更新包含什么

主要变更围绕 Codex plugin 同步工具和文档维护：

- `2026-04-14` `8c8c5e8` 新增 `scripts/sync-to-codex-plugin.sh` — 将 superpowers 仓库自动同步为 Codex plugin 的完整工具链
- `2026-04-14` `ac1c715` 重写同步脚本，改为 clone fork → rsync → 生成 overlay → 提交 → 开 PR 的流程
- `2026-04-14` `777a977` 同步时 mirror CODE_OF_CONDUCT.md，移除 agents/openai.yaml overlay
- `2026-04-14` `6149f36` 对齐 plugin.json heredoc 与实际线上结构
- `2026-04-14` `bcdd7fa` 排除 assets/，增加 `--bootstrap` 标志用于首次创建 plugin
- `2026-04-14` `bc25777` 将 EXCLUDES 模式锚定到源根目录，防止误排除嵌套同名目录
- `2026-04-15` `34c17ae` 为 Codex plugin 生成 `interface.defaultPrompt`
- `2026-04-15` `c4bbe65` 术语清理
- `2026-04-06` `a6b1a1f` / `917e5f5` 修复 Discord 邀请链接
- `2026-04-14` `a5d36b1` 移除遗留的 CHANGELOG.md

### 具体变化

- 新增：`scripts/sync-to-codex-plugin.sh`（388 行），完整的 superpowers → Codex plugin 自动同步流程
- 调整：术语统一、EXCLUDES 锚定优化
- 修复：Discord 邀请链接失效
- 删除：`CHANGELOG.md`

### 与本项目的关系

- 可以直接复用：`sync-to-codex-plugin.sh` 思路可借鉴，但本项目通过 `ce` CLI + `skills-install.yaml` 管理，不需要此脚本
- 暂时无需跟进：本次变更不影响已同步的 dev-* skill 内容

## upstream/everything-claude-code

### 本次更新包含什么

372 个 commit，以 ecc2 Rust TUI 大规模开发和 bug 修复为主，按主题归类：

**ecc2 TUI 脚手架**（约 192 个 commit，ecc2/ 目录 +48000/-1400 行）：
- 多代理协调：delegate team board、session handoff、auto-dispatch、rebalance
- 工作树管理：status checks、merge actions、patch previews、pruning、conflict protocol
- 会话管理：budget thresholds、cost tracking、heartbeat stale detection
- TUI 增强：split diff viewer、output search/filter、pane layout switching、theme toggle
- 记忆系统：graph recall、markdown/dotenv memory connectors、connector sync checkpoints
- 通知系统：desktop/webhook/draft PR 通知
- CI 兼容：merge queue、release surface、pnpm 版本固定

**新增 skill**（3 个有独立 SKILL.md）：
- `skills/accessibility/` — WCAG 2.2 无障碍合规检查（`50dc4b04`, `aa8948d5`, `228be4f8`, `51abaf0f`）
- `skills/agent-introspection-debugging/` — agent 自省调试（`e09c548e`）
- `skills/frontend-design/` — 从 hermes 分支恢复的前端设计 skill（`ff303d71`）

**hook 系统修复**：
- `gateguard` fact-forcing pre-action gate（`5a039229`）
- bash hook fork storm 修复（`1fabf4d2`）
- 停止向 claude settings 注入 managed hooks（`2ece2cfc`）
- plugin-installed hook 命令安全引导（`1b7c5789`）

**中文文档**：
- 删除了 `docs/zh-CN/skills/project-guidelines-example/`（`0f4f95b3`）
- 修复了 configure-ecc 和 visa-doc-translate 的 markdownlint 错误（`dbdbcef5`）

### 与本项目的关系

- 暂时无需跟进：ecc2 TUI 是独立 Rust 项目，与本项目 `ce` CLI 不相关
- 可以关注：
  - `accessibility` skill 思路可借鉴，但本项目暂无 WCAG 合规需求
  - `gateguard` hook 模式（action 前强制事实确认）可在自定义 hook 中参考
  - bash hook fork storm 修复说明 Claude Code 的 hook 分发存在平台级问题，本项目如果遇到类似问题可参考
- 不需要同步：中文文档变动不影响本项目的上游跟踪

## upstream/karpathy-llm-wiki

### 本次更新包含什么

全部为文档变更，SKILL.md 和 references/ 无修改：

- `2026-04-12` `d8afa65` 新增 PROMOTION.md 推广日志（展示 94 篇文章、99 个来源、87 条日志）
- `2026-04-12` `2d37566` 压缩 PROMOTION.md（256→97 行，62% 缩减）
- `2026-04-12` `6b94cc1` 将 PROMOTION.md 加入 .gitignore（仅作内部记录）
- `2026-04-13` `7f2e2ae` / `76eafef` README SEO 优化（标题、结构、关键词）
- `2026-04-13` `637ecca` 示例文件从中文翻译为英文
- `2026-04-13` `7566892` GitHub SEO 文案优化
- `2026-04-13` `9e8c4f4` README 精简（保留 SEO 结构但提升可读性）

### 与本项目的关系

- 暂时无需跟进：skill 核心逻辑（SKILL.md、references/）无变化
- 可以关注：README 中"LLM Wiki vs RAG"对比表的精简思路可借鉴到本项目文档

## 值得关注

### 1. superpowers 新增 Codex plugin 同步脚本

- 证据：`scripts/sync-to-codex-plugin.sh`（`8c8c5e8` - `34c17ae` 共 7 个 commit）
- 为什么重要：superpowers 正式建立 Codex plugin 自动发布流程，后续版本同步可能更快
- 建议动作：观察，暂不需要在本项目中引入

### 2. everything-claude-code hook 系统稳定性提升

- 证据：bash hook fork storm 修复（`1fabf4d2`）、停止注入 managed hooks（`2ece2cfc`）、plugin-installed hook 安全引导（`1b7c5789`）
- 为什么重要：如果本项目 Claude Code 环境出现 hook 执行异常，可参考这些修复
- 建议动作：观察

### 3. karpathy-llm-wiki 纯文档更新

- 证据：9 个 commit 全部以 `docs:` 开头，无 SKILL.md / references/ 变更
- 为什么重要：不影响本项目的 `learn-llm-wiki` skill
- 建议动作：暂不处理

## 后续动作

- [x] 确认 3 个 submodule 已切回本地 `main`
- [x] 生成 `docs/upstream-updates/2026-04-17-upstream-updates.md` 报告
- [ ] 检查 `AGENTS.md` / `CLAUDE.md` 是否需要同步更新（本次无架构/目录/流程变化，暂不需要）
