# dev-code-cleanup Skill Implementation Plan

> **给 Kimi：** 必需子 skill：使用 `dev-executing-plans` 逐个任务实施此计划。

**目标：** 将 upstream/everything-claude-code/commands/refactor-clean.md 转换为符合标准的 Kimi skill

**架构：** 基于现有 command 内容，按照 dev-writing-skills 规范重构为 SKILL.md 格式，包含 YAML frontmatter、概述、流程、工具参考等标准章节

**技术栈：** Markdown, YAML frontmatter, Graphviz (可选流程图)

---

### 任务 1：分析源文件结构

**文件：**
- 读取：`upstream/everything-claude-code/commands/refactor-clean.md`
- 创建：`kimi/skills/dev-code-cleanup/SKILL.md`

**步骤 1：读取并分析源文件内容**

运行：`cat upstream/everything-claude-code/commands/refactor-clean.md`

预期：获取 command 的完整内容，包括检测工具、分类策略、删除流程等

**步骤 2：提取核心内容模块**

识别以下模块：
- 死代码检测工具列表 (knip, depcheck, ts-prune, vulture, deadcode)
- 三级分类策略 (SAFE/CAUTION/DANGER)
- 安全删除循环流程
- 重复代码合并步骤
- 规则和约束

**步骤 3：提交**

```bash
git add docs/plans/2025-02-27-dev-code-cleanup-skill.md
git commit -m "docs: add implementation plan for dev-code-cleanup skill"
```

---

### 任务 2：创建 Skill 目录结构

**文件：**
- 创建目录：`kimi/skills/dev-code-cleanup/`
- 创建文件：`kimi/skills/dev-code-cleanup/SKILL.md`

**步骤 1：创建目录**

运行：`mkdir -p kimi/skills/dev-code-cleanup`

预期：目录创建成功

**步骤 2：提交**

```bash
git add kimi/skills/dev-code-cleanup/
git commit -m "chore: create dev-code-cleanup skill directory"
```

---

### 任务 3：编写 SKILL.md Frontmatter

**文件：**
- 修改：`kimi/skills/dev-code-cleanup/SKILL.md`

**步骤 1：编写 YAML Frontmatter**

```markdown
---
name: dev-code-cleanup
description: 当需要清理代码库中的死代码、未使用导出、重复代码或未使用依赖时使用 - 安全地识别和删除无用代码
---
```

**要求：**
- name 只使用字母、数字和连字符
- description 以"何时使用..."开头
- description 描述触发条件，不总结流程
- 总字符数不超过 1024

**步骤 2：提交**

```bash
git add kimi/skills/dev-code-cleanup/SKILL.md
git commit -m "feat: add dev-code-cleanup skill frontmatter"
```

---

### 任务 4：编写概述和何时使用章节

**文件：**
- 修改：`kimi/skills/dev-code-cleanup/SKILL.md`

**步骤 1：编写概述**

```markdown
# 代码清理

## 概述

系统化识别和删除死代码、未使用依赖和重复代码。通过工具检测、分级分类和测试验证确保安全清理。

**核心原则：** 工具检测 → 风险分级 → 测试验证 → 安全删除
```

**步骤 2：编写何时使用章节**

```markdown
## 何时使用

**使用场景：**
- 代码库中存在未使用的函数、变量或导出
- 需要移除未使用的 npm/pip/cargo 依赖
- 发现重复或近重复的代码块
- 项目维护阶段需要减少技术债务
- 构建产物过大需要优化

**不使用场景：**
- 正在活跃开发新功能期间
- 即将部署到生产环境前
- 代码缺乏测试覆盖
- 不熟悉代码库架构时
```

**步骤 3：提交**

```bash
git add kimi/skills/dev-code-cleanup/SKILL.md
git commit -m "feat: add overview and when-to-use sections"
```

---

### 任务 5：编写检测工具快速参考表

**文件：**
- 修改：`kimi/skills/dev-code-cleanup/SKILL.md`

**步骤 1：编写工具参考表**

```markdown
## 检测工具

| 工具 | 语言/框架 | 检测内容 | 安装/运行 |
|------|----------|----------|----------|
| knip | TypeScript/JavaScript | 未使用文件、导出、依赖 | `npx knip` |
| depcheck | Node.js | 未使用 npm 依赖 | `npx depcheck` |
| ts-prune | TypeScript | 未使用 TypeScript 导出 | `npx ts-prune` |
| vulture | Python | 未使用 Python 代码 | `vulture src/` |
| deadcode | Go | 未使用 Go 代码 | `deadcode ./...` |
| cargo-udeps | Rust | 未使用 Rust 依赖 | `cargo +nightly udeps` |

**无工具时：** 使用 Grep 搜索导出定义，然后检查是否有导入引用
```

**步骤 2：提交**

```bash
git add kimi/skills/dev-code-cleanup/SKILL.md
git commit -m "feat: add detection tools reference table"
```

---

### 任务 6：编写风险分级和清理流程

**文件：**
- 修改：`kimi/skills/dev-code-cleanup/SKILL.md`

**步骤 1：编写风险分级**

```markdown
## 风险分级

| 级别 | 示例 | 处理方式 |
|------|------|----------|
| **SAFE** | 未使用的工具函数、内部辅助函数、测试工具 | 可安全删除 |
| **CAUTION** | 组件、API 路由、中间件 | 检查动态导入和外部调用者 |
| **DANGER** | 配置文件、入口点、类型定义 | 深入调查后再操作 |
```

**步骤 2：编写清理流程**

```markdown
## 清理流程

### 1. 检测

运行适合项目的检测工具：
```bash
# TypeScript/JavaScript
npx knip
npx depcheck
npx ts-prune

# Python
vulture src/

# Go
deadcode ./...
```

### 2. 分类

将发现的问题按风险分级归类。

### 3. 安全删除 (SAFE 级别)

对每个 SAFE 项目：
1. **运行完整测试套件** - 建立基线
2. **删除死代码** - 使用精准编辑
3. **重新运行测试** - 验证无破坏
4. **测试失败** → 立即 `git checkout -- <file>` 恢复并跳过
5. **测试通过** → 继续下一个

### 4. 谨慎处理 (CAUTION 级别)

删除前检查：
- 动态导入：`import()`, `require()`, `__import__`
- 字符串引用：路由名、配置中的组件名
- 是否从公共 API 导出
- 外部消费者（如果是发布包）

### 5. 合并重复代码

删除死代码后，检查：
- 相似度 >80% 的函数 → 合并为一个
- 冗余类型定义 → 统一
- 无价值的包装函数 → 内联
- 无意义的重导出 → 移除间接层
```

**步骤 3：提交**

```bash
git add kimi/skills/dev-code-cleanup/SKILL.md
git commit -m "feat: add risk classification and cleanup workflow"
```

---

### 任务 7：编写规则和常见错误

**文件：**
- 修改：`kimi/skills/dev-code-cleanup/SKILL.md`

**步骤 1：编写规则**

```markdown
## 规则

- **绝不未经测试就删除** - 始终先运行测试建立基线
- **一次只删一项** - 原子变更便于回滚
- **不确定就跳过** - 保留死代码好过破坏生产
- **清理时不重构** - 先清理，再重构，分离关注点
```

**步骤 2：编写常见错误**

```markdown
## 常见错误

**未经测试直接删除**
- **问题：** 误删正在使用的代码导致功能损坏
- **修复：** 始终先运行完整测试套件建立基线

**批量删除多个项目**
- **问题：** 出错时难以定位具体问题
- **修复：** 一次处理一个，逐个验证

**忽略动态导入**
- **问题：** 字符串形式的导入未被静态分析捕获
- **修复：** CAUTION 级别项目搜索 `import()` 和字符串引用

**清理时顺便重构**
- **问题：** 混合关注点，出错时难以回滚
- **修复：** 先完成清理，再单独进行重构
```

**步骤 3：提交**

```bash
git add kimi/skills/dev-code-cleanup/SKILL.md
git commit -m "feat: add rules and common mistakes sections"
```

---

### 任务 8：编写报告格式和总结

**文件：**
- 修改：`kimi/skills/dev-code-cleanup/SKILL.md`

**步骤 1：编写报告格式**

```markdown
## 清理报告模板

```
死代码清理报告
──────────────────────────────
已删除:
  - 12 个未使用函数
  - 3 个未使用文件
  - 5 个未使用依赖

已跳过:
  - 2 个项目 (测试失败)

节省:
  - 约 450 行代码
  - 约 200KB 构建产物

状态: 所有测试通过 ✅
──────────────────────────────
```
```

**步骤 2：提交**

```bash
git add kimi/skills/dev-code-cleanup/SKILL.md
git commit -m "feat: add report template"
```

---

### 任务 9：更新 AGENTS.md 文档

**文件：**
- 修改：`AGENTS.md`

**步骤 1：在技能列表中添加新 skill**

在 AGENTS.md 的"技能列表"表格中添加：

```markdown
| `dev-code-cleanup` | 代码清理和死代码删除 | 严格 |
```

**步骤 2：提交**

```bash
git add AGENTS.md
git commit -m "docs: add dev-code-cleanup to skills list in AGENTS.md"
```

---

### 任务 10：创建软链接（可选）

**文件：**
- 软链接：`~/.agents/skills/dev-code-cleanup`

**步骤 1：检查现有软链接结构**

运行：`ls -la ~/.agents/skills/`

**步骤 2：创建软链接**

```bash
ln -sf "$(pwd)/kimi/skills/dev-code-cleanup" ~/.agents/skills/dev-code-cleanup
```

预期：软链接创建成功

**步骤 3：验证**

运行：`ls -la ~/.agents/skills/dev-code-cleanup/`

预期：能看到 SKILL.md 文件

---

## 质量检查清单

- [ ] SKILL.md 包含 YAML frontmatter (name, description)
- [ ] name 只使用字母、数字和连字符
- [ ] description 以"何时使用..."开头，不超过 1024 字符
- [ ] 目录名与 frontmatter name 完全一致
- [ ] 包含概述章节，1-2 句话说明核心原则
- [ ] 包含何时使用章节，明确使用和不使用场景
- [ ] 包含快速参考表（检测工具、风险分级）
- [ ] 包含实现流程（检测 → 分类 → 删除 → 合并）
- [ ] 包含规则章节
- [ ] 包含常见错误章节
- [ ] AGENTS.md 已更新
- [ ] 遵循命名前缀规范 `dev-`

---

## 执行完成标准

1. `kimi/skills/dev-code-cleanup/SKILL.md` 文件完整
2. 文件遵循 dev-writing-skills 规范
3. AGENTS.md 技能列表已更新
4. 所有变更已提交到 git
