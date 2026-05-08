# AGENTS.md Pattern

## 核心判断

AGENTS.md 是给 coding agent 看的项目级操作手册，不是给人看的 README。它应该降低猜测，而不是增加额外仪式。

2026 年的公开资料给出两个相互补充的结论：

- AGENTS.md 已成为常见的跨工具项目说明文件；根目录示例通常包含开发环境提示、测试命令和 PR 要求。
- 研究结果提醒：上下文文件会被 agent 遵守，但无关要求会增加探索、token 成本和失败率；只写最小必要规则。

## 推荐结构

```markdown
# AGENTS.md

## Scope

- This file applies to this directory and all children unless a nested AGENTS.md overrides it.
- Nested files inherit parent rules and only add local differences.

## Project Map

- `src/`: ...
- `tests/`: ...
- `docs/`: ...

## Commands

- Install: `...`
- Format: `...`
- Lint: `...`
- Typecheck: `...`
- Test: `...`
- Build: `...`

## Working Rules

- Search existing code before adding new helpers or dependencies.
- Keep diffs scoped to the user request.
- Add or update tests for behavior changes.

## Local Conventions

- ...

## Safety

- Ask before installing new dependencies, deleting large trees, changing migrations, pushing, or touching production data.

## Done

- Run the smallest relevant checks first.
- Run broader checks before handing off if the change crosses module boundaries.
- Update stable project docs when directory structure, workflow, commands, or architecture change.
```

## 子目录模板

```markdown
# AGENTS.md

## Scope

This file applies to `path/to/subtree/`. It inherits parent AGENTS.md rules and only records local differences.

## Local Map

- `...`: ...

## Commands

- Test this package: `...`

## Local Rules

- ...
```

## 多级目录放置策略

```text
repo/
├── AGENTS.md                  # 全局约束、通用命令、仓库地图
├── CLAUDE.md -> AGENTS.md
├── apps/web/
│   ├── AGENTS.md              # 前端特有命令和 UI 约定
│   └── CLAUDE.md -> AGENTS.md
├── packages/api/
│   ├── AGENTS.md              # API/DB/测试边界
│   └── CLAUDE.md -> AGENTS.md
└── docs/                      # 无独立规则则不放
```

## 高价值内容

- 文件级验证命令，而不是只给全量 build
- 真实入口路径，例如 router、API client、schema、design tokens、test fixtures
- 明确禁止事项及替代做法
- 好示例和反例文件路径
- 何时必须询问用户

## 删除或避免

- 已经由 formatter/linter 强制的规则
- 与父级重复的段落
- 不会影响行为的口号
- 临时任务记录
- 未验证的工具版本或命令

## 参考来源

- https://github.com/agentsmd/agents.md
- https://github.com/openai/codex/blob/main/docs/agents_md.md
- https://www.builder.io/c/docs/ai-instruction-best-practices
- https://arxiv.org/abs/2602.11988
- https://arxiv.org/abs/2601.20404
