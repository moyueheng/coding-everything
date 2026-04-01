---
name: obsidian-bases
description: 创建和编辑包含视图、过滤器、公式和汇总的 Obsidian Bases（.base 文件）。适用于处理 .base 文件、创建类似数据库的笔记视图，或当用户在 Obsidian 中提到 Bases、表格视图、卡片视图、过滤器或公式时。
---

# Obsidian Bases Skill

## Workflow

1. **Create the file**：在 vault 中创建一个包含合法 YAML 内容的 `.base` 文件
2. **Define scope**：添加 `filters` 来选择哪些笔记会出现（按标签、文件夹、property 或日期）
3. **Add formulas**（可选）：在 `formulas` 部分定义计算属性
4. **Configure views**：添加一个或多个视图（`table`、`cards`、`list` 或 `map`），并在 `order` 中指定显示哪些属性
5. **Validate**：确认文件是合法 YAML 且没有语法错误。检查所有引用的属性和公式都存在。常见问题：包含特殊 YAML 字符但未加引号的字符串、公式表达式中的引号不匹配、引用了 `formula.X` 但没有在 `formulas` 中定义 `X`
6. **Test in Obsidian**：在 Obsidian 中打开该 `.base` 文件，确认视图渲染正确。如果出现 YAML 错误，检查下方的引号规则

## Schema

Base 文件使用 `.base` 扩展名，并包含合法 YAML。

```yaml
# Global filters apply to ALL views in the base
filters:
  # Can be a single filter string
  # OR a recursive filter object with and/or/not
  and: []
  or: []
  not: []

# Define formula properties that can be used across all views
formulas:
  formula_name: 'expression'

# Configure display names and settings for properties
properties:
  property_name:
    displayName: "Display Name"
  formula.formula_name:
    displayName: "Formula Display Name"
  file.ext:
    displayName: "Extension"

# Define custom summary formulas
summaries:
  custom_summary_name: 'values.mean().round(3)'

# Define one or more views
views:
  - type: table | cards | list | map
    name: "View Name"
    limit: 10                    # Optional: limit results
    groupBy:                     # Optional: group results
      property: property_name
      direction: ASC | DESC
    filters:                     # View-specific filters
      and: []
    order:                       # Properties to display in order
      - file.name
      - property_name
      - formula.formula_name
    summaries:                   # Map properties to summary formulas
      property_name: Average
```

## Filter Syntax

过滤器用于缩小结果范围。它们既可以全局应用，也可以按视图单独应用。

### Filter Structure

```yaml
# Single filter
filters: 'status == "done"'

# AND - all conditions must be true
filters:
  and:
    - 'status == "done"'
    - 'priority > 3'

# OR - any condition can be true
filters:
  or:
    - 'file.hasTag("book")'
    - 'file.hasTag("article")'

# NOT - exclude matching items
filters:
  not:
    - 'file.hasTag("archived")'

# Nested filters
filters:
  or:
    - file.hasTag("tag")
    - and:
        - file.hasTag("book")
        - file.hasLink("Textbook")
    - not:
        - file.hasTag("book")
        - file.inFolder("Required Reading")
```

### Filter Operators

| Operator | Description |
|----------|-------------|
| `==` | 等于 |
| `!=` | 不等于 |
| `>` | 大于 |
| `<` | 小于 |
| `>=` | 大于等于 |
| `<=` | 小于等于 |
| `&&` | 逻辑与 |
| `\|\|` | 逻辑或 |
| <code>!</code> | 逻辑非 |

## Properties

### Three Types of Properties

1. **Note properties**：来自 frontmatter，例如 `note.author` 或直接写 `author`
2. **File properties**：文件元数据，例如 `file.name`、`file.mtime`
3. **Formula properties**：计算得到的值，例如 `formula.my_formula`

### File Properties Reference

| Property | Type | Description |
|----------|------|-------------|
| `file.name` | String | 文件名 |
| `file.basename` | String | 不含扩展名的文件名 |
| `file.path` | String | 文件完整路径 |
| `file.folder` | String | 父文件夹路径 |
| `file.ext` | String | 文件扩展名 |
| `file.size` | Number | 文件大小（字节） |
| `file.ctime` | Date | 创建时间 |
| `file.mtime` | Date | 修改时间 |
| `file.tags` | List | 文件中的所有标签 |
| `file.links` | List | 文件中的内部链接 |
| `file.backlinks` | List | 链接到此文件的文件 |
| `file.embeds` | List | 笔记中的嵌入内容 |
| `file.properties` | Object | 所有 frontmatter 属性 |

### The `this` Keyword

- 在主内容区中：指向 base 文件本身
- 被嵌入时：指向嵌入它的文件
- 在侧边栏中：指向主内容区当前激活的文件

## Formula Syntax

公式用于基于属性计算值，定义在 `formulas` 部分。

```yaml
formulas:
  # Simple arithmetic
  total: "price * quantity"

  # Conditional logic
  status_icon: 'if(done, "✅", "⏳")'

  # String formatting
  formatted_price: 'if(price, price.toFixed(2) + " dollars")'

  # Date formatting
  created: 'file.ctime.format("YYYY-MM-DD")'

  # Calculate days since created (use .days for Duration)
  days_old: '(now() - file.ctime).days'

  # Calculate days until due date
  days_until_due: 'if(due_date, (date(due_date) - today()).days, "")'
```

## Key Functions

最常用的函数列在下面。所有类型（Date、String、Number、List、File、Link、Object、RegExp）的完整参考见 [FUNCTIONS_REFERENCE.md](references/FUNCTIONS_REFERENCE.md)。

| Function | Signature | Description |
|----------|-----------|-------------|
| `date()` | `date(string): date` | 将字符串解析为日期（`YYYY-MM-DD HH:mm:ss`） |
| `now()` | `now(): date` | 当前日期和时间 |
| `today()` | `today(): date` | 当前日期（时间 = `00:00:00`） |
| `if()` | `if(condition, trueResult, falseResult?)` | 条件判断 |
| `duration()` | `duration(string): duration` | 解析 duration 字符串 |
| `file()` | `file(path): file` | 获取文件对象 |
| `link()` | `link(path, display?): Link` | 创建链接 |

### Duration Type

两个日期相减时，结果是 **Duration** 类型，而不是数字。

**Duration Fields：** `duration.days`、`duration.hours`、`duration.minutes`、`duration.seconds`、`duration.milliseconds`

**IMPORTANT：** Duration 不能直接使用 `.round()`、`.floor()`、`.ceil()`。必须先取出数值字段（如 `.days`），再应用数字函数。

```yaml
# CORRECT: Calculate days between dates
"(date(due_date) - today()).days"                    # Returns number of days
"(now() - file.ctime).days"                          # Days since created
"(date(due_date) - today()).days.round(0)"           # Rounded days

# WRONG - will cause error:
# "((date(due) - today()) / 86400000).round(0)"      # Duration doesn't support division then round
```

### Date Arithmetic

```yaml
# Duration units: y/year/years, M/month/months, d/day/days,
#                 w/week/weeks, h/hour/hours, m/minute/minutes, s/second/seconds
"now() + \"1 day\""       # Tomorrow
"today() + \"7d\""        # A week from today
"now() - file.ctime"      # Returns Duration
"(now() - file.ctime).days"  # Get days as number
```

## View Types

### Table View

```yaml
views:
  - type: table
    name: "My Table"
    order:
      - file.name
      - status
      - due_date
    summaries:
      price: Sum
      count: Average
```

### Cards View

```yaml
views:
  - type: cards
    name: "Gallery"
    order:
      - file.name
      - cover_image
      - description
```

### List View

```yaml
views:
  - type: list
    name: "Simple List"
    order:
      - file.name
      - status
```

### Map View

需要经纬度属性以及 Maps 社区插件。

```yaml
views:
  - type: map
    name: "Locations"
    # Map-specific settings for lat/lng properties
```

## Default Summary Formulas

| Name | Input Type | Description |
|------|------------|-------------|
| `Average` | Number | 算术平均值 |
| `Min` | Number | 最小值 |
| `Max` | Number | 最大值 |
| `Sum` | Number | 总和 |
| `Range` | Number | 最大值 - 最小值 |
| `Median` | Number | 中位数 |
| `Stddev` | Number | 标准差 |
| `Earliest` | Date | 最早日期 |
| `Latest` | Date | 最晚日期 |
| `Range` | Date | 最晚日期 - 最早日期 |
| `Checked` | Boolean | `true` 值的数量 |
| `Unchecked` | Boolean | `false` 值的数量 |
| `Empty` | Any | 空值数量 |
| `Filled` | Any | 非空值数量 |
| `Unique` | Any | 唯一值数量 |

## Complete Examples

### Task Tracker Base

```yaml
filters:
  and:
    - file.hasTag("task")
    - 'file.ext == "md"'

formulas:
  days_until_due: 'if(due, (date(due) - today()).days, "")'
  is_overdue: 'if(due, date(due) < today() && status != "done", false)'
  priority_label: 'if(priority == 1, "🔴 High", if(priority == 2, "🟡 Medium", "🟢 Low"))'

properties:
  status:
    displayName: Status
  formula.days_until_due:
    displayName: "Days Until Due"
  formula.priority_label:
    displayName: Priority

views:
  - type: table
    name: "Active Tasks"
    filters:
      and:
        - 'status != "done"'
    order:
      - file.name
      - status
      - formula.priority_label
      - due
      - formula.days_until_due
    groupBy:
      property: status
      direction: ASC
    summaries:
      formula.days_until_due: Average

  - type: table
    name: "Completed"
    filters:
      and:
        - 'status == "done"'
    order:
      - file.name
      - completed_date
```

### Reading List Base

```yaml
filters:
  or:
    - file.hasTag("book")
    - file.hasTag("article")

formulas:
  reading_time: 'if(pages, (pages * 2).toString() + " min", "")'
  status_icon: 'if(status == "reading", "📖", if(status == "done", "✅", "📚"))'
  year_read: 'if(finished_date, date(finished_date).year, "")'

properties:
  author:
    displayName: Author
  formula.status_icon:
    displayName: ""
  formula.reading_time:
    displayName: "Est. Time"

views:
  - type: cards
    name: "Library"
    order:
      - cover
      - file.name
      - author
      - formula.status_icon
    filters:
      not:
        - 'status == "dropped"'

  - type: table
    name: "Reading List"
    filters:
      and:
        - 'status == "to-read"'
    order:
      - file.name
      - author
      - pages
      - formula.reading_time
```

### Daily Notes Index

```yaml
filters:
  and:
    - file.inFolder("Daily Notes")
    - '/^\d{4}-\d{2}-\d{2}$/.matches(file.basename)'

formulas:
  word_estimate: '(file.size / 5).round(0)'
  day_of_week: 'date(file.basename).format("dddd")'

properties:
  formula.day_of_week:
    displayName: "Day"
  formula.word_estimate:
    displayName: "~Words"

views:
  - type: table
    name: "Recent Notes"
    limit: 30
    order:
      - file.name
      - formula.day_of_week
      - formula.word_estimate
      - file.mtime
```

## Embedding Bases

在 Markdown 文件中嵌入：

```markdown
![[MyBase.base]]

<!-- Specific view -->
![[MyBase.base#View Name]]
```

## YAML Quoting Rules

- 公式中如果包含双引号，使用单引号包裹整个公式：`'if(done, "Yes", "No")'`
- 简单字符串使用双引号：`"My View Name"`
- 复杂表达式中的嵌套引号要正确转义

## Troubleshooting

### YAML Syntax Errors

**未加引号的特殊字符**：字符串中如果包含 `:`、`{`、`}`、`[`、`]`、`,`、`&`、`*`、`#`、`?`、`|`、`-`、`<`、`>`、`=`、`!`、`%`、`@`、`` ` ``，必须加引号。

```yaml
# WRONG - colon in unquoted string
displayName: Status: Active

# CORRECT
displayName: "Status: Active"
```

**公式中的引号不匹配**：如果公式内部含有双引号，用单引号包住整个公式。

```yaml
# WRONG - double quotes inside double quotes
formulas:
  label: "if(done, "Yes", "No")"

# CORRECT - single quotes wrapping double quotes
formulas:
  label: 'if(done, "Yes", "No")'
```

### Common Formula Errors

**未访问字段就直接做 Duration 运算**：日期相减返回的是 Duration，不是数字。必须始终访问 `.days`、`.hours` 等字段。

```yaml
# WRONG - Duration is not a number
"(now() - file.ctime).round(0)"

# CORRECT - access .days first, then round
"(now() - file.ctime).days.round(0)"
```

**缺少空值保护**：某些属性并不会在所有笔记中都存在。使用 `if()` 做保护。

```yaml
# WRONG - crashes if due_date is empty
"(date(due_date) - today()).days"

# CORRECT - guard with if()
'if(due_date, (date(due_date) - today()).days, "")'
```

**引用了未定义的公式**：确保 `order` 或 `properties` 中出现的每个 `formula.X`，在 `formulas` 中都有对应定义。

```yaml
# This will fail silently if 'total' is not defined in formulas
order:
  - formula.total

# Fix: define it
formulas:
  total: "price * quantity"
```

## References

- [Bases Syntax](https://help.obsidian.md/bases/syntax)
- [Functions](https://help.obsidian.md/bases/functions)
- [Views](https://help.obsidian.md/bases/views)
- [Formulas](https://help.obsidian.md/formulas)
- [Complete Functions Reference](references/FUNCTIONS_REFERENCE.md)
