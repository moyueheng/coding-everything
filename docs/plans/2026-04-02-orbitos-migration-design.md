# OrbitOS Skills 迁移与 Obsidian Vault 重构设计

日期：2026-04-02
来源：upstream/orbitos (MarsWang42/OrbitOS)
目标：coding-everything skills/ + ~/00-Life/ob-note vault

## 1. 背景

OrbitOS 是一个 AI 驱动的 Obsidian 个人生产力系统，提供 12 个 Agent Skills、15 个 AI Persona 提示词、5 个 Markdown 模板和 3 个 Obsidian Bases 视图。本设计将其中 8 个工作流 skills 和全部 Persona 提示词迁移到 coding-everything 项目，并对 Obsidian vault 目录结构进行全面重构以对齐 OrbitOS EN 版。

### 与现有 skills 的关系

| 新 skill | 与现有 skill 关系 |
|----------|-------------------|
| `life-brainstorm` | 与 `dev-brainstorming` 互补：前者是生活/知识侧轻量头脑风暴，后者是编码前设计审查 |
| `life-research` | 与 `learn-deep-research` 互补：前者是 vault 内研究笔记+原子知识库，后者是正式研究报告 |

## 2. Skills 迁移清单

### 2.1 新增 Skills（8 个）

| Skill 名称 | 来源 | 分类 | 说明 |
|-------------|------|------|------|
| `life-start-my-day` | start-my-day | life | 每日规划：回顾昨日、活跃项目、推荐重点、处理收件箱、AI 摘要 |
| `life-kickoff` | kickoff | life | 想法 -> 结构化项目（双 agent 模式，C.A.P. 结构） |
| `life-research` | research | life | 深度调研 + 原子知识库创建 |
| `life-brainstorm` | brainstorm | life | 苏格拉底式头脑风暴，可选创建项目/整理知识 |
| `life-parse-knowledge` | parse-knowledge | life | 零散文本 -> 结构化知识库概念 |
| `life-archive` | archive | life | 归档已完成项目和已处理收件箱 |
| `work-ai-newsletters` | ai-newsletters | work | AI 新闻抓取去重排名摘要 |
| `work-ai-products` | ai-products | work | 多源 AI 产品发现与排名 |

### 2.2 适配原则

1. **目录路径**：所有 OrbitOS 硬编码路径统一适配为 `20_Project/`、`30_Research/`、`40_Wiki/` 等重构后的英文路径（见第 3 节）
2. **UPSTREAM.md**：每个 skill 目录下创建 UPSTREAM.md 跟踪来源（仓库、分支、SHA）
3. **Skill 标准**：遵循 Agent Skills 开放标准，SKILL.md 带 YAML frontmatter
4. **语言**：SKILL.md 使用英文（与上游一致），路径使用英文

### 2.3 skills-install.yaml 变更

```yaml
obsidian:
  skills:
    # 现有 5 个 Obsidian 技术类
    - obsidian-markdown
    - obsidian-bases
    - json-canvas
    - obsidian-cli
    - defuddle
    # 新增 8 个 OrbitOS 工作流
    - life-start-my-day
    - life-kickoff
    - life-research
    - life-brainstorm
    - life-parse-knowledge
    - life-archive
    - work-ai-newsletters
    - work-ai-products
  targets:
    - ~/00-Life/ob-note/.claude/skills
    - ~/00-Life/ob-note/.agents/skills
```

## 3. Vault 目录重构

### 3.1 目标结构

```
ob-note/
├── 00_Inbox/               # 快速捕获
├── 10_Daily/               # 每日日志 YYYY-MM-DD.md
├── 20_Project/             # 活跃项目（唯一规范路径）
├── 30_Research/            # 深度研究笔记
├── 40_Wiki/                # 原子知识库
├── 50_Resources/           # 精选内容
│   └── People/             # 人物关系
├── 70_Assets/              # 图片与附件
├── 90_Plans/               # OKR 与执行方案
├── 99_System/              # 系统目录
│   ├── Prompts/            # 15 个 AI Persona 提示词
│   ├── Templates/          # Markdown 模板
│   ├── Bases/              # Obsidian Bases 视图
│   └── docs/               # 文档
└── 99_Archive/             # 归档（已完成项目+历史日志）
```

### 3.2 目录映射

| 现有 | 目标 | 操作 |
|------|------|------|
| `00_Inbox/` | `00_Inbox/` | 不变 |
| `50_Logs/Daily/` | `10_Daily/` | 移动 294 篇日志 |
| `20_Projects/` | `20_Project/` | 直接重命名；后续所有 skill / 文档引用统一改写为单数路径 |
| _(新增)_ | `30_Research/` | 新建 |
| _(新增)_ | `40_Wiki/` | 新建 |
| `40_Resources/` | `50_Resources/` | 移动 |
| `60_People/` | `50_Resources/People/` | 移入子目录 |
| `70_Assets/` + `05-Assets/` | `70_Assets/` | 合并 |
| `10_OKR/` | `90_Plans/` | 移动 |
| `50_Logs/Weekly/` `Monthly/` `Quarterly/` | `99_Archive/` | 移入归档参考 |
| `99_Templates/` | `99_System/Templates/` | 移动 |
| `90_Archive/` | `99_Archive/` | 移动 |
| `01_Home/` | `99_System/` | 移入系统目录 |
| `docs/` | `99_System/docs/` | 移入系统目录 |
| `比赛/` | `99_Archive/` | 移入归档 |

### 3.3 Obsidian 配置更新

- Daily Notes 文件夹：`50_Logs/Daily` → `10_Daily`
- Daily Notes 模板：`99_Templates/T_Daily` → `99_System/Templates/Daily_Note`
- 附件文件夹：确认指向 `70_Assets/`

### 3.4 路径规范与上游引用改写

最终规范路径固定为 `20_Project/`，不保留 `20_Projects/` 兼容目录，也不额外套一层中转目录。

原因：上游 OrbitOS EN 在项目目录命名上本身不一致，README / 部分 skill 使用 `20_Project/`，而 `kickoff`、`brainstorm`、`research` 等流程仍引用 `20_Projects/`。如果只重命名 vault 而不重写这些上游引用，迁移后的 skill 会指向不存在的目录。

迁移时必须同步改写的已知上游引用：

- `upstream/orbitos/EN/.agents/skills/kickoff/SKILL.md` 中的 `20_Projects`
- `upstream/orbitos/EN/.agents/skills/brainstorm/SKILL.md` 中的 `20_Projects`
- `upstream/orbitos/EN/.agents/skills/research/SKILL.md` 中的 `20_Projects`
- `upstream/orbitos/EN/AGENTS.md` 中的 `20_Projects`
- `upstream/orbitos/EN/GEMINI.md` 中的 `20_Projects`

迁移后保留不变、可作为对齐基准的已知上游引用：

- `upstream/orbitos/EN/README.md` 中的 `20_Project`
- `upstream/orbitos/EN/CLAUDE.md` 中的 `20_Project`
- `upstream/orbitos/EN/.agents/skills/start-my-day/SKILL.md` 中的 `20_Project`
- `upstream/orbitos/EN/.agents/skills/archive/SKILL.md` 中的 `20_Project`

## 4. 模板更新

| OrbitOS 模板 | 操作 | 说明 |
|-------------|------|------|
| `Daily_Note.md` | 替换 `T_Daily.md` | 加入精力/专注评分、AI 摘要区 |
| `Project_Template.md` | 替换 `T_Project.md` | C.A.P. 结构（Context/Actions/Progress） |
| `Wiki_Template.md` | 新增 | 原子知识库条目模板 |
| `Inbox_Template.md` | 新增 | 收件箱条目模板 |
| `Content_Template.md` | 新增 | 内容创作模板 |

## 5. AI Persona 提示词迁移

15 个提示词迁移到 `99_System/Prompts/`：

| 领域 | 提示词 |
|------|--------|
| 软件工程 | SE_Architect, SE_CodeBase, SE_Interview |
| 通用思维 | General_FirstPrinciples, General_SecondOrderThinking, General_Latticework |
| 健康 | Health_General, Health_Sympton, Health_Nutrition, Health_Medication |
| 金融 | Finance_StockMarket, Finance_Portfolio, Finance_Debt, Finance_Tax, Finance_Crypto |

统计口径以 `upstream/orbitos/EN/99_System/Prompts/` 的实际文件数为准，迁移验收时必须逐文件核对 15 个文件全部存在。

## 6. Obsidian Bases 视图

3 个 Bases 视图迁移到 `99_System/Bases/`：

| Base | 用途 |
|------|------|
| `Projects.base` | 活跃项目 + 待处理收件箱 |
| `Projects_Archive.base` | 已完成/搁置项目 |
| `Knowledge.base` | 研究笔记 + Wiki 知识库 |

路径适配：将 OrbitOS 的中文路径（`20_项目/`、`40_知识库/`）替换为英文路径（`20_Project/`、`40_Wiki/`），并统一消除上游 `20_Projects/` / `20_Project/` 混用问题。

## 7. 实施顺序

### 阶段 1 - Skills 迁移（在 coding-everything 仓库）

1. 逐一创建 8 个新 skill 目录，基于 OrbitOS SKILL.md 适配英文路径，并统一将所有 `20_Projects/` 改写为 `20_Project/`
2. 每个 skill 添加 UPSTREAM.md
3. 更新 skills-install.yaml

### 阶段 2 - Vault 重构

1. 备份 vault（git commit 或 tar）
2. 执行目录移动/重命名/新建
3. 迁移模板到 99_System/Templates/
4. 迁移 15 个 Persona 提示词到 99_System/Prompts/
5. 创建 3 个 Bases 视图到 99_System/Bases/
6. 更新 Obsidian 配置（daily-notes、附件路径等）
7. 更新所有 CLAUDE.md / AGENTS.md
8. 运行 `ce install --group obsidian` 安装新 skills

### 阶段 3 - 验证

1. 在 vault 中测试各 skill
2. 验证 Daily Notes 配置正确
3. 验证 wikilinks 完整性
