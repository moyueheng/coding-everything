# Shared Skills Directory Implementation Plan

> **给 Agent：** 必需子 skill：使用 `dev-executing-plans` 逐个任务实施此计划。

**目标：** 将跨平台共享 skill 从 `kimi/skills/` 提升到仓库顶层 `skills/`，并同步更新安装说明与文档表述。

**架构：** 共享 skill 资产统一收敛到顶层 `skills/`，`kimi/` 仅保留 Kimi 专属 agent/config。用户侧安装目标路径保持不变，只调整仓库内源路径与文档说明。为降低迁移风险，先完成主路径迁移与引用修正，再视需要保留短期兼容层。

**技术栈：** Markdown 文档、仓库目录结构、symlink 安装说明、shell 路径引用

---

## 文件结构

- `skills/`
  - 新的跨平台共享 skill 主目录，由当前 `kimi/skills/` 迁移而来
- `kimi/agents/superpower/`
  - 保持不变，继续承载 Kimi 专属 agent 配置
- `README.md`
  - 更新快速安装、项目结构和文档说明
- `AGENTS.md`
  - 更新项目结构、快速安装、个人配置描述和目录约束
- `.agents/skills/setup/SKILL.md`
  - 更新 setup skill 中的源目录、symlink 指令和实时同步示例
- `docs/kimi-skills-architecture.md`
  - 更新标题、正文和版本表述，使其反映共享 skill 顶层化后的结构
- `docs/plans/2025-02-27-setup-skill-refactor.md`
  - 修正仍引用 `kimi/skills/` 的仓库内路径示例，避免计划文档继续误导

### 任务 1：迁移共享 skill 主目录

**文件：**
- 创建：`skills/`（由移动生成）
- 删除：`kimi/skills/`（若不保留兼容层）

**步骤 1：移动目录**

运行：`mv kimi/skills skills`
预期：仓库顶层出现 `skills/`，原 `kimi/skills/` 消失

**步骤 2：确认 skill 数量与关键目录完整**

运行：`find skills -maxdepth 1 -mindepth 1 -type d | wc -l`
预期：目录数量与迁移前一致

运行：`test -f skills/dev-using-skills/SKILL.md && test -f skills/dev-writing-plans/SKILL.md`
预期：命令退出码为 0

### 任务 2：更新安装与入口文档

**文件：**
- 修改：`README.md`
- 修改：`AGENTS.md`
- 修改：`.agents/skills/setup/SKILL.md`

> **给 Agent：** 此任务是文档/配置路径修正，不需要 `dev-tdd`。

**步骤 1：将共享 skill 源路径改为 `skills/`**

需要修改的内容：
- 安装章节中的 `ln -sf "$(pwd)/kimi/skills"` 改为 `ln -sf "$(pwd)/skills"`
- 目录结构中的共享 skill 所在位置改为顶层 `skills/`
- 文案从 “Kimi skill” 或 “Kimi/Codex/OpenCode 共享的 kimi/skills” 改为 “跨平台共享 skill”

**步骤 2：保留 Kimi 专属 agent 路径说明**

需要确认以下说明保持不变：
- `kimi/agents/superpower/`
- `~/.kimi/agents/superpower`
- `ks` 作为 Kimi 启动入口

**步骤 3：校验文本替换**

运行：`rg -n "kimi/skills" README.md AGENTS.md .agents/skills/setup/SKILL.md`
预期：不再出现共享 skill 主路径引用

### 任务 3：更新架构文档

**文件：**
- 修改：`docs/kimi-skills-architecture.md`

> **给 Agent：** 此任务是文档修正，不需要 `dev-tdd`。

**步骤 1：调整标题与导语**

需要修改的内容：
- 标题从 “Kimi Skills 架构全景图” 改成反映共享定位的名称
- 导语不再将共享 skill 描述为 Kimi 专属

**步骤 2：调整结构图与说明**

需要修改的内容：
- 结构图中共享 skill 改为顶层 `skills/`
- Kimi 仅描述为平台专属 agent/config 所在目录

**步骤 3：更新版本或路径表述**

例如：
- `kimi/skills v1.2` 改为 `skills v1.2`

### 任务 4：清理遗留计划文档中的错误仓库路径示例

**文件：**
- 修改：`docs/plans/2025-02-27-setup-skill-refactor.md`

> **给 Agent：** 此任务是文档修正，不需要 `dev-tdd`。

**步骤 1：仅修正“当前主路径”类示例**

需要修正的内容：
- `ln -sf "$(pwd)/kimi/skills" ~/.agents/skills`
- `vim kimi/skills/...`
- “use kimi/skills as single source” 之类表述

**步骤 2：保留历史上下文**

如果某些段落是在描述当时旧方案，应保留其历史语境，但要避免让读者误以为这是当前仓库结构。必要时在文档开头补充一句说明：该计划包含历史路径示例，已按当前结构更新主路径名。

### 任务 5：全仓检索与收尾验证

**文件：**
- 验证：全仓关键文档与目录

> **给 Agent：** 此任务是验证，不需要 `dev-tdd`。

**步骤 1：检查关键残留引用**

运行：

```bash
rg -n "kimi/skills" . --glob '!upstream/**'
```

预期：
- 不再出现在 README、AGENTS、setup、架构文档等当前事实文档中
- 若仍出现在历史记录型计划文档，必须确认是否属于有意保留

**步骤 2：检查目标结构**

运行：

```bash
test -d skills
test -d kimi/agents/superpower
test ! -d kimi/skills
```

预期：全部通过；如果选择保留兼容 symlink，则最后一条改为 `test -L kimi/skills`

**步骤 3：检查需要同步的 agent 文档**

运行：

```bash
find . -type f \( -name 'AGENTS.md' -o -name 'CLAUDE.md' \) | sort
```

预期：确认本次只需更新仓库根 `AGENTS.md`

**步骤 4：查看工作区改动**

运行：`git status --short`
预期：只包含本次目录迁移与文档更新

## 审查说明

根据 `dev-writing-plans`，计划写完后应进入 reviewer 审查闭环。本会话未获得用户对 subagent/并行代理的明确授权，因此不执行 plan-document-reviewer subagent。进入实施前由主会话人工自检计划范围、路径和验证步骤。

## 执行交接

计划已完成并保存到 `docs/plans/2026-03-20-shared-skills-directory-implementation-plan.md`。

下一步在本会话中使用 `dev-executing-plans` 按任务顺序执行：

1. 迁移共享 skill 目录
2. 更新安装与结构文档
3. 更新架构文档
4. 清理遗留路径示例
5. 运行全仓验证
