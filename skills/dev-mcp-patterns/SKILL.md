---
name: dev-mcp-patterns
description: 使用 Node/TypeScript SDK 构建 MCP (Model Context Protocol) 服务器 —— tools、resources、prompts、Zod 验证、stdio vs Streamable HTTP。需要最新 API 时查询 Context7 或官方 MCP 文档。
---

# MCP Server 开发模式

Model Context Protocol (MCP) 让 AI 助手能够调用工具、读取资源和使用来自你服务器的 prompts。使用此 skill 构建或维护 MCP 服务器。SDK API 会演进；通过 Context7 (query-docs for "MCP") 或官方 MCP 文档检查当前方法名和签名。

## 何时使用

使用场景：实现新的 MCP 服务器、添加工具或资源、选择 stdio vs HTTP、升级 SDK、调试 MCP 注册和传输问题。

## 工作原理

### 核心概念

- **Tools**: 模型可以调用的动作（例如搜索、运行命令）。使用 `registerTool()` 或 `tool()` 注册，取决于 SDK 版本。
- **Resources**: 模型可以获取的只读数据（例如文件内容、API 响应）。使用 `registerResource()` 或 `resource()` 注册。处理器通常接收 `uri` 参数。
- **Prompts**: 客户端可以展示的、可复用的、参数化的 prompt 模板（例如在 Claude Desktop 中）。使用 `registerPrompt()` 或等效方法注册。
- **Transport**: stdio 用于本地客户端（例如 Claude Desktop）；Streamable HTTP 推荐用于远程（Cursor、云端）。遗留 HTTP/SSE 用于向后兼容。

Node/TypeScript SDK 可能暴露 `tool()` / `resource()` 或 `registerTool()` / `registerResource()`；官方 SDK 随时间变化。始终根据当前 [MCP 文档](https://modelcontextprotocol.io) 或 Context7 验证 `@modelcontextprotocol/sdk` 签名，避免复制粘贴错误。

### 使用 stdio 连接

对于本地客户端，创建 stdio transport 并传递给你服务器的 connect 方法。确切 API 因 SDK 版本而异（例如 constructor vs factory）。查询官方 MCP 文档或 Context7 "MCP stdio server" 获取当前模式。

保持服务器逻辑（tools + resources）独立于 transport，这样你可以在 entrypoint 中插入 stdio 或 HTTP。

### 远程（Streamable HTTP）

对于 Cursor、云端或其他远程客户端，使用 **Streamable HTTP**（根据当前 spec 的单个 MCP HTTP 端点）。仅当需要向后兼容时才支持遗留 HTTP/SSE。

## 示例

### 安装和服务器设置

```bash
npm install @modelcontextprotocol/sdk zod
```

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({ name: "my-server", version: "1.0.0" });
```

使用你的 SDK 版本提供的 API 注册工具和资源：某些版本使用 `server.tool(name, description, schema, handler)`（位置参数），其他使用 `server.tool({ name, description, inputSchema }, handler)` 或 `registerTool()`。Resources 同理 —— 当 API 提供时在处理器中包含 `uri`。查询官方 MCP 文档或 Context7 获取当前 `@modelcontextprotocol/sdk` 签名，避免复制粘贴错误。

使用 **Zod**（或 SDK 首选的 schema 格式）进行输入验证。

## 最佳实践

- **Schema 优先**: 为每个工具定义输入 schemas；记录参数和返回形状。
- **错误处理**: 返回模型能够理解的结构化错误或消息；避免原始堆栈跟踪。
- **幂等性**: 尽可能使用幂等工具，这样重试是安全的。
- **速率和成本**: 对于调用外部 API 的工具，考虑速率限制和成本；在工具描述中记录。
- **版本控制**: 在 package.json 中固定 SDK 版本；升级时查看 release notes。

## 官方 SDK 和文档

- **JavaScript/TypeScript**: `@modelcontextprotocol/sdk` (npm)。使用 Context7 库名 "MCP" 获取当前注册和传输模式。
- **Go**: GitHub 上的官方 Go SDK (`modelcontextprotocol/go-sdk`)。
- **C#**: 用于 .NET 的官方 C# SDK。

## 参考

- origin: everything-claude-code/skills/mcp-server-patterns
