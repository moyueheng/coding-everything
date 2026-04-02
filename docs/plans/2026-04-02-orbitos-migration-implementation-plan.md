# OrbitOS Migration Implementation Plan

> **给 Agent：** 必需子 skill：使用 `dev-executing-plans` 逐个任务实施此计划。

**目标：** 将 OrbitOS 的 8 个工作流 skill 迁移到本仓库，并把 `~/00-Life/ob-note` 重构为与 OrbitOS EN 一致的英文目录结构，统一项目目录为 `20_Project/`。

**架构：** 本次工作拆成两个独立子系统。仓库侧只处理 `skills/`、`skills-install.yaml` 与设计文档；vault 侧只处理 `~/00-Life/ob-note` 的目录、模板、Prompts、Bases、Obsidian 配置和相关 `AGENTS.md` / `CLAUDE.md`。统一路径策略为只保留 `20_Project/`，不保留 `20_Projects/` 兼容层。

**技术栈：** Markdown、YAML、Obsidian vault 目录结构、shell 文件操作、`ce` CLI

---

## 执行进度

- [x] 任务 1：冻结实施依据并记录上游事实
- [x] 任务 2：创建 8 个 OrbitOS workflow skill 目录
- [x] 任务 3：统一仓库侧所有项目路径为 `20_Project/`
- [x] 任务 4：为 8 个新 skill 添加 `UPSTREAM.md`
- [x] 任务 5：把新 skill 接入 `obsidian` 组安装配置
- [x] 任务 6：备份并重构 `~/00-Life/ob-note` 目录结构
- [x] 任务 7：迁移 Templates、Prompts、Bases 到 `99_System/`
- [x] 任务 8：更新 Obsidian 配置到新路径
- [x] 任务 9：同步 vault 内 `AGENTS.md` / `CLAUDE.md`
- [x] 任务 10：安装、验证与收尾

## 执行记录

- 2026-04-02：已完成仓库侧 8 个 OrbitOS workflow skill 迁移、frontmatter 重命名、`20_Project/` 路径统一、`UPSTREAM.md` 写入和 `skills-install.yaml` 接入。
- 2026-04-02：已完成 `~/00-Life/ob-note` 目录重构，顶层结构已切换到 `10_Daily/`、`20_Project/`、`30_Research/`、`40_Wiki/`、`50_Resources/`、`90_Plans/`、`99_System/`、`99_Archive/`。
- 2026-04-02：已复制 15 个 Prompts、3 个 Bases、5 个 OrbitOS 模板，并更新 `.obsidian`、vault 内 `AGENTS.md` / `CLAUDE.md`。
- 2026-04-02：已运行 `uv run ce install --group obsidian`，确认 8 个新增 skill 已安装到 vault 的 `.claude/skills` 与 `.agents/skills`。

---

## 文件结构

- `skills/life-start-my-day/`
  - 从 `upstream/orbitos/EN/.agents/skills/start-my-day/SKILL.md` 迁移，统一引用 `20_Project/`
- `skills/life-kickoff/`
  - 从 `upstream/orbitos/EN/.agents/skills/kickoff/SKILL.md` 迁移，显式把 `20_Projects/` 改为 `20_Project/`
- `skills/life-research/`
  - 从 `upstream/orbitos/EN/.agents/skills/research/SKILL.md` 迁移，显式把 `20_Projects/` 改为 `20_Project/`
- `skills/life-brainstorm/`
  - 从 `upstream/orbitos/EN/.agents/skills/brainstorm/SKILL.md` 迁移，显式把 `20_Projects/` 改为 `20_Project/`
- `skills/life-parse-knowledge/`
  - 从 `upstream/orbitos/EN/.agents/skills/parse-knowledge/SKILL.md` 迁移
- `skills/life-archive/`
  - 从 `upstream/orbitos/EN/.agents/skills/archive/SKILL.md` 迁移
- `skills/work-ai-newsletters/`
  - 从 `upstream/orbitos/EN/.agents/skills/ai-newsletters/SKILL.md` 迁移
- `skills/work-ai-products/`
  - 从 `upstream/orbitos/EN/.agents/skills/ai-products/SKILL.md` 迁移
- `skills/*/UPSTREAM.md`
  - 记录 OrbitOS 上游仓库、分支、源路径和 commit SHA
- `skills-install.yaml`
  - 把 8 个新 skill 加入 `obsidian` 组
- `docs/plans/2026-04-02-orbitos-migration-design.md`
  - 作为实施依据，已固定规范路径为 `20_Project/` 并修正 Persona 数量为 15
- `/Users/moyueheng/00-Life/ob-note/20_Project/`
  - 由 `/Users/moyueheng/00-Life/ob-note/20_Projects/` 直接重命名而来
- `/Users/moyueheng/00-Life/ob-note/30_Research/`
  - 新建研究目录
- `/Users/moyueheng/00-Life/ob-note/40_Wiki/`
  - 新建原子知识目录
- `/Users/moyueheng/00-Life/ob-note/50_Resources/`
  - 由 `/Users/moyueheng/00-Life/ob-note/40_Resources/` 迁移而来，并吸收 `60_People/`
- `/Users/moyueheng/00-Life/ob-note/90_Plans/`
  - 由 `/Users/moyueheng/00-Life/ob-note/10_OKR/` 迁移而来
- `/Users/moyueheng/00-Life/ob-note/99_System/`
  - 承载 `Prompts/`、`Templates/`、`Bases/`、`docs/` 与系统说明
- `/Users/moyueheng/00-Life/ob-note/.obsidian/daily-notes.json`
  - 当前配置仍指向 `50_Logs/Daily` 和 `99_Templates/T_Daily`
- `/Users/moyueheng/00-Life/ob-note/.obsidian/plugins/templater-obsidian/data.json`
  - 当前配置仍指向 `99_Templates`、`50_Logs/Daily`、`50_Logs/Weekly`、`20_Projects`

## 任务 1：冻结实施依据并记录上游事实

**文件：**
- 修改：`docs/plans/2026-04-02-orbitos-migration-design.md`
- 创建：`docs/plans/2026-04-02-orbitos-migration-implementation-plan.md`

> **给 Agent：** 此任务是文档基线整理，不需要 `dev-tdd`。

**步骤 1：核对上游 Skill 和 Prompts 的真实数量**

运行：

```bash
find upstream/orbitos/EN/.agents/skills -mindepth 1 -maxdepth 1 -type d | wc -l
find upstream/orbitos/EN/99_System/Prompts -maxdepth 1 -type f | wc -l
```

预期：
- skill 目录数输出 `12`
- Prompt 文件数输出 `15`

**步骤 2：核对上游 `20_Project` / `20_Projects` 混用位置**

运行：

```bash
rg -n "20_Project|20_Projects" upstream/orbitos/EN
```

预期：
- 同时出现两种写法
- `kickoff`、`brainstorm`、`research` 至少包含 `20_Projects`
- `README`、`start-my-day`、`archive` 至少包含 `20_Project`

**步骤 3：确认实施设计已经写死单一路径**

检查 `docs/plans/2026-04-02-orbitos-migration-design.md`，确认以下事实已存在：
- 最终规范路径固定为 `20_Project/`
- 明确不保留兼容层
- Persona 数量为 15

**步骤 4：提交**

```bash
git add docs/plans/2026-04-02-orbitos-migration-design.md docs/plans/2026-04-02-orbitos-migration-implementation-plan.md
git commit -m "docs: finalize orbitos migration design constraints"
```

## 任务 2：创建 8 个 OrbitOS workflow skill 目录

**文件：**
- 创建：`skills/life-start-my-day/SKILL.md`
- 创建：`skills/life-kickoff/SKILL.md`
- 创建：`skills/life-research/SKILL.md`
- 创建：`skills/life-brainstorm/SKILL.md`
- 创建：`skills/life-parse-knowledge/SKILL.md`
- 创建：`skills/life-archive/SKILL.md`
- 创建：`skills/work-ai-newsletters/SKILL.md`
- 创建：`skills/work-ai-products/SKILL.md`

> **给 Agent：** 此任务是内容迁移，不需要 `dev-tdd`。

**步骤 1：逐个复制上游 SKILL.md 到目标目录**

来源与目标对应：

- `upstream/orbitos/EN/.agents/skills/start-my-day/SKILL.md` -> `skills/life-start-my-day/SKILL.md`
- `upstream/orbitos/EN/.agents/skills/kickoff/SKILL.md` -> `skills/life-kickoff/SKILL.md`
- `upstream/orbitos/EN/.agents/skills/research/SKILL.md` -> `skills/life-research/SKILL.md`
- `upstream/orbitos/EN/.agents/skills/brainstorm/SKILL.md` -> `skills/life-brainstorm/SKILL.md`
- `upstream/orbitos/EN/.agents/skills/parse-knowledge/SKILL.md` -> `skills/life-parse-knowledge/SKILL.md`
- `upstream/orbitos/EN/.agents/skills/archive/SKILL.md` -> `skills/life-archive/SKILL.md`
- `upstream/orbitos/EN/.agents/skills/ai-newsletters/SKILL.md` -> `skills/work-ai-newsletters/SKILL.md`
- `upstream/orbitos/EN/.agents/skills/ai-products/SKILL.md` -> `skills/work-ai-products/SKILL.md`

**步骤 2：统一 frontmatter 的 `name`**

目标命名：

- `life-start-my-day`
- `life-kickoff`
- `life-research`
- `life-brainstorm`
- `life-parse-knowledge`
- `life-archive`
- `work-ai-newsletters`
- `work-ai-products`

**步骤 3：检查目录全部创建完成**

运行：

```bash
test -f skills/life-start-my-day/SKILL.md
test -f skills/life-kickoff/SKILL.md
test -f skills/life-research/SKILL.md
test -f skills/life-brainstorm/SKILL.md
test -f skills/life-parse-knowledge/SKILL.md
test -f skills/life-archive/SKILL.md
test -f skills/work-ai-newsletters/SKILL.md
test -f skills/work-ai-products/SKILL.md
```

预期：全部退出码为 0

**步骤 4：提交**

```bash
git add skills/life-start-my-day skills/life-kickoff skills/life-research skills/life-brainstorm skills/life-parse-knowledge skills/life-archive skills/work-ai-newsletters skills/work-ai-products
git commit -m "feat: add orbitos workflow skills"
```

## 任务 3：统一仓库侧所有项目路径为 `20_Project/`

**文件：**
- 修改：`skills/life-kickoff/SKILL.md`
- 修改：`skills/life-research/SKILL.md`
- 修改：`skills/life-brainstorm/SKILL.md`
- 修改：`skills/life-start-my-day/SKILL.md`
- 修改：`skills/life-archive/SKILL.md`

> **给 Agent：** 此任务是文案路径统一，不需要 `dev-tdd`。

**步骤 1：把所有 `20_Projects/` 改成 `20_Project/`**

至少要覆盖以下已知位置：

- `skills/life-kickoff/SKILL.md`
- `skills/life-research/SKILL.md`
- `skills/life-brainstorm/SKILL.md`

**步骤 2：校对 `20_Project/` 使用场景是否自洽**

重点检查：
- `kickoff` 中创建项目 note 的路径示例
- `research` 中检查活跃项目的路径
- `brainstorm` 中 quick search 和后续 action path
- `start-my-day` 中搜索活跃项目的路径
- `archive` 中归档已完成项目的路径

**步骤 3：全仓检索确认没有遗留 `20_Projects/`**

运行：

```bash
rg -n "20_Projects" skills/life-* skills/work-ai-*
```

预期：无输出

**步骤 4：提交**

```bash
git add skills/life-kickoff/SKILL.md skills/life-research/SKILL.md skills/life-brainstorm/SKILL.md skills/life-start-my-day/SKILL.md skills/life-archive/SKILL.md
git commit -m "refactor: normalize orbitos project path to 20_Project"
```

## 任务 4：为 8 个新 skill 添加 `UPSTREAM.md`

**文件：**
- 创建：`skills/life-start-my-day/UPSTREAM.md`
- 创建：`skills/life-kickoff/UPSTREAM.md`
- 创建：`skills/life-research/UPSTREAM.md`
- 创建：`skills/life-brainstorm/UPSTREAM.md`
- 创建：`skills/life-parse-knowledge/UPSTREAM.md`
- 创建：`skills/life-archive/UPSTREAM.md`
- 创建：`skills/work-ai-newsletters/UPSTREAM.md`
- 创建：`skills/work-ai-products/UPSTREAM.md`

> **给 Agent：** 此任务是元数据补充，不需要 `dev-tdd`。

**步骤 1：获取 OrbitOS 当前 SHA**

运行：

```bash
git -C upstream/orbitos rev-parse HEAD
```

预期：输出 40 位 commit SHA

**步骤 2：按现有仓库格式写入 `UPSTREAM.md`**

每个文件至少包含：
- upstream 仓库：`https://github.com/MarsWang42/OrbitOS`
- branch：`main`
- source path：对应 `upstream/orbitos/EN/.agents/skills/.../SKILL.md`
- synced commit：步骤 1 输出的 SHA
- local adaptations：列出本地重命名、路径统一到 `20_Project/`、是否调整语言/说明

**步骤 3：抽查两个文件格式**

运行：

```bash
sed -n '1,120p' skills/life-kickoff/UPSTREAM.md
sed -n '1,120p' skills/work-ai-products/UPSTREAM.md
```

预期：字段完整，source path 与本地目录一一对应

**步骤 4：提交**

```bash
git add skills/life-start-my-day/UPSTREAM.md skills/life-kickoff/UPSTREAM.md skills/life-research/UPSTREAM.md skills/life-brainstorm/UPSTREAM.md skills/life-parse-knowledge/UPSTREAM.md skills/life-archive/UPSTREAM.md skills/work-ai-newsletters/UPSTREAM.md skills/work-ai-products/UPSTREAM.md
git commit -m "docs: track orbitos upstream metadata"
```

## 任务 5：把新 skill 接入 `obsidian` 组安装配置

**文件：**
- 修改：`skills-install.yaml`

> **给 Agent：** 此任务是配置更新，不需要 `dev-tdd`。

**步骤 1：将 8 个新 skill 加入 `groups.obsidian.skills`**

在现有 5 个 Obsidian skill 之后追加：

```yaml
      - life-start-my-day
      - life-kickoff
      - life-research
      - life-brainstorm
      - life-parse-knowledge
      - life-archive
      - work-ai-newsletters
      - work-ai-products
```

**步骤 2：校验 YAML 可以被当前安装器读取**

运行：

```bash
uv run python -c "from pathlib import Path; from install_skills.config import load_install_config; print(load_install_config(Path('skills-install.yaml'))['obsidian'].skills)"
```

预期：输出的列表同时包含旧 5 个 skill 和新增 8 个 skill

**步骤 3：提交**

```bash
git add skills-install.yaml
git commit -m "feat: add orbitos skills to obsidian install group"
```

## 任务 6：备份并重构 `~/00-Life/ob-note` 目录结构

**文件：**
- 修改：`/Users/moyueheng/00-Life/ob-note/` 下的目录结构

> **给 Agent：** 此任务是文件系统迁移，不需要 `dev-tdd`。

**步骤 1：确认当前关键目录存在**

运行：

```bash
test -d /Users/moyueheng/00-Life/ob-note/20_Projects
test -d /Users/moyueheng/00-Life/ob-note/40_Resources
test -d /Users/moyueheng/00-Life/ob-note/50_Logs
test -d /Users/moyueheng/00-Life/ob-note/60_People
test -d /Users/moyueheng/00-Life/ob-note/10_OKR
```

预期：全部退出码为 0

**步骤 2：做一次可回滚备份**

运行：

```bash
tar -czf /Users/moyueheng/00-Life/ob-note-backup-2026-04-02.tar.gz -C /Users/moyueheng/00-Life ob-note
```

预期：生成 `/Users/moyueheng/00-Life/ob-note-backup-2026-04-02.tar.gz`

**步骤 3：执行目录重构**

按下列顺序操作：

```bash
mv /Users/moyueheng/00-Life/ob-note/20_Projects /Users/moyueheng/00-Life/ob-note/20_Project
mkdir -p /Users/moyueheng/00-Life/ob-note/30_Research
mkdir -p /Users/moyueheng/00-Life/ob-note/40_Wiki
mv /Users/moyueheng/00-Life/ob-note/40_Resources /Users/moyueheng/00-Life/ob-note/50_Resources
mkdir -p /Users/moyueheng/00-Life/ob-note/50_Resources/People
mv /Users/moyueheng/00-Life/ob-note/60_People/* /Users/moyueheng/00-Life/ob-note/50_Resources/People/
mv /Users/moyueheng/00-Life/ob-note/10_OKR /Users/moyueheng/00-Life/ob-note/90_Plans
mv /Users/moyueheng/00-Life/ob-note/99_Templates /Users/moyueheng/00-Life/ob-note/99_System/Templates
mv /Users/moyueheng/00-Life/ob-note/docs /Users/moyueheng/00-Life/ob-note/99_System/docs
mv /Users/moyueheng/00-Life/ob-note/01_Home /Users/moyueheng/00-Life/ob-note/99_System/Home
mv /Users/moyueheng/00-Life/ob-note/90_Archive /Users/moyueheng/00-Life/ob-note/99_Archive
```

执行前先创建缺失的父目录：

```bash
mkdir -p /Users/moyueheng/00-Life/ob-note/99_System
```

**步骤 4：确认新旧路径切换完成**

运行：

```bash
test -d /Users/moyueheng/00-Life/ob-note/20_Project
test ! -d /Users/moyueheng/00-Life/ob-note/20_Projects
test -d /Users/moyueheng/00-Life/ob-note/30_Research
test -d /Users/moyueheng/00-Life/ob-note/40_Wiki
test -d /Users/moyueheng/00-Life/ob-note/50_Resources
test -d /Users/moyueheng/00-Life/ob-note/90_Plans
test -d /Users/moyueheng/00-Life/ob-note/99_System/Templates
test -d /Users/moyueheng/00-Life/ob-note/99_System/docs
test -d /Users/moyueheng/00-Life/ob-note/99_Archive
```

预期：全部退出码为 0

## 任务 7：迁移 Templates、Prompts、Bases 到 `99_System/`

**文件：**
- 创建：`/Users/moyueheng/00-Life/ob-note/99_System/Prompts/*.md`
- 创建：`/Users/moyueheng/00-Life/ob-note/99_System/Templates/*.md`
- 创建：`/Users/moyueheng/00-Life/ob-note/99_System/Bases/*.base`

> **给 Agent：** 此任务是内容迁移，不需要 `dev-tdd`。

**步骤 1：复制 5 个模板**

来源：
- `upstream/orbitos/EN/99_System/Templates/Daily_Note.md`
- `upstream/orbitos/EN/99_System/Templates/Project_Template.md`
- `upstream/orbitos/EN/99_System/Templates/Wiki_Template.md`
- `upstream/orbitos/EN/99_System/Templates/Inbox_Template.md`
- `upstream/orbitos/EN/99_System/Templates/Content_Template.md`

目标：
- `/Users/moyueheng/00-Life/ob-note/99_System/Templates/`

**步骤 2：复制 15 个 Persona Prompt**

运行：

```bash
mkdir -p /Users/moyueheng/00-Life/ob-note/99_System/Prompts
cp upstream/orbitos/EN/99_System/Prompts/*.md /Users/moyueheng/00-Life/ob-note/99_System/Prompts/
find /Users/moyueheng/00-Life/ob-note/99_System/Prompts -maxdepth 1 -type f | wc -l
```

预期：输出 `15`

**步骤 3：复制 3 个 Bases 文件**

运行：

```bash
mkdir -p /Users/moyueheng/00-Life/ob-note/99_System/Bases
cp upstream/orbitos/EN/99_System/Bases/*.base /Users/moyueheng/00-Life/ob-note/99_System/Bases/
find /Users/moyueheng/00-Life/ob-note/99_System/Bases -maxdepth 1 -type f | wc -l
```

预期：输出 `3`

**步骤 4：检查旧模板文件是否需要保留**

需要人工决定的旧文件：
- `/Users/moyueheng/00-Life/ob-note/99_System/Templates/T_Daily.md`
- `/Users/moyueheng/00-Life/ob-note/99_System/Templates/T_Project.md`
- `/Users/moyueheng/00-Life/ob-note/99_System/Templates/T_Weekly.md`

处理规则：
- `T_Daily.md` 与 `T_Project.md` 被新模板替代，可移入 `99_Archive/` 或保留待人工清理
- `T_Weekly.md` 当前 OrbitOS 无替代模板，暂时保留

## 任务 8：更新 Obsidian 配置到新路径

**文件：**
- 修改：`/Users/moyueheng/00-Life/ob-note/.obsidian/daily-notes.json`
- 修改：`/Users/moyueheng/00-Life/ob-note/.obsidian/plugins/templater-obsidian/data.json`

> **给 Agent：** 此任务是配置更新，不需要 `dev-tdd`。

**步骤 1：更新 Daily Notes 核心配置**

把 `/Users/moyueheng/00-Life/ob-note/.obsidian/daily-notes.json` 从：

```json
{
  "folder": "50_Logs/Daily",
  "template": "99_Templates/T_Daily"
}
```

改为：

```json
{
  "folder": "10_Daily",
  "template": "99_System/Templates/Daily_Note"
}
```

**步骤 2：更新 Templater 配置**

至少改这三处：
- `"templates_folder": "99_System/Templates"`
- `folder_templates` 中 `50_Logs/Daily` -> `10_Daily`
- `folder_templates` 中 `50_Logs/Weekly` 如继续保留 weekly 模板，则改成新的 weekly 存放目录；若 weekly 目录进入 `99_Archive/`，则移除该模板映射
- `folder_templates` 中 `20_Projects` -> `20_Project`

同时修正当前坏值：
- `"template": "99_Templates/T_Project:md"` 应改为有效文件路径

**步骤 3：校验 JSON 合法**

运行：

```bash
uv run python -m json.tool /Users/moyueheng/00-Life/ob-note/.obsidian/daily-notes.json >/dev/null
uv run python -m json.tool /Users/moyueheng/00-Life/ob-note/.obsidian/plugins/templater-obsidian/data.json >/dev/null
```

预期：两条命令都退出码为 0

## 任务 9：同步 vault 内 `AGENTS.md` / `CLAUDE.md`

**文件：**
- 修改：`/Users/moyueheng/00-Life/ob-note/AGENTS.md`
- 修改：`/Users/moyueheng/00-Life/ob-note/CLAUDE.md`
- 视重构范围修改：`/Users/moyueheng/00-Life/ob-note/20_Project/AGENTS.md`
- 视重构范围修改：`/Users/moyueheng/00-Life/ob-note/20_Project/CLAUDE.md`
- 视重构范围修改：其他目录下因路径变化而失真的 `AGENTS.md` / `CLAUDE.md`

> **给 Agent：** 此任务是文档同步，不需要 `dev-tdd`。

**步骤 1：扫描所有受影响文档**

运行：

```bash
find /Users/moyueheng/00-Life/ob-note -type f \( -name 'AGENTS.md' -o -name 'CLAUDE.md' \) | sort
```

预期：至少包含根目录、`20_Project/`、`50_Resources/`、`99_System/Templates/` 等位置的文档

**步骤 2：只修改高信息密度事实**

需要同步的稳定事实：
- 项目目录统一为 `20_Project/`
- Daily Notes 目录改为 `10_Daily/`
- 模板目录改为 `99_System/Templates/`
- `Prompts/` 和 `Bases/` 位于 `99_System/`
- `40_Resources` / `60_People` 已并入 `50_Resources/`

**步骤 3：避免记录临时性迁移日志**

不要写：
- “今天把某目录搬了”
- “这次迁移做了什么”

只写迁移后的稳定结构和约束。

## 任务 10：安装、验证与收尾

**文件：**
- 验证：仓库改动与 vault 改动

> **给 Agent：** 此任务是验证，不需要 `dev-tdd`。

**步骤 1：安装新的 obsidian skill 组**

运行：

```bash
ce install --group obsidian
```

预期：
- `~/00-Life/ob-note/.claude/skills` 和 `~/00-Life/ob-note/.agents/skills` 下出现新增 8 个 skill 的 symlink

**步骤 2：检查安装结果**

运行：

```bash
ls -1 /Users/moyueheng/00-Life/ob-note/.claude/skills | rg "life-|work-ai-"
ls -1 /Users/moyueheng/00-Life/ob-note/.agents/skills | rg "life-|work-ai-"
```

预期：两个目录都能看到 8 个新增 skill

**步骤 3：检查仓库侧残留路径**

运行：

```bash
rg -n "20_Projects" skills skills-install.yaml docs/plans/2026-04-02-orbitos-migration-*.md
```

预期：
- 只允许出现在设计文档中“说明上游曾经混用”的段落
- 不允许出现在本地 skill 的实际执行路径中

**步骤 4：检查 Persona、Bases、模板数量**

运行：

```bash
find /Users/moyueheng/00-Life/ob-note/99_System/Prompts -maxdepth 1 -type f | wc -l
find /Users/moyueheng/00-Life/ob-note/99_System/Bases -maxdepth 1 -type f | wc -l
find /Users/moyueheng/00-Life/ob-note/99_System/Templates -maxdepth 1 -type f | wc -l
```

预期：
- Prompts 为 `15`
- Bases 为 `3`
- Templates 至少包含 OrbitOS 的 5 个模板

**步骤 5：检查工作区改动**

运行：

```bash
git status --short
```

预期：只包含本次仓库内设计文档、计划文档、skill 目录和 `skills-install.yaml` 的改动

## 审查说明

按 `dev-writing-plans` 要求完成自审：

- **Spec 覆盖度：** 已覆盖 8 个 skill、15 个 Prompts、5 个 Templates、3 个 Bases、vault 目录重构、Obsidian 配置迁移、文档同步和安装验证。
- **占位符扫描：** 计划中不保留 `TBD`、`TODO`、`后续决定` 这类占位语句；唯一保留的人为判断点是旧模板是否归档，但处理边界已写明。
- **类型一致性：** 全文统一使用 `20_Project/` 作为唯一规范路径，Persona 统计统一为 15。

## 执行交接

**计划已完成并保存到 `docs/plans/2026-04-02-orbitos-migration-implementation-plan.md`。两种执行选项：**

**1. Subagent-Driven（推荐）** - 我为每个任务分派 fresh subagent，任务间审查，快速迭代

**2. 内联执行** - 在本会话中使用 `dev-executing-plans` 执行任务，批量执行带检查点
