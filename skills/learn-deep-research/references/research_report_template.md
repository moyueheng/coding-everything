# Research Report Template (Obsidian-Ready)

## Frontmatter

Every report MUST start with YAML frontmatter:

```yaml
---
title: "Report Title"
date: YYYY-MM-DD
tags:
  - research/<topic>
  - deep-research
aliases:
  - Short Alias
status: draft
research_scope: "scope keywords"
research_period: "YYYY-MM to YYYY-MM"
---
```

## Title

Use H1 (`#`) for the report title, matching `title` in frontmatter.

## Executive Summary

Use a `[!abstract]` callout block:

```markdown
> [!abstract] Executive Summary
> - Conclusion 1 (source [[Source - X]])
> - Conclusion 2 (source [[Source - Y]])
> - Conclusion 3
```

3-6 bullets, each supported by evidence.

## Research Question and Scope

- Primary question
- Scope boundaries (included / excluded)
- Time range and geography

## Methodology

- Data sources used
- Search strategy and inclusion criteria
- Limitations and known gaps

## Key Findings

Wrap the top findings in a `[!success]` callout:

```markdown
> [!success] Core Findings
> - Finding 1 (source [[Source - X]])
> - Finding 2 (source [[Source - Y]])
```

### Section 1: [Theme]

Structured paragraphs with inline citations. Use wikilinks when referencing vault notes.

### Section 2: [Theme]

Structured paragraphs with citations.

### Section 3: [Theme]

Structured paragraphs with citations.

## Risks and Limitations

Use a `[!warning]` callout:

```markdown
> [!warning] Risks and Limitations
> - Data gap description
> - Conflicting source note
> - Uncertainty range
```

Unverified inferences use `[!question]`:

```markdown
> [!question] Needs Verification
> - This inference has not been cross-validated
```

## Recommendations (If requested)

- Actionable recommendations tied to findings
- Each recommendation cites evidence

## Evidence Table

```markdown
| Source ID | Title | Publisher | Date | Claim | Confidence |
| --- | --- | --- | --- | --- | --- |
| [[Source - X]] | Title | Publisher | YYYY-MM-DD | Claim text | High |
```

Source IDs use wikilink format to enable future note creation.

## Sources

- `[Title](URL)` — Publisher, Date

For sources that have dedicated vault notes, use `[[Source - Name]]` wikilink instead of or in addition to the URL.
