---
name: tool-macos-hidpi
description: 当用户需要为 macOS 带鱼屏新增任意分辨率（HiDPI/标准）、验证模式是否真实可用，或在注入失败时切换虚拟屏兜底方案时使用。
---

# macOS 带鱼屏任意分辨率设置

## 概述

本 skill 的核心目标不是“调外接屏”，而是为带鱼屏新增并落地任意分辨率（HiDPI 或标准），再通过闭环验证确认系统真实可用。适用于主屏/扩展屏两种场景，重点解决“写入了但不出现”“出现了但不可切换”的问题。

## 第一性原理背景

从底层看，分辨率是否“可用”由 5 层共同决定：

1. 显示器 EDID（声明支持的时序与能力）
2. 连接链路能力（DP/HDMI、线材、色深、色度采样、带宽）
3. GPU/驱动可输出的时序集合
4. macOS 对模式的过滤与映射策略
5. UI 缩放层（HiDPI 逻辑分辨率）

关键结论：
- `LoDPI`（标准）和 `HiDPI`（逻辑缩放）是两套不同模式，不是同一个开关。
- 覆盖文件/脚本“写入成功”不等于“模式必然出现”；系统仍可能基于链路或策略过滤。
- 任何方案都应以“当前可用模式列表”作为最终真值，而不是以配置文件内容为准。

## 实战结论（2026-03）

- 推荐目标分辨率：`3008×1260`。
- 在部分机型/链路（例如 Mac mini + 外接屏作为主屏）中，即使覆盖文件写入成功，`3008×1260`、`3200×1340` 仍可能被系统过滤，不会出现在可用模式列表。
- 这种情况下优先使用 BetterDisplay 虚拟屏方案，避免反复重启和无效注入。

## 工作流程

### 1. 评估当前显示器配置

```bash
displayplacer list
```

记录：
- 显示器名称和 ID
- 当前分辨率
- 原生分辨率（通常是最高可用分辨率）
- 主屏标记（确认目标是主屏还是扩展屏）

补充验证（推荐）：

```bash
betterdisplaycli get --displayWithMainStatus --displayModeList
```

先确认目标分辨率是否真的在系统可用模式中，再继续。

### 2. 计算目标分辨率

根据用户需求的字体大小，计算 21:9 带鱼屏的中间分辨率：

| 缩放比例 | 计算公式 | 分辨率示例 (3440×1440 原生) |
|---------|---------|---------------------------|
| 75% | 3440×0.75 : 1440×0.75 | 2580×1080 |
| 80% | 3440×0.80 : 1440×0.80 | 2752×1152 |
| 85% | 3440×0.85 : 1440×0.85 | 2924×1224 |

**原则**：保持 21:9 宽高比，确保整数像素值。

### 3. 安装 one-key-hidpi

```bash
curl -fsSL https://raw.githubusercontent.com/xzhih/one-key-hidpi/master/hidpi.sh -o /tmp/hidpi.sh
chmod +x /tmp/hidpi.sh
```

### 4. 运行配置脚本

使用 expect 自动化交互（需要 sudo 密码）：

```bash
expect << 'EXPECT'
spawn sudo /tmp/hidpi.sh
expect "Password:"
send "SUDO_PASSWORD\r"
expect "Choose the display:"
send "DISPLAY_INDEX\r"
expect "Enter your choice \[1~2\]:"
send "1\r"
expect "Enter your choice \[1~6\]:"
send "1\r"
expect "resolution config"
expect -regexp "\\(7\\) Manual input"
send "7\r"
expect "HIDPI"
send "RESOLUTION_LIST\r"
expect eof
EXPECT
```

参数说明：
- `SUDO_PASSWORD`: 用户 sudo 密码
- `DISPLAY_INDEX`: 显示器序号（从 displayplacer list 获取）
- `RESOLUTION_LIST`: 空格分隔的分辨率列表，如 `2560x1070 2700x1130 2880x1206`

### 5. 重启生效

用户必须重启电脑才能看到新的分辨率选项。

### 6. 若 one-key-hidpi 失败，切换到 BetterDisplay 虚拟屏（推荐兜底）

当 `3008×1260` 等分辨率在主屏不可用时，使用虚拟屏落地：

```bash
brew install --cask betterdisplay
open -a /Applications/BetterDisplay.app

# 创建虚拟屏，内置三档分辨率，默认可切到 3008x1260
betterdisplaycli create --type=VirtualScreen \
  --virtualScreenName=VS3008 \
  --useResolutionList=on \
  --resolutionList=2880x1206,3008x1260 \
  --virtualScreenHiDPI=on

betterdisplaycli set --name=VS3008 --connected=on
betterdisplaycli set --name=VS3008 --main=on
betterdisplaycli set --name=VS3008 --mirror=on --specifier=34C1Q
betterdisplaycli set --name=VS3008 --resolution=3008x1260 --hiDPI=on
```

说明：
- 这是“虚拟主屏 + 实体屏镜像”方案。
- 优点：无需重启，成功率高。
- 代价：不是实体屏原生 timing。

## 常用分辨率参考

### 带鱼屏 (3440×1440 原生)

| 目标字体大小 | 分辨率 | HiDPI 效果 |
|------------|--------|-----------|
| 较大 | 2048×858 | 系统预设，字体大 |
| 较大 | 2880×1206 | 自定义 |
| 推荐（默认） | 3008×1260 | 自定义 |
| 最小 | 3440×1440 | 原生，字体小 |

### 4K 显示器 (3840×2160)

| 目标字体大小 | 分辨率 |
|------------|--------|
| 较大 | 1920×1080 HiDPI |
| 中等 | 2560×1440 HiDPI |
| 较小 | 3008×1692 HiDPI |
| 原生 | 3840×2160 |

## 故障排除

### 分辨率未出现

1. 确认已重启电脑
2. 检查系统设置 → 显示器 → 按住 Option 点击"缩放"
3. 运行 `displayplacer list` 查看可用分辨率
4. 使用 `betterdisplaycli get --displayWithMainStatus --displayModeList` 做闭环验证（仅以此列表为准）
5. 若列表无目标分辨率，直接切换 BetterDisplay 虚拟屏方案

### 覆盖文件写入但仍无效

重点检查 plist 内 ID 是否为十进制：
- `DisplayVendorID` 和 `DisplayProductID` 的 `<integer>` 必须是十进制值
- 目录名通常是十六进制（如 `DisplayVendorID-3103`），不要直接把 `3103/3400` 写入 integer

示例（34C1Q）：
- 目录：`DisplayVendorID-3103/DisplayProductID-3400`
- plist integer：`DisplayVendorID=12547`、`DisplayProductID=13312`

### 显示异常

- 黑边：分辨率宽高比与显示器不匹配
- 模糊：未启用 HiDPI（scaling:on）
- 无信号：分辨率超出显示器支持范围

### 恢复默认

重新运行脚本选择 "(2) Disable HIDPI" 或删除配置文件：
```bash
sudo rm -rf /Library/Displays/Contents/Resources/Overrides/DisplayVendorID-*/
```
