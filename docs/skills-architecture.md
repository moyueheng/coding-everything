# 共享 Skills 架构全景图

本文档描述 `coding-everything` 中跨平台共享 skills 的分层、安装流、调用流和当前清单。当前事实来源以仓库中的 `skills/`、`.agents/skills/`、`install_skills/`、`mcp-configs/required.json` 为准。

---

## 目录

- [仓库分层](#仓库分层)
- [安装与运行时流向](#安装与运行时流向)
- [Skill 调用关系](#skill-调用关系)
- [核心原则与反模式](#核心原则与反模式)
- [Skill 清单](#skill-清单)
- [来源映射](#来源映射)

---

## 仓库分层

当前仓库把“可复用能力”和“平台适配”分开维护：

```text
coding-everything/
├── skills/                 # 46 个跨平台共享 skill，均含 SKILL.md
│   ├── dev-*               # 开发流程、架构、测试、样式、MCP 等
│   ├── obsidian-*          # Obsidian vault 编辑与结构化文件
│   ├── life-*              # OrbitOS 迁移来的个人工作流
│   ├── work-*              # PM / 市场 / 用户故事类工作流
│   ├── learn-*             # 深度研究与 LLM Wiki
│   └── tool-*              # 独立工具类 skill
├── .agents/skills/         # 3 个系统级 skill
│   ├── setup/
│   ├── update-upstream-repos/
│   └── dev-creating-subagents/
├── install_skills/         # ce CLI：安装、更新、卸载、状态、同步
├── mcp-configs/            # global 组安装时合并到 ~/.claude.json 的 MCP 模板
├── kimi/                   # Kimi 专属 agent/config
├── opencode/               # OpenCode 配置占位
└── upstream/               # 作为 submodule 跟踪的上游仓库
```

### 逻辑分层

```text
┌──────────────────────────────────────────────────────────────────────┐
│ 第零层：入口与规则                                                   │
│ dev-using-skills                                                     │
│ - 先检查适用 skill，再响应或行动                                      │
│ - 优先级：用户请求 > AGENTS/CLAUDE > skill > 默认行为                 │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 设计与计划层                                                         │
│ dev-brainstorming → dev-writing-plans                                │
│ - 新功能先澄清需求和方案                                             │
│ - 计划拆成可验证的小任务                                             │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 执行与验证层                                                         │
│ dev-executing-plans / dev-tdd / dev-debugging / dev-verification      │
│ dev-requesting-review / dev-finishing-branch / dev-git-worktrees      │
│ - 写代码走 TDD，修 bug 先定位根因                                    │
│ - 声称完成前必须有新鲜验证证据                                       │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 开发实现层                                                           │
│ dev-backend-patterns / dev-frontend-patterns / dev-design-system      │
│ dev-ui-styling / dev-e2e-testing / dev-mcp-patterns                   │
│ dev-code-cleanup / dev-update-codemaps / dev-search-first             │
│ dev-continuous-agent-loop / dev-writing-skills                        │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 领域工作流层                                                         │
│ obsidian-* / json-canvas / defuddle / life-* / learn-* / work-*       │
│ tool-humanizer-zh / tool-macos-hidpi / agent-browser                  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 安装与运行时流向

`ce` CLI 由 `install_skills/` 实现。当前推荐路径是先运行 `ce init`，生成用户级配置，再按配置安装。

```text
ce init
  │
  ├─ 扫描 repo/skills/*/SKILL.md
  ├─ 将 Obsidian 相关 skill 分到 obsidian 组
  └─ 写入 ~/.ce/config.yaml

~/.ce/config.yaml
  │
  ▼
ce install / update / sync / status / uninstall [--group NAME]
  │
  ├─ global 组
  │   ├─ symlink skill 到 ~/.agents/skills/
  │   ├─ symlink skill 到 ~/.claude/skills/
  │   ├─ symlink kimi/agents/superpower 到 ~/.kimi/agents/superpower
  │   ├─ symlink ks 到 ~/.local/bin/ks
  │   └─ 合并 mcp-configs/required.json 到 ~/.claude.json
  │
  ├─ obsidian 组
  │   ├─ symlink skill 到 <vault>/.claude/skills/
  │   └─ symlink skill 到 <vault>/.agents/skills/
  │
  └─ 写入 ~/.ce/install-manifest.json
```

配置模式：

| 模式 | 触发条件 | 配置来源 | 说明 |
|------|----------|----------|------|
| UserConfig | `~/.ce/config.yaml` 存在 | `ce init` 生成，可用 `ce add-skill` / `ce add-target` 修改 | 当前推荐模式 |
| Legacy grouped | `~/.ce/config.yaml` 不存在且仓库根存在 `skills-install.yaml` | 仓库级 YAML | 兼容旧实现；当前工作区根目录没有该文件 |
| Legacy flat | 前两者都不存在 | 自动发现全部 `skills/` | 无分组回退模式 |

`ce init` 的 Obsidian 组分类规则在 `install_skills/cli.py`：

| 规则 | 当前内容 |
|------|----------|
| 前缀 / 名称匹配 | `obsidian-*`、`defuddle`、`json-canvas` |
| 显式归入 Obsidian | `learn-llm-wiki`、`life-ai-newsletters`、`life-ai-products`、`life-ask`、`life-parse-knowledge`、`life-start-my-day` |
| 其余 | 归入 `global` 组 |

global 组额外管理 MCP。`mcp-configs/required.json` 当前包含 `auggie-mcp`、`zai-github-read`、`zai-web-reader`、`zai-web-search-prime`、`context7` 等模板；ZAI 相关配置依赖已有 `~/.claude.json` 或环境变量中的 `ZAI_API_KEY`。

---

## Skill 调用关系

### 典型开发工作流

```text
用户需求
  │
  ▼
dev-using-skills
  │
  ▼
dev-brainstorming
  │  设计文档与设计审查
  ▼
dev-writing-plans
  │  实施计划与分段审查
  ▼
dev-executing-plans
  │
  ├─ 涉及代码：dev-tdd
  ├─ 遇到异常：dev-debugging
  ├─ 需要隔离：dev-git-worktrees
  └─ 批次审查：dev-requesting-review
  │
  ▼
dev-verification
  │
  ▼
dev-finishing-branch
```

### 调试工作流

```text
Bug / 测试失败
  │
  ▼
dev-debugging
  ├─ 阶段 1：根本原因调查
  ├─ 阶段 2：模式分析
  ├─ 阶段 3：假设和最小验证
  └─ 阶段 4：调用 dev-tdd 实现修复
  │
  ▼
dev-verification
```

### TDD 核心循环

```text
RED: 写一个失败测试
  │
  ▼
验证 RED：确认失败原因正确
  │
  ▼
GREEN：写最小实现
  │
  ▼
验证 GREEN：测试通过
  │
  ▼
REFACTOR：保持绿色的前提下清理
```

---

## 核心原则与反模式

### 严格型流程

| Skill | 不可绕过的点 |
|-------|--------------|
| `dev-using-skills` | 即使只有 1% 可能适用，也先检查相关 skill |
| `dev-brainstorming` | 新功能先设计和审查，未获批准不写代码 |
| `dev-writing-plans` | 实施计划要小步、可验证，并说明验证方式 |
| `dev-executing-plans` | 按计划执行，遇到阻塞要停下来处理阻塞 |
| `dev-tdd` | 没有先失败的测试，就不写生产代码 |
| `dev-debugging` | 没有完成根因调查，就不直接修 |
| `dev-verification` | 没有新鲜验证证据，就不声称完成 |

### 常见反模式

| 反模式 | 正确做法 |
|--------|----------|
| “先看一下代码再说” | 先检查适用 skill，再检索代码 |
| “这个很简单，不用流程” | 简单任务也要先判断适用流程 |
| “先写完再补测试” | 用 TDD 先写失败测试 |
| “应该有效” | 运行验证命令并读取输出 |
| “找到相似方案就直接照抄” | 用 `dev-search-first` 做 Adopt / Extend / Build 判断 |

---

## Skill 清单

### 流程型与开发型

| Skill | 类型 | 作用 |
|-------|------|------|
| `dev-using-skills` | 严格 | skill 入口、指令优先级与触发规则 |
| `dev-brainstorming` | 严格 | 编码前设计、澄清和方案收敛 |
| `dev-writing-plans` | 严格 | 编写可执行实施计划 |
| `dev-executing-plans` | 严格 | 执行书面计划 |
| `dev-tdd` | 严格 | 测试驱动开发 |
| `dev-debugging` | 严格 | 系统化调试 |
| `dev-verification` | 严格 | 完成前验证 |
| `dev-requesting-review` | 严格 | 审查请求与问题修复 |
| `dev-finishing-branch` | 严格 | 分支完成、合并或清理 |
| `dev-git-worktrees` | 严格 | 隔离工作区 |
| `dev-writing-skills` | 严格 | 编写和验证新 skill |
| `dev-code-cleanup` | 严格 | 清理死代码、未用依赖和重复代码 |
| `dev-search-first` | 严格 | 编码前检索现有实现和外部方案 |
| `dev-backend-patterns` | 灵活 | 后端架构与 API 模式 |
| `dev-frontend-patterns` | 灵活 | React / Next.js / 状态管理模式 |
| `dev-design-system` | 灵活 | 设计 token、语义颜色、组件状态 |
| `dev-ui-styling` | 灵活 | UI 样式、响应式、可访问性 |
| `dev-continuous-agent-loop` | 灵活 | 长时间自治执行和质量门 |
| `dev-e2e-testing` | 灵活 | Playwright Python 端到端测试 |
| `dev-mcp-patterns` | 灵活 | Node/TypeScript MCP server 开发 |
| `dev-update-codemaps` | 灵活 | 生成 token-lean 架构索引 |

### 领域与工具型

| Skill | 分组倾向 | 作用 |
|-------|----------|------|
| `agent-browser` | global | 浏览器自动化 CLI、表单、截图、抓取 |
| `defuddle` | obsidian | 网页提取为干净 markdown |
| `json-canvas` | obsidian | JSON Canvas 文件创建和编辑 |
| `obsidian-markdown` | obsidian | Obsidian Flavored Markdown |
| `obsidian-bases` | obsidian | Obsidian Bases 语法 |
| `obsidian-cli` | obsidian | Obsidian CLI 与 vault 交互 |
| `learn-deep-research` | global | 正式研究报告与证据追踪 |
| `learn-llm-wiki` | obsidian | Karpathy 风格 LLM Wiki 构建与维护 |
| `life-start-my-day` | obsidian | OrbitOS 日启动工作流 |
| `life-kickoff` | global | 将想法转为项目笔记 |
| `life-research` | global | Obsidian 研究工作流 |
| `life-brainstorm` | global | 交互式头脑风暴 |
| `life-ask` | obsidian | Vault 问答工作流 |
| `life-parse-knowledge` | obsidian | 知识解析与归档 |
| `life-archive` | global | 归档完成项目和收件箱项 |
| `life-ai-newsletters` | obsidian | AI newsletter 处理 |
| `life-ai-products` | obsidian | AI 产品信息处理 |
| `work-market-research` | global | 市场规模、竞品和进入策略 |
| `work-jobs-to-be-done` | global | JTBD 结构化分析 |
| `work-problem-statement` | global | 问题陈述 |
| `work-user-story` | global | 用户故事与验收标准 |
| `work-user-story-mapping` | global | 用户故事地图 |
| `work-user-story-splitting` | global | 大故事拆分 |
| `tool-humanizer-zh` | global | 中文 AI 写作去痕 |
| `tool-macos-hidpi` | global | macOS HiDPI 分辨率配置 |

系统级 `.agents/skills/`：

| Skill | 作用 |
|-------|------|
| `setup` | 安装本项目共享 skills、Kimi agent、`ks` 和 MCP 配置 |
| `update-upstream-repos` | 更新上游 submodule 并生成更新报告 |
| `dev-creating-subagents` | Kimi CLI / Codex subagent 创建与管理 |

---

## 来源映射

| 本地 skill / 模块 | 来源 | 维护方式 |
|-------------------|------|----------|
| `dev-*` 核心流程 | `upstream/superpowers` 为主要参考 | 本地适配为 `dev-` 前缀，按项目规则维护 |
| `dev-search-first`、`work-market-research` | `upstream/everything-claude-code` | 吸收 workflow 后本地化 |
| `obsidian-markdown`、`obsidian-bases`、`json-canvas`、`obsidian-cli`、`defuddle` | `upstream/obsidian-skills` | 迁移到 `skills/`，各目录用 `UPSTREAM.md` 跟踪 |
| `life-*` | `upstream/orbitos` | 迁移 OrbitOS workflow 并按本地 vault 约束适配 |
| `learn-llm-wiki` | `upstream/karpathy-llm-wiki` | 迁移 Karpathy 风格 LLM Wiki workflow |
| `tool-humanizer-zh` | `upstream/humanizer-zh` | 本地工具型 skill |
| `agent-browser` | `vercel-labs/agent-browser/skills/agent-browser` | 通过 `scripts/sync-agent-browser-skill.sh` 单独镜像 |

---

## 总结

| 设计原则 | 当前落点 |
|----------|----------|
| 共享能力与平台适配分离 | `skills/` 放跨平台 skill，`kimi/` / `opencode/` 放平台配置 |
| 安装配置用户化 | `~/.ce/config.yaml` 优先，manifest 记录真实安装项 |
| 分组隔离 | global 与 obsidian 组可独立安装、更新、卸载、同步 |
| 可验证工作流 | 开发、调试、清理、完成前都绑定验证门 |
| 上游可追踪 | submodule、`UPSTREAM.md`、同步脚本记录来源 |

---

*文档更新时间: 2026-04-20*
*对应 skill 目录: `skills/` 46 个共享 skill，`.agents/skills/` 3 个系统级 skill*
