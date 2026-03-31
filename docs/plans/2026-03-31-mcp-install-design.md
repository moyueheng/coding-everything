# MCP 安装集成设计文档

日期: 2026-03-31

## 目标

在现有 `make install` 流程中新增 MCP 服务器配置管理，自动将 4 个必装 MCP 写入 `~/.claude.json`。

## 必装 MCP 列表

| MCP | 类型 | 认证方式 |
|-----|------|----------|
| `auggie-mcp` | stdio | `auggie login` (浏览器 OAuth) |
| `zai-github-read` | http | Bearer token (共享) |
| `zai-web-reader` | http | Bearer token (共享) |
| `zai-web-search-prime` | http | Bearer token (共享) |

## 方案：扩展现有 `install_skills.py`

在现有安装脚本中新增 MCP 管理逻辑，单入口维护。

## 新增文件

### `mcp-configs/required.json`

```json
{
  "mcpServers": {
    "auggie-mcp": {
      "command": "auggie",
      "args": ["--mcp", "--mcp-auto-workspace"],
      "type": "stdio",
      "_install_note": "需要先安装 Auggie CLI 并执行 `auggie login` 完成浏览器 OAuth 认证。文档: https://docs.augmentcode.com/context-services/mcp/overview"
    },
    "zai-github-read": {
      "type": "http",
      "url": "https://open.bigmodel.cn/api/mcp/zread/mcp",
      "headers": {
        "Authorization": "Bearer {{ZAI_API_KEY}}"
      }
    },
    "zai-web-reader": {
      "type": "http",
      "url": "https://open.bigmodel.cn/api/mcp/web_reader/mcp",
      "headers": {
        "Authorization": "Bearer {{ZAI_API_KEY}}"
      }
    },
    "zai-web-search-prime": {
      "type": "http",
      "url": "https://open.bigmodel.cn/api/mcp/web_search_prime/mcp",
      "headers": {
        "Authorization": "Bearer {{ZAI_API_KEY}}"
      }
    }
  }
}
```

- 3 个 zai 服务共享 `{{ZAI_API_KEY}}` 占位符
- `_install_note` 仅用于安装时输出提示，不写入 `~/.claude.json`

## 代码变更：`scripts/install_skills.py`

### 新增常量

```python
MCP_CONFIG_PATH = "mcp-configs/required.json"
```

### 新增函数

| 函数 | 职责 |
|------|------|
| `load_mcp_template(repo_root)` | 读取 `required.json`，返回 dict |
| `resolve_zai_api_key(claude_config)` | 从现有配置或环境变量解析 zai token |
| `merge_mcp_config(home, repo_root, manifest)` | 合并 MCP 到 `~/.claude.json`，返回已安装列表 |
| `remove_managed_mcps(home, managed_names)` | 根据 manifest 删除已管理的 MCP |
| `collect_mcp_status(home, repo_root)` | 收集 MCP 配置状态用于 status 输出 |

### Token 解析策略

`resolve_zai_api_key()` 优先级：

1. 读 `~/.claude.json` 中已配置的任一 zai 服务的 Bearer token
2. 环境变量 `ZAI_API_KEY`
3. 返回 `None` → 跳过 zai 配置并输出提示

### Manifest 扩展

`install-manifest.json` 新增字段：

```json
{
  "mcp_servers": ["auggie-mcp", "zai-github-read", "zai-web-reader", "zai-web-search-prime"]
}
```

### 各命令行为变化

| 命令 | 新增行为 |
|------|----------|
| `install` | 调用 `merge_mcp_config()`，写入 4 个 MCP，输出结果 + auggie 登录提醒 |
| `update` | 同 install，保留原 `installed_at` |
| `uninstall` | 根据 manifest 中的 `managed_mcp_servers` 删除对应 MCP |
| `status` | 新增 MCP 状态段落：已配置 / 缺失 / 需登录 |

### 终端输出示例

全部成功：

```
MCP servers:
  ✓ auggie-mcp → configured (run `auggie login` if not authenticated)
  ✓ zai-github-read → configured
  ✓ zai-web-reader → configured
  ✓ zai-web-search-prime → configured
```

zai token 缺失：

```
MCP servers:
  ✓ auggie-mcp → configured (run `auggie login` if not authenticated)
  ⚠ zai-github-read → skipped (set ZAI_API_KEY or configure any zai service in ~/.claude.json first)
  ⚠ zai-web-reader → skipped (...)
  ⚠ zai-web-search-prime → skipped (...)
```

## 约束

- **ADD-ONLY**：不删除用户已有的任何 MCP
- **幂等**：重复 install 不产生副作用
- **最小依赖**：仅用标准库 `json` / `pathlib` / `os`
- **Manifest 驱动**：只有 manifest 记录的 MCP 才会在 uninstall 时被移除
- **无交互**：脚本不弹出 prompt，缺失 token 时跳过并提示

## 不做的事

- 不管理 auggie CLI 安装（用户自行安装）
- 不管理 zai API key 的注册/获取
- 不修改项目级 `.mcp.json`
- 不处理 MCP 服务器启动/健康检查
