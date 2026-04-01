---
name: obsidian-cli
description: 使用 Obsidian CLI 与 Obsidian vault 交互，以读取、创建、搜索和管理笔记、任务、properties 等内容。也支持 plugin 和 theme 开发，可执行重载插件、运行 JavaScript、抓取错误、截图和检查 DOM 等命令。适用于用户要求与其 Obsidian vault 交互、管理笔记、搜索 vault 内容、在命令行执行 vault 操作，或开发和调试 Obsidian plugin 与 theme 时。
---

# Obsidian CLI

使用 `obsidian` CLI 与正在运行的 Obsidian 实例交互。要求 Obsidian 已经打开。

## Command reference

运行 `obsidian help` 查看所有可用命令。这始终是最新的。完整文档：https://help.obsidian.md/cli

## Syntax

**Parameters** 通过 `=` 传值。含空格的值需要加引号：

```bash
obsidian create name="My Note" content="Hello world"
```

**Flags** 是不带值的布尔开关：

```bash
obsidian create name="My Note" silent overwrite
```

多行内容使用 `\n` 表示换行，使用 `\t` 表示制表符。

## File targeting

很多命令接受 `file` 或 `path` 来指定目标文件。如果两者都不传，则使用当前活动文件。

- `file=<name>`：按 wikilink 方式解析（只需名称，不需要路径或扩展名）
- `path=<path>`：相对于 vault 根目录的精确路径，例如 `folder/note.md`

## Vault targeting

命令默认作用于最近一次聚焦的 vault。使用 `vault=<name>` 作为第一个参数来指定 vault：

```bash
obsidian vault="My Vault" search query="test"
```

## Common patterns

```bash
obsidian read file="My Note"
obsidian create name="New Note" content="# Hello" template="Template" silent
obsidian append file="My Note" content="New line"
obsidian search query="search term" limit=10
obsidian daily:read
obsidian daily:append content="- [ ] New task"
obsidian property:set name="status" value="done" file="My Note"
obsidian tasks daily todo
obsidian tags sort=count counts
obsidian backlinks file="My Note"
```

任意命令都可以加 `--copy` 将输出复制到剪贴板。使用 `silent` 可阻止文件自动打开。列表类命令使用 `total` 可以直接获取数量。

## Plugin development

### Develop/test cycle

修改 plugin 或 theme 代码后，按以下流程执行：

1. **Reload** 插件以加载变更：
   ```bash
   obsidian plugin:reload id=my-plugin
   ```
2. **Check for errors**：如果出现错误，修复后回到第 1 步：
   ```bash
   obsidian dev:errors
   ```
3. **Verify visually**：通过截图或 DOM 检查确认界面状态：
   ```bash
   obsidian dev:screenshot path=screenshot.png
   obsidian dev:dom selector=".workspace-leaf" text
   ```
4. **Check console output**：查看是否有警告或异常日志：
   ```bash
   obsidian dev:console level=error
   ```

### Additional developer commands

在应用上下文中执行 JavaScript：

```bash
obsidian eval code="app.vault.getFiles().length"
```

检查 CSS 属性值：

```bash
obsidian dev:css selector=".workspace-leaf" prop=background-color
```

切换移动端模拟：

```bash
obsidian dev:mobile on
```

运行 `obsidian help` 可查看其他开发类命令，包括 CDP 和调试器控制。
