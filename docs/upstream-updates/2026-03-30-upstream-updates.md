# 上游仓库更新报告（2026-03-30）

## 更新范围

- 更新时间：2026-03-30
- 更新方式：`git submodule update --remote`
- 随后执行：`uv run .agents/skills/update-upstream-repos/scripts/switch_updated_submodules_to_main.py`
- 覆盖仓库：`upstream/everything-claude-code`、`upstream/product-manager-skills`、`upstream/superpowers`、`upstream/ui-ux-pro-max-skill`
- 最终状态：所有已变化 submodule 已切回本地 `main`，`HEAD == origin/main`
- 证据来源：git diff、git log、上游 RELEASE-NOTES.md、README、CLAUDE.md

---

## 变更概览

| 仓库 | 旧 SHA | 新 SHA | commit 数 | 结论 |
|------|--------|--------|-----------|------|
| `upstream/everything-claude-code` | `4bdbf57` | `a4d4b1d` | 314 | 大量新增 skill、agent 和 ECC 2.0 Rust TUI 脚手架 |
| `upstream/superpowers` | `7e51643` | `eafe962` | 22 | v5.0.6 发布：内联自审替代 subagent 审查循环 |
| `upstream/product-manager-skills` | `0c59857` | `2a2f27c` | 5 | Claude Code 插件市场上线 |
| `upstream/ui-ux-pro-max-skill` | `07f4ef3` | `4255c21` | 18 | v2.5.0 发布：Three.js 支持、Claude GitHub Actions |

---

## upstream/everything-claude-code

### 本次更新包含什么

**新增 Agents（6 个）：**
- `flutter-reviewer` — Flutter/Dart 代码审查专家
- `healthcare-reviewer` — 医疗健康领域审查 agent
- `performance-optimizer` — 代码性能分析与优化（446 行详细配置）
- `pytorch-build-resolver` — PyTorch 构建问题解析器
- `typescript-reviewer` — TypeScript 代码审查专家

**新增 Skills（30+ 个）：**
| Skill | 用途 |
|-------|------|
| `agent-eval` | 多 agent 对比评估 |
| `agent-payment-x402` | 自主 agent 支付（X402 协议） |
| `architecture-decision-records` | 架构决策记录管理 |
| `benchmark` | 性能基准测试 |
| `browser-qa` | 浏览器 QA 自动化 |
| `canary-watch` | 金丝雀发布监控 |
| `ck` (context-keeper) | 持久化项目记忆 v2 |
| `click-path-audit` | 状态交互 bug 发现 |
| `codebase-onboarding` | 代码库接入指南 |
| `design-system` | 设计系统模式 |
| `flutter-dart-code-review` | Flutter 代码审查模式 |
| `git-workflow` | Git 工作流（715 行详细指南） |
| `healthcare-*` (4个) | 医疗健康领域专项（CDSS、EMR、PHI 合规、评估框架） |
| `laravel-plugin-discovery` | Laravel 插件发现（LaraPlugins MCP） |
| `nuxt4-patterns` | Nuxt 4 模式 |
| `product-lens` | 产品视角代码审查 |
| `pytorch-patterns` | PyTorch 开发模式 |
| `repo-scan` | 仓库扫描与发现 |
| `rules-distill` | 规则提炼与整理 |
| `rust-patterns` | Rust 模式（更新） |
| `safety-guard` | 安全检查 |
| `santa-method` | 多 agent 对抗验证 |
| `skill-comply` | 自动化行为合规测量 |
| `token-budget-advisor` | Token 预算建议 |

**新增 Commands：**
- `/prune` — 清理过期的 instinct
- `/context-budget` — 上下文预算优化
- `/rules-distill` — 规则提炼

**ECC 2.0 重大更新：**
- Rust TUI 脚手架（agentic IDE 控制平面）
- 实时输出流（per agent live streaming）
- Token/成本计量器（token/cost meter widget）
- Agent 状态面板（agent status panel with Table widget）
- 会话生命周期管理（session create/destroy）
- 崩溃恢复（crash resume session recovery）
- 分屏仪表板调整（split-pane dashboard resizing）
- 工具调用日志和历史（tool call logging）
- 工具风险评分（tool risk scoring）

**其他重要变更：**
- 新增 Kiro IDE 完整支持（18 个 skill、16 个 agent）
- 新增 Trae IDE 支持
- 新增 Brazilian Portuguese (pt-BR) 文档翻译
- 新增 Turkish (tr) 文档翻译
- 日文文档翻译完善
- 简体中文文档同步更新
- 新增 59 个命令快速参考指南
- 新增安全指南（SECURITY.md）
- 新增 repo 评估与设置建议文档
- MCP 配置新增 omega-memory、context7 等
- 新增安装目录和项目配置自动检测

### 具体变化

- **新增：** 30+ skills、6 agents、多个 commands、ECC 2.0 Rust TUI
- **调整：** skills 目录结构优化、多语言文档完善
- **修复：** 大量 CI、安装脚本、Windows 兼容性修复

### 与本项目的关系

- **可以直接复用：**
  - `skills/git-workflow/` — 本项目有类似需求
  - `skills/ck/` — 持久化项目记忆，值得评估
  - `skills/rules-distill/` — 规则提炼，可与现有 skill 整合
  - `skills/architecture-decision-records/` — 架构文档化
  
- **需要手动适配：**
  - `skills/ck/` 需要 Node.js 运行时和 MCP 配置
  - ECC 2.0 是 Rust 项目，与本项目 Python/Node 技术栈不同
  - `skills/skill-comply/` 需要 Python 依赖和测试框架

- **暂时无需跟进：**
  - 医疗健康领域 skills（`healthcare-*`）— 领域特定
  - `flutter-dart-code-review`、`pytorch-patterns` — 技术栈不匹配
  - Kiro/Trae IDE 特定配置 — 本项目使用 Kimi/Claude

---

## upstream/superpowers

### 本次更新包含什么

**v5.0.6 发布（2026-03-24）：**

1. **内联自审替代 Subagent 审查循环**
   - `brainstorming`：用内联 Spec Self-Review checklist 替代 Spec Review Loop
   - `writing-plans`：用内联 Self-Review checklist 替代 Plan Review Loop
   - 效果：25 分钟开销降至 30 秒，缺陷率相当

2. **Brainstorm Server 重构**
   - 会话目录拆分为 `content/`（HTTP 服务）和 `state/`（内部状态）
   - 修复 owner-PID 跨平台和跨用户问题

3. **Codex App 兼容性**
   - 添加 named agent dispatch mapping
   - 添加环境检测和 worktree-safe skill 行为设计文档（PRI-823）

4. **社区治理**
   - 新增 Issue 模板和 PR 模板
   - 新增 Contributor Covenant 行为准则

### 具体变化

- **新增：** Codex App 兼容性设计规范、Issue/PR 模板
- **调整：** brainstorming 和 writing-plans 审查流程（性能优化）
- **修复：** brainstorm server owner-PID 生命周期、writing-skills 文档错误

### 与本项目的关系

- **可以直接复用：**
  - v5.0.6 的内联自审 checklist 模式 — 更新本项目的 `dev-brainstorming` 和 `dev-writing-plans`
  - Codex App 兼容性设计 — 如果未来支持 Codex

- **建议动作：**
  - 同步 `dev-brainstorming` 和 `dev-writing-plans` 到 v5.0.6 的内联自审模式

---

## upstream/product-manager-skills

### 本次更新包含什么

- Claude Code 插件市场上线（`a30cfe1`）
- 更新 marketplace.json 配置
- README 和 CLAUDE.md 标记市场上线状态

### 具体变化

- **新增：** `.claude-plugin/` 目录和 marketplace.json
- **调整：** 文档标记市场上线状态

### 与本项目的关系

- **观察即可：** PM skills 已通过 submodule 跟踪，市场上线对本项目无直接影响
- **建议动作：** 观察 marketplace 分发模式，评估是否适用于本项目的 skills 分发

---

## upstream/ui-ux-pro-max-skill

### 本次更新包含什么

**v2.5.0 发布：**

1. **Three.js 技术栈支持（`ddef277`）**
   - 完整的 Three.js stack 集成

2. **多 IDE/平台增强**
   - Angular 技术栈支持
   - Laravel 技术栈支持
   - KiloCode 支持
   - Warp 终端支持
   - Augment 支持
   - 全局安装支持
   - uninstall 命令完善

3. **GitHub Actions 集成**
   - Claude Code Review workflow
   - Claude PR Assistant workflow

4. **其他改进**
   - CLI 版本升级到 2.5.0
   - Antigravity 文件夹映射更新到 `.agents`
   - 平台配置模板添加 YAML frontmatter
   - 清理孤立的 demo 文件

### 具体变化

- **新增：** Three.js 技术栈、Angular、Laravel、多个 IDE 支持
- **调整：** CLI 版本、Antigravity 映射、平台配置格式
- **修复：** uninstall 目录存在性检查

### 与本项目的关系

- **暂时无需跟进：**
  - UI/UX Pro Max 是独立 CLI 工具，本项目使用 skill 方式集成
  - Three.js、Angular、Laravel 技术栈支持与本项目当前需求不匹配

---

## 值得关注

### 1. superpowers v5.0.6 的内联自审模式

- **证据：** [RELEASE-NOTES.md](upstream/superpowers/RELEASE-NOTES.md) v5.0.6 节
- **为什么重要：** 本项目当前的 `dev-brainstorming` 和 `dev-writing-plans` 可能使用 subagent 审查循环，同步内联自审可显著降低延迟（25min → 30s）
- **建议动作：** 同步更新本项目的 brainstorming 和 writing-plans skill

### 2. everything-claude-code 的 `ck` (context-keeper) skill

- **证据：** [skills/ck/SKILL.md](upstream/everything-claude-code/skills/ck/SKILL.md)、commit `1e226ba`
- **为什么重要：** 提供持久化项目记忆，支持跨会话恢复上下文，可能改善本项目的开发体验
- **建议动作：** 评估是否引入，需要 Node.js + MCP 配置

### 3. everything-claude-code 的 `git-workflow` skill

- **证据：** [skills/git-workflow/SKILL.md](upstream/everything-claude-code/skills/git-workflow/SKILL.md)、715 行详细指南
- **为什么重要：** 本项目有 `dev-git-worktrees` skill，但 git-workflow 更全面
- **建议动作：** 对比现有 skill，考虑合并或替换

### 4. ECC 2.0 Rust TUI

- **证据：** commit `00dce30`、`44c2bf6` 等
- **为什么重要：** ECC 正在重写为 Rust TUI 应用，架构变化可能影响 Codex/Claude Code 生态
- **建议动作：** 观察，暂不跟进（技术栈不匹配）

---

## 后续动作

- [ ] 同步 `dev-brainstorming` 到 superpowers v5.0.6 内联自审模式
- [ ] 同步 `dev-writing-plans` 到 superpowers v5.0.6 内联自审模式
- [ ] 评估引入 `ck` (context-keeper) skill 的可行性
- [ ] 对比 `git-workflow` 与现有 `dev-git-worktrees`，决定是否整合
- [ ] 更新 `AGENTS.md` 中的上游仓库状态（如有必要）
- [ ] 下次同步时继续补跑 `switch_updated_submodules_to_main.py`

---

## 验证

已验证所有 submodule 状态：

```bash
$ git submodule status
 a4d4b1d756f08f9127de3dc4b6b1a557c3449517 upstream/everything-claude-code (v1.7.0-545-ga4d4b1d)
 91f3d394db8419c20d67ebe22a96cf8fee0a404b upstream/humanizer-zh (heads/main)
 bb9ec95e1b59c3471bd6fd77a78a4042430bfac3 upstream/obsidian-skills (heads/main)
 921bd14bde0edbf94cd914aa331976e81e54cdbe upstream/orbitos (heads/main)
 2a2f27c71c562dd6b6797c8f4d224825d6005c7f upstream/product-manager-skills (heads/main)
 eafe962b18f6c5dc70fb7c8cc7e83e61f4cdde06 upstream/superpowers (v5.0.6)
 4255c218a6762c945a782701fd38dfb24fc10064 upstream/ui-ux-pro-max-skill (v2.5.0-1-g4255c21)
```

所有已更新仓库已切回 `main` 分支，与远端同步。
