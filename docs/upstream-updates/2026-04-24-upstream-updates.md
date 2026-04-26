# 上游仓库更新报告（2026-04-24）

## 更新范围

- 更新时间：2026-04-24
- 更新方式：`git submodule update --remote`
- 后续动作：执行 `uv run .agents/skills/update-upstream-repos/scripts/switch_updated_submodules_to_main.py`
- 覆盖仓库：`upstream/everything-claude-code`、`upstream/obsidian-skills`、`upstream/superpowers`、`upstream/ui-ux-pro-max-skill`
- 最终状态：4 个发生变化的 submodule 都已切回本地 `main`，且 `HEAD == origin/main`
- 证据来源：根仓库 `git diff --submodule=short HEAD`、各上游 `git log`、`git describe`、上游 `README.md`

## 变更概览

| 仓库 | 旧 SHA | 新 SHA | commit 数 | 结论 |
|------|--------|--------|-----------|------|
| `upstream/everything-claude-code` | `bf3fd69` | `4e66b28` | 412 | 上游公开面与安装链路变化很大，本仓库文档必须同步真实体量与插件边界 |
| `upstream/obsidian-skills` | `bb9ec95` | `fa1e131` | 2 | `defuddle` 跳过 `.md` URL，属于低风险行为修正，本地无需额外适配 |
| `upstream/superpowers` | `b7a8f76` | `b557648` | 18 | Codex plugin 镜像工具链继续推进，值得保留关注但暂不直接回灌本仓库 skills |
| `upstream/ui-ux-pro-max-skill` | `4255c21` | `b7e3af8` | 4 | 新增 Conda 包流程并强化设计系统输出，当前仅需更新 gitlink |

## upstream/everything-claude-code

### 本次更新包含什么

- `2026-04-22` `4e66b288` docs: fix plugin quick start for continuous learning v2
- `2026-04-22` `df9a478e` fix(hooks): avoid Claude Code v2.1.116 argv-dup bug in settings.local.json
- `2026-04-21` `92e0c7e9` fix: install native Cursor hook and MCP config
- `2026-04-21` `c19fde22` fix: remove agents field from plugin.json manifest
- `2026-04-19` `7992f8fc` feat: integrate ecc2 board observability prototype

### 具体变化

- 新增：
  - ECC 2.0 继续扩展，包含 board observability、dashboard / session / budget / graph context 相关能力
- 调整：
  - README 公共目录与安装说明继续收敛，公开面现在明确写到 `48 agents / 183 skills / 79 legacy command shims`
  - Cursor 安装链路增加原生 hook / MCP 配置处理
- 修复：
  - 多个 hook 安装脚本针对 Windows 与 Claude Code 2.1.116 做兼容修复
  - plugin manifest 去掉 `agents` 字段，避免重复或错误安装面

### 与本项目的关系

- 可以直接复用：
  - 对插件安装边界、hook 自动加载、Cursor 原生安装的最新表述
- 需要手动适配：
  - 如果后续继续借鉴 ECC 的 Codex / Cursor / OpenCode 做法，需要按本仓库 `ce` 安装器与 `mcp-configs/required.json` 重新映射
- 暂时无需跟进：
  - ECC 2.0 alpha 的大部分 Rust 控制面能力，当前不属于本仓库近期维护范围

## upstream/obsidian-skills

### 本次更新包含什么

- `2026-04-24` `fa1e131` Merge pull request #64 from petersolopov/improve/defuddle-skip-md-urls
- `2026-04-23` `1e1df34` Skip defuddle for .md URLs

### 具体变化

- 修复：
  - `defuddle` 现在会跳过已经是 Markdown 的 URL，避免做无意义二次抽取

### 与本项目的关系

- 可以直接复用：
  - 本地 `skills/defuddle/` 的行为预期应与此保持一致
- 需要手动适配：
  - 暂无
- 暂时无需跟进：
  - 这次没有目录结构或安装方式变化

## upstream/superpowers

### 本次更新包含什么

- `2026-04-24` `b557648` formatting
- `2026-04-23` `99e4c65` reorder installs
- `2026-04-23` `a5dd364` README updates for Codex, other cleanup
- `2026-04-22` `34c17ae` sync-to-codex-plugin: seed interface.defaultPrompt
- `2026-04-22` `bc25777` sync-to-codex-plugin: anchor EXCLUDES patterns to source root
- `2026-04-22` `ac1c715` rewrites sync tool to clone the fork, open a PR, and regenerate overlays inline
- `2026-04-22` `8c8c5e8` adds tooling to mirror superpowers as a codex plugin with the appropriate metadata changes

### 具体变化

- 新增：
  - 面向 Codex plugin 的镜像脚本与 overlay 生成链路
- 调整：
  - README / install 顺序与表述继续围绕 Codex plugin 形态整理
- 修复：
  - EXCLUDES 根路径锚定、heredoc 形状、镜像同步流程等细节被校正

### 与本项目的关系

- 可以直接复用：
  - 对 Codex plugin 镜像和默认提示词注入的最新思路
- 需要手动适配：
  - 本仓库当前还是以共享 skill + `ce` 安装器为主，不能直接照搬 superpowers 的 plugin 镜像脚本
- 暂时无需跟进：
  - 纯格式化和 README 文案整理

## upstream/ui-ux-pro-max-skill

### 本次更新包含什么

- `2026-04-24` `83692f7` Create python-package-conda.yml
- `2026-04-24` `e3102cb` Improve design system output with Unicode borders, ANSI color swatches, extended palette, and dark/light mode

### 具体变化

- 新增：
  - Python package 的 Conda workflow
- 调整：
  - 设计系统输出更强调调色板表达与终端可视化

### 与本项目的关系

- 可以直接复用：
  - 后续若继续打磨 `dev-design-system` / `dev-ui-styling`，可以参考其终端输出表达
- 需要手动适配：
  - 本仓库不直接消费该上游的 CI
- 暂时无需跟进：
  - 这轮无需改本地 skill 内容

## 值得关注

### 1. `ce` 安装文档必须完全摆脱 `skills-install.yaml` 叙事

- 证据：本仓库当前没有 `skills-install.yaml`；安装入口实际是 `ce init` + `~/.ce/config.yaml`，而上游同步后 `everything-claude-code` 与 `superpowers` 也都在继续收敛安装表面
- 为什么重要：继续保留旧文档会让用户按不存在的文件排查问题，属于高频误导
- 建议动作：已在 `README.md`、`AGENTS.md`、`CLAUDE.md` 同步为当前实现

### 2. `everything-claude-code` 的公开面已经和旧记录不在一个量级

- 证据：`upstream/everything-claude-code/README.md` 当前明确写到 `48 agents / 183 skills / 79 legacy command shims`
- 为什么重要：本仓库若继续记录为 `69+ / 28+ / 58+`，会让后续筛选和评估严重失真
- 建议动作：已把项目文档中的体量描述更新为真实值

### 3. OrbitOS workflow 和 Obsidian 编辑类 skill 的分组边界需要写清楚

- 证据：`ce init` 的实现只把 `obsidian-*`、`json-canvas`、`defuddle` 识别为 `obsidian` 组；`life-*` / `work-*` 默认归入 `global`
- 为什么重要：旧文档把 OrbitOS workflow 也写成 Obsidian 组的一部分，容易让安装预期出错
- 建议动作：已在根文档中明确新的分组规则

## 后续动作

- [x] 更新 4 个 submodule gitlink 并切回本地 `main`
- [x] 生成 `docs/upstream-updates/2026-04-24-upstream-updates.md`
- [x] 同步 `README.md`、`AGENTS.md`、`CLAUDE.md` 中的稳定事实
- [ ] 下次若继续吸收 `everything-claude-code`，优先评估其 Cursor / Codex / hook 安装边界，而不是盲目扩大镜像范围
