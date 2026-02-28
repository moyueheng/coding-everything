# OpenCode Configuration

OpenCode 平台的 AI 编程助手配置（开发中）。

## 状态

🏗️ **开发中** - 正在迁移 skills 配置

## 技能目录

位于 `opencode/skills/` 下的技能：

| 技能 | 状态 | 说明 |
|------|------|------|
| `using-skills` | 🏗️ 待完善 | 技能入口 |
| `brainstorming` | 🏗️ 待完善 | 头脑风暴 |
| `tdd` | 🏗️ 待完善 | 测试驱动开发 |
| `debugging` | 🏗️ 待完善 | 调试 |
| `writing-plans` | 🏗️ 待完善 | 编写计划 |
| `executing-plans` | 🏗️ 待完善 | 执行计划 |
| `git-worktrees` | 🏗️ 待完善 | Git 工作树 |
| `requesting-review` | 🏗️ 待完善 | 代码审查 |
| `verification` | 🏗️ 待完善 | 验证 |
| `finishing-branch` | 🏗️ 待完善 | 完成分支 |
| `update-codemaps` | ✅ 已完成 | 分析代码库结构并生成架构文档 |

## 与 Kimi 配置的差异

OpenCode 技能目前主要从上游仓库 `everything-claude-code` 的 `.opencode/` 目录同步。

## 安装

```bash
# 创建软链接
ln -sf "$(pwd)/opencode/skills" ~/.opencode/skills
```

## 参考

- [upstream/everything-claude-code/.opencode/](../upstream/everything-claude-code/.opencode/)
