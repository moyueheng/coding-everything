---
name: dev-writing-plans
description: 当有多步骤任务的规范或需求时，在接触代码前使用 - 创建全面的实施计划
---

# 编写实施计划

## 概述

编写全面的实施计划，假设工程师对代码库零了解。记录他们需要知道的一切：每个任务要修改哪些文件、代码、测试、可能需要查看的文档、如何测试。将整个计划拆分成小任务。遵循 DRY、YAGNI、TDD。频繁提交。

假设他们是熟练开发者，但几乎不了解我们的工具集或问题领域。假设他们对 good test design 也不太熟。

**开始时宣布：** "I'm using the dev-writing-plans skill to create the implementation plan."

**上下文：** 这应该在专用 worktree 中运行（由 dev-brainstorming skill 创建）。

**保存计划到：** `docs/plans/YYYY-MM-DD-<feature-name>.md`
- （用户对计划位置的偏好覆盖此默认值）

## 范围检查

如果 spec 涵盖多个独立子系统，它应该在头脑风暴期间就被拆分为子项目 spec。如果没有，建议将其拆分为单独的计划 —— 每个子系统一个计划。每个计划应该独立产生可工作的、可测试的软件。

## 计划自审（Self-Review）

计划不是写完就结束。写完后必须立刻进行自我审查：

用 fresh eyes 对照 spec 检查计划，这是一个你自己运行的 checklist —— 不是分派 subagent：

**1. Spec 覆盖度：** 浏览 spec 的每个章节/需求。能否指出实现它的任务？列出任何遗漏项。

**2. 占位符扫描：** 搜索计划中的红旗 —— "TBD"、"TODO"、"稍后实现"、"添加适当的错误处理"、"类似于任务 N"（却不重复代码）等。修复它们。

**3. 类型一致性：** 后面任务中使用的类型、方法签名、属性名是否与前面任务定义的一致？任务 3 叫 `clearLayers()` 但任务 7 叫 `clearFullLayers()` 就是一个 bug。

如果发现问题，直接 inline 修复。无需重新审查 —— 修复后继续。如果发现某个 spec 需求没有对应任务，添加该任务。

## 小任务粒度

**每一步是一个动作（2-5 分钟）：**
- "编写失败的测试" - 一步
- "运行测试确保它失败" - 一步
- "编写最小代码使测试通过" - 一步
- "运行测试确保通过" - 一步
- "提交" - 一步

## TDD 要求

**每个实现任务必须使用 TDD：**
- 任务涉及编写代码时，**步骤必须体现 RED-GREEN-REFACTOR 循环**
- 步骤应明确引用 `dev-tdd` skill
- 不要假设执行者知道 TDD - 给出具体的测试代码和预期输出

## 计划文档头部

**每个计划必须以这个头部开始：**

```markdown
# [Feature Name] Implementation Plan

> **给 Agent：** 必需子 skill：使用 `dev-executing-plans` 逐个任务实施此计划。

**目标：** [一句话描述要构建什么]

**架构：** [2-3 句话关于方案]

**技术栈：** [关键技术/库]

---
```

## 任务结构

```markdown
### 任务 N：[组件名称]

**文件：**
- 创建：`exact/path/to/file.py`
- 修改：`exact/path/to/existing.py:123-145`
- 测试：`tests/exact/path/to/test.py`

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1：RED - 编写失败的测试**

**调用 dev-tdd**：编写一个最小测试展示应该发生什么。

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**步骤 2：验证 RED - 看着它失败**

**调用 dev-tdd**：运行测试确认它因正确原因失败。

运行：`pytest tests/path/test.py::test_name -v`
预期：FAIL with "function not defined"

**步骤 3：GREEN - 编写最小实现**

**调用 dev-tdd**：编写最简单的代码使测试通过。

```python
def function(input):
    return expected
```

**步骤 4：验证 GREEN - 看着它通过**

**调用 dev-tdd**：运行测试确认通过且其他测试未损坏。

运行：`pytest tests/path/test.py::test_name -v`
预期：PASS

**步骤 5：REFACTOR（可选）**

**调用 dev-tdd**：清理代码，保持测试绿色。
- 删除重复
- 改进名称
- 提取辅助函数

**步骤 6：提交**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```

## 文件结构

在定义任务之前，先规划哪些文件将被创建或修改，以及每个文件的职责。这是分解决策被锁定的地方。

- 设计具有清晰边界和良好定义接口的单元。每个文件应该有一个清晰的职责。
- 你最能理解那些能一次性在上下文中掌握的代码，当文件聚焦时，你的编辑也更可靠。优先选择更小、更聚焦的文件，而不是做太多事情的大文件。
- 一起变化的文件应该放在一起。按职责拆分，而不是按技术层拆分。
- 在现有代码库中，遵循既定模式。如果代码库使用大文件，不要单方面重构 —— 但如果你修改的文件已经变得笨重，在计划中包含拆分是合理的。

这种结构指导任务分解。每个任务应该产生独立的、有意义的变更。

## 记住
- 始终使用精确文件路径
- 计划中包含完整代码（不是"添加验证"）
- 精确命令及预期输出
- **每个实现任务必须引用 `dev-tdd` skill**
- 计划中的测试代码要完整可运行
- DRY、YAGNI、TDD、频繁提交

## TDD 集成说明

### 为什么必须引用 dev-tdd

编写计划时，你**必须**在每个实现任务中引用 `dev-tdd` skill：

1. **执行者可能不熟悉 TDD** - 显式引用确保他们遵循正确的流程
2. **RED-GREEN-REFACTOR 必须完整** - 跳过"验证失败"步骤是常见的错误
3. **测试是设计工具** - 测试定义了期望的 API 和行为

### 计划中引用 dev-tdd 的方式

每个实现任务应包含：

```markdown
> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1: RED - 编写失败的测试**
**调用 dev-tdd**: ...

**步骤 2: 验证 RED - 看着它失败**
**调用 dev-tdd**: ...
```

### 没有测试的任务

纯配置、文档或基础设施任务不需要 TDD：
- 添加配置文件
- 更新文档
- 设置 CI/CD pipeline

但只要有代码逻辑，**就必须使用 TDD**。

## 执行交接

保存计划后，提供执行选择：

**"计划已完成并保存到 `docs/plans/<文件名>.md`。两种执行选项：**

**1. Subagent-Driven（推荐）** - 我为每个任务分派 fresh subagent，任务间审查，快速迭代

**2. 内联执行** - 在本会话中使用 dev-executing-plans 执行任务，批量执行带检查点

**选择哪种方式？"**

**如果选择 Subagent-Driven：**
- **必需子 skill：** 使用 `dev-executing-plans` 或专用的 subagent-driven 模式
- 每个任务 fresh subagent + 任务间审查

**如果选择内联执行：**
- 在 worktree 中引导他们打开新会话
- **必需子 skill：** 新会话使用 `dev-executing-plans`

## 计划完成前禁止事项

- 不要把“实现细节待定”留给执行阶段现场决定
- 不要省略高风险步骤的验证方式
- 不要让一个任务同时改多个大模块，除非设计文档已经明确说明
- 不要在计划未通过审查前交给执行
