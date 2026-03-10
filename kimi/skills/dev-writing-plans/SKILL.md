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

## 计划审查闭环

计划不是写完就结束。写完后必须立刻进入审查循环：

1. 以审稿人视角检查计划
2. 发现问题就修计划
3. 重新审查
4. 通过后才交给 `dev-executing-plans`

计划审查至少覆盖：

- 是否与设计文档一致
- 是否已拆到 2-5 分钟级别
- 是否提前映射了文件边界和职责
- 是否每个实现任务都包含可执行的 TDD 闭环
- 是否把高风险/高不确定任务拆开，而不是混成大步

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

## 分段编写，分段审查

不要把整份计划一口气写完再看。正确顺序是：

```text
计划头部
  ->
文件结构与边界
  ->
一组任务
  ->
立即审查这一组任务
  ->
继续下一组任务
```

每写完一段，都要检查：

- 这段是否仍然和设计一致
- 任务是否过大
- 路径是否精确
- 是否存在隐式耦合
- 执行者是否能在不脑补的情况下直接执行
```

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

**1. Subagent-Driven（本会话）** - 我为每个任务分派 fresh subagent，任务间审查，快速迭代(Agent的subagent默认就是 fresh subagent 不需要额外设置)

**2. 并行会话（分开）** - 打开新会话使用 dev-executing-plans，批量执行带检查点

**选择哪种方式？"**

**如果选择 Subagent-Driven：**
- **必需子 skill：** 使用 `dev-subagent-driven-development`
- 保持在本会话
- 每个任务 fresh subagent + 代码审查

**如果选择并行会话：**
- 引导他们在 worktree 中打开新会话
- **必需子 skill：** 新会话使用 `dev-executing-plans`

## 计划完成前禁止事项

- 不要把“实现细节待定”留给执行阶段现场决定
- 不要省略高风险步骤的验证方式
- 不要让一个任务同时改多个大模块，除非设计文档已经明确说明
- 不要在计划未通过审查前交给执行
