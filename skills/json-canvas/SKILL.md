---
name: json-canvas
description: 创建和编辑包含节点、边、分组和连接关系的 JSON Canvas 文件（.canvas）。适用于处理 .canvas 文件、创建可视化画布、思维导图、流程图，或当用户在 Obsidian 中提到 Canvas 文件时。
---

# JSON Canvas Skill

## File Structure

一个 canvas 文件（`.canvas`）遵循 [JSON Canvas Spec 1.0](https://jsoncanvas.org/spec/1.0/)，包含两个顶层数组：

```json
{
  "nodes": [],
  "edges": []
}
```

- `nodes`（可选）：节点对象数组
- `edges`（可选）：连接节点的边对象数组

## Common Workflows

### 1. Create a New Canvas

1. 创建一个 `.canvas` 文件，基础结构为 `{"nodes": [], "edges": []}`
2. 为每个节点生成唯一的 16 字符十六进制 ID（例如 `"6f0ad84f44ce9c17"`）
3. 添加节点，并填写必需字段：`id`、`type`、`x`、`y`、`width`、`height`
4. 添加边，并通过 `fromNode` 和 `toNode` 引用合法的节点 ID
5. **Validate**：解析 JSON 确认其合法，并验证所有 `fromNode` / `toNode` 的值都存在于 `nodes` 数组中

### 2. Add a Node to an Existing Canvas

1. 读取并解析现有 `.canvas` 文件
2. 生成一个不会与现有节点或边 ID 冲突的唯一 ID
3. 选择不会与现有节点重叠的位置（`x`、`y`），至少保留 50-100px 间距
4. 将新节点对象追加到 `nodes` 数组
5. 按需添加边，将新节点连接到现有节点
6. **Validate**：确认所有 ID 都唯一，且所有边引用都能解析到现有节点

### 3. Connect Two Nodes

1. 找到源节点和目标节点的 ID
2. 生成唯一的边 ID
3. 设置 `fromNode` 和 `toNode`
4. 可选设置 `fromSide` / `toSide`（top、right、bottom、left）作为锚点
5. 可选设置 `label` 作为边上的说明文本
6. 将该边追加到 `edges` 数组
7. **Validate**：确认 `fromNode` 和 `toNode` 都引用了存在的节点 ID

### 4. Edit an Existing Canvas

1. 将 `.canvas` 文件读取并解析为 JSON
2. 根据 `id` 定位目标节点或边
3. 修改所需属性（文本、位置、颜色等）
4. 将更新后的 JSON 写回文件
5. **Validate**：编辑后重新检查所有 ID 的唯一性和边引用完整性

## Nodes

节点是放置在画布上的对象。数组顺序决定 z-index：第一个节点在最底层，最后一个节点在最上层。

### Generic Node Attributes

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `id` | Yes | string | 唯一的 16 字符十六进制标识符 |
| `type` | Yes | string | `text`、`file`、`link` 或 `group` |
| `x` | Yes | integer | X 坐标，单位像素 |
| `y` | Yes | integer | Y 坐标，单位像素 |
| `width` | Yes | integer | 宽度，单位像素 |
| `height` | Yes | integer | 高度，单位像素 |
| `color` | No | canvasColor | 预设值 `"1"`-`"6"` 或十六进制颜色（如 `"#FF0000"`） |

### Text Nodes

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `text` | Yes | string | 支持 Markdown 语法的纯文本 |

```json
{
  "id": "6f0ad84f44ce9c17",
  "type": "text",
  "x": 0,
  "y": 0,
  "width": 400,
  "height": 200,
  "text": "# Hello World\n\nThis is **Markdown** content."
}
```

**Newline pitfall**：JSON 字符串中的换行必须使用 `\n`。不要使用字面量 `\\n`，否则 Obsidian 会把它渲染成字符 `\` 和 `n`。

### File Nodes

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `file` | Yes | string | 系统中的文件路径 |
| `subpath` | No | string | 指向标题或块的链接（以 `#` 开头） |

```json
{
  "id": "a1b2c3d4e5f67890",
  "type": "file",
  "x": 500,
  "y": 0,
  "width": 400,
  "height": 300,
  "file": "Attachments/diagram.png"
}
```

### Link Nodes

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `url` | Yes | string | 外部 URL |

```json
{
  "id": "c3d4e5f678901234",
  "type": "link",
  "x": 1000,
  "y": 0,
  "width": 400,
  "height": 200,
  "url": "https://obsidian.md"
}
```

### Group Nodes

分组是用于组织其他节点的可视容器。子节点应放在分组边界内部。

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `label` | No | string | 分组标签文本 |
| `background` | No | string | 背景图片路径 |
| `backgroundStyle` | No | string | `cover`、`ratio` 或 `repeat` |

```json
{
  "id": "d4e5f6789012345a",
  "type": "group",
  "x": -50,
  "y": -50,
  "width": 1000,
  "height": 600,
  "label": "Project Overview",
  "color": "4"
}
```

## Edges

边通过 `fromNode` 和 `toNode` ID 连接节点。

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `id` | Yes | string | - | 唯一标识符 |
| `fromNode` | Yes | string | - | 源节点 ID |
| `fromSide` | No | string | - | `top`、`right`、`bottom` 或 `left` |
| `fromEnd` | No | string | `none` | `none` 或 `arrow` |
| `toNode` | Yes | string | - | 目标节点 ID |
| `toSide` | No | string | - | `top`、`right`、`bottom` 或 `left` |
| `toEnd` | No | string | `arrow` | `none` 或 `arrow` |
| `color` | No | canvasColor | - | 线条颜色 |
| `label` | No | string | - | 文本标签 |

```json
{
  "id": "0123456789abcdef",
  "fromNode": "6f0ad84f44ce9c17",
  "fromSide": "right",
  "toNode": "a1b2c3d4e5f67890",
  "toSide": "left",
  "toEnd": "arrow",
  "label": "leads to"
}
```

## Colors

`canvasColor` 类型接受十六进制字符串或预设数字：

| Preset | Color |
|--------|-------|
| `"1"` | 红色 |
| `"2"` | 橙色 |
| `"3"` | 黄色 |
| `"4"` | 绿色 |
| `"5"` | 青色 |
| `"6"` | 紫色 |

预设颜色的实际值有意不固定，不同应用会使用自己的品牌色。

## ID Generation

生成 16 字符的小写十六进制字符串（64 位随机值）：

```
"6f0ad84f44ce9c17"
"a3b2c1d0e9f8a7b6"
```

## Layout Guidelines

- 坐标可以为负数（画布是无限延展的）
- `x` 向右增大，`y` 向下增大；位置基于左上角
- 节点之间保留 50-100px 间距；group 内部保留 20-50px 内边距
- 对齐到网格（10 或 20 的倍数）可以让布局更整齐

| Node Type | Suggested Width | Suggested Height |
|-----------|-----------------|------------------|
| Small text | 200-300 | 80-150 |
| Medium text | 300-450 | 150-300 |
| Large text | 400-600 | 300-500 |
| File preview | 300-500 | 200-400 |
| Link preview | 250-400 | 100-200 |

## Validation Checklist

创建或编辑 canvas 文件后，检查：

1. 所有 `id` 在节点和边之间都唯一
2. 每个 `fromNode` 和 `toNode` 都引用了存在的节点 ID
3. 每种节点类型都具备必需字段（文本节点需要 `text`，文件节点需要 `file`，链接节点需要 `url`）
4. `type` 只能是：`text`、`file`、`link`、`group`
5. `fromSide` / `toSide` 只能是：`top`、`right`、`bottom`、`left`
6. `fromEnd` / `toEnd` 只能是：`none`、`arrow`
7. 颜色预设必须在 `"1"` 到 `"6"` 之间，或者是合法十六进制值（如 `"#FF0000"`）
8. JSON 合法且可解析

如果校验失败，优先检查重复 ID、悬空边引用，或格式错误的 JSON 字符串，尤其是文本内容中未转义的换行。

## Complete Examples

完整 canvas 示例，包括思维导图、项目看板、研究画布和流程图，见 [references/EXAMPLES.md](references/EXAMPLES.md)。

## References

- [JSON Canvas Spec 1.0](https://jsoncanvas.org/spec/1.0/)
- [JSON Canvas GitHub](https://github.com/obsidianmd/jsoncanvas)
