---
name: life-ai-products
description: Curate AI product launches from Product Hunt, Hacker News, GitHub, and Techmeme. Use when user invokes /life-ai-products or when /life-start-my-day needs product launches.
---
# AI 产品发现

从多个来源抓取、去重、排序 AI 产品发布信息。

## 来源

| 来源 | URL | 说明 |
|------|-----|------|
| Product Hunt | `https://www.producthunt.com/feed` | 筛选 AI 相关 |
| Hacker News | `https://hn.algolia.com/api/v1/search?tags=show_hn&numericFilters=created_at_i>TIMESTAMP` | Show HN 帖子，24 小时窗口 |
| GitHub Trending | `https://mshibanami.github.io/GitHubTrendingRSS/daily/python.xml` | Python 仓库 |
| Techmeme | `https://techmeme.com/river` | 产品公告 |

## 工作流

1. **检查缓存**：查找 `50_Resources/ProductLaunches/YYYY-MM/YYYY-MM-DD-Digest.md`。如果存在且日期为今天，返回缓存。

2. **抓取来源**：使用 网页阅读工具 逐个访问。提取产品名称、URL、描述和互动指标（votes/points/stars）。

3. **筛选**：仅保留 AI 相关产品（关键词：AI、ML、LLM、GPT、Claude、automation、agent、model）。

4. **去重**：同一产品出现在多个来源则合并。保留最佳描述，合并指标，跟踪所有来源。

5. **排序**，依据：
   - AI 相关度
   - 互动量（归一化：PH votes/500、HN points/100、GH stars/1000）
   - 内容潜力（适合教程、值得评测、开源加分）
   - 时效性和新颖度

6. **生成摘要**：格式参考 [TEMPLATE.md](TEMPLATE.md)。区域包括：
   - Top Picks（3-5 个）附带内容角度
   - LLM & AI 模型
   - 开发者工具
   - 生产力与自动化
   - 开源精选

7. **保存文件**：
   - `50_Resources/ProductLaunches/YYYY-MM/YYYY-MM-DD-Digest.md`
   - `50_Resources/ProductLaunches/YYYY-MM/Raw/YYYY-MM-DD_ProductHunt-Raw.md`
   - `50_Resources/ProductLaunches/YYYY-MM/Raw/YYYY-MM-DD_HackerNews-Raw.md`
   - `50_Resources/ProductLaunches/YYYY-MM/Raw/YYYY-MM-DD_GitHub-Raw.md`

## 输出格式

**手动调用**：展示包含所有区域的完整摘要。

**由 /life-start-my-day 调用**：返回精简列表：
```
**产品发布机会（5）：**
- [Product] - [角度] - [核心指标]
...
完整摘要：[[YYYY-MM-DD-Digest]]
```

## 错误处理

- 单个来源不可用：使用其余来源继续，在摘要中备注
- 可用来源少于 2 个：回退到昨日存档
- 结果为空：创建最小化摘要，注明"No new AI products"

## 内容角度逻辑

- 高互动 + 适合教程："教程机会"
- 新颖 + 早期阶段："先发优势"
- 开源 + 复杂："深度分析"
- SaaS + 实用："工具评测"
- 与已有产品相似："与 [competitor] 对比"
