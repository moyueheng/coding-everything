---
name: dev-tdd
description: 实现任何功能或修复 bug 前使用，在编写实现代码之前 - 测试驱动开发
---

# 测试驱动开发（TDD）

## 概述

先写测试。看着它失败。编写最小代码使其通过。

**核心原则：** 如果你没有看着测试失败，你就不知道它是否测试了正确的东西。

**违反规则的文字就是违反规则的精神。**

## 何时使用

**始终：**
- 新功能
- Bug 修复
- 重构
- 行为变更

**例外（询问用户）：**
- 一次性原型
- 生成的代码
- 配置文件

想"就这一次跳过 TDD"？停下来。那是合理化。

## 铁律

```
没有先有失败的测试，就没有生产代码
```

先写代码再写测试？删除它。重新开始。

**没有例外：**
- 不要保留作为"参考"
- 不要写测试时"适配"它
- 不要看它
- 删除意味着删除

从测试重新实现。就这样。

## 红-绿-重构循环

```dot
digraph tdd_cycle {
    rankdir=LR;
    red [label="红\n编写失败测试", shape=box, style=filled, fillcolor="#ffcccc"];
    verify_red [label="验证失败\n正确", shape=diamond];
    green [label="绿\n最小代码", shape=box, style=filled, fillcolor="#ccffcc"];
    verify_green [label="验证通过\n全部绿色", shape=diamond];
    refactor [label="重构\n清理", shape=box, style=filled, fillcolor="#ccccff"];
    next [label="下一个", shape=ellipse];

    red -> verify_red;
    verify_red -> green [label="是"];
    verify_red -> red [label="错误\n失败"];
    green -> verify_green;
    verify_green -> refactor [label="是"];
    verify_green -> green [label="否"];
    refactor -> verify_green [label="保持\n绿色"];
    verify_green -> next;
    next -> red;
}
```

## 红-绿-重构详情

### 红 - 编写失败测试

编写一个最小测试展示应该发生什么。

**好的例子：**
```typescript
test('失败操作重试 3 次', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```
名称清晰，测试真实行为，一件事

**坏的例子：**
```typescript
test('重试有效', async () => {
  const mock = jest.fn()
    .mockRejectedValueOnce(new Error())
    .mockRejectedValueOnce(new Error())
    .mockResolvedValueOnce('success');
  await retryOperation(mock);
  expect(mock).toHaveBeenCalledTimes(3);
});
```
名称模糊，测试的是 mock 而不是代码

**要求：**
- 一个行为
- 名称清晰
- 真实代码（除非不可避免，否则不要用 mock）

### 验证红 - 看着它失败

**强制。绝不跳过。**

```bash
npm test path/to/test.test.ts
```

确认：
- 测试失败（不是错误）
- 失败消息是预期的
- 因功能缺失而失败（不是拼写错误）

**测试通过了？** 你在测试已有行为。修复测试。

**测试报错？** 修复错误，重新运行直到正确失败。

### 绿 - 最小代码

编写最简单的代码使测试通过。

**好的例子：**
```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error('unreachable');
}
```
刚好够通过

**坏的例子：**
```typescript
async function retryOperation<T>(
  fn: () => Promise<T>,
  options?: {
    maxRetries?: number;
    backoff?: 'linear' | 'exponential';
    onRetry?: (attempt: number) => void;
  }
): Promise<T> {
  // YAGNI
}
```
过度工程

不要添加功能、重构其他代码，或"改进"超出测试范围。

### 验证绿 - 看着它通过

**强制。**

```bash
npm test path/to/test.test.ts
```

确认：
- 测试通过
- 其他测试仍通过
- 输出干净（无错误、警告）

**测试失败？** 修复代码，不是测试。

**其他测试失败？** 立即修复。

### 重构 - 清理

仅在绿之后：
- 删除重复
- 改进名称
- 提取辅助函数

保持测试绿。不要添加行为。

### 重复

下一个失败测试对应下一个功能。

## 好的测试

| 质量 | 好 | 坏 |
|------|-----|-----|
| **最小** | 一件事。名称中有"和"？拆分。 | `test('验证邮箱和域名和空白')` |
| **清晰** | 名称描述行为 | `test('test1')` |
| **展示意图** | 展示期望的 API | 模糊代码应该做什么 |

## 为什么顺序重要

**"我稍后写测试来验证它有效"**

稍后写的测试立即通过。立即通过证明不了什么：
- 可能测试错了东西
- 可能测试实现而不是行为
- 可能漏掉你忘记的边界情况
- 你从没看到它捕获 bug

先测试迫使你看到测试失败，证明它确实测试了某些东西。

**"我已经手动测试了所有边界情况"**

手动测试是临时的。你以为你测试了所有东西但：
- 没有测试记录
- 代码更改时无法重新运行
- 压力下容易忘记情况
- "我试的时候有效" ≠ 全面

自动化测试是系统的。每次运行方式相同。

## 常见合理化借口

| 借口 | 现实 |
|--------|--------|
| "太简单不用测" | 简单代码也会坏。测试只需 30 秒。 |
| "我稍后测试" | 立即通过的测试证明不了什么。 |
| "稍后测试达到同样目标" | 稍后测试 = "这做什么？" 先测试 = "这应该做什么？" |
| "已经手动测过了" | 临时 ≠ 系统。无记录，无法重新运行。 |
| "删除 X 小时工作是浪费" | 沉没成本谬误。时间已经花了。选择：删除用 TDD 重写（高信心）vs 保留稍后加测试（低信心，可能有 bug）。 |

## 红旗 - 停止并重新开始

- 代码在测试前
- 实现后写测试
- 测试立即通过
- 无法解释测试为什么失败
- "稍后"加测试
- 合理化"就这一次"
- "已经手动测过了"
- "稍后测试达到同样目的"
- "是关于精神不是仪式"
- "保留作为参考"或"适配现有代码"
- "已经花了 X 小时，删除是浪费"
- "TDD 是教条，我是务实的"
- "这次不同因为..."

**所有这些意味着：删除代码。用 TDD 重新开始。**

## 验证清单

标记工作完成前：

- [ ] 每个新函数/方法都有测试
- [ ] 实现前看着每个测试失败
- [ ] 每个测试因预期原因失败（功能缺失，不是拼写错误）
- [ ] 编写最小代码使每个测试通过
- [ ] 所有测试通过
- [ ] 输出干净（无错误、警告）
- [ ] 测试使用真实代码（仅必要时用 mock）
- [ ] 覆盖边界情况和错误

无法勾选所有？你跳过了 TDD。重新开始。

## 卡住时

| 问题 | 解决方案 |
|---------|----------|
| 不知道怎么测试 | 写期望的 API。先写断言。询问用户。 |
| 测试太复杂 | 设计太复杂。简化接口。 |
| 必须 mock 所有东西 | 代码太耦合。用依赖注入。 |
| 测试 setup 庞大 | 提取辅助函数。还复杂？简化设计。 |

## 与其他 skill 的集成

### 与 dev-debugging 集成

在系统化调试中，找到根本原因后，**必须使用 dev-tdd**：

1. **Phase 4 步骤 1** - 创建失败测试用例时：使用 `dev-tdd` skill 编写正确的失败测试
2. 遵循 RED-GREEN-REFACTOR 循环实现修复
3. 测试证明了修复并防止回归

**永远不要无测试修复 bug。**

### 与 dev-writing-plans 集成

编写计划时，每个任务的步骤应体现 TDD：
- 步骤 1: 编写失败的测试（红）
- 步骤 2: 运行测试验证失败（验证红）
- 步骤 3: 编写最小实现（绿）
- 步骤 4: 运行测试验证通过（验证绿）
- 步骤 5: 重构清理（可选）
- 步骤 6: 提交

### 与 dev-executing-plans 集成

执行计划中的每个任务时：
- 如果计划中的步骤包含"编写测试"，则 **调用 dev-tdd skill**
- 严格按照 TDD 循环执行，不要跳过验证步骤
- 测试失败时必须先解决才能继续下一步

## 最后规则

```
生产代码 → 测试存在且先失败
否则 → 不是 TDD
```

未经用户许可没有例外。
