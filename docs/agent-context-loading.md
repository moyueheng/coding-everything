# Codex、Claude Code、Kimi CLI 与 OpenCode 的上下文加载机制

本文整理 Codex、Claude Code、Kimi CLI 与 OpenCode 在嵌套目录、多 Git 仓库工作区中的上下文加载机制，覆盖 `AGENTS.md`、`CLAUDE.md` 等指令文件以及 skill 发现方式。目标是为本仓库的跨平台配置、`ce` 安装策略、项目级 rules 设计提供稳定参考。

示例工作区：

```text
workspace/
  a/
    AGENTS.md
    CLAUDE.md
    .agents/skills/
    .claude/skills/
    b/c/
      .git/
      AGENTS.md
      CLAUDE.md

  a1/
    AGENTS.md
    CLAUDE.md
```

在这个例子中，`a` 是大工作区边界，`c` 是嵌套 Git 仓库。不同工具对 `a` 的父级指令和 skill 是否生效并不一致。

## 总览

### 指令文件

| 维度 | Codex `AGENTS.md` | Claude Code `CLAUDE.md` | Kimi CLI `AGENTS.md` | OpenCode `AGENTS.md` |
| --- | --- | --- | --- | --- |
| 向上搜索边界 | 停在项目根 | 从当前目录向上加载父目录 | 停在最近 `.git` | 停在当前 Git worktree |
| 默认根 marker | `.git` | 官方文档未描述为基于 `.git` 截断 | `.git` | `.git` worktree |
| 自定义根 marker | `project_root_markers` | 通常不需要 | 未发现 | 未发现；可用 `instructions` 显式补充 |
| 没有 marker/root 时 | 只看 cwd | 父目录仍可生效 | 只看 work_dir | worktree 为 `/`，可向上到根目录 |
| 同目录覆盖 | `AGENTS.override.md` 优先 | `CLAUDE.local.md` 追加 | `.kimi/AGENTS.md` 可共存 | `AGENTS.md` 优先于 `CLAUDE.md` |
| 大小预算 | 默认 32 KiB，root-first | 建议保持精简 | 32 KiB，leaf-first | 未在本次整理中确认同类预算 |
| Prompt 位置 | user contextual fragment | user message | system prompt variable | system instruction 列表 |

### Skills

| 维度 | Codex | Claude Code | Kimi CLI | OpenCode |
| --- | --- | --- | --- | --- |
| 用户级稳定路径 | `~/.agents/skills` | `~/.claude/skills` | `~/.config/agents/skills`、`~/.agents/skills` | `~/.config/opencode/skills`、`~/.agents/skills`、`~/.claude/skills` |
| 项目级通用路径 | `.agents/skills` | `.claude/skills` | `.agents/skills` | `.opencode/skills`、`.agents/skills`、`.claude/skills` |
| 父级到 cwd 发现 | 是，项目根到 cwd | 支持父级 project boundary 和嵌套发现 | 否，只看 work_dir | 是，但停在 Git worktree |
| 是否被 Git 截断 | 默认会，可配置 | 未描述为基于 Git marker 截断 | skill 不使用 Git-root 链路 | 会，被当前 worktree 截断 |
| 多品牌支持 | generic + Codex roots | Claude roots | Kimi、Claude、Codex、generic roots | OpenCode、Claude、agent-compatible roots |

## Codex

Codex 的 `AGENTS.md` 和 repo-level skills 都使用“项目根到 cwd”的发现方式。默认项目根 marker 是最近的 `.git`。

```text
cwd
  -> 向上查找项目根
  -> 从项目根到 cwd 逐层加载指令文件和 .agents/skills
  -> 不会越过项目根继续向上
```

如果目录是：

```text
a/
  AGENTS.md
  b/c/
    .git/
    AGENTS.md
```

在 `c` 运行 Codex 时，默认只加载：

```text
a/b/c/AGENTS.md
```

不会加载：

```text
a/AGENTS.md
```

原因是 `c/.git` 是距离当前目录最近的项目根 marker。

多仓库工作区推荐在大工作区根目录放空 marker：

```bash
touch /path/to/a/.codex-root
```

然后在 `~/.codex/config.toml` 中配置：

```toml
project_root_markers = [".codex-root"]
```

此时在 `a/b/c` 运行 Codex，会把 `a` 当作项目根，加载：

```text
a/AGENTS.md
a/b/c/AGENTS.md
a/.agents/skills/*/SKILL.md
a/b/c/.agents/skills/*/SKILL.md
```

不推荐在多仓库工作区里写：

```toml
project_root_markers = [".git", ".codex-root"]
```

Codex 会停在最近命中的 marker。如果 `c/.git` 比 `a/.codex-root` 更近，父级 `a/AGENTS.md` 仍然不会生效。

Codex 同目录指令文件优先级：

```text
AGENTS.override.md
AGENTS.md
project_doc_fallback_filenames 中配置的文件
```

同一目录只加载第一个命中的文件。默认项目文档总预算是：

```toml
project_doc_max_bytes = 32768
```

多个文件共享预算，并按 root-to-leaf 顺序读取；父级文件过大可能挤占子级文件预算。

## Claude Code

Claude Code 的 `CLAUDE.md` 行为比 Codex 默认行为更适合“大工作区包含多个 Git 仓库”的场景。官方文档描述的是从当前目录向上加载父目录中的 `CLAUDE.md`，没有描述为会被 `.git` 截断。

目录如下时：

```text
a/
  CLAUDE.md
  b/c/
    .git/
    CLAUDE.md
```

在 `c` 运行 Claude Code 时，可以加载：

```text
a/CLAUDE.md
a/b/c/CLAUDE.md
```

`CLAUDE.local.md` 适合放个人本地补充。一个实用兼容模式是让 `CLAUDE.md` 引用共享源：

```md
@AGENTS.md

## Claude Code

Claude Code 专属补充。
```

Claude Code skill 常用位置：

```text
企业级：托管设置
个人级：~/.claude/skills/<skill-name>/SKILL.md
项目级：.claude/skills/<skill-name>/SKILL.md
插件级：<plugin>/skills/<skill-name>/SKILL.md
```

同名优先级：

```text
enterprise > personal > project
```

Plugin skills 有命名空间，不会和这些层级冲突。若要在互不相关的多个仓库之间共享 skill，最稳定的位置仍是：

```text
~/.claude/skills/<skill-name>/SKILL.md
```

## Kimi CLI

Kimi CLI 的 `AGENTS.md` 项目根是工作目录上方最近的 `.git`。如果没有找到 `.git` marker，只检查当前工作目录。

目录如下时：

```text
a/
  AGENTS.md
  b/c/
    .git/
    AGENTS.md
```

在 `c` 运行 Kimi CLI 时只加载：

```text
a/b/c/AGENTS.md
```

不会加载：

```text
a/AGENTS.md
```

每层目录检查：

```text
.kimi/AGENTS.md
AGENTS.md
agents.md
```

`.kimi/AGENTS.md` 和 `AGENTS.md` 可以同时加载；`AGENTS.md` 与 `agents.md` 互斥，且 `AGENTS.md` 优先。Kimi CLI 使用 32 KiB 预算，按 leaf-first 保留更深层文件，父级文件可能被截断。

Kimi CLI skill roots：

```text
内置 skills

用户级品牌目录：
  ~/.kimi/skills/
  ~/.claude/skills/
  ~/.codex/skills/

用户级通用目录：
  ~/.config/agents/skills/
  ~/.agents/skills/

项目级品牌目录：
  .kimi/skills/
  .claude/skills/
  .codex/skills/

项目级通用目录：
  .agents/skills/
```

项目级路径相对于当前 `work_dir` 解析。因此在 `a/b/c` 运行 Kimi CLI 时，只检查 `c` 下的项目级 skill 目录，不会自动发现 `a/.agents/skills`。

跨仓库共享 Kimi skills，优先使用：

```text
~/.config/agents/skills/<skill-name>/SKILL.md
~/.agents/skills/<skill-name>/SKILL.md
```

也可以用：

```bash
kimi --skills-dir /path/to/my-skills --skills-dir /path/to/more-skills
```

注意：`--skills-dir` 会覆盖默认 user/project discovery，但 built-in skills 仍可用。如果还需要当前仓库自己的 skills，要把当前仓库 skill 目录也显式传入。

`--add-dir` 只扩大文件工具可访问的 workspace scope，不会让父级 `AGENTS.md` 自动进入 Kimi 的 `${KIMI_AGENTS_MD}`。

## OpenCode

OpenCode 的项目边界来自当前 Git worktree：

```text
cwd
  -> 向上找最近的 .git
  -> 用 git rev-parse --show-toplevel 计算 worktree/sandbox
```

本地指令文件从当前目录向上查找，但停止在当前项目的 `worktree`。同一路径上检查：

```text
AGENTS.md
CLAUDE.md
CONTEXT.md
```

`CONTEXT.md` 已 deprecated。`AGENTS.md` 优先于 `CLAUDE.md`；只要当前目录到 worktree 之间找到一个或多个 `AGENTS.md`，就不会继续使用 `CLAUDE.md` 作为本地 fallback。

目录如下时：

```text
a/
  AGENTS.md
  b/c/
    .git/
    AGENTS.md
```

在 `c` 运行 OpenCode，只会加载：

```text
a/b/c/AGENTS.md
```

不会加载：

```text
a/AGENTS.md
```

如果 `c` 不是 Git 仓库，OpenCode 的 project worktree 会是 `/`，从 `c` 向上查找可以经过 `a`。

OpenCode 全局指令文件：

```text
~/.config/opencode/AGENTS.md
~/.claude/CLAUDE.md
```

全局层级中，`~/.config/opencode/AGENTS.md` 优先；如果它存在，就不会使用 `~/.claude/CLAUDE.md` 作为全局 fallback。

OpenCode 也支持在 `opencode.json` 中显式配置额外指令文件：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["CONTRIBUTING.md", "docs/guidelines.md", "packages/*/AGENTS.md"]
}
```

OpenCode project-level skill 目录：

```text
.opencode/skills/<skill-name>/SKILL.md
.opencode/skill/<skill-name>/SKILL.md
.claude/skills/<skill-name>/SKILL.md
.agents/skills/<skill-name>/SKILL.md
```

其中 `.opencode/skill` 是源码仍支持的单数目录；官方文档主要写 `.opencode/skills`。

用户级目录：

```text
~/.config/opencode/skills/<skill-name>/SKILL.md
~/.claude/skills/<skill-name>/SKILL.md
~/.agents/skills/<skill-name>/SKILL.md
```

也可以通过 `opencode.json` 配置额外 skill paths 或远程 skill URLs：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "skills": {
    "paths": ["../shared-skills"],
    "urls": ["https://example.com/.well-known/skills/"]
  }
}
```

如果 `c` 是 Git 仓库，父级 `a` 下的 `.opencode/skills` 和 `.agents/skills` 会被当前 Git worktree 截断。需要共享时，优先使用用户级目录，或在子仓库 `opencode.json` 中显式配置绝对路径。

## 手动注入与 Alias 方案

如果 `a` 是开发大工作区，下面有多个 Git 仓库：

```text
~/workspace/a/
  .codex-root
  AGENTS.md
  CLAUDE.md
  .agents/skills/
  .claude/skills/
  .opencode/skills/

  repo1/.git/
  repo2/.git/
  group/repo3/.git/
```

目标是在子仓库中启动工具时继承 `a/AGENTS.md` 和共享 skills。Codex 优先用 `.codex-root` 解决；Kimi CLI 和 OpenCode 在嵌套 Git 仓库中需要启动参数或本地薄文件补齐。

### OpenCode function

OpenCode 支持 `OPENCODE_CONFIG_CONTENT`，适合用 shell function 显式注入：

```bash
export DEV_AI_ROOT="$HOME/workspace/a"

oca() {
  local root="${DEV_AI_ROOT:?DEV_AI_ROOT is not set}"
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
```

用法：

```bash
cd ~/workspace/a/repo1
oca
oca run "帮我检查这个仓库"
```

这个方案不依赖 OpenCode 的 upward discovery，而是显式传入绝对路径，所以不会被 `repo1/.git` 截断。

实际效果：

```text
repo1/.git
  不再阻止 OpenCode 读取 a/AGENTS.md
  不再阻止 OpenCode 发现 a/.agents/skills
  不再阻止 OpenCode 发现 a/.opencode/skills
```

### Kimi CLI function

Kimi CLI 可以通过 `--skills-dir` 注入父级 skills：

```bash
export DEV_AI_ROOT="$HOME/workspace/a"

kimia() {
  local root="${DEV_AI_ROOT:?DEV_AI_ROOT is not set}"
  local args=()

  args+=(--add-dir "$root")
  args+=(--skills-dir "$root/.agents/skills")

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
```

这个方案可以加载父级 `a/.agents/skills`，也能把当前仓库存在的 skill 目录补回。但它不能自动把 `a/AGENTS.md` 合并进 `${KIMI_AGENTS_MD}`。

本次检查的 Kimi CLI 启动参数中，没有发现等价于下面形式的参数：

```bash
kimi --instructions /path/to/AGENTS.md
kimi --agents-md /path/to/AGENTS.md
```

Kimi CLI 共享父级 `AGENTS.md` 的稳定做法是在每个仓库放一个很薄的 `.kimi/AGENTS.md`：

```text
repo1/
  .kimi/AGENTS.md
```

内容：

```md
请先读取并遵守：

$DEV_AI_ROOT/AGENTS.md
```

也可以使用 symlink：

```bash
mkdir -p .kimi
ln -s "$DEV_AI_ROOT/AGENTS.md" .kimi/AGENTS.md
```

如果不想改每个仓库，也可以用启动 prompt 做轻量补齐：

```bash
kimia-start() {
  local root="${DEV_AI_ROOT:?DEV_AI_ROOT is not set}"
  kimia --prompt "开始前请读取并遵守 $root/AGENTS.md。之后等待我的下一步指令。"
}
```

这个方式轻量，但稳定性低于 `.kimi/AGENTS.md` 或 symlink，因为它依赖模型在启动回合主动读取文件。

### 多工作区分层示例

如果要拆分开发、生活和 Obsidian vault 上下文，可以使用三个工作区 root。下面使用可迁移的 `$HOME` 路径；实际目录名可按个人机器调整。

```text
$HOME/
  .codex/AGENTS.md                 # 只放跨场景全局规则

  <projects-dir>/
    .codex-root
    AGENTS.md                      # 代码开发通用规则
    CLAUDE.md                      # @AGENTS.md
    .agents/skills/                # 可选：dev-* 工作区级 skills
    .claude/skills/                # 可选：Claude Code 工作区级 skills
    .opencode/skills/              # 可选：OpenCode 工作区级 skills

  <life-dir>/
    .codex-root
    AGENTS.md                      # 生活、研究、写作、知识管理通用规则
    CLAUDE.md                      # @AGENTS.md
    .agents/skills/                # 可选：life-* / work-* / learn-* 工作区级 skills

    <obsidian-vault>/
      AGENTS.md                    # Obsidian vault 专属规则
      CLAUDE.md
      .agents/skills/              # Obsidian 专用 skills
      .claude/skills/
```

对应 shell function 可以按 root 拆三套：

```bash
export PROJECTS_AI_ROOT="$HOME/<projects-dir>"
export LIFE_AI_ROOT="$HOME/<life-dir>"
export OBSIDIAN_AI_ROOT="$LIFE_AI_ROOT/<obsidian-vault>"
```

OpenCode：

```bash
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

Kimi CLI：

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

Kimi 的 `AGENTS.md` 仍建议用 repo-local `.kimi/AGENTS.md` symlink 补齐：

```bash
mkdir -p .kimi
ln -s "$PROJECTS_AI_ROOT/AGENTS.md" .kimi/AGENTS.md
```

如果当前目录是 Obsidian vault，则链接到：

```bash
ln -s "$OBSIDIAN_AI_ROOT/AGENTS.md" .kimi/AGENTS.md
```

## 推荐实践

只考虑 Codex 的多仓库工作区：

```text
a/
  .codex-root
  AGENTS.md
  .agents/skills/shared-dev/SKILL.md

  repo1/
    .git/
    AGENTS.md
    .agents/skills/repo1-specific/SKILL.md
```

配置：

```toml
project_root_markers = [".codex-root"]
```

同时支持 Codex、Claude Code 和 OpenCode：

```text
a/
  .codex-root
  AGENTS.md
  CLAUDE.md
  .agents/skills/
  .claude/skills/
  .opencode/skills/
```

`CLAUDE.md` 可以用 `@AGENTS.md` 复用共享指令源。

如果要在多个仓库和多个工具之间稳定共享 skills，优先使用用户级位置：

```text
~/.agents/skills/<skill-name>/SKILL.md
~/.claude/skills/<skill-name>/SKILL.md
~/.config/agents/skills/<skill-name>/SKILL.md
~/.config/opencode/skills/<skill-name>/SKILL.md
```

如果希望单一来源供多个工具使用，可以用 symlink 或同步脚本分发到各工具对应的位置。

如果希望把 `a` 当作“开发大目录”，并让下面多个 Git 仓库尽量继承 `a` 的规范，推荐组合是：

```text
a/
  .codex-root
  AGENTS.md
  CLAUDE.md
  .agents/skills/
  .claude/skills/
  .opencode/skills/

  repo1/
    .git/
    .kimi/AGENTS.md -> <workspace-root>/AGENTS.md
```

工具侧做法：

```text
Codex
  用 .codex-root + project_root_markers

Claude Code
  用 CLAUDE.md 引用 AGENTS.md，并使用 a/.claude/skills

OpenCode
  用 oca/ocp/ocl/oco function，通过 OPENCODE_CONFIG_CONTENT 注入 a/AGENTS.md 和 a 下 skills

Kimi CLI
  用 kimia/kimip/kimil/kimio function 注入 --skills-dir
  用 repo-local .kimi/AGENTS.md 或 symlink 补齐 a/AGENTS.md
```

## 关键结论

- Codex `AGENTS.md` 和 repo skills 都使用 project-root-to-cwd discovery。
- Codex 默认使用 `.git`，嵌套 Git 仓库会遮蔽父级工作区规则；可用 `.codex-root` 和 `project_root_markers` 修正。
- `.codex-root` 可以是空 marker 文件。
- Claude Code `CLAUDE.md` 的父目录加载比 Codex 默认 `AGENTS.md` 更宽。
- Kimi CLI `AGENTS.md` 停在最近的 `.git`，本次整理未发现可配置 root marker。
- OpenCode `AGENTS.md` 会从 cwd 向上找，但停在当前 Git worktree；`AGENTS.md` 优先于 `CLAUDE.md`。
- Codex 使用 `.codex-root` 后，skills 可以从父级工作区继承。
- Claude Code 可以发现父级 project boundary 的 `.claude/skills`；互不相关仓库之间共享时，`~/.claude/skills` 更稳定。
- Kimi CLI skills 跨仓库共享的稳定位置是 `~/.config/agents/skills` 或 `~/.agents/skills`。
- OpenCode project-level skills 会被当前 Git worktree 截断；可用 `OPENCODE_CONFIG_CONTENT` 或 `opencode.json` 显式注入父级指令和 skills。
- Kimi CLI `--skills-dir` 可以注入父级 skills，但会覆盖默认 discovery；需要当前仓库自己的 skills 时也要一起传入。
- Kimi CLI `--add-dir` 只扩大工具可访问目录，不会让父级 `AGENTS.md` 自动并入 `${KIMI_AGENTS_MD}`。
- Kimi CLI 未发现 `--instructions` 或 `--agents-md` 这类直接注入父级 `AGENTS.md` 的启动参数；要用 `.kimi/AGENTS.md`、symlink 或启动 prompt 补齐。
- OpenCode 的 alias/function 方案可以同时注入 `instructions` 和 `skills.paths`，是多 Git 仓库工作区下最干净的手动继承方案。
- 推荐把 `AGENTS.md` 作为共享指令源，并在 `CLAUDE.md` 中通过 `@AGENTS.md` 引用。
