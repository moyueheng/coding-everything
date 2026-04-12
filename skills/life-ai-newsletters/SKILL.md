---
name: life-ai-newsletters
description: Curate AI newsletter content with smart deduplication and ranking. Use when user invokes /life-ai-newsletters or when /life-start-my-day needs newsletter content.
---
# AI Newsletter 内容策划

抓取、去重、排序 AI newsletter 内容，生成每日摘要。

## RSS 来源

- **TLDR AI**: `https://bullrich.dev/tldr-rss/ai.rss`
- **The Rundown AI**: `https://rss.beehiiv.com/feeds/2R3C6Bt5wj.xml`

## 工作流

1. **检查缓存**：查找 `50_Resources/NewsLetter/YYYY-MM/YYYY-MM-DD-Digest.md`。如果存在且日期为今天，返回缓存内容。

2. **抓取订阅源**：使用 网页阅读工具 访问两个 RSS URL。提取每条内容的 title、link、pubDate、description。

3. **去重**：合并标题相似的内容（80% 以上词汇重叠）。保留较长的描述，跟踪两个来源。

4. **排序**，依据：
   - AI 相关度（LLM、GPT、Claude、agents、ML 关键词）
   - 生产力相关度（workflow、automation、tools、PKM）
   - 时效性（越新越靠前）
   - 新颖度（检查近期存档，惩罚重复内容）

5. **生成摘要**：格式参考 [TEMPLATE.md](TEMPLATE.md)。包含：
   - Top Picks（3-5 个最高分）附带内容创作角度
   - AI 趋势区域
   - 生产力工具区域
   - 统计信息页脚

6. **保存文件**：
   - `50_Resources/NewsLetter/YYYY-MM/YYYY-MM-DD-Digest.md`（精选摘要）
   - `50_Resources/NewsLetter/YYYY-MM/Raw/YYYY-MM-DD_TLDR-AI-Raw.md`
   - `50_Resources/NewsLetter/YYYY-MM/Raw/YYYY-MM-DD_Rundown-AI-Raw.md`

## 输出格式

**手动调用**：展示包含所有区域的完整摘要。

**由 /life-start-my-day 调用**：返回精简列表：
```
**内容机会（5）：**
- [Title] - [角度]
...
完整摘要：[[YYYY-MM-DD-Digest]]
```

## 错误处理

- 单个订阅源不可用：使用另一个继续，在摘要中备注
- 两个订阅源都不可用：使用昨日存档并附加警告
- 订阅源为空：创建最小化摘要，注明"No new items"
