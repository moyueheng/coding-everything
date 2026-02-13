# Kimi Configuration

基于 [superpowers](https://github.com/obra/superpowers) 框架的 Kimi Code CLI 配置。

## 快速开始

### 使用 Makefile（推荐）

```bash
# 查看所有可用命令
make help

# 安装配置
make install

# 更新配置
make update

# 查看状态
make status

# 运行测试
make test
```

### 直接使用脚本

```bash
# 安装配置
./scripts/install.sh

# 启动 Kimi
./kimi-superpower
```

## 包含内容

### Skills (11 个)

| Skill | 用途 | 类型 |
|-------|------|------|
| `dev-using-skills` | 技能使用入口 | 严格 |
| `dev-brainstorming` | 编码前苏格拉底式对话 | 严格 |
| `dev-debugging` | 四阶段调试流程 | 严格 |
| `dev-tdd` | 测试驱动开发 | 严格 |
| `dev-writing-plans` | 编写实施计划 | 严格 |
| `dev-executing-plans` | 执行计划 | 严格 |
| `dev-git-worktrees` | Git 工作树管理 | 严格 |
| `dev-requesting-review` | 代码审查请求 | 严格 |
| `dev-verification` | 完成前验证 | 严格 |
| `dev-finishing-branch` | 分支完成工作流 | 严格 |
| `dev-writing-skills` | 编写新技能 | 严格 |

### Agent

- `superpower/` - 基于 superpowers 框架的智能体配置

## 安装脚本

单文件脚本：`scripts/install.sh`

```bash
# 安装（默认）
./scripts/install.sh
./scripts/install.sh install

# 强制安装（覆盖）
./scripts/install.sh install -f

# 更新配置
./scripts/install.sh update

# 卸载配置
./scripts/install.sh uninstall

# 查看状态
./scripts/install.sh status

# 帮助
./scripts/install.sh --help
```

## 测试

```bash
# 运行测试
./tests/test_install.sh
```

## 安装路径

统一安装到 `~/.kimi/`：
- Skills: `~/.kimi/skills/`
- Agent: `~/.kimi/agents/superpower/`

## 使用方法

### 方式1: 使用生成的启动脚本（推荐）

```bash
# 安装后会在项目根目录生成 kimi-superpower 脚本
./kimi-superpower
```

### 方式2: 直接指定 agent-file

```bash
kimi --agent-file ~/.kimi/agents/superpower/agent.yaml
```

### 方式3: 创建别名

添加到 `~/.bashrc` 或 `~/.zshrc`:

```bash
alias kimi-superpower='kimi --agent-file ~/.kimi/agents/superpower/agent.yaml'
```

## 目录结构

```
kimi/
├── README.md                    # 本文件
├── agents/
│   └── superpower/              # Agent 配置
│       ├── agent.yaml           # Agent 定义
│       ├── system.md            # 系统提示词
│       └── README.md
└── skills/                      # Skills 目录
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

## 核心工作流

```
1. 头脑风暴 → 通过提问完善想法
         ↓
2. 编写计划 → 将工作分解为 2-5 分钟任务
         ↓
3. 执行计划 → 按步骤实现
         ↓
4. TDD 开发 → RED → GREEN → REFACTOR
         ↓
5. 代码审查 → 检查清单
         ↓
6. 完成分支 → 验证并合并
```

## 相关链接

- [Kimi Code CLI 文档](https://moonshotai.github.io/kimi-cli/)
- [superpowers 框架](https://github.com/obra/superpowers)
- [Agent Skills 规范](https://agentskills.io/)
