# Agent Context Workspace Split Design

## 背景

当前开发相关规则和 `dev-*` skills 主要放在用户全局层。这样能解决多 Git 仓库中 skill 可见性问题，但也会把开发规则带入生活、写作、研究、Obsidian vault 等非开发场景。

目标是把规则按目录边界拆开，同时保留跨工具可用性：

```text
global user context
  -> only stable personal defaults

projects workspace
  -> coding rules and dev workflow

life workspace
  -> notes, research, writing, personal workflows

obsidian vault
  -> Obsidian-specific rules and skills
```

## 设计目标

- 全局 `AGENTS.md` 只保留跨场景稳定规则，例如语言、署名、工具优先、环境默认值、git 不自动提交。
- 开发规则迁移到 projects workspace，例如测试、架构边界、文档同步、`dev-*` skill 使用边界。
- 生活/知识管理规则迁移到 life workspace。
- Obsidian vault 规则保留在 vault 根目录，并加载 Obsidian 专属 skills。
- Codex、Claude Code、Kimi CLI、OpenCode 都有明确的继承或注入路径。
- 文档和示例必须使用可迁移路径，避免写死个人绝对路径。

## 推荐结构

```text
$HOME/
  .codex/
    AGENTS.md

  <projects-dir>/
    .codex-root
    AGENTS.md
    CLAUDE.md
    .agents/skills/
    .claude/skills/
    .opencode/skills/

  <life-dir>/
    .codex-root
    AGENTS.md
    CLAUDE.md
    .agents/skills/

    <obsidian-vault>/
      AGENTS.md
      CLAUDE.md
      .agents/skills/
      .claude/skills/
```

`<projects-dir>`、`<life-dir>`、`<obsidian-vault>` 是用户本机路径占位符。开源文档和脚本模板只使用 `$HOME`、环境变量或占位符，不使用个人绝对路径。

## 工具策略

### Codex

Codex 使用 `.codex-root` 修正嵌套 Git 仓库的父级继承边界。

```toml
project_root_markers = [".codex-root"]
```

在 `<projects-dir>/<repo>` 中启动 Codex 时，应加载：

```text
<projects-dir>/AGENTS.md
<projects-dir>/<repo>/AGENTS.md
<projects-dir>/.agents/skills/*
<projects-dir>/<repo>/.agents/skills/*
```

在 `<life-dir>/<obsidian-vault>` 中启动 Codex 时，应加载：

```text
<life-dir>/AGENTS.md
<life-dir>/<obsidian-vault>/AGENTS.md
```

### Claude Code

Claude Code 继续使用 `CLAUDE.md`。工作区级 `CLAUDE.md` 推荐引用同目录 `AGENTS.md`：

```md
@AGENTS.md

## Claude Code

Claude Code 专属补充。
```

Claude Code 的 skills 可放在：

```text
<workspace-root>/.claude/skills/
~/.claude/skills/
```

### OpenCode

OpenCode 在嵌套 Git 仓库中会被当前 Git worktree 截断。推荐通过 shell function 注入工作区规则和 skills。

```bash
export PROJECTS_AI_ROOT="$HOME/<projects-dir>"
export LIFE_AI_ROOT="$HOME/<life-dir>"
export OBSIDIAN_AI_ROOT="$LIFE_AI_ROOT/<obsidian-vault>"

_oc_with_root() {
  local root="${1:?root is required}"
  shift
  local cfg

  cfg="$(jq -nc \
    --arg agents "$root/AGENTS.md" \
    --arg agents_skills "$root/.agents/skills" \
    --arg opencode_skills "$root/.opencode/skills" \
    '{
      "$schema": "https://opencode.ai/config.json",
      "instructions": [$agents],
      "skills": {
        "paths": [$agents_skills, $opencode_skills]
      }
    }')"

  OPENCODE_CONFIG_CONTENT="$cfg" opencode "$@"
}

ocp() { _oc_with_root "$PROJECTS_AI_ROOT" "$@"; }
ocl() { _oc_with_root "$LIFE_AI_ROOT" "$@"; }
oco() { _oc_with_root "$OBSIDIAN_AI_ROOT" "$@"; }
```

### Kimi CLI

Kimi CLI 可用 `--skills-dir` 注入父级 skills，但没有直接注入父级 `AGENTS.md` 的启动参数。推荐组合：

- 用 wrapper 注入 `--skills-dir`。
- 用 repo-local `.kimi/AGENTS.md` 或 symlink 补齐父级 `AGENTS.md`。
- 只在不能修改仓库时使用启动 prompt 作为轻量补齐。

```bash
_kimi_with_root() {
  local root="${1:?root is required}"
  shift
  local args=()

  args+=(--add-dir "$root")
  [ -d "$root/.agents/skills" ] && args+=(--skills-dir "$root/.agents/skills")
  [ -d "$root/.claude/skills" ] && args+=(--skills-dir "$root/.claude/skills")
  [ -d "$root/.codex/skills" ] && args+=(--skills-dir "$root/.codex/skills")

  for d in \
    "$PWD/.kimi/skills" \
    "$PWD/.claude/skills" \
    "$PWD/.codex/skills" \
    "$PWD/.agents/skills"
  do
    [ -d "$d" ] && args+=(--skills-dir "$d")
  done

  kimi "${args[@]}" "$@"
}

kimip() { _kimi_with_root "$PROJECTS_AI_ROOT" "$@"; }
kimil() { _kimi_with_root "$LIFE_AI_ROOT" "$@"; }
kimio() { _kimi_with_root "$OBSIDIAN_AI_ROOT" "$@"; }
```

Kimi 的父级规则补齐：

```bash
mkdir -p .kimi
ln -s "$PROJECTS_AI_ROOT/AGENTS.md" .kimi/AGENTS.md
```

Obsidian vault 使用：

```bash
mkdir -p .kimi
ln -s "$OBSIDIAN_AI_ROOT/AGENTS.md" .kimi/AGENTS.md
```

## 规则分层

全局层只保留跨场景稳定规则：

- 回复语言和署名约束。
- 不确定时使用工具检索或询问。
- Python 使用 `uv`，Node 使用 `fnm`。
- 除非用户主动要求，否则不提交 commit。

Projects 层承载开发规则：

- 代码修改前先检索已有实现。
- 禁止引入新的重型框架。
- 禁止跨模块隐式耦合。
- 测试、验证、文档同步和 `dev-*` skill 使用边界。

Life 层承载非开发工作流：

- 生活、研究、写作、知识管理默认规则。
- 避免强制开发 workflow 污染非代码任务。

Obsidian vault 层承载 vault 专属规则：

- Obsidian Markdown、wikilink、frontmatter、Bases、Canvas、vault 目录约定。
- Obsidian 专属 skills 只安装到 vault 的 `.agents/skills` 和 `.claude/skills`。

## 落地顺序

1. 更新文档：在 `docs/agent-context-loading.md` 固化跨工具加载机制和 alias 方案。
2. 设计 shell snippet 模板：提供 OpenCode 和 Kimi wrapper，不写死个人路径。
3. 拆分全局规则：把开发规则从用户全局 `AGENTS.md` 迁移到 projects workspace 模板。
4. 增加 `.codex-root` 说明：推荐 projects 和 life 两类大目录各自放 marker。
5. 可选自动化：后续由 `ce` CLI 或 setup skill 生成 wrapper snippet 和 workspace template。

## 风险与约束

- Kimi CLI 的父级 `AGENTS.md` 无法仅靠启动参数完整继承，需要 `.kimi/AGENTS.md`、symlink 或启动 prompt 补齐。
- OpenCode 可通过 `OPENCODE_CONFIG_CONTENT` 干净注入，但依赖 `jq` 构造 JSON。
- 全局 skills 保留过多时，仍可能增加可用 skill 列表噪音；规则层应明确不同场景下的触发边界。
- `.codex-root` 配置应避免与 `.git` 同时作为等价 marker，否则嵌套 Git 仓库仍可能遮蔽父级规则。

## 验收标准

- 文档中所有示例路径均为 `$HOME`、环境变量或占位符，不含个人绝对路径。
- `docs/agent-context-loading.md` 明确记录 Codex、Kimi CLI、OpenCode 的继承差异和补救方式。
- 设计支持开发、生活、Obsidian 三类上下文隔离。
- 后续实现可以在不改源码架构的前提下，以文档、模板、setup 脚本逐步落地。
