# Kimi Superpower Agent 配置

这是从 [superpowers](https://github.com/obra/superpowers) 项目适配的 Kimi Agent 配置，用于在启动时自动注入 skills 使用要求。

## 文件说明

| 文件 | 说明 |
|------|------|
| `agent.yaml` | Agent 配置文件，继承内置 default agent 并覆盖系统提示词 |
| `system.md` | 系统提示词模板，包含强制使用 skills 的规则 |

## 使用方法

### 方法一：命令行参数（推荐用于测试）

```bash
kimi --agent-file /path/to/my/kimi/agents/superpower/agent.yaml
```

### 方法二：设置别名（推荐日常使用）

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
alias kimi='kimi --agent-file ~/.kimi/agents/superpower/agent.yaml'
```

然后重新加载配置：

```bash
source ~/.zshrc  # 或 source ~/.bashrc
```

### 方法三：复制到 Kimi 配置目录

```bash
# 创建 Kimi agent 配置目录
mkdir -p ~/.kimi/agents

# 复制 agent 配置
cp -r my/kimi/agents/superpower ~/.kimi/agents/

# 然后使用
kimi --agent-file ~/.kimi/agents/superpower/agent.yaml
```

### 方法四：使用安装脚本

运行项目根目录的安装脚本：

```bash
./install.sh
```

这将自动安装 agent 配置到 `~/.kimi/agents/superpower/` 目录。

## 工作原理

1. **系统提示词注入**：`system.md` 中包含了强制要求在每次对话开始时检查和使用 skills 的指令

2. **`${KIMI_SKILLS}` 变量**：Kimi 会自动将发现的 skills 列表注入到这个变量中

3. **自动加载要求**：系统提示词明确要求在每次用户消息时：
   - 首先检查 `${KIMI_SKILLS}` 列表
   - 调用 `/skill:dev-using-skills`（如果可用）
   - 根据任务调用其他适用的 skills

## 自定义配置

你可以修改 `system.md` 来添加：
- 项目特定的规则
- 自定义行为准则
- 额外的环境变量使用

修改 `agent.yaml` 来：
- 排除不需要的工具
- 添加子 agent 定义
- 配置自定义参数

## 验证配置

启动 Kimi 后，可以通过以下方式验证配置是否生效：

1. 查看启动时是否自动加载了 skills 列表
2. 询问 Kimi "请列出可用的 skills"
3. 检查 Kimi 是否在开始任务前主动调用相关 skills
