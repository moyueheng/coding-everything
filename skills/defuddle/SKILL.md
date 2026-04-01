---
name: defuddle
description: 使用 Defuddle CLI 从网页提取干净的 markdown 内容，去除导航和杂项以节省 token。适用于用户提供 URL 让你阅读或分析在线文档、文章、博客或其他常规网页时，优先替代 WebFetch。
---

# Defuddle

使用 Defuddle CLI 从网页中提取干净、可读的内容。对于常规网页，优先使用它而不是 WebFetch，它会移除导航、广告和杂项内容，从而减少 token 消耗。

如果尚未安装：`npm install -g defuddle`

## 用法

输出 markdown 时始终使用 `--md`：

```bash
defuddle parse <url> --md
```

保存到文件：

```bash
defuddle parse <url> --md -o content.md
```

提取特定元数据：

```bash
defuddle parse <url> -p title
defuddle parse <url> -p description
defuddle parse <url> -p domain
```

## 输出格式

| Flag | Format |
|------|--------|
| `--md` | Markdown（默认选择） |
| `--json` | 同时包含 HTML 和 markdown 的 JSON |
| (none) | HTML |
| `-p <name>` | 指定的元数据属性 |
