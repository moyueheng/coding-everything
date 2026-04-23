# Agent Context Workspace Split Implementation Plan

> **给 Agent：** 必需子 skill：使用 `dev-executing-plans` 逐个任务实施此计划。

**目标：** 将 agent 指令与 skill 加载规则拆成可复用的全局、开发工作区、生活工作区、Obsidian vault 四层，并为 Codex、Claude Code、Kimi CLI、OpenCode 提供可执行落地路径。

**架构：** 以 `docs/agent-context-loading.md` 为机制说明，以模板文档承载可复制的 `AGENTS.md`、`CLAUDE.md`、Kimi/OpenCode shell function。后续可由 `setup` 或 `ce` CLI 把模板安装到用户机器，但本计划第一阶段只做文档和模板，不修改用户本机配置。

**技术栈：** Markdown、POSIX shell snippet、Codex `.codex-root`、Kimi CLI `--skills-dir`、OpenCode `OPENCODE_CONFIG_CONTENT`。

---

## 文件结构

- 修改：`docs/agent-context-loading.md`
  - 保持跨工具加载机制说明。
  - 保留 alias/function 方案，确保示例不写死个人路径。

- 已创建：`docs/plans/2026-04-21-agent-context-workspace-split-design.md`
  - 作为已批准设计 spec。

- 创建：`docs/templates/agent-context/global-AGENTS.md`
  - 用户全局 `AGENTS.md` 模板，只放跨场景稳定规则。

- 创建：`docs/templates/agent-context/projects-AGENTS.md`
  - 开发工作区 `AGENTS.md` 模板。

- 创建：`docs/templates/agent-context/life-AGENTS.md`
  - 生活/研究/写作/知识管理工作区 `AGENTS.md` 模板。

- 创建：`docs/templates/agent-context/obsidian-vault-AGENTS.md`
  - Obsidian vault `AGENTS.md` 模板。

- 创建：`docs/templates/agent-context/CLAUDE.md`
  - 通用 `CLAUDE.md` 模板，通过 `@AGENTS.md` 复用同目录规则。

- 创建：`docs/templates/agent-context/agent-context-functions.sh`
  - Kimi/OpenCode wrapper function 模板。

- 修改：`README.md`
  - 在文档列表中补充 agent context workspace split 模板入口。

- 修改：`AGENTS.md` 和 `CLAUDE.md`
  - 仅在项目文档目录结构或开发约定需要反映新模板目录时更新。

## 任务 1：整理已批准设计与机制文档

**文件：**
- 修改：`docs/agent-context-loading.md`
- 保留：`docs/plans/2026-04-21-agent-context-workspace-split-design.md`

**步骤 1：检查现有内容**

运行：

```bash
rg -n "/Users/|01-Projects|00-Life|myhron-os" docs/agent-context-loading.md docs/plans/2026-04-21-agent-context-workspace-split-design.md
```

预期：无输出。

**步骤 2：检查 alias/function 方案完整性**

确认 `docs/agent-context-loading.md` 包含：

```text
OPENCODE_CONFIG_CONTENT
_oc_with_root
_kimi_with_root
project_root_markers = [".codex-root"]
```

运行：

```bash
rg -n "OPENCODE_CONFIG_CONTENT|_oc_with_root|_kimi_with_root|project_root_markers" docs/agent-context-loading.md
```

预期：每个关键词至少出现一次。

**步骤 3：如检查失败，修正文档**

使用 `apply_patch` 修正文档。不得引入个人绝对路径；所有路径使用 `$HOME`、`<projects-dir>`、`<life-dir>`、`<obsidian-vault>` 或环境变量。

**步骤 4：验证**

运行：

```bash
rg -n "/Users/|01-Projects|00-Life|myhron-os" docs/agent-context-loading.md docs/plans/2026-04-21-agent-context-workspace-split-design.md
```

预期：无输出。

## 任务 2：创建全局和工作区 AGENTS 模板

**文件：**
- 创建：`docs/templates/agent-context/global-AGENTS.md`
- 创建：`docs/templates/agent-context/projects-AGENTS.md`
- 创建：`docs/templates/agent-context/life-AGENTS.md`
- 创建：`docs/templates/agent-context/obsidian-vault-AGENTS.md`

**步骤 1：创建模板目录**

使用 `apply_patch` 添加新文件时自动创建路径；不要用 shell 写文件。

**步骤 2：创建 `global-AGENTS.md`**

内容必须表达：

```markdown
# AGENTS.md

## 全局规则

- 所有回复使用中文。
- 作者署名仅允许：myhron <moyueheng@gmail.com>。
- 禁止虚构、猜测、脑补；不确定时使用工具检索或询问。
- 工具优先于推理。
- 除非用户主动要求，否则不要提交 commit。

## 环境

- Python 包管理使用 `uv`，执行统一使用 `uv run`。
- Node 管理器使用 `fnm`。
- 网络慢时可按本机代理配置处理。
```

注意：作者署名是项目硬规则，允许保留固定邮箱。

**步骤 3：创建 `projects-AGENTS.md`**

内容必须覆盖：

```markdown
# AGENTS.md

## 开发工作区规则

- 开始任务先检索已有实现和文档，避免重复造轮子。
- 禁止引入新的重型框架，除非用户明确批准。
- 禁止跨模块隐式耦合。
- 代码修改后运行与改动相关的最小验证命令。
- 触及目录结构、架构边界、工作流、安装步骤、测试入口时，同步相关 `AGENTS.md` / `CLAUDE.md`。

## Skill 使用

- `dev-*` skill 只在代码开发、调试、测试、架构、前端、后端、MCP、代码清理等任务中使用。
- 非开发任务不强制进入开发 workflow。
```

**步骤 4：创建 `life-AGENTS.md`**

内容必须覆盖：

```markdown
# AGENTS.md

## 生活工作区规则

- 用于生活、研究、写作、知识管理任务。
- 不默认触发代码开发 workflow。
- 输出优先清晰、可执行、可归档。
- 涉及外部事实、政策、价格、新闻、软件版本时先检索。

## Skill 使用

- `life-*` 用于个人流程。
- `learn-*` 用于学习和研究。
- `work-*` 用于产品、市场、用户故事等工作流。
```

**步骤 5：创建 `obsidian-vault-AGENTS.md`**

内容必须覆盖：

```markdown
# AGENTS.md

## Obsidian Vault 规则

- 使用 Obsidian Flavored Markdown。
- 保留 wikilink、frontmatter、callout、embed 等 Obsidian 语法。
- 修改 vault 文件前先理解所在目录约定。
- 涉及 Bases、Canvas、vault CLI 时优先使用对应 Obsidian skill。

## Skill 使用

- `obsidian-markdown` 用于 Markdown 文件。
- `obsidian-bases` 用于 `.base` 文件。
- `json-canvas` 用于 `.canvas` 文件。
- `obsidian-cli` 用于 vault 交互。
```

**步骤 6：验证**

运行：

```bash
find docs/templates/agent-context -maxdepth 1 -type f | sort
rg -n "/Users/|01-Projects|00-Life|myhron-os" docs/templates/agent-context || true
```

预期：

```text
docs/templates/agent-context/CLAUDE.md
docs/templates/agent-context/agent-context-functions.sh
docs/templates/agent-context/global-AGENTS.md
docs/templates/agent-context/life-AGENTS.md
docs/templates/agent-context/obsidian-vault-AGENTS.md
docs/templates/agent-context/projects-AGENTS.md
```

第二条命令无输出。

## 任务 3：创建 `CLAUDE.md` 和 shell function 模板

**文件：**
- 创建：`docs/templates/agent-context/CLAUDE.md`
- 创建：`docs/templates/agent-context/agent-context-functions.sh`

**步骤 1：创建 `CLAUDE.md` 模板**

内容：

```markdown
@AGENTS.md

## Claude Code

Claude Code 专属补充写在这里。默认复用同目录 `AGENTS.md`。
```

**步骤 2：创建 `agent-context-functions.sh` 模板**

内容必须包含：

```bash
# Configure these paths for your machine.
export PROJECTS_AI_ROOT="$HOME/<projects-dir>"
export LIFE_AI_ROOT="$HOME/<life-dir>"
export OBSIDIAN_AI_ROOT="$LIFE_AI_ROOT/<obsidian-vault>"
```

并包含：

```bash
_oc_with_root()
ocp()
ocl()
oco()
_kimi_with_root()
kimip()
kimil()
kimio()
```

实现可复用 `docs/agent-context-loading.md` 中的版本，但应增加注释：

```bash
# OpenCode uses OPENCODE_CONFIG_CONTENT to inject workspace instructions and skills.
# Kimi CLI uses --skills-dir for skills; AGENTS.md still needs .kimi/AGENTS.md or symlink.
```

**步骤 3：验证 shell 语法**

运行：

```bash
zsh -n docs/templates/agent-context/agent-context-functions.sh
```

预期：退出码 0，无输出。

## 任务 4：更新项目索引文档

**文件：**
- 修改：`README.md`
- 修改：`AGENTS.md`
- 修改：`CLAUDE.md`

**步骤 1：更新 README 文档列表**

在 `README.md` 的文档列表中补充：

```markdown
- **[docs/templates/agent-context/](./docs/templates/agent-context/)** - 全局、开发、生活、Obsidian 多工作区 agent context 模板和 Kimi/OpenCode wrapper 示例
```

**步骤 2：更新 AGENTS/CLAUDE 项目结构**

如果 `AGENTS.md` 和 `CLAUDE.md` 的项目结构中已有 `docs/` 描述，则补充：

```text
docs/templates/agent-context/ # 多工作区 agent context 模板
```

不得记录本次修改日志，只记录稳定结构事实。

**步骤 3：验证**

运行：

```bash
rg -n "docs/templates/agent-context|多工作区 agent context" README.md AGENTS.md CLAUDE.md
```

预期：至少在 `README.md` 和相关项目文档中出现。

## 任务 5：最终验证和交接

**文件：**
- 检查：全部已修改文件

**步骤 1：路径泄漏检查**

运行：

```bash
rg -n "/Users/|01-Projects|00-Life|myhron-os" docs/agent-context-loading.md docs/plans/2026-04-21-agent-context-workspace-split-design.md docs/plans/2026-04-21-agent-context-workspace-split-implementation.md docs/templates/agent-context README.md AGENTS.md CLAUDE.md || true
```

预期：无输出。

**步骤 2：模板文件检查**

运行：

```bash
find docs/templates/agent-context -maxdepth 1 -type f | sort
zsh -n docs/templates/agent-context/agent-context-functions.sh
```

预期：文件列表完整，shell 语法检查通过。

**步骤 3：Markdown 检查**

运行：

```bash
rg -n "TBD|TODO|稍后实现" docs/agent-context-loading.md docs/plans docs/templates/agent-context README.md AGENTS.md CLAUDE.md || true
```

预期：无输出。

**步骤 4：Git 状态检查**

运行：

```bash
git status --short
git diff --stat
```

预期：只包含本计划相关文档和模板文件。

**步骤 5：不要提交**

除非用户明确要求，不运行 `git commit`。
