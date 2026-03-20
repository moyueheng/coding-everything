---
name: dev-design-system
description: 何时使用设计 token、组件规范、语义颜色、间距与排版层级来统一前端实现，或当你需要在编码前先定义设计系统边界、主题来源和组件状态时使用。
---

# 设计系统模式

在写 UI 代码前，先把视觉规则变成可复用的系统，而不是把颜色、字号、阴影和间距散落在组件里。

## 何时使用

- 需要定义主题、颜色、字号、间距、圆角、阴影
- 需要统一多个页面或组件的视觉语言
- 需要把品牌约束转成前端可消费的 token
- 需要避免组件里到处写硬编码样式

## 核心结构

```text
原始值 Primitive
    ->
语义值 Semantic
    ->
组件值 Component
```

### 1. Primitive

最底层原始值，只表达数值本身：

- `color-blue-600`
- `space-4`
- `radius-lg`
- `font-size-2xl`

### 2. Semantic

表达用途，不表达实现：

- `color-primary`
- `color-surface`
- `color-danger`
- `space-section`
- `text-title`

### 3. Component

只在组件层定义最终消费项：

- `button-bg`
- `card-border`
- `input-ring`

## 实施规则

- 先定义 token，再写组件
- 语义层优先，不要让组件直接依赖 primitive
- 同一含义只保留一个 token 名，不要并存多个近义名称
- 组件状态必须明确：`default / hover / active / disabled / focus`
- 主题切换只改 token 映射，不改组件实现

## 快速检查

- 颜色是否仍有十六进制硬编码？
- 组件是否直接依赖 `blue-500` 这类实现细节？
- 相同间距/字号是否反复手写？
- 状态是否只定义了默认态，没有 hover/focus？

## 推荐输出

至少先写出这几类表：

- 颜色 token 表
- 排版层级表
- 间距 token 表
- 组件状态表

## 何时不要使用

- 单个一次性页面，且不会复用
- 纯文档演示，不会落到真实实现

## 关联 skill

- 需要具体 UI 实现时，配合 `dev-ui-styling`
- 需要通用 React / Next.js 模式时，配合 `dev-frontend-patterns`
