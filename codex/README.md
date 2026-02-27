# Codex 配置

个人 Codex CLI 配置集合。

## 目录

- [目录结构](#目录结构)
- [安装](#安装)
- [使用](#使用)
- [Codex Skills 加载机制](#codex-skills-加载机制)

---

## 目录结构

```
codex/
├── README.md
└── skills/              # 11 个技能
    ├── dev-using-skills/
    ├── dev-brainstorming/
    ├── dev-debugging/
    ├── dev-tdd/
    ├── dev-writing-plans/
    ├── dev-executing-plans/
    ├── dev-git-worktrees/
    ├── dev-requesting-review/
    ├── dev-verification/
    ├── dev-finishing-branch/
    └── dev-writing-skills/
```

## 安装

```bash
# 安装 codex 配置（skills 到 ~/.agents/skills/）
./scripts/install.sh codex install

# 或使用 Makefile
make install-codex
```

## 使用

```bash
# 启动 codex，skills 会自动加载
codex

# 查看已加载的 skills
/skills
```

## Codex Skills 加载机制

Codex 按以下顺序扫描 skills：

| 范围 | 路径 | 用途 |
|------|------|------|
| USER | `~/.agents/skills/` | 用户个人 skills（本项目安装位置）|
| REPO | `./.agents/skills/` | 仓库级别 skills |
| SYSTEM | 内置 | OpenAI 内置 skills |

安装脚本将 skills 安装到 `~/.agents/skills/`，这样在任何目录运行 `codex` 都能使用这些技能。
