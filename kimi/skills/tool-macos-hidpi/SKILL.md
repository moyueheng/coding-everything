---
name: tool-macos-hidpi
description: 为 macOS 外接显示器创建自定义 HiDPI 分辨率。当用户需要调整显示器分辨率、字体大小、HiDPI 缩放时使用。适用于带鱼屏、4K 显示器等需要精细分辨率控制的场景。
---

# macOS HiDPI 分辨率设置

## 概述

macOS 系统只提供有限的分辨率选项，对于带鱼屏或高分辨率显示器，预设档位往往要么字体太大、要么太小。本技能通过注入自定义 HiDPI 分辨率，让用户获得精细的字体大小控制。

## 工作流程

### 1. 评估当前显示器配置

```bash
displayplacer list
```

记录：
- 显示器名称和 ID
- 当前分辨率
- 原生分辨率（通常是最高可用分辨率）

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

## 常用分辨率参考

### 带鱼屏 (3440×1440 原生)

| 目标字体大小 | 分辨率 | HiDPI 效果 |
|------------|--------|-----------|
| 较大 | 2048×858 | 系统预设，字体大 |
| 中等偏大 | 2560×1070 | 自定义，推荐 |
| 中等 | 2700×1130 | 自定义，推荐 |
| 中等偏小 | 2880×1206 | 自定义 |
| 较小 | 3008×1260 | 自定义 |
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

### 显示异常

- 黑边：分辨率宽高比与显示器不匹配
- 模糊：未启用 HiDPI（scaling:on）
- 无信号：分辨率超出显示器支持范围

### 恢复默认

重新运行脚本选择 "(2) Disable HIDPI" 或删除配置文件：
```bash
sudo rm -rf /System/Library/Displays/Contents/Resources/Overrides/DisplayVendorID-*/
```

## 替代方案

如果 one-key-hidpi 不适用，可考虑：

1. **BetterDisplay**: `brew install --cask betterdisplay`
   - 图形界面操作
   - 无需重启
   - 支持虚拟显示器

2. **RDM**: `brew install --cask usr-sse2-rdm`
   - 轻量级
   - 只能启用系统已有分辨率

3. **displayplacer**: `brew install displayplacer`
   - 命令行工具
   - 只能切换已有分辨率
