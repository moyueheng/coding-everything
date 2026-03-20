---
name: dev-finishing-branch
description: 实现完成、所有测试通过且需要决定如何集成工作时使用 - 指导完成开发工作
---

# 完成开发分支

## 概述

通过展示清晰选项和处理选定工作流来指导开发工作的完成。

**核心原则：** 验证测试 → 展示选项 → 执行选择 → 清理。

**开始时宣布：** "我正在使用完成开发分支 skill 来完成此工作。"

## 流程

### 步骤 1：验证测试

**展示选项前，验证测试通过：**

```bash
# 运行项目测试套件
npm test / cargo test / pytest / go test ./...
```

**如果测试失败：**
```
测试失败（<N> 失败）。必须先修复：

[显示失败]

测试通过前无法继续合并/PR。
```

停止。不要继续步骤 2。

**如果测试通过：** 继续步骤 2。

### 步骤 2：确定基础分支

```bash
# 尝试常见基础分支
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

或问："此分支从 main 分离 - 正确吗？"

### 步骤 3：展示选项

精确展示这 4 个选项：

```
实现完成。你想做什么？

1. 本地合并回 <base-branch>
2. 推送并创建 Pull Request
3. 保持分支原样（我稍后处理）
4. 丢弃此工作

选择哪个选项？
```

**不要添加解释** - 保持选项简洁。

### 步骤 4：执行选择

#### 选项 1：本地合并

```bash
# 切换到基础分支
git checkout <base-branch>

# 拉取最新
git pull

# 合并功能分支
git merge <feature-branch>

# 验证合并结果上的测试
<test command>

# 如果测试通过
git branch -d <feature-branch>
```

然后：清理 worktree（步骤 5）

#### 选项 2：推送并创建 PR

```bash
# 推送分支
git push -u origin <feature-branch>

# 创建 PR
gh pr create --title "<标题>" --body "$(cat <<'EOF'
## 总结
<2-3 点变更内容>

## 测试计划
- [ ] <验证步骤>
EOF
)"
```

然后：清理 worktree（步骤 5）

#### 选项 3：保持原样

报告："保持分支 <名称>。Worktree 保留在 <路径>。"

**不要清理 worktree。**

#### 选项 4：丢弃

**先确认：**
```
这将永久删除：
- 分支 <名称>
- 所有提交：<提交列表>
- <路径> 的 worktree

输入 'discard' 确认。
```

等待确切确认。

如果确认：
```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

然后：清理 worktree（步骤 5）

### 步骤 5：清理 Worktree

**对于选项 1、2、4：**

检查是否在 worktree 中：
```bash
git worktree list | grep $(git branch --show-current)
```

如果是：
```bash
git worktree remove <worktree-path>
```

**对于选项 3：** 保持 worktree。

## 快速参考

| 选项 | 合并 | 推送 | 保持 Worktree | 清理分支 |
|--------|-------|------|---------------|----------------|
| 1. 本地合并 | ✓ | - | - | ✓ |
| 2. 创建 PR | - | ✓ | ✓ | - |
| 3. 保持原样 | - | - | ✓ | - |
| 4. 丢弃 | - | - | - | ✓（强制） |

## 常见错误

**跳过测试验证**
- **问题：** 合并损坏代码，创建失败 PR
- **修复：** 提供选项前总是验证测试

**开放式问题**
- **问题：** "接下来应该做什么？" → 模糊
- **修复：** 精确展示 4 个结构化选项

**自动 worktree 清理**
- **问题：** 在可能需要时移除 worktree（选项 2、3）
- **修复：** 仅对选项 1 和 4 清理

**丢弃无确认**
- **问题：** 意外删除工作
- **修复：** 要求输入 "discard" 确认

## 红旗

**绝不：**
- 测试失败仍继续
- 不验证合并结果上的测试就合并
- 无确认删除工作
- 未经明确要求强制推送

**总是：**
- 提供选项前验证测试
- 精确展示 4 个选项
- 选项 4 获取输入确认
- 仅对选项 1 和 4 清理 worktree

## 集成

**被以下调用：**
- **dev-subagent-driven-development**（步骤 7）- 所有任务完成后
- **dev-executing-plans**（步骤 5）- 所有批次完成后

**配对：**
- **dev-git-worktrees** - 清理该 skill 创建的 worktree
