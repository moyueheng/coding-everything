# Codex 目录创建与 Skill 迁移实施计划

> **给 Kimi：** 必需子 skill：使用 `dev-executing-plans` 逐个任务实施此计划。

**目标：** 创建 codex/ 目录，将 kimi 的 skills 迁移到 codex，并更新安装脚本支持 codex

---

## 目录

- [任务 1：创建 codex/ 目录结构](#任务-1创建-codex-目录结构)
- [任务 2：迁移 Skills 从 kimi/ 到 codex/](#任务-2迁移-skills-从-kimi-到-codex)
- [任务 3：创建 Codex Agent 配置](#任务-3创建-codex-agent-配置)
- [任务 4：重构安装脚本支持多平台](#任务-4重构安装脚本支持多平台)
- [任务 5：更新 Makefile 添加 Codex 命令](#任务-5更新-makefile-添加-codex-命令)
- [任务 6：更新测试脚本支持多平台](#任务-6更新测试脚本支持多平台)
- [任务 7：更新 AGENTS.md 文档](#任务-7更新-agentsmd-文档)
- [任务 8：创建 codex-superpower 启动脚本](#任务-8创建-codex-superpower-启动脚本)
- [任务 9：最终验证](#任务-9最终验证)
- [执行交接](#执行交接)

---

**架构：** 保持与 kimi/ 相同的目录结构（skills/ + agents/），安装脚本通过参数区分平台（kimi/codex），共享核心逻辑但使用不同的目标路径和配置文件格式

**技术栈：** Bash, YAML (codex config), Markdown

---

## 任务 1：创建 codex/ 目录结构

**文件：**
- 创建：`codex/README.md`
- 创建：`codex/skills/` (目录)
- 创建：`codex/agents/superpower/` (目录)

**步骤 1：创建 codex 目录结构**

```bash
mkdir -p codex/skills codex/agents/superpower
```

**步骤 2：创建 codex README.md**

创建 `codex/README.md`：
```markdown
# Codex 配置

个人 Codex CLI 配置集合。

## 目录结构

```
codex/
├── README.md
├── agents/
│   └── superpower/      # agent 配置
│       ├── config.yaml  # Codex agent 配置
│       └── instructions.md
└── skills/              # skill 集合
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
# 安装 codex 配置
./scripts/install.sh codex install

# 或使用 Makefile
make install-codex
```

## 使用

```bash
# 使用 superpower agent 启动 codex
./codex-superpower
```
```

**步骤 3：验证目录创建**

```bash
ls -la codex/
ls -la codex/skills/
ls -la codex/agents/superpower/
```

预期：目录存在且为空

**步骤 4：提交**

```bash
git add codex/
git commit -m "feat: add codex directory structure with README"
```

---

## 任务 2：迁移 Skills 从 kimi/ 到 codex/

**文件：**
- 源：`kimi/skills/*`
- 目标：`codex/skills/*`

**步骤 1：复制所有 skills**

```bash
cp -r kimi/skills/* codex/skills/
```

**步骤 2：验证迁移**

```bash
ls codex/skills/
find codex/skills -name "SKILL.md" | wc -l
```

预期：显示 11 个 skill 目录，11 个 SKILL.md 文件

**步骤 3：提交**

```bash
git add codex/skills/
git commit -m "feat: migrate 11 skills from kimi to codex"
```

---

## 任务 3：创建 Codex Agent 配置

**文件：**
- 创建：`codex/agents/superpower/config.yaml`
- 创建：`codex/agents/superpower/instructions.md`
- 参考：`kimi/agents/superpower/agent.yaml`
- 参考：`kimi/agents/superpower/system.md`

**步骤 1：读取源文件**

读取 `kimi/agents/superpower/agent.yaml` 和 `kimi/agents/superpower/system.md`

**步骤 2：创建 Codex 格式的 config.yaml**

```yaml
name: superpower
description: Superpower agent for systematic software development
instructions: |
  # 系统指令内容（从 system.md 转换）
  ...
model: o3-mini
tools:
  - code
  - search
  - read
  - write
```

**步骤 3：创建 instructions.md**

从 `kimi/agents/superpower/system.md` 复制并适配 Codex 格式

**步骤 4：提交**

```bash
git add codex/agents/
git commit -m "feat: add codex superpower agent configuration"
```

---

## 任务 4：重构安装脚本支持多平台

**文件：**
- 修改：`scripts/install.sh`

**步骤 1：备份原脚本**

```bash
cp scripts/install.sh scripts/install.sh.backup
```

**步骤 2：修改脚本结构**

新的命令格式：`./scripts/install.sh [platform] [command] [options]`

需要修改：
1. 添加 `PLATFORM` 变量（kimi/codex）
2. 路径配置改为基于 platform
3. 所有函数支持 platform 参数
4. 保持向后兼容（默认 kimi）

关键修改点：
```bash
# 平台配置
PLATFORM="${PLATFORM:-kimi}"  # 默认 kimi
INSTALL_DIR="${HOME}/.${PLATFORM}"
SKILLS_SOURCE="${PROJECT_ROOT}/${PLATFORM}/skills"
AGENT_SOURCE="${PROJECT_ROOT}/${PLATFORM}/agents/superpower"
```

**步骤 3：更新 usage 函数**

```bash
usage() {
    cat << EOF
Usage: $0 [PLATFORM] [COMMAND] [OPTIONS]

Platforms:
    kimi        Kimi CLI (默认)
    codex       Codex CLI

Commands:
    install     安装配置 (默认)
    update      更新配置
    uninstall   卸载配置
    status      查看状态

Options:
    -f, --force     强制安装/卸载，不询问
    -h, --help      显示帮助

Examples:
    $0                      # 安装 kimi 配置
    $0 kimi install         # 安装 kimi 配置
    $0 codex install        # 安装 codex 配置
    $0 codex install -f     # 强制安装 codex 配置
    $0 kimi update          # 更新 kimi 配置
    $0 codex status         # 查看 codex 状态
EOF
}
```

**步骤 4：修改 main 函数解析 platform 和 command**

```bash
main() {
    local platform="kimi"
    local cmd="install"
    local args=()

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            kimi|codex)
                platform="$1"
                shift
                ;;
            install|i|update|u|uninstall|remove|rm|status|s|check)
                cmd="$1"
                shift
                ;;
            -f|--force|-h|--help)
                args+=("$1")
                shift
                ;;
            *)
                args+=("$1")
                shift
                ;;
        esac
    done

    export PLATFORM="$platform"
    # 重新初始化路径
    init_paths
    
    # 执行命令
    ...
}
```

**步骤 5：创建 init_paths 函数**

```bash
init_paths() {
    INSTALL_DIR="${HOME}/.${PLATFORM}"
    SKILLS_DIR="${INSTALL_DIR}/skills"
    AGENT_DIR="${INSTALL_DIR}/agents/superpower"
    SKILLS_SOURCE="${PROJECT_ROOT}/${PLATFORM}/skills"
    AGENT_SOURCE="${PROJECT_ROOT}/${PLATFORM}/agents/superpower"
}
```

**步骤 6：修改 create_wrapper 函数支持多平台**

```bash
create_wrapper() {
    local wrapper="${PROJECT_ROOT}/${PLATFORM}-superpower"
    if [[ "$PLATFORM" == "kimi" ]]; then
        cat > "$wrapper" << EOF
#!/usr/bin/env bash
# ${PLATFORM} Superpower 启动脚本
exec kimi --agent-file "${AGENT_DIR}/agent.yaml" "\$@"
EOF
    else
        # codex 使用不同格式
        cat > "$wrapper" << EOF
#!/usr/bin/env bash
# ${PLATFORM} Superpower 启动脚本
exec codex --config "${AGENT_DIR}/config.yaml" "\$@"
EOF
    fi
    chmod +x "$wrapper"
    echo "$wrapper"
}
```

**步骤 7：更新所有函数中的硬编码路径**

确保所有函数使用变量而非硬编码的 `.kimi`

**步骤 8：测试脚本语法**

```bash
bash -n scripts/install.sh
```

预期：无语法错误

**步骤 9：提交**

```bash
git add scripts/install.sh
git rm scripts/install.sh.backup
git commit -m "feat: refactor install script to support both kimi and codex"
```

---

## 任务 5：更新 Makefile 添加 Codex 命令

**文件：**
- 修改：`Makefile`

**步骤 1：添加 codex 相关目标**

在 Makefile 中添加：
```makefile
# Codex 安装命令
install-codex:
	@./scripts/install.sh codex install

install-codex-force:
	@./scripts/install.sh codex install -f

update-codex:
	@./scripts/install.sh codex update

uninstall-codex:
	@./scripts/install.sh codex uninstall

status-codex:
	@./scripts/install.sh codex status

# 运行 codex
run-codex: install-codex
	@./codex-superpower
```

**步骤 2：更新 help 目标**

```makefile
help:
	@echo "Configuration Manager - 常用命令"
	@echo ""
	@echo "Kimi 命令:"
	@echo "  make install          安装配置到 ~/.kimi/"
	@echo "  make install-force    强制安装 kimi（覆盖现有配置）"
	@echo "  make update           更新已安装的 kimi 配置"
	@echo "  make uninstall        卸载 kimi 配置"
	@echo "  make status           查看 kimi 安装状态"
	@echo "  make run              安装并启动 kimi-superpower"
	@echo ""
	@echo "Codex 命令:"
	@echo "  make install-codex        安装配置到 ~/.codex/"
	@echo "  make install-codex-force  强制安装 codex（覆盖现有配置）"
	@echo "  make update-codex         更新已安装的 codex 配置"
	@echo "  make uninstall-codex      卸载 codex 配置"
	@echo "  make status-codex         查看 codex 安装状态"
	@echo "  make run-codex            安装并启动 codex-superpower"
	@echo ""
	@echo "其他命令:"
	@echo "  make test             运行测试"
	@echo "  make clean            清理测试文件"
```

**步骤 3：提交**

```bash
git add Makefile
git commit -m "feat: add codex commands to Makefile"
```

---

## 任务 6：更新测试脚本支持多平台

**文件：**
- 修改：`tests/test_install.sh`

**步骤 1：读取测试脚本了解测试结构**

**步骤 2：添加 PLATFORM 支持**

类似 install.sh，添加 platform 参数支持，默认测试 kimi

**步骤 3：添加 codex 测试用例**

为 codex 添加对应的测试用例

**步骤 4：提交**

```bash
git add tests/test_install.sh
git commit -m "feat: update test script to support codex platform"
```

---

## 任务 7：更新 AGENTS.md 文档

**文件：**
- 修改：`AGENTS.md`

**步骤 1：更新项目结构部分**

添加 codex/ 到项目结构中

**步骤 2：添加 Codex 配置说明**

在 "个人配置" 表格中添加 codex 行

**步骤 3：添加 Codex 安装说明**

添加 codex 的安装和使用说明

**步骤 4：提交**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md with codex configuration"
```

---

## 任务 8：创建 codex-superpower 启动脚本

**文件：**
- 创建：`codex-superpower` (通过 install.sh 创建)

这个文件是由 install.sh 动态生成的，但需要确保：
1. install.sh 正确生成 codex-superpower
2. 脚本使用正确的 codex 命令格式

**步骤 1：验证 codex-superpower 生成**

运行安装后检查：
```bash
./scripts/install.sh codex install
cat codex-superpower
```

**步骤 2：提交（如果有修改）**

---

## 任务 9：最终验证

**步骤 1：完整测试安装流程**

```bash
# 测试 kimi（向后兼容）
./scripts/install.sh status
./scripts/install.sh kimi status

# 测试 codex
./scripts/install.sh codex status
```

**步骤 2：运行测试**

```bash
make test
```

预期：所有测试通过

**步骤 3：验证目录结构**

```bash
tree -L 3 codex/
```

预期：codex/ 目录结构与 kimi/ 一致

---

## 执行交接

**计划已完成并保存到 `docs/plans/2026-02-25-codex-migration.md`。两种执行选项：**

**1. Subagent-Driven（本会话）** - 我为每个任务分派 fresh subagent，任务间审查，快速迭代

**2. 并行会话（分开）** - 打开新会话使用 `dev-executing-plans`，批量执行带检查点

**选择哪种方式？**
