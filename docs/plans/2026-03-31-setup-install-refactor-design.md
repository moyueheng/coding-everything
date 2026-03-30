# setup 安装模型重构设计

日期：2026-03-31

## 背景

当前仓库的安装方式使用目录级 symlink：

```bash
ln -sf "$(pwd)/skills" ~/.agents/skills
ln -sf "$(pwd)/skills" ~/.claude/skills
```

这会直接接管 `~/.agents/skills` 和 `~/.claude/skills` 的根目录，带来两个问题：

1. 用户后续单独安装的其他 skill 无法稳定共存。
2. uninstall/update/status 无法只处理本仓库安装的内容，边界不清晰。

用户已经明确新的目标：

1. 默认需要覆盖同名 skill，不保留单独的冲突交互。
2. 安装范围只包含仓库根目录 `skills/`。
3. 默认安装仍需包含 `~/.kimi/agents/superpower` 和 `ks`。
4. 安装入口改为 `make install / update / uninstall / status`。

## 上游调研结论

几个上游仓库都没有把“替换整个全局 skills 根目录”作为推荐主路径：

- `upstream/superpowers/`
  - Claude Code / Cursor / Gemini CLI 走插件或扩展安装。
  - Codex 也采用子目录命名空间或平台原生发现，而不是替换整个 `~/.agents/skills`。
- `upstream/everything-claude-code/`
  - 以插件安装和 selective install 为主。
  - 手动安装也是增量复制，不是目录级接管。
- `upstream/product-manager-skills/`
  - 更偏单 skill 安装和按需引入。
- `upstream/obsidian-skills/`
  - 更像通用 skill 库，适合按需安装或项目内使用。

结论：本仓库当前的目录级覆盖模型偏激进，应改为“逐项合并安装”。

## 目标

将 setup 从“目录级覆盖安装”重构为“逐项合并安装 + 状态登记”，同时保留以下体验：

1. 修改仓库内 skill 后，安装结果立即生效。
2. 默认覆盖同名 skill。
3. 用户自己的其他 skill 不受影响。
4. Kimi agent 和 `ks` 仍属于默认安装的一部分。

## 非目标

- 不改写任何共享 skill 内容。
- 不把系统级 `.agents/skills/` 纳入本次默认安装范围。
- 不引入新的重型框架或外部安装器。
- 不把安装入口拆成额外的 Kimi 专用命令。
- 不在本次设计中处理插件市场分发。

## 新安装模型

### 1. skills 使用逐项合并安装

源目录：

```text
repo/skills/<skill-name>/
```

目标目录：

```text
~/.agents/skills/<skill-name>
~/.claude/skills/<skill-name>
```

安装方式为逐个 skill 建立 symlink，而不是把整个 `skills/` 目录直接链接到目标根目录。

### 2. 默认覆盖语义

新的默认行为等同于旧设计中的 `--force`：

- 如果目标位置已经存在同名 skill，先删除该项，再重建为新的 symlink。
- 只处理同名项。
- 不处理其他无关目录或文件。

ASCII 示意：

```text
安装前
~/.agents/skills/
├── third-party-a/
├── dev-tdd/              # 已存在，可能不是本仓库安装
└── custom-local/

执行 make install 后
~/.agents/skills/
├── third-party-a/
├── dev-tdd -> <repo>/skills/dev-tdd
└── custom-local/
```

### 3. Kimi agent 和 ks 继续默认安装

除共享 skills 外，默认安装仍然包含：

```text
kimi/agents/superpower -> ~/.kimi/agents/superpower
~/.local/bin/ks
```

其中 `ks` 继续作为：

```bash
kimi -y --agent-file ~/.kimi/agents/superpower/agent.yaml
```

的快捷入口。

## manifest 设计

### 作用

manifest 是安装登记表，用于记录“本仓库安装器创建了哪些项”。

没有 manifest 时：

```text
uninstall
-> 不知道该删哪些项
-> 只能扫目录猜
-> 容易误删用户自己的 skill
```

有 manifest 时：

```text
uninstall
-> 只删除登记过的项
-> 不碰用户其他 skill
```

### 建议路径

```text
~/.local/share/coding-everything/install-manifest.json
```

### 建议记录字段

- `repo_root`
- `installed_at`
- `updated_at`
- `targets`
  - `agents_skills_dir`
  - `claude_skills_dir`
  - `kimi_agent_dir`
  - `ks_path`
- `skills`
  - 已安装的 skill 名单

manifest 的目的不是做复杂状态机，而是保证 uninstall/update/status 的边界安全。

## 命令面设计

统一使用 `Makefile` 作为短入口：

```bash
make install
make update
make uninstall
make status
```

### `make install`

职责：

1. 将 `skills/*` 逐项安装到 `~/.agents/skills/`
2. 将 `skills/*` 逐项安装到 `~/.claude/skills/`
3. 安装 `~/.kimi/agents/superpower`
4. 安装 `~/.local/bin/ks`
5. 写入或覆盖 manifest

### `make update`

职责：

1. 读取 manifest
2. 校验登记项是否仍存在且仍指向当前仓库
3. 漂移、缺失时重建
4. 如果仓库新增 skill，则自动补装
5. 刷新 manifest

### `make uninstall`

职责：

1. 读取 manifest
2. 只删除 manifest 中登记过的 skills symlink
3. 删除 `~/.kimi/agents/superpower`
4. 删除 `~/.local/bin/ks`
5. 删除 manifest

约束：

- 不扫描目录猜测“哪些可能是本仓库装的”
- 不删除用户其他第三方 skill

### `make status`

职责：

输出以下状态：

1. 已正确安装
2. 缺失
3. 漂移
4. 仓库新增但尚未登记

如果 manifest 不存在：

- `install`：正常全量安装并创建 manifest
- `update`：退化为 install
- `uninstall`：拒绝执行，避免误删
- `status`：报告“未受管”

## setup skill 的新职责

`.agents/skills/setup/SKILL.md` 不删除，改写为新的默认安装入口说明。

### 保留

- `setup` 作为仓库官方安装入口
- 安装 `~/.kimi/agents/superpower`
- 安装 `ks`

### 删除

- “整目录 symlink 到 `~/.agents/skills` / `~/.claude/skills`” 的写法
- “只要 symlink 整个目录即可” 的描述

### 改写后应表达

```text
setup
├── 合并安装共享 skills
├── 安装 Kimi superpower agent
└── 安装 ks
```

## 目标结构

```text
make install
|
+-- ~/.agents/skills/<repo skills...>
+-- ~/.claude/skills/<repo skills...>
+-- ~/.kimi/agents/superpower
`-- ~/.local/bin/ks
```

不是：

```text
~/.agents/skills -> repo/skills
~/.claude/skills -> repo/skills
```

## 风险与缓解

### 风险 1：同名覆盖导致用户原有 skill 被替换

这是用户明确接受的默认语义，因此不提供冲突确认。

缓解：

- 文档明确“默认覆盖同名项”
- `status` 输出当前由本仓库接管的 skill 名单

### 风险 2：manifest 丢失后 uninstall 不安全

缓解：

- `uninstall` 在 manifest 缺失时直接拒绝执行
- `update` 在 manifest 缺失时退化为 install

### 风险 3：README / AGENTS / setup 文档仍保留旧模型

缓解：

- 实施时同步更新：
  - `README.md`
  - `AGENTS.md`
  - `.agents/skills/setup/SKILL.md`

## 验收标准

- 不再使用目录级 symlink 接管 `~/.agents/skills` 或 `~/.claude/skills`
- `skills/` 中每个 skill 都作为独立条目安装
- 默认同时写入 `~/.agents/skills` 和 `~/.claude/skills`
- 默认同时安装 `~/.kimi/agents/superpower` 和 `ks`
- 同名 skill 默认直接覆盖
- uninstall 仅删除 manifest 登记过的项
- 文档中不再把旧的整目录安装方式当作推荐路径

## 实施顺序

1. 设计并实现 manifest 驱动的安装脚本
2. 增加 `Makefile` 入口：`install/update/uninstall/status`
3. 重写 `.agents/skills/setup/SKILL.md`
4. 更新 `README.md`
5. 更新 `AGENTS.md`
