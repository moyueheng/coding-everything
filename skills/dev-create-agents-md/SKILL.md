---
name: dev-create-agents-md
description: 何时使用需要为编程项目、monorepo 或多级目录创建/更新 AGENTS.md、CLAUDE.md 软链接、项目级 agent 操作手册、子目录局部规则、验证命令和 Coding Agent 上下文边界时使用。
---

# Create AGENTS.md

## 概述

为项目生成分层的 agent-readable 操作手册。根目录 `AGENTS.md` 写全局事实，子目录 `AGENTS.md` 只写相对父级新增或覆盖的规则；每个同级 `CLAUDE.md` 必须是指向 `AGENTS.md` 的软链接，避免多份规则分叉。

<EXTREMELY-IMPORTANT>
先用工具检索项目真实结构、脚本、测试入口、现有文档和邻近 AGENTS.md/CLAUDE.md，再写规则。禁止凭经验补全技术栈、命令、目录职责或团队偏好。

AGENTS.md 只记录会改变 agent 行为的稳定事实：目录边界、操作约束、验证命令、风格偏好、禁止事项、示例入口和升级路径。不要写日志、愿景、空泛原则或一次性任务过程。
</EXTREMELY-IMPORTANT>

## 工作流

```text
1. 选目录层级 -> 验证：每个 AGENTS.md 都对应真实边界
2. 读取证据 -> 验证：每条规则能追溯到文件、脚本或用户指令
3. 写 AGENTS.md -> 验证：子目录只写差异，不复制父级
4. 建 CLAUDE.md 软链 -> 验证：readlink 指向 AGENTS.md
5. 复查冗余和命令 -> 验证：规则最小、命令可执行或明确说明未运行
```

### 1. 选目录层级

默认只在这些位置创建或更新：

- 仓库根目录
- monorepo 的 `apps/*`、`packages/*`、`services/*`、`libs/*`
- 技术栈、部署方式、测试入口或权限边界明显不同的子目录
- 用户明确指定的目录

默认跳过：

- `.git/`、`node_modules/`、`.venv/`、`dist/`、`build/`、`coverage/`
- vendored/upstream/submodule 目录，除非用户明确要求
- 没有独立操作规则的小目录

### 2. 读取证据

至少检索：

- `find . -type f \( -name 'AGENTS.md' -o -name 'CLAUDE.md' \)`
- `rg --files` 或同等文件清单
- package/config 文件：`package.json`、`pyproject.toml`、`Cargo.toml`、`go.mod`、`Makefile`、CI workflow 等
- 现有 README、docs、测试目录和主要入口文件
- 最近或局部的团队约束：formatter、lint、typecheck、test、build、dev server

如果需要通用模板，读取 [references/agents-md-pattern.md](references/agents-md-pattern.md)。不要把模板当事实；模板只提供结构，内容必须来自项目证据。

### 3. 写分层 AGENTS.md

根目录建议覆盖：

- Scope：本文件适用范围和子目录覆盖关系
- Project Map：只列 agent 定位必需的目录
- Commands：安装、格式化、lint、typecheck、test、build 的最小可靠命令
- Workflows：修改前检索、测试优先、验证门槛、文档同步规则
- Code Rules：本项目特有技术栈、依赖、样式、状态管理、API 约定
- Safety：必须询问的动作，例如删除大量文件、安装重依赖、推送、迁移生产数据
- PR/Done：完成前需要的检查项

子目录 `AGENTS.md` 只写：

- 与父级不同的命令、测试、代码风格或权限
- 当前目录的关键入口和反例
- 当前目录特有的依赖边界
- “继承父级，其余只覆盖以下内容”这类明确说明

避免：

- “写高质量代码”“保持简洁”这类无法执行的空话
- 复制父级整段规则
- 记录一次性任务日志
- 无证据的命令、版本或架构判断
- 长篇背景故事

### 4. 创建 CLAUDE.md 软链接

每个创建或更新 `AGENTS.md` 的目录，都创建同级软链接：

```bash
uv run python skills/dev-create-agents-md/scripts/link_claude_to_agents.py <dir> [<dir> ...]
```

脚本会拒绝覆盖已有普通文件或指向其他位置的软链接；如确实要替换，先向用户说明风险，再使用 `--force`。

### 5. 复查

完成前检查：

- `AGENTS.md` 内容是否能追溯到真实文件、命令或用户指令
- 子目录规则是否只保留差异
- `CLAUDE.md` 是否为相对软链接 `AGENTS.md`
- 是否更新了项目要求同步的上层 AGENTS/CLAUDE 文档
- 是否运行了可用验证命令；没运行必须说明原因

## 输出要求

最终回复列出创建/更新的目录、软链状态和验证命令。不要把完整 AGENTS.md 内容贴回聊天，除非用户要求审阅全文。
