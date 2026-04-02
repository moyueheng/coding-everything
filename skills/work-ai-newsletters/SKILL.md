---
name: work-ai-newsletters
description: Curate AI newsletter content with smart deduplication and ranking. Use when user invokes /ai-newsletters or when /start-my-day needs newsletter content.
---
# AI Newsletter Curation

Fetch, deduplicate, and rank AI newsletter content into a daily digest.

## RSS Sources

- **TLDR AI**: `https://bullrich.dev/tldr-rss/ai.rss`
- **The Rundown AI**: `https://rss.beehiiv.com/feeds/2R3C6Bt5wj.xml`

## Workflow

1. **Check cache**: Look for `50_Resources/NewsLetter/YYYY-MM/YYYY-MM-DD-Digest.md`. If exists with today's date, return cached content.

2. **Fetch feeds**: Use WebFetch on both RSS URLs. Extract title, link, pubDate, description for each item.

3. **Deduplicate**: Merge items with similar titles (80%+ word overlap). Keep longer description, track both sources.

4. **Rank items** by:
   - AI relevance (LLM, GPT, Claude, agents, ML keywords)
   - Productivity relevance (workflow, automation, tools, PKM)
   - Recency (newer = higher)
   - Novelty (check recent archives, penalize repeats)

5. **Generate digest**: See [TEMPLATE.md](TEMPLATE.md) for format. Include:
   - Top Picks (3-5 highest scoring) with content creation angles
   - AI Trends section
   - Productivity Tools section
   - Stats footer

6. **Save files**:
   - `50_Resources/NewsLetter/YYYY-MM/YYYY-MM-DD-Digest.md` (curated)
   - `50_Resources/NewsLetter/YYYY-MM/Raw/YYYY-MM-DD_TLDR-AI-Raw.md`
   - `50_Resources/NewsLetter/YYYY-MM/Raw/YYYY-MM-DD_Rundown-AI-Raw.md`

## Output Format

**Manual invocation**: Display full digest with all sections.

**From /start-my-day**: Return condensed list:
```
**Content Opportunities (5):**
- [Title] - [Angle]
...
Full digest: [[YYYY-MM-DD-Digest]]
```

## Error Handling

- One feed down: Continue with other, note in digest
- Both down: Use yesterday's archive with warning
- Empty feeds: Create minimal digest noting "No new items"
