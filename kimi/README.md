# Kimi Configuration

基于 [superpowers](https://github.com/obra/superpowers) 框架的 Kimi Code CLI 配置。

## 目录

- [快速开始](#快速开始)
  - [使用 ce 命令（推荐）](#使用-ce-命令推荐)
  - [直接使用 ks](#直接使用-ks)
- [包含内容](#包含内容)
  - [Skills (24 个)](#skills-24-个)
  - [Agent](#agent)
- [测试](#测试)
- [安装路径](#安装路径)
- [使用方法](#使用方法)
  - [方式1: 使用 ks（推荐）](#方式1-使用-ks推荐)
  - [方式2: 直接指定 agent-file](#方式2-直接指定-agent-file)
  - [方式3: 创建别名](#方式3-创建别名)
- [目录结构](#目录结构)
- [核心工作流](#核心工作流)
- [相关链接](#相关链接)

---

## 快速开始

### 使用 ce 命令（推荐）

```bash
# 安装 ce CLI（一次性）
uv tool install -e .

# 安装所有 skill（含 kimi agent）
ce install

# 查看状态
ce status

# 更新
ce update

# 卸载
ce uninstall
```

### 直接使用 ks

```bash
ks
```

## 包含内容

### Skills (25 个)

#### 核心 workflow skill（严格类型）

| Skill | 用途 |
|-------|------|
| `dev-using-skills` | skill 入口 |
| `dev-brainstorming` | 编码前苏格拉底式对话 |
| `dev-debugging` | 四阶段调试流程 |
| `dev-tdd` | 测试驱动开发 |
| `dev-writing-plans` | 编写实施计划 |
| `dev-executing-plans` | 执行计划 |
| `dev-git-worktrees` | Git 工作树管理 |
| `dev-requesting-review` | 代码审查请求 |
| `dev-verification` | 完成前验证 |
| `dev-finishing-branch` | 分支完成工作流 |
| `dev-writing-skills` | 编写新 skill |
| `dev-code-cleanup` | 代码清理和死代码删除 |
| `dev-search-first` | 编码前先检索仓库、依赖、MCP 与开源方案 |

#### 辅助 skill（灵活类型）

| Skill | 用途 |
|-------|------|
| `dev-update-codemaps` | 分析代码库结构并生成架构文档 |
| `dev-backend-patterns` | 后端架构模式与最佳实践 |
| `dev-frontend-patterns` | 前端架构模式与最佳实践 |
| `dev-design-system` | 设计 token、语义层与组件状态模式 |
| `dev-ui-styling` | 组件样式、响应式布局、主题与可访问性模式 |
| `dev-continuous-agent-loop` | 顺序流水线、并行分发和持续 agent 循环模式 |
| `dev-e2e-testing` | Playwright Python 端到端测试模式 |
| `learn-deep-research` | 通用深度调研与正式研究报告 |
| `work-market-research` | 市场、竞品、价格与区域机会调研 |
| `tool-humanizer-zh` | 去除文本中的 AI 生成痕迹 |
| `tool-macos-hidpi` | 为 macOS 新增或验证 HiDPI/标准分辨率 |
| `agent-browser` | 浏览器自动化 CLI 使用与网页交互 workflow |

### Agent

- `superpower/` - 基于 superpowers 框架的 agent 配置

## 测试

```bash
# 运行根仓库安装器测试
uv run python -m unittest tests.test_install_skills -v
```

## 安装路径

统一安装路径：
- Skills: `~/.agents/skills/` 和 `~/.claude/skills/`
- Agent: `~/.kimi/agents/superpower/`（仅 Kimi）
- 快捷入口: `~/.local/bin/ks`
- Manifest: `~/.ce/install-manifest.json`

## 使用方法

### 方式1: 使用 ks（推荐）

```bash
ks
```

### 方式2: 直接指定 agent-file

```bash
kimi --agent-file ~/.kimi/agents/superpower/agent.yaml
```

### 方式3: 创建别名

添加到 `~/.bashrc` 或 `~/.zshrc`:

```bash
alias ks='kimi -y --agent-file ~/.kimi/agents/superpower/agent.yaml'
```

## 目录结构

```text
coding-everything/
├── install_skills/             # ce CLI 工具
├── pyproject.toml              # ce CLI 入口定义
├── skills-install.yaml         # 分组安装配置
├── skills/                      # 共享 skills（仓库根目录）
│   ├── dev-using-skills/
│   ├── dev-brainstorming/
│   ├── ...                     # 其余 dev-/learn-/work-/tool- skill
│   ├── obsidian-markdown/      # Obsidian skill（项目级安装）
│   └── agent-browser/          # 浏览器自动化 skill
└── kimi/
    ├── README.md                # 本文件
    └── agents/
        └── superpower/          # Agent 配置
            ├── agent.yaml       # Agent 定义
            ├── system.md        # 系统提示词
            └── README.md
```

## 核心工作流

```
1. 头脑风暴 → 通过提问完善想法
         ↓
2. 编写计划 → 将工作分解为 2-5 分钟任务
         ↓
3. 执行计划 → 按步骤实现
         ↓
4. TDD 开发 → RED → GREEN → REFACTOR
         ↓
5. 代码审查 → 检查清单
         ↓
6. 完成分支 → 验证并合并
```

## 相关链接

- [Kimi Code CLI 文档](https://moonshotai.github.io/kimi-cli/)
- [superpowers 框架](https://github.com/obra/superpowers)
- [Agent Skills 规范](https://agentskills.io/)
