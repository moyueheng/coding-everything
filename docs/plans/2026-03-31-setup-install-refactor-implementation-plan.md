# Setup Install Refactor Implementation Plan

> **给 Agent：** 必需子 skill：使用 `dev-executing-plans` 逐个任务实施此计划。

**目标：** 将 setup 从整目录覆盖安装重构为逐项合并安装，默认同时安装共享 `skills/`、Kimi agent 和 `ks`，并用 manifest 保证 `update/uninstall/status` 只管理本仓库安装的项。

**架构：** 新增一个轻量 Python 安装器脚本，集中处理四类行为：扫描仓库 `skills/`、向 `~/.agents/skills` 和 `~/.claude/skills` 逐项建立 symlink、安装 `~/.kimi/agents/superpower` 与 `~/.local/bin/ks`、读写 manifest。`Makefile` 只作为短入口转发到该脚本。文档层同步废弃旧的整目录 symlink 说明。 

**技术栈：** Python 标准库、`uv run`、GNU Make、symlink、`unittest`

---

## 文件结构

本次实现涉及以下文件：

- 创建：`/Users/moyueheng/Projects/moyueheng/coding-everything/scripts/install_skills.py`
- 创建：`/Users/moyueheng/Projects/moyueheng/coding-everything/tests/test_install_skills.py`
- 创建：`/Users/moyueheng/Projects/moyueheng/coding-everything/Makefile`
- 修改：`/Users/moyueheng/Projects/moyueheng/coding-everything/.agents/skills/setup/SKILL.md`
- 修改：`/Users/moyueheng/Projects/moyueheng/coding-everything/README.md`
- 修改：`/Users/moyueheng/Projects/moyueheng/coding-everything/AGENTS.md`
- 修改：`/Users/moyueheng/Projects/moyueheng/coding-everything/kimi/README.md`
- 修改：`/Users/moyueheng/Projects/moyueheng/coding-everything/kimi/agents/superpower/README.md`
- 验证参考：`/Users/moyueheng/Projects/moyueheng/coding-everything/ks`

文件职责：

- `scripts/install_skills.py`
  - 唯一安装实现入口
  - 提供 `install/update/uninstall/status`
  - 管理 manifest
- `tests/test_install_skills.py`
  - 用临时目录覆盖 home 路径，验证安装器行为
- `Makefile`
  - 提供短命令入口，不承载安装逻辑
- 各文档
  - 同步新的安装模型、命令面和边界

## 任务 1：搭建安装器测试骨架

**文件：**
- 创建：`/Users/moyueheng/Projects/moyueheng/coding-everything/tests/test_install_skills.py`

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1：RED - 编写失败的测试**

**调用 dev-tdd**：为未来安装器定义最小行为测试，覆盖：

- `install` 会在临时 home 下创建：
  - `~/.agents/skills/<skill-name>`
  - `~/.claude/skills/<skill-name>`
  - `~/.kimi/agents/superpower`
  - `~/.local/bin/ks`
- `install` 会写入 manifest

建议测试结构：

```python
import tempfile
import unittest
from pathlib import Path


class InstallSkillsTest(unittest.TestCase):
    def test_install_creates_skill_links_kimi_agent_ks_and_manifest(self):
        self.fail("write installer first")
```

**步骤 2：验证 RED - 看着它失败**

**调用 dev-tdd**：运行测试，确认因安装器模块不存在或断言失败而红灯。

运行：

```bash
uv run python -m unittest tests.test_install_skills.InstallSkillsTest.test_install_creates_skill_links_kimi_agent_ks_and_manifest -v
```

预期：`FAILED`，原因是安装器模块缺失或测试中显式 `fail()`

**步骤 3：GREEN - 创建最小测试文件骨架**

**调用 dev-tdd**：只写最小可运行的测试骨架和辅助夹具，不实现安装逻辑。

至少包含：

- `tempfile.TemporaryDirectory()`
- 指向仓库根 `skills/` 的 fixture
- 可注入 home 目录的调用方式占位

**步骤 4：验证 GREEN - 测试文件可被发现**

**调用 dev-tdd**：重新运行同一命令，确认失败原因已收敛到“安装器未实现”而不是测试文件自身语法错误。

运行：

```bash
uv run python -m unittest tests.test_install_skills -v
```

预期：测试被发现并失败，错误集中在待实现安装器

**步骤 5：REFACTOR**

**调用 dev-tdd**：抽取临时目录和仓库根准备逻辑为测试辅助函数，保持测试文件短小。

**步骤 6：提交**

```bash
git add tests/test_install_skills.py
git commit -m "test: add install skills test scaffold"
```

## 任务 2：实现 `install` 最小闭环

**文件：**
- 创建：`/Users/moyueheng/Projects/moyueheng/coding-everything/scripts/install_skills.py`
- 测试：`/Users/moyueheng/Projects/moyueheng/coding-everything/tests/test_install_skills.py`

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1：RED - 扩展失败测试**

**调用 dev-tdd**：在测试中明确断言以下行为：

- 枚举仓库 `skills/` 下所有一级目录
- 在目标目录中创建同名 symlink
- 若同名目标已存在则先删除再重建
- 为 `kimi/agents/superpower` 创建 symlink
- 为 `ks` 创建可执行文件或 symlink
- 生成 manifest 文件

**步骤 2：验证 RED - 看着它失败**

**调用 dev-tdd**：运行与安装相关的单测，确认当前失败。

运行：

```bash
uv run python -m unittest tests.test_install_skills.InstallSkillsTest.test_install_creates_skill_links_kimi_agent_ks_and_manifest -v
```

预期：`FAILED`，断言缺少脚本或文件不存在

**步骤 3：GREEN - 编写最小实现**

**调用 dev-tdd**：在 `scripts/install_skills.py` 中实现最小可用的 `install`：

- 使用 `argparse` 接收子命令
- 使用 `Path.home()` 的可注入包装，支持测试替换 home
- 扫描仓库根 `skills/`
- 确保以下目录存在：
  - `~/.agents/skills`
  - `~/.claude/skills`
  - `~/.kimi/agents`
  - `~/.local/bin`
  - `~/.local/share/coding-everything`
- 对每个 skill 同名项执行“删除后重建 symlink”
- 创建 `~/.kimi/agents/superpower`
- 创建或更新 `~/.local/bin/ks`
- 写入 manifest：`~/.local/share/coding-everything/install-manifest.json`

建议将实现拆成这些函数：

- `discover_skills(repo_root: Path) -> list[str]`
- `force_symlink(src: Path, dst: Path) -> None`
- `write_manifest(...) -> None`
- `command_install(repo_root: Path, home: Path) -> int`

**步骤 4：验证 GREEN - 看着它通过**

**调用 dev-tdd**：运行安装测试，确认测试通过。

运行：

```bash
uv run python -m unittest tests.test_install_skills.InstallSkillsTest.test_install_creates_skill_links_kimi_agent_ks_and_manifest -v
```

预期：`OK`

**步骤 5：REFACTOR**

**调用 dev-tdd**：将路径计算、manifest 构造和 symlink 创建逻辑拆成小函数，避免 `main()` 过长。

**步骤 6：提交**

```bash
git add scripts/install_skills.py tests/test_install_skills.py
git commit -m "feat: add merge-based install command for skills"
```

## 任务 3：补齐 `update`、`status`、`uninstall`

**文件：**
- 修改：`/Users/moyueheng/Projects/moyueheng/coding-everything/scripts/install_skills.py`
- 测试：`/Users/moyueheng/Projects/moyueheng/coding-everything/tests/test_install_skills.py`

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1：RED - 为三个子命令补测试**

**调用 dev-tdd**：新增以下测试：

- `update` 在 manifest 缺失时退化为 `install`
- `update` 会修复被删掉或漂移的 symlink
- `status` 会报告：
  - `installed`
  - `missing`
  - `drifted`
  - `untracked_new_skills`
- `uninstall` 在 manifest 存在时只删除登记项
- `uninstall` 在 manifest 缺失时返回非零并提示“拒绝执行”

建议新增测试方法：

```python
def test_update_repairs_missing_and_drifted_entries(self): ...
def test_status_reports_install_state(self): ...
def test_uninstall_removes_only_manifest_managed_entries(self): ...
def test_uninstall_refuses_when_manifest_is_missing(self): ...
```

**步骤 2：验证 RED - 看着它失败**

**调用 dev-tdd**：运行全量单测，确认新增断言全部失败。

运行：

```bash
uv run python -m unittest tests.test_install_skills -v
```

预期：新增测试失败，错误定位到未实现子命令

**步骤 3：GREEN - 编写最小实现**

**调用 dev-tdd**：在安装器中加入：

- `load_manifest()`
- `command_update()`
- `command_status()`
- `command_uninstall()`

输出建议：

- `status` 以纯文本逐行输出，方便人看也方便测试断言
- `uninstall` 只根据 manifest 的 `skills` 列表和目标路径删除项
- `update` 在发现仓库新增 skill 时将其补装并更新 manifest

**步骤 4：验证 GREEN - 看着它通过**

**调用 dev-tdd**：运行全量测试。

运行：

```bash
uv run python -m unittest tests.test_install_skills -v
```

预期：`OK`

**步骤 5：REFACTOR**

**调用 dev-tdd**：统一命令输出文案和返回码，避免四个子命令各写一套路径逻辑。

**步骤 6：提交**

```bash
git add scripts/install_skills.py tests/test_install_skills.py
git commit -m "feat: add update status and uninstall for skills installer"
```

## 任务 4：添加 `Makefile` 短入口

**文件：**
- 创建：`/Users/moyueheng/Projects/moyueheng/coding-everything/Makefile`
- 修改：`/Users/moyueheng/Projects/moyueheng/coding-everything/scripts/install_skills.py`

**步骤 1：创建 `Makefile`**

新增目标：

- `install`
- `update`
- `uninstall`
- `status`
- `test`

目标行为：

```make
install:
	uv run python scripts/install_skills.py install

update:
	uv run python scripts/install_skills.py update
```

`test` 统一运行：

```bash
uv run python -m unittest tests.test_install_skills -v
```

**步骤 2：验证入口可调用**

运行：

```bash
make -n install
make -n update
make -n uninstall
make -n status
make -n test
```

预期：输出正确的 `uv run python ...` 命令，不真正执行安装

**步骤 3：提交**

```bash
git add Makefile
git commit -m "build: add make targets for skills installer"
```

## 任务 5：重写 setup skill 文档

**文件：**
- 修改：`/Users/moyueheng/Projects/moyueheng/coding-everything/.agents/skills/setup/SKILL.md`

**步骤 1：重写安装流程说明**

将旧文档中的以下内容替换掉：

- 整目录 symlink 到 `~/.agents/skills`
- 整目录 symlink 到 `~/.claude/skills`
- 旧的手工 `ln -sf "$(pwd)/skills" ...`

新文档需要明确：

- 默认命令是：
  - `make install`
  - `make update`
  - `make uninstall`
  - `make status`
- `skills/` 逐项安装到两个目录：
  - `~/.agents/skills/`
  - `~/.claude/skills/`
- 默认同时安装：
  - `~/.kimi/agents/superpower`
  - `~/.local/bin/ks`
- 默认覆盖同名项
- `uninstall` 依赖 manifest，只移除本仓库受管项

**步骤 2：校验旧模型已移除**

运行：

```bash
rg -n 'ln -sf "\\$\\(pwd\\)/skills" ~/.agents/skills|ln -sf "\\$\\(pwd\\)/skills" ~/.claude/skills' .agents/skills/setup/SKILL.md
```

预期：无匹配

**步骤 3：提交**

```bash
git add .agents/skills/setup/SKILL.md
git commit -m "docs: rewrite setup skill for merge-based installer"
```

## 任务 6：同步仓库主文档

**文件：**
- 修改：`/Users/moyueheng/Projects/moyueheng/coding-everything/README.md`
- 修改：`/Users/moyueheng/Projects/moyueheng/coding-everything/AGENTS.md`
- 修改：`/Users/moyueheng/Projects/moyueheng/coding-everything/kimi/README.md`
- 修改：`/Users/moyueheng/Projects/moyueheng/coding-everything/kimi/agents/superpower/README.md`

**步骤 1：更新根 README**

将安装章节改为以 `make install` 为主，明确：

- 共享 skills 是逐项合并安装
- 默认同时写入 `~/.agents/skills` 和 `~/.claude/skills`
- 默认同时安装 Kimi agent 与 `ks`
- 不再推荐整目录 symlink

**步骤 2：更新 AGENTS.md**

同步高信息密度事实：

- 安装入口为 `make install / update / uninstall / status`
- setup 安装器采用逐项 symlink
- 默认双写入 skills 目标目录
- manifest 用于受管 uninstall/update/status

**步骤 3：更新 Kimi 文档**

清理 `kimi/README.md` 和 `kimi/agents/superpower/README.md` 中已失效的：

- `scripts/install.sh`
- `./install.sh`
- 旧的 Makefile 语义
- 已迁移的 `kimi/skills/` 描述

改成引用仓库根的安装器和当前目录结构。

**步骤 4：验证文档一致性**

运行：

```bash
rg -n 'scripts/install\\.sh|\\.\\/install\\.sh|ln -sf "\\$\\(pwd\\)/skills" ~/.agents/skills|kimi/skills/' README.md AGENTS.md kimi/README.md kimi/agents/superpower/README.md .agents/skills/setup/SKILL.md
```

预期：无匹配，或只保留明确标注为“旧模型已废弃”的上下文

**步骤 5：提交**

```bash
git add README.md AGENTS.md kimi/README.md kimi/agents/superpower/README.md
git commit -m "docs: update install docs for merge-based setup"
```

## 任务 7：端到端验证

**文件：**
- 验证：`/Users/moyueheng/Projects/moyueheng/coding-everything/Makefile`
- 验证：`/Users/moyueheng/Projects/moyueheng/coding-everything/scripts/install_skills.py`
- 验证：`/Users/moyueheng/Projects/moyueheng/coding-everything/tests/test_install_skills.py`

**步骤 1：运行单元测试**

```bash
make test
```

预期：所有 `tests/test_install_skills.py` 用例通过

**步骤 2：查看状态命令**

```bash
make status
```

预期：在真实用户环境中输出已安装、缺失、漂移或未受管状态之一；不报 Python 异常

**步骤 3：干跑文档入口检查**

```bash
rg -n 'make install|make update|make uninstall|make status' README.md AGENTS.md .agents/skills/setup/SKILL.md kimi/README.md
```

预期：四个入口在核心文档中都可见

**步骤 4：提交**

```bash
git add Makefile scripts/install_skills.py tests/test_install_skills.py README.md AGENTS.md kimi/README.md kimi/agents/superpower/README.md .agents/skills/setup/SKILL.md
git commit -m "test: verify merge-based setup workflow"
```

## Self-Review

### Spec 覆盖度

- 逐项合并安装：任务 2
- 默认覆盖同名项：任务 2
- 默认安装 Kimi agent 与 `ks`：任务 2、任务 5、任务 6
- manifest 保护 uninstall/update/status：任务 2、任务 3
- `Makefile` 短入口：任务 4
- setup/README/AGENTS 文档同步：任务 5、任务 6

### 占位符扫描

- 无 `TODO`、`TBD`、`稍后实现`
- 所有新文件路径已明确
- 所有测试和验证命令已明确

### 类型一致性

- 安装器统一命名为 `scripts/install_skills.py`
- manifest 路径统一为 `~/.local/share/coding-everything/install-manifest.json`
- 四个入口统一为 `make install/update/uninstall/status`

## 执行交接

计划已完成并保存到 `docs/plans/2026-03-31-setup-install-refactor-implementation-plan.md`。两种执行选项：

**1. Subagent-Driven（推荐）** - 我为每个任务分派 fresh subagent，任务间审查，快速迭代

**2. 内联执行** - 在本会话中使用 `dev-executing-plans` 执行任务，批量执行带检查点

选择哪种方式？
