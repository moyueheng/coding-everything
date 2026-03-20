---
name: dev-update-codemaps
description: 分析代码库结构并生成 token-lean 架构文档。
---

# 更新 Codemaps

分析代码库结构并生成 token-lean 架构文档。

## 第 1 步：扫描项目结构

1. 识别项目类型（monorepo、单应用、库、microservice）
2. 查找所有源代码目录（src/、lib/、app/、packages/）
3. 映射入口点（main.ts、index.ts、app.py、main.go 等）

## 第 2 步：生成 Codemaps

在 `docs/CODEMAPS/`（或 `.reports/codemaps/`）中创建或更新 codemaps：

| 文件 | 内容 |
|------|----------|
| `architecture.md` | 高层系统图、服务边界、数据流 |
| `backend.md` | API routes、middleware chain、service → repository 映射 |
| `frontend.md` | 页面树、组件层级、状态管理流 |
| `data.md` | 数据库表、关系、迁移历史 |
| `dependencies.md` | 外部服务、第三方集成、共享库 |

### Codemap 格式

每个 codemap 应为 token-lean —— 针对 AI 上下文消费进行优化：

```markdown
# Backend Architecture

## Routes
POST /api/users → UserController.create → UserService.create → UserRepo.insert
GET  /api/users/:id → UserController.get → UserService.findById → UserRepo.findById

## Key Files
src/services/user.ts (业务逻辑, 120 行)
src/repos/user.ts (数据库访问, 80 行)

## Dependencies
- PostgreSQL (主数据存储)
- Redis (会话缓存、限流)
- Stripe (支付处理)
```

## 第 3 步：差异检测

1. 如果存在先前的 codemaps，计算差异百分比
2. 如果变更 > 30%，显示差异并在覆盖前请求用户批准
3. 如果变更 <= 30%，就地更新

## 第 4 步：添加元数据

为每个 codemap 添加新鲜度标头：

```markdown
<!-- 生成时间: 2026-02-11 | 扫描文件: 142 | Token 估算: ~800 -->
```

## 第 5 步：保存分析报告

将摘要写入 `.reports/codemap-diff.txt`：
- 自上次扫描以来添加/删除/修改的文件
- 检测到的新依赖
- 架构变更（新 routes、新 services 等）
- 90+ 天未更新文档的陈旧警告

## 提示

- 关注**高层结构**，而非实现细节
- 优先使用**文件路径和函数签名**，而非完整代码块
- 保持每个 codemap 在 **1000 tokens** 以内，以实现高效的上下文加载
- 使用 ASCII 图表示数据流，而非冗长描述
- 在主要功能添加或重构会话后运行
