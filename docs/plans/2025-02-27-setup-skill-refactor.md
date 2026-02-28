# Setup Skill 重构实施计划

> **给 Kimi：** 必需子 skill：使用 `dev-executing-plans` 逐个任务实施此计划。

**目标：** 重构安装方式：删除 `scripts/install.sh` 和 `Makefile`，创建 `.skills/setup/SKILL.md` 实现 symlink 安装，统一安装到 `~/.agents/skills/`，删除重复的 `codex/` 目录。

**架构：** 创建 setup skill 驱动安装流程，使用 symlink 而非复制实现实时同步。Kimi 独有的 agent 配置也使用 symlink。

**技术栈：** Bash, Skill 规范 (Agent Skills), Symlink

---

## 任务 1：创建 setup skill 目录结构

**文件：**
- 创建：`.skills/setup/SKILL.md`

**步骤 1：创建目录**

```bash
mkdir -p .skills/setup
```

**步骤 2：验证目录创建**

```bash
ls -la .skills/
```
预期输出：包含 `setup/` 目录

**步骤 3：提交**

```bash
git add .skills/
git commit -m "chore: add setup skill directory structure"
```

---

## 任务 2：编写 setup/SKILL.md

**文件：**
- 创建：`.skills/setup/SKILL.md`

**步骤 1：编写 skill 文件**

内容如下：
```markdown
---
name: setup
description: 安装 coding-everything 配置到系统。当用户需要安装 skills、初始化配置或运行 setup 时使用。
license: MIT
---

# Setup: 安装 Coding Everything 配置

安装个人 AI 编程助手配置到系统，使用 symlink 模式实现实时同步。

## 安装流程

### 1. 检查源目录

确认项目目录结构完整：
- `kimi/skills/` - skill 目录
- `kimi/agents/superpower/` - Kimi Agent 配置

### 2. 创建目标目录

```bash
mkdir -p ~/.agents
mkdir -p ~/.kimi/agents
```

### 3. 创建 Symlink

**Skills（所有 Agent 工具共享）：**
```bash
ln -sf "$(pwd)/kimi/skills" ~/.agents/skills
```

**Agent 配置（仅 Kimi）：**
```bash
ln -sf "$(pwd)/kimi/agents/superpower" ~/.kimi/agents/superpower
```

### 4. 验证安装

检查 symlink 是否正确创建：
```bash
ls -la ~/.agents/skills
ls -la ~/.kimi/agents/superpower
```

### 5. 输出结果

显示安装状态：
- Skills 数量
- Agent 配置状态
- 使用方法

## 使用方式

安装完成后：

**Kimi CLI:**
```bash
kimi --agent-file ~/.kimi/agents/superpower/agent.yaml
```

**Codex:**
```bash
codex
```

**OpenCode:**
```bash
opencode
```

## 实时同步

由于使用 symlink，修改项目中的 skill 文件会立即生效：

```bash
vim kimi/skills/dev-tdd/SKILL.md  # 修改后立即生效
```

## 卸载

如需卸载，删除 symlink 即可：

```bash
rm ~/.agents/skills
rm -rf ~/.kimi/agents/superpower
```
```

**步骤 2：验证文件创建**

```bash
ls -la .skills/setup/
head -20 .skills/setup/SKILL.md
```

**步骤 3：提交**

```bash
git add .skills/setup/SKILL.md
git commit -m "feat: add setup skill for symlink-based installation"
```

---

## 任务 3：删除 codex/ 目录

**文件：**
- 删除：`codex/` 整个目录

**步骤 1：确认 codex/ 与 kimi/skills/ 内容一致**

```bash
diff -r kimi/skills/ codex/skills/ | head -20
```
预期：输出为空或只有 SKILL.md 中的细微差异（如 dev-update-codemaps 只在 kimi 中）

**步骤 2：删除 codex/ 目录**

```bash
rm -rf codex/
```

**步骤 3：验证删除**

```bash
ls -d codex/ 2>&1
```
预期输出：`No such file or directory`

**步骤 4：提交**

```bash
git rm -rf codex/
git commit -m "refactor: remove codex/ directory, use kimi/skills/ as single source"
```

---

## 任务 4：删除 scripts/install.sh

**文件：**
- 删除：`scripts/install.sh`
- 修改：`scripts/`（如为空则删除目录）

**步骤 1：删除 install.sh**

```bash
rm scripts/install.sh
```

**步骤 2：检查 scripts/ 目录是否为空**

```bash
ls -la scripts/
```

**步骤 3：如为空，删除整个 scripts/ 目录**

```bash
rmdir scripts/ 2>/dev/null || echo "Directory not empty or has other files"
```

**步骤 4：提交**

```bash
git rm scripts/install.sh
[ -d scripts/ ] && git rm -rf scripts/ || true
git commit -m "refactor: remove install.sh, replaced by setup skill"
```

---

## 任务 5：删除 Makefile

**文件：**
- 删除：`Makefile`

**步骤 1：删除 Makefile**

```bash
rm Makefile
```

**步骤 2：验证删除**

```bash
ls Makefile 2>&1
```
预期输出：`No such file or directory`

**步骤 3：提交**

```bash
git rm Makefile
git commit -m "refactor: remove Makefile, replaced by setup skill"
```

---

## 任务 6：更新 AGENTS.md 安装文档

**文件：**
- 修改：`AGENTS.md`

**步骤 1：更新"快速安装"章节**

将原来的 Makefile 方式替换为 skill 方式：

```markdown
### 快速安装

使用 setup skill（推荐）：

```bash
cd coding-everything
/skill:setup
```

或直接执行：

```bash
ln -sf "$(pwd)/kimi/skills" ~/.agents/skills
ln -sf "$(pwd)/kimi/agents/superpower" ~/.kimi/agents/superpower
```
```

**步骤 2：删除旧章节**

删除以下章节：
- "安装脚本功能"
- Makefile 相关命令
- install.sh 相关说明

**步骤 3：更新"项目结构"章节**

更新目录结构，删除 codex/、scripts/、Makefile 的引用。

**步骤 4：验证修改**

```bash
grep -n "Makefile\|install.sh\|make install" AGENTS.md
```
预期：无匹配（或仅剩历史记录）

**步骤 5：提交**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md with new setup skill installation"
```

---

## 任务 7：测试 setup skill 安装流程

**文件：**
- 验证：`.skills/setup/SKILL.md`

**步骤 1：备份现有配置（如有）**

```bash
[ -L ~/.agents/skills ] && mv ~/.agents/skills ~/.agents/skills.backup.$(date +%s)
[ -L ~/.kimi/agents/superpower ] && mv ~/.kimi/agents/superpower ~/.kimi/agents/superpower.backup.$(date +%s)
```

**步骤 2：执行 setup skill 指令**

创建目录：
```bash
mkdir -p ~/.agents
mkdir -p ~/.kimi/agents
```

创建 symlink：
```bash
ln -sf "$(pwd)/kimi/skills" ~/.agents/skills
ln -sf "$(pwd)/kimi/agents/superpower" ~/.kimi/agents/superpower
```

**步骤 3：验证 symlink**

```bash
ls -la ~/.agents/skills
ls -la ~/.kimi/agents/superpower
```
预期输出：显示 symlink 指向项目目录

**步骤 4：验证 skills 加载**

```bash
ls ~/.agents/skills/
```
预期输出：显示 dev-using-skills、dev-tdd 等目录

**步骤 5：测试实时同步**

```bash
echo "# Test" >> kimi/skills/dev-tdd/SKILL.md
grep "# Test" ~/.agents/skills/dev-tdd/SKILL.md
```
预期：能找到添加的测试内容

**步骤 6：清理测试修改**

```bash
git checkout kimi/skills/dev-tdd/SKILL.md
```

**步骤 7：提交（如有文档更新）**

```bash
git add -A
git commit -m "test: verify setup skill installation workflow" || echo "No changes to commit"
```

---

## 完成标准

- [ ] `.skills/setup/SKILL.md` 存在且符合规范
- [ ] `codex/` 目录已删除
- [ ] `scripts/install.sh` 已删除
- [ ] `Makefile` 已删除
- [ ] `AGENTS.md` 已更新安装说明
- [ ] Symlink 安装工作正常
- [ ] 所有测试通过

---

## 回滚方案

如需回滚：
1. 从 git 历史恢复删除的文件
2. 删除 `.skills/setup/`
3. 删除 symlink
4. 恢复旧安装方式
