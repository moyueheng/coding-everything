---
name: update-upstream-repos
description: 更新本项目的上游 submodule，并基于真实 git 变更分析生成文档报告。用于用户要求同步 `upstream/` 下仓库、检查上游最近更新、梳理新增内容、在 `docs/` 写更新说明，或筛选哪些更新值得优先吸收和推荐时。
---

# Update Upstream Repos

用这个 skill 处理“更新上游仓库并写总结”这一类任务。目标不是只改 gitlink，而是产出一份有证据的更新报告。

## 工作流

按下面顺序执行，不要跳步：

```text
用户请求
   |
   v
检查约束与受影响文档
   |
   v
识别要更新的 submodule
   |
   v
拉取远端并更新 gitlink
   |
   v
基于真实 commit 区间生成摘要
   |
   v
阅读必要的上游 README / docs / skill 文件
   |
   v
写 docs 报告 + 同步 AGENTS/CLAUDE
```

## 1. 建立上下文

先做这些检查：

- 运行 `find . -type f \( -name 'AGENTS.md' -o -name 'CLAUDE.md' \)`，识别需要同步的文档。
- 读取根目录 `AGENTS.md`、`.gitmodules`、`README.md` 中与 submodule 和文档同步有关的段落。
- 确认用户是要：
  - 更新全部上游仓库
  - 只更新某几个上游仓库
  - 只分析、不实际更新

如果网络慢或访问失败，先设置项目约定的代理：

```bash
export https_proxy=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897
export all_proxy=socks5://127.0.0.1:7897
```

## 2. 更新 submodule

先看当前状态：

```bash
git submodule status --recursive
git status --short
```

推荐更新方式：

- 更新全部：

```bash
git submodule update --remote
```

- 更新单个仓库：

```bash
git -C upstream/<repo> fetch --all --tags
git -C upstream/<repo> pull --ff-only
```

更新后不要立刻总结，先确认根仓库里真的有 gitlink 变化：

```bash
git diff --submodule=short HEAD
```

如果没有变化，就明确写明“已检查但当前没有可同步更新”。

## 3. 生成变更证据

使用本 skill 自带脚本生成 Markdown 草稿：

```bash
uv run .agents/skills/update-upstream-repos/scripts/generate_upstream_report.py
```

常用变体：

- 写入文件：

```bash
uv run .agents/skills/update-upstream-repos/scripts/generate_upstream_report.py \
  --output docs/upstream-updates/YYYY-MM-DD-upstream-updates.md
```

- 仅分析指定范围：

```bash
uv run .agents/skills/update-upstream-repos/scripts/generate_upstream_report.py \
  --range upstream/superpowers:<old_sha>..<new_sha>
```

脚本只负责整理事实：

- 哪些 submodule 发生变化
- 每个仓库从哪个 SHA 更新到哪个 SHA
- 这段区间有哪些 commit
- 每个区间的简短 diff 统计

脚本不会替你下结论。任何“值得推荐”的判断都必须回到真实 commit、README、docs 或具体文件 diff。

## 3.1 验证 skill 自身可用性

优先使用本 skill 自带的零依赖校验脚本：

```bash
uv run .agents/skills/update-upstream-repos/scripts/validate_skill.py
```

这个脚本只使用 Python 标准库，避免 `uv run` 环境下缺少 `PyYAML` 时校验失败。

## 4. 深读必要上游内容

只针对发生变化的仓库补充阅读，避免把整个上游仓库都塞进上下文：

- 先读变更区间里最关键的 commit subject
- 再读对应的 README、docs、skill 定义、脚本或配置文件
- 如果某条更新只是重命名、格式化、文案微调，不要夸大

判断“值得推荐”的依据只能来自这些证据：

- 新增了本项目可直接复用的 skill / agent / workflow
- 修复了当前仓库已知痛点
- 改进了安装、兼容性、验证、脚本化能力
- 更新涉及架构边界或目录结构，且会影响后续同步方式

## 5. 写 docs 报告

写报告前，先打开 [references/report-template.md](references/report-template.md)。

输出文档时遵守这些规则：

- 文档放到 `docs/upstream-updates/`，命名优先使用 `YYYY-MM-DD-upstream-updates.md`
- 先写“变更概览”，再写各仓库详情，最后写“值得关注”
- 每个结论都要能追溯到 commit、文件或 README
- 不要把“我觉得不错”写成“上游已经证明有效”
- 如果只更新了单个仓库，文档仍然保留统一结构，但未涉及仓库可以省略

## 6. 同步项目文档

如果本次更新改变了稳定事实，必须同步更新相关 `AGENTS.md` 或 `CLAUDE.md`。稳定事实包括：

- 上游仓库数量或名称变化
- 目录结构变化
- 更新流程变化
- 新增固定脚本入口
- 文档位置或命名规范变化

不要写流水账。只写后续 agent 真正需要知道的高信息密度知识。

## 失败处理

- 如果某个 submodule 拉取失败，保留其他仓库的分析结果，并明确标出失败仓库与命令输出要点。
- 如果脚本发现没有 submodule diff，就不要伪造“更新报告”，应改写成“检查结果”。
- 除非用户明确要求，否则不要自己提交 commit。
