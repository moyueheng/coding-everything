# 上游仓库更新报告（2026-05-03）

## 更新范围

- 更新时间：2026-05-03
- 更新方式：`git submodule update --init --remote`
- 后续处理：已执行 `uv run .agents/skills/update-upstream-repos/scripts/switch_updated_submodules_to_main.py`
- 覆盖仓库：全部 `.gitmodules` 中的 `upstream/*` submodule
- 发生 gitlink 变化：`upstream/everything-claude-code`、`upstream/karpathy-skills`、`upstream/product-manager-skills`、`upstream/superpowers`
- 最终状态：全部已初始化 `upstream/*` submodule 均已切回本地 `main`；上述 4 个发生 gitlink 变化的 submodule 均 `HEAD == origin/main`
- 证据来源：`git diff --submodule=short HEAD`、各 submodule 的 `git log` / `git diff --stat`、上游 README / docs / scripts / plugin manifest

## 变更概览

| 仓库 | 旧 SHA | 新 SHA | commit 数 | 结论 |
|------|--------|--------|-----------|------|
| `upstream/everything-claude-code` | `4e66b28` | `841beea` | 88 | ECC 2.0 rc1、跨 harness 文档、loop-status / auto-update / consult 工具链继续成型 |
| `upstream/karpathy-skills` | `fb7a22c` | `2c60614` | 1 | 仅同步中文 README 的 Cursor 使用说明 |
| `upstream/product-manager-skills` | `4aa4196` | `d68d280` | 4 | 新增 v0.78 release packaging，提供 Claude / Codex 可下载包构建脚本 |
| `upstream/superpowers` | `b557648` | `e7a2d16` | 2 | Codex plugin 同步改为使用已提交 manifest/assets，并提高新 harness PR 证据要求 |

## upstream/everything-claude-code

### 本次更新包含什么

- `2026-04-28` `0a87323e` `feat(ecc2): finalize rc1 release surface`
- `2026-04-29` `a7a56fa2` `feat: add auto-update command`
- `2026-04-30` `9a3f7271` `feat: add ECC consult command`
- `2026-04-30` `b8452dc1` `feat: add loop status transcript inspector`
- `2026-04-30` `38f4265a` `feat: add loop-status watch mode`
- `2026-04-30` `fbd441b4` `feat: add loop-status exit-code mode`
- `2026-04-30` `20154ddb` `feat: write loop-status snapshots`

### 具体变化

- 新增 `docs/releases/2.0.0-rc.1/`，包含 quickstart、release notes、launch checklist、demo prompts 等发布材料。
- 新增 `docs/architecture/cross-harness.md`，README 明确 ECC 面向 Claude Code、Codex、Cursor、OpenCode、Gemini 等 harness。
- 新增 `scripts/loop-status.js` 与 `/loop-status` 的跨会话 CLI 说明，支持 transcript 扫描、watch、exit-code、snapshot 写入。
- 新增 `scripts/auto-update.js` 与 `/auto-update` 命令，基于记录的 install-state 重新执行 install-apply。
- 新增 `scripts/consult.js`，可按查询词推荐安装 profile / component，并支持 `--target codex` 等目标。
- 公开面从本仓库旧文档记录的 `48 agents / 183 skills / 79 legacy command shims`，调整为上游 README 当前记录的 `48 agents / 182 skills / 68 legacy command shims`。
- Codex 表面继续收敛：上游 README 记录 `.agents/skills/` 为 32 个 Codex auto-loaded skill，并移除对 canonical Anthropic skills 的重复打包。

### 与本项目的关系

- 可以直接复用：`loop-status` 的 bounded watch / snapshot 思路，适合本项目后续长循环 agent 监控设计借鉴。
- 需要手动适配：`auto-update` 绑定 ECC 的 install-state / install-apply，不应直接搬进 `ce`，但可作为 `ce update` 恢复安装状态的参考。
- 暂时无需跟进：ECC 2.0 rc1 / Hermes operator 属于上游产品化发布表面，本项目当前没有直接迁移需求。

## upstream/karpathy-skills

### 本次更新包含什么

- `2026-04-20` `2c60614` `Sync Chinese README with English version (add Cursor section) (#95)`

### 具体变化

- `README.zh.md` 新增 Cursor 使用章节，说明仓库包含 `.cursor/rules/karpathy-guidelines.mdc`，并指向 `CURSOR.md`。

### 与本项目的关系

- 可以直接复用：中文文档里 Cursor 规则说明更完整。
- 需要手动适配：无。
- 暂时无需跟进：本项目已经有自己的高优先级 AGENTS/CLAUDE 约束，不应整段覆盖。

## upstream/product-manager-skills

### 本次更新包含什么

- `2026-04-26` `9894fdd` `Add v0.78 release packaging automation`
- `2026-04-28` `a723558` `Add direct release download links`
- `2026-04-28` `ad770b0` `Fix release download links`
- `2026-04-28` `d68d280` `Package Claude packs as skill zip bundles`

### 具体变化

- 新增 `.github/workflows/build-release.yml`，通过版本 tag 构建 release artifact。
- 新增 `scripts/build-release.sh`、`scripts/build-claude-desktop-packs.sh`、`scripts/build-codex-skills.sh`、`scripts/validate-skills.sh`。
- 新增 `docs/RELEASE-PACKAGING.md`，明确 `skills/` 是 canonical source，`dist/` 是生成物。
- 新增 `docs/INSTALL-CODEX.md`，Codex ZIP 展开后提供 `.agents/skills/<skill-name>/SKILL.md` 与 `AGENTS.md`。
- 新增 Claude Desktop/Web、Claude Code、Codex 三类安装文档。

### 与本项目的关系

- 可以直接复用：PM skills 的 Codex 包形态与本项目 `.agents/skills` / `skills/` 兼容，可作为后续 PM skills 批量迁移或可选安装组的参考。
- 需要手动适配：release 脚本面向上游 `dist/` 包，不应直接并入本仓库安装路径。
- 暂时无需跟进：当前本项目已有 `work-*` PM workflow，不需要因为 release packaging 立即扩大迁移范围。

## upstream/superpowers

### 本次更新包含什么

- `2026-04-23` `6efe32c` `Use committed Codex plugin files in sync script`
- `2026-04-27` `e7a2d16` `Require session transcript for new-harness PRs`

### 具体变化

- 新增 `.codex-plugin/plugin.json`，包含 `skills: "./skills/"`、display metadata、icon/logo 路径等 Codex plugin manifest。
- 新增 `assets/app-icon.png` 与 `assets/superpowers-small.svg`。
- `scripts/sync-to-codex-plugin.sh` 改为读取已提交的 `.codex-plugin/plugin.json` 与 assets，再同步到 `prime-radiant-inc/openai-codex-plugins`。
- PR 模板要求新增 harness 支持必须贴出 clean session transcript，并以 `Let's make a react todo list` 自动触发 `brainstorming` 作为验收标准。

### 与本项目的关系

- 可以直接复用：已提交 manifest/assets 的同步策略比临时生成 plugin 文件更稳定，适合本项目后续做 Codex plugin 包装时参考。
- 需要手动适配：Superpowers 的同步目标是外部 `openai-codex-plugins` fork，本项目不直接使用。
- 暂时无需跟进：PR transcript 要求是上游贡献门槛，本项目只需在文档里保留“新增 harness 必须有真实会话证据”的思路。

## 值得关注

### 1. ECC 的 loop-status 已经从 slash command 变成可脚本化监控入口

- 证据：`scripts/loop-status.js`、`commands/loop-status.md`，以及 `b8452dc1`、`38f4265a`、`fbd441b4`、`20154ddb`。
- 为什么重要：它把 transcript 检查、watch、exit code、snapshot 文件分离出来，能服务 sibling terminal / watchdog，而不是只能等当前会话执行 slash command。
- 建议动作：观察并借鉴到 `dev-continuous-agent-loop`，不要直接迁移 ECC 命令实现。

### 2. PM Skills 开始提供标准 release packaging

- 证据：`docs/RELEASE-PACKAGING.md`、`docs/INSTALL-CODEX.md`、`scripts/build-codex-skills.sh`、`scripts/build-release.sh`。
- 为什么重要：它证明上游已经把 `skills/` 作为 canonical source，把 Codex 发布包整理成 `.agents/skills` 结构，这与本项目安装器的目标形态一致。
- 建议动作：后续筛选 PM skills 时优先读取 release packaging，而不是手工猜测目录。

### 3. Superpowers Codex plugin 同步转向 committed manifest

- 证据：`.codex-plugin/plugin.json`、`scripts/sync-to-codex-plugin.sh`、`6efe32c`。
- 为什么重要：把 plugin manifest 和资产纳入版本控制，减少同步脚本里的隐式生成逻辑。
- 建议动作：本项目如果后续提供 Codex plugin，应优先采用“提交 manifest + 脚本只同步”的边界。

## 后续动作

- [ ] 评估是否把 ECC `loop-status` 的 snapshot / bounded watch 思路写入 `dev-continuous-agent-loop`
- [ ] 评估 PM Skills v0.78 Codex package 是否能作为 `work-*` 后续迁移证据源
- [x] 同步根 `AGENTS.md` / `CLAUDE.md` 的上游版本与公开体量信息
- [x] 同步根 `README.md` 的上游清单
