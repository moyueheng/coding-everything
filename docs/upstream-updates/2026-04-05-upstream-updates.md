# 上游仓库更新报告（2026-04-05）

## 更新范围

- 更新时间：2026-04-05
- 更新方式：`git submodule update --remote`，随后执行 `uv run .agents/skills/update-upstream-repos/scripts/switch_updated_submodules_to_main.py`
- 覆盖仓库：`upstream/everything-claude-code`、`upstream/obsidian-skills`、`upstream/ui-ux-pro-max-skill`、`upstream/product-manager-skills`、`upstream/superpowers`
- 最终状态：5 个 submodule 已切回本地 `main`，`HEAD == origin/main`
- 未变化仓库：`upstream/humanizer-zh`、`upstream/orbitos`
- 证据来源：git log、git diff --stat、上游 skill 文件

## 变更概览

| 仓库 | 旧 SHA | 新 SHA | commit 数 | 结论 |
|------|--------|--------|-----------|------|
| `upstream/everything-claude-code` | `bf3fd69` | `5df943e` | 10 | 新增 5 个 skill（nestjs/jira/dart/dotnet/csharp），新增 web 规则体系，修复 hook 和 observer |
| `upstream/obsidian-skills` | `bb9ec95` | `fa1e131` | 2 | defuddle 跳过 `.md` URL，小修复 |
| `upstream/ui-ux-pro-max-skill` | `4255c21` | `b7e3af8` | 4 | design_system 输出改进（Unicode 边框、ANSI 色板、暗色模式） |
| `upstream/product-manager-skills` | `2a2f27c` | `4aa4196` | 2 | 新增 product-sense-interview-answer skill |
| `upstream/superpowers` | `dd23728` | `b7a8f76` | 3 | README 精简社区/支持信息，新增发布公告订阅链接 |

---

## upstream/everything-claude-code

### 本次更新包含什么

67 files changed, 4779 insertions(+), 214 deletions(-)

按主题归类：

**新增 skill（5 个）**：
- `nestjs-patterns` — NestJS 模块/控制器/DTO/guard/interceptor 模式
- `jira-integration` — Jira ticket 读取、分析、更新，支持 MCP 和 REST API 两种方式
- `dart-flutter-patterns` — Dart 空安全、BLoC/Riverpod/Provider 状态管理、GoRouter 导航
- `dotnet-patterns` — C# .NET 依赖注入、async/await、不可变性模式
- `csharp-testing` — xUnit + FluentAssertions 测试模式
- `hexagonal-architecture` — 端口与适配器架构模式（已有 skill 修复内容，非新增目录）

**新增规则体系（web 前端）**：
- `rules/web/` 下新增 6 个规则文件：coding-style、design-quality、hooks、patterns、performance、security
- 新增 `.cursor/hooks/after-file-edit.js` 和 `scripts/hooks/design-quality-check.js`（Cursor 设计质量 hook）

**新增 agent/command**：
- `agents/csharp-reviewer.md`、`agents/dart-build-resolver.md`
- `commands/jira.md`、`commands/flutter-build.md`、`commands/flutter-review.md`、`commands/flutter-test.md`

**Bug 修复**：
- `scripts/lib/utils.js`：修复 hook 工具未尊重 HOME 覆盖路径的问题
- `scripts/hooks/session-start.js` / `session-end-marker.js`：清理 observer sessions 生命周期
- `skills/continuous-learning-v2/hooks/observe.sh`：POSIX 兼容 fallback
- markdownlint 基线修复

**重构**：
- `skills/article-writing`、`content-engine`、`crosspost`、`investor-outreach` 写作语调规则整合

### 与本项目的关系

- 可以直接复用：`nestjs-patterns`、`hexagonal-architecture` 与本项目已有的 `dev-backend-patterns` 定位互补，但当前项目不涉及 NestJS 或 hexagonal 架构，暂无需引入
- 需要手动适配：`rules/web/` 体系与 Cursor hook 机制耦合，不适合直接迁移到 Claude Code / Kimi
- 暂时无需跟进：Dart/C# 相关 skill 和 Jira 集成不在当前技术栈内

---

## upstream/obsidian-skills

### 本次更新包含什么

1 file changed, 1 insertion(+), 1 deletion(-)

- `2026-04-02` `fa1e131` Merge PR #64 — defuddle skill 跳过 `.md` URL
- `2026-03-29` `1e1df34` Skip defuddle for .md URLs

### 具体变化

- defuddle skill 在遇到 `.md` 结尾的 URL 时不再调用 defuddle 处理，避免对纯 Markdown 链接做不必要的提取

### 与本项目的关系

- 本项目已迁移 `defuddle` skill 到 `skills/defuddle/`，此修复应同步到本地副本
- 修复内容与 `UPSTREAM.md` 跟踪机制一致

---

## upstream/ui-ux-pro-max-skill

### 本次更新包含什么

5 files changed, 344 insertions(+), 142 deletions(-)

- `2026-03-15` `e3102cb` design_system.py 输出改进：Unicode 边框、ANSI 色板、扩展调色板、暗色/亮色模式
- `2026-03-17` `83692f7` 新增 GitHub Actions conda 工作流
- `2026-04-03` 两个 merge commit 合并上述变更

### 与本项目的关系

- 暂时无需跟进：本项目未使用 ui-ux-pro-max-skill 的 design system 输出功能

---

## upstream/product-manager-skills

### 本次更新包含什么

- `2026-04-02` `dc8dec7` Add product sense interview answer skill
- `2026-04-02` `4aa4196` Merge PR #4 — Add product-sense-interview-answer skill

新增文件：
- `skills/product-sense-interview-answer/SKILL.md` — 250 行，PM 面试产品设计题的六段式答题框架
- `skills/product-sense-interview-answer/template.md` — 155 行答题模板
- `skills/product-sense-interview-answer/examples/improve-youtube.md` — 118 行示例（"How would you improve YouTube?"）

其他变更：
- `.claude-plugin/marketplace.json` 更新
- `README.md` / `catalog/` / `docs/` 元数据同步

### 与本项目的关系

- 暂时无需跟进：本项目已有 `work-*` 系列 PM skill，product-sense-interview-answer 面向 PM 求职场景，与当前开发工作流不直接相关

---

## upstream/superpowers

### 本次更新包含什么

1 file changed, 2 insertions(+), 6 deletions(-)

- `2026-04-02` `eeaf2ad` Add release announcements link, consolidate Community section
- `2026-04-02` `4b1b20f` Add detailed Discord description to Community section
- `2026-04-02` `b7a8f76` Merge PR #1029

### 具体变化

- README.md 精简社区/支持段落，移除独立的 Support section 和 Marketplace 链接
- 新增 Prime Radiant 发布公告订阅链接

### 与本项目的关系

- 无需跟进：纯文档变更，不影响 skill 内容

---

## 值得关注

### 1. obsidian-skills defuddle 跳过 .md URL 修复

- 证据：`upstream/obsidian-skills` commit `1e1df34`，修改 defuddle skill 的 URL 过滤逻辑
- 为什么重要：本项目已迁移 defuddle skill 到 `skills/defuddle/`，上游修复了一个实际边界 case（对 `.md` 链接做不必要的 defuddle 处理）
- 建议动作：同步修复到 `skills/defuddle/SKILL.md`

---

## 后续动作

- [ ] 同步 obsidian-skills defuddle `.md` URL 修复到 `skills/defuddle/SKILL.md`
- [ ] 检查 `upstream/everything-claude-code` 新增的 `hexagonal-architecture` skill 是否值得引入（与 `dev-backend-patterns` 互补评估）
- [ ] 确认 product-manager-skills 新 skill 是否需要加入 `skills-install.yaml`
