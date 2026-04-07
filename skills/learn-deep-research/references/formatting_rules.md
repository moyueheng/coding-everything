# Formatting Rules

Use these rules to enforce strict report formatting.

## Headings
- Use H1 for the report title (once per file)
- Use H2 for top-level sections
- Use H3 for subsections
- Keep heading titles consistent with the report spec

## Section Order
- Follow the report spec order exactly
- Do not add or remove sections without approval

## Bullets and Tables
- Use bullets for lists of findings and actions
- Use tables for comparisons, metrics, or timelines
- Keep tables compact and label all columns

## Citations
- Use the citation style defined in the report spec
- Place citations immediately after the claim
- If a claim has multiple sources, list all relevant sources

## Terminology
- Define key terms once and reuse consistently
- Preserve technical terms in English

## Formatting Hygiene
- Avoid mixed numbering styles in the same section
- Avoid inline URLs in prose unless the spec requires it
- Do not embed new assets unless requested

## Obsidian-Specific Rules

### Frontmatter Properties
- Every report file MUST have YAML frontmatter
- Required properties: `title`, `date`, `tags`
- Recommended properties: `aliases`, `status`, `research_scope`, `research_period`
- Use `date` in `YYYY-MM-DD` format

### Callout Usage
- `[!abstract]` for Executive Summary
- `[!success]` for confirmed key findings
- `[!warning]` for risks, limitations, data gaps
- `[!question]` for unverified inferences requiring further validation
- `[!info]` for methodology notes or background context
- Do NOT use callouts for regular body text

### Wikilinks
- Reference vault-internal notes with `[[Note Name]]`
- Source IDs in evidence tables use `[[Source - Name Year]]` format
- For display text different from note name: `[[Source - X|X]]`
- External URLs remain standard Markdown `[text](url)`

### Tags
- Use nested tag format: `#research/<topic>`
- Always include `#deep-research` tag
- Tags in frontmatter `tags` property, not inline `#tag` in prose (avoids rendering issues)

### Embeds
- Use `![[note]]` to embed shared sections (e.g., methodology notes) when vault structure supports it
- Do NOT embed unless the referenced note exists in the vault
