---
name: agent-browser
description: 面向 AI agent 的浏览器自动化 CLI。当用户需要与网站交互时使用，包括页面导航、填写表单、点击按钮、截图、提取数据、测试 Web 应用，或执行任何浏览器自动化任务。触发场景包括“打开网站”“填写表单”“点击按钮”“截图”“抓取页面数据”“测试这个 Web 应用”“登录某个网站”“自动化浏览器操作”，以及任何需要通过程序控制网页交互的任务。
allowed-tools: Bash(npx agent-browser:*), Bash(agent-browser:*)
---

# 使用 agent-browser 做浏览器自动化

这个 CLI 通过 CDP 直接使用 Chrome/Chromium。可通过 `npm i -g agent-browser`、`brew install agent-browser` 或 `cargo install agent-browser` 安装。运行 `agent-browser install` 下载 Chrome。运行 `agent-browser upgrade` 更新到最新版本。

## 核心工作流

所有浏览器自动化都遵循这个模式：

1. **导航**：`agent-browser open <url>`
2. **抓取快照**：`agent-browser snapshot -i`（获取 `@e1`、`@e2` 这类元素引用）
3. **交互**：使用这些引用执行点击、填写、选择等操作
4. **重新抓取快照**：导航后或 DOM 变化后，获取新的引用

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# 输出：@e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Submit"

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i  # 检查结果
```

## 命令串联

命令可以在一次 shell 调用中用 `&&` 串起来执行。浏览器会通过后台 daemon 在多条命令之间保持存活，因此串联执行既安全，又比逐条单独调用更高效。

```bash
# 一次性串联 open + wait + snapshot
agent-browser open https://example.com && agent-browser wait --load networkidle && agent-browser snapshot -i

# 串联多个交互动作
agent-browser fill @e1 "user@example.com" && agent-browser fill @e2 "password123" && agent-browser click @e3

# 导航并截图
agent-browser open https://example.com && agent-browser wait --load networkidle && agent-browser screenshot page.png
```

**何时适合串联：** 当你不需要先读取某条中间命令的输出再继续时，使用 `&&`（例如 open + wait + screenshot）。如果你需要先解析输出再继续，就分开执行（例如先 snapshot 找到 refs，再基于 refs 交互）。

## 处理认证

当自动化的网站需要登录时，选择适合当前场景的方案：

**方案 1：从用户浏览器导入认证状态（一次性任务最快）**

```bash
# 连接到用户正在运行的 Chrome（用户已经登录）
agent-browser --auto-connect state save ./auth.json
# 使用该认证状态
agent-browser --state ./auth.json open https://app.example.com/dashboard
```

状态文件以明文保存会话令牌，请将其加入 `.gitignore`，并在不再需要时删除。设置 `AGENT_BROWSER_ENCRYPTION_KEY` 可实现静态加密。

**方案 2：持久化 profile（重复任务最简单）**

```bash
# 首次运行：手动或自动化登录
agent-browser --profile ~/.myapp open https://app.example.com/login
# ... 填写凭据并提交 ...

# 以后每次运行：已保持登录态
agent-browser --profile ~/.myapp open https://app.example.com/dashboard
```

**方案 3：会话名（自动保存/恢复 cookies + localStorage）**

```bash
agent-browser --session-name myapp open https://app.example.com/login
# ... 登录流程 ...
agent-browser close  # 状态会自动保存

# 下次运行：状态自动恢复
agent-browser --session-name myapp open https://app.example.com/dashboard
```

**方案 4：Auth Vault（凭据加密存储，按名称登录）**

```bash
echo "$PASSWORD" | agent-browser auth save myapp --url https://app.example.com/login --username user --password-stdin
agent-browser auth login myapp
```

`auth login` 会先导航并等待登录表单选择器出现，再执行填写和点击；在延迟加载的 SPA 登录页上，这种方式更可靠。

**方案 5：状态文件（手动保存/加载）**

```bash
# 登录后：
agent-browser state save ./auth.json
# 后续会话中：
agent-browser state load ./auth.json
agent-browser open https://app.example.com/dashboard
```

有关 OAuth、2FA、基于 cookie 的认证和令牌刷新模式，见 [references/authentication.md](references/authentication.md)。

## 常用命令

```bash
# 导航
agent-browser open <url>              # 导航（别名：goto, navigate）
agent-browser close                   # 关闭浏览器
agent-browser close --all             # 关闭所有活动会话

# 快照
agent-browser snapshot -i             # 输出带 refs 的可交互元素（推荐）
agent-browser snapshot -s "#selector" # 仅对指定 CSS 选择器范围抓取快照

# 交互（使用 snapshot 得到的 @refs）
agent-browser click @e1               # 点击元素
agent-browser click @e1 --new-tab     # 点击并在新标签页打开
agent-browser fill @e2 "text"         # 清空并输入文本
agent-browser type @e2 "text"         # 不清空直接输入
agent-browser select @e1 "option"     # 选择下拉项
agent-browser check @e1               # 勾选复选框
agent-browser press Enter             # 按键
agent-browser keyboard type "text"    # 在当前焦点处输入（无选择器）
agent-browser keyboard inserttext "text"  # 不触发键盘事件直接插入
agent-browser scroll down 500         # 滚动页面
agent-browser scroll down 500 --selector "div.content"  # 在指定容器内滚动

# 获取信息
agent-browser get text @e1            # 获取元素文本
agent-browser get url                 # 获取当前 URL
agent-browser get title               # 获取页面标题
agent-browser get cdp-url             # 获取 CDP WebSocket URL

# 等待
agent-browser wait @e1                # 等待元素出现
agent-browser wait --load networkidle # 等待网络空闲
agent-browser wait --url "**/page"    # 等待 URL 模式匹配
agent-browser wait 2000               # 等待指定毫秒数
agent-browser wait --text "Welcome"    # 等待文本出现（子串匹配）
agent-browser wait --fn "!document.body.innerText.includes('Loading...')"  # 等待文本消失
agent-browser wait "#spinner" --state hidden  # 等待元素消失

# 下载
agent-browser download @e1 ./file.pdf          # 点击元素触发下载
agent-browser wait --download ./output.zip     # 等待任意下载完成
agent-browser --download-path ./downloads open <url>  # 设置默认下载目录

# 网络
agent-browser network requests                 # 查看已跟踪请求
agent-browser network requests --type xhr,fetch  # 按资源类型过滤
agent-browser network requests --method POST   # 按 HTTP 方法过滤
agent-browser network requests --status 2xx    # 按状态码过滤（200、2xx、400-499）
agent-browser network request <requestId>      # 查看完整请求/响应详情
agent-browser network route "**/api/*" --abort  # 拦截并终止匹配请求
agent-browser network har start                # 开始录制 HAR
agent-browser network har stop ./capture.har   # 停止并保存 HAR 文件

# 视口与设备模拟
agent-browser set viewport 1920 1080          # 设置视口大小（默认：1280x720）
agent-browser set viewport 1920 1080 2        # 2x retina（CSS 尺寸不变，截图分辨率更高）
agent-browser set device "iPhone 14"          # 模拟设备（视口 + user agent）

# 捕获
agent-browser screenshot              # 截图到临时目录
agent-browser screenshot --full       # 整页截图
agent-browser screenshot --annotate   # 给可交互元素加编号标注的截图
agent-browser screenshot --screenshot-dir ./shots  # 保存到自定义目录
agent-browser screenshot --screenshot-format jpeg --screenshot-quality 80
agent-browser pdf output.pdf          # 导出为 PDF

# 实时预览 / 流式输出
agent-browser stream enable           # 在自动选择的端口启动运行时 WebSocket 流
agent-browser stream enable --port 9223  # 绑定指定 localhost 端口
agent-browser stream status           # 查看启用状态、端口、连接和 screencast 状态
agent-browser stream disable          # 停止运行时流并移除 .stream 元数据文件

# 剪贴板
agent-browser clipboard read                      # 读取剪贴板文本
agent-browser clipboard write "Hello, World!"     # 写入文本到剪贴板
agent-browser clipboard copy                      # 复制当前选区
agent-browser clipboard paste                     # 粘贴剪贴板内容

# 对话框（alert、confirm、prompt）
agent-browser dialog accept              # 接受对话框
agent-browser dialog accept "my input"   # 接受 prompt 并输入文本
agent-browser dialog dismiss             # 取消/关闭对话框
agent-browser dialog status              # 检查当前是否有对话框打开

# Diff（比较页面状态）
agent-browser diff snapshot                          # 比较当前状态与最近一次快照
agent-browser diff snapshot --baseline before.txt    # 与已保存文件比较
agent-browser diff screenshot --baseline before.png  # 像素级视觉比较
agent-browser diff url <url1> <url2>                 # 比较两个页面
agent-browser diff url <url1> <url2> --wait-until networkidle  # 自定义等待策略
agent-browser diff url <url1> <url2> --selector "#main"  # 限定到某个元素范围
```

## 流式输出

每个会话都会自动在操作系统分配的端口上启动一个 WebSocket 流服务。使用 `agent-browser stream status` 查看绑定端口和连接状态。使用 `stream disable` 关闭它，使用 `stream enable --port <port>` 在指定端口重新启用。

## 批量执行

把“字符串数组的 JSON 数组”通过管道传给 `batch`，即可在一次调用中执行多条命令。这样可以避免多步骤工作流中每条命令都重复启动进程的开销。

```bash
echo '[
  ["open", "https://example.com"],
  ["snapshot", "-i"],
  ["click", "@e1"],
  ["screenshot", "result.png"]
]' | agent-browser batch --json

# 遇到第一个错误就停止
agent-browser batch --bail < commands.json
```

当你已经知道一组命令的顺序，且不依赖中间输出时，用 `batch`。如果中间步骤需要先解析输出（例如先 snapshot 找 refs，再交互），则使用分步命令或 `&&` 串联。

## 常见模式

### 提交表单

```bash
agent-browser open https://example.com/signup
agent-browser snapshot -i
agent-browser fill @e1 "Jane Doe"
agent-browser fill @e2 "jane@example.com"
agent-browser select @e3 "California"
agent-browser check @e4
agent-browser click @e5
agent-browser wait --load networkidle
```

### 使用 Auth Vault 认证（推荐）

```bash
# 保存一次凭据（使用 AGENT_BROWSER_ENCRYPTION_KEY 加密）
# 推荐：通过 stdin 传入密码，避免暴露在 shell history 中
echo "pass" | agent-browser auth save github --url https://github.com/login --username user --password-stdin

# 使用已保存的配置登录（LLM 不会看到密码）
agent-browser auth login github

# 列出 / 查看 / 删除配置
agent-browser auth list
agent-browser auth show github
agent-browser auth delete github
```

`auth login` 会等待用户名、密码、提交按钮对应的选择器出现后再交互，超时时间与默认 action timeout 绑定。

### 使用状态持久化认证

```bash
# 登录一次并保存状态
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "$USERNAME"
agent-browser fill @e2 "$PASSWORD"
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser state save auth.json

# 后续会话复用
agent-browser state load auth.json
agent-browser open https://app.example.com/dashboard
```

### 会话持久化

```bash
# 浏览器重启后自动保存 / 恢复 cookies 和 localStorage
agent-browser --session-name myapp open https://app.example.com/login
# ... 登录流程 ...
agent-browser close  # 状态会自动保存到 ~/.agent-browser/sessions/

# 下次运行时自动加载状态
agent-browser --session-name myapp open https://app.example.com/dashboard

# 对静态存储状态进行加密
export AGENT_BROWSER_ENCRYPTION_KEY=$(openssl rand -hex 32)
agent-browser --session-name secure open https://app.example.com

# 管理已保存的状态
agent-browser state list
agent-browser state show myapp-default.json
agent-browser state clear myapp
agent-browser state clean --older-than 7
```

### 处理 Iframe

Iframe 内容会自动内联到快照中。iframe 内的 refs 自带 frame 上下文，因此可以直接对它们交互。

```bash
agent-browser open https://example.com/checkout
agent-browser snapshot -i
# @e1 [heading] "Checkout"
# @e2 [Iframe] "payment-frame"
#   @e3 [input] "Card number"
#   @e4 [input] "Expiry"
#   @e5 [button] "Pay"

# 直接交互，无需手动切换 frame
agent-browser fill @e3 "4111111111111111"
agent-browser fill @e4 "12/28"
agent-browser click @e5

# 只针对某个 iframe 范围抓取快照：
agent-browser frame @e2
agent-browser snapshot -i         # 仅 iframe 内容
agent-browser frame main          # 返回主 frame
```

### 数据提取

```bash
agent-browser open https://example.com/products
agent-browser snapshot -i
agent-browser get text @e5           # 获取指定元素文本
agent-browser get text body > page.txt  # 获取整页文本

# 输出 JSON 以便解析
agent-browser snapshot -i --json
agent-browser get text @e1 --json
```

### 并行会话

```bash
agent-browser --session site1 open https://site-a.com
agent-browser --session site2 open https://site-b.com

agent-browser --session site1 snapshot -i
agent-browser --session site2 snapshot -i

agent-browser session list
```

### 连接已有的 Chrome

```bash
# 自动发现已开启 remote debugging 的 Chrome
agent-browser --auto-connect open https://example.com
agent-browser --auto-connect snapshot

# 或显式指定 CDP 端口
agent-browser --cdp 9222 snapshot
```

自动连接会通过 `DevToolsActivePort`、常见调试端口（9222、9229）发现 Chrome；如果基于 HTTP 的 CDP 发现失败，则回退到直接 WebSocket 连接。

### 配色方案（深色模式）

```bash
# 通过 flag 持久启用深色模式（作用于所有页面和新标签页）
agent-browser --color-scheme dark open https://example.com

# 或通过环境变量
AGENT_BROWSER_COLOR_SCHEME=dark agent-browser open https://example.com

# 或在会话中设置（后续命令持续生效）
agent-browser set media dark
```

### 视口与响应式测试

```bash
# 设置自定义视口尺寸（默认 1280x720）
agent-browser set viewport 1920 1080
agent-browser screenshot desktop.png

# 测试移动端宽度布局
agent-browser set viewport 375 812
agent-browser screenshot mobile.png

# Retina/HiDPI：CSS 布局不变，但像素密度为 2x
# 截图仍按逻辑视口尺寸输出，但内容以更高 DPI 渲染
agent-browser set viewport 1920 1080 2
agent-browser screenshot retina.png

# 设备模拟（一次性设置 viewport + user agent）
agent-browser set device "iPhone 14"
agent-browser screenshot device.png
```

`scale` 参数（第 3 个参数）会设置 `window.devicePixelRatio`，但不会改变 CSS 布局。测试 retina 渲染或生成更高分辨率截图时使用它。

### 可视化浏览器（调试）

```bash
agent-browser --headed open https://example.com
agent-browser highlight @e1          # 高亮元素
agent-browser inspect                # 为当前活动页面打开 Chrome DevTools
agent-browser record start demo.webm # 录制会话
agent-browser profiler start         # 启动 Chrome DevTools profiling
agent-browser profiler stop trace.json # 停止并保存 profile（路径可选）
```

使用 `AGENT_BROWSER_HEADED=1` 可通过环境变量启用 headed 模式。浏览器扩展在 headed 和 headless 模式下都可用。

### 本地文件（PDF、HTML）

```bash
# 使用 file:// URL 打开本地文件
agent-browser --allow-file-access open file:///path/to/document.pdf
agent-browser --allow-file-access open file:///path/to/page.html
agent-browser screenshot output.png
```

### iOS 模拟器（Mobile Safari）

```bash
# 列出可用的 iOS 模拟器
agent-browser device list

# 在指定设备上启动 Safari
agent-browser -p ios --device "iPhone 16 Pro" open https://example.com

# 与桌面端相同的流程：snapshot、交互、重新 snapshot
agent-browser -p ios snapshot -i
agent-browser -p ios tap @e1          # 点按（click 的别名）
agent-browser -p ios fill @e2 "text"
agent-browser -p ios swipe up         # 移动端专用手势

# 截图
agent-browser -p ios screenshot mobile.png

# 关闭会话（同时关闭模拟器）
agent-browser -p ios close
```

**要求：** macOS + Xcode + Appium（`npm install -g appium && appium driver install xcuitest`）

**真机：** 若已预配置，也支持物理 iOS 设备。使用 `--device "<UDID>"`，其中 UDID 可通过 `xcrun xctrace list devices` 获取。

## 安全性

所有安全特性均为 opt-in。默认情况下，agent-browser 不会限制导航、操作或输出。

### 内容边界（推荐 AI agent 使用）

启用 `--content-boundaries` 后，页面来源的输出会被包裹在标记中，帮助 LLM 区分工具输出与不可信页面内容：

```bash
export AGENT_BROWSER_CONTENT_BOUNDARIES=1
agent-browser snapshot
# 输出：
# --- AGENT_BROWSER_PAGE_CONTENT nonce=<hex> origin=https://example.com ---
# [accessibility tree]
# --- END_AGENT_BROWSER_PAGE_CONTENT nonce=<hex> ---
```

### 域名白名单

将导航限制在可信域名内。像 `*.example.com` 这样的通配符也会匹配裸域名 `example.com`。对子资源请求、WebSocket 和 EventSource 到非允许域名的连接也会被阻止。记得把目标页面依赖的 CDN 域名也加入进去：

```bash
export AGENT_BROWSER_ALLOWED_DOMAINS="example.com,*.example.com"
agent-browser open https://example.com        # 允许
agent-browser open https://malicious.com       # 阻止
```

### 操作策略

通过策略文件限制破坏性操作：

```bash
export AGENT_BROWSER_ACTION_POLICY=./policy.json
```

示例 `policy.json`：

```json
{ "default": "deny", "allow": ["navigate", "snapshot", "click", "scroll", "wait", "get"] }
```

Auth Vault 操作（如 `auth login`）会绕过 action policy，但仍受域名白名单约束。

### 输出限制

防止大页面内容淹没上下文：

```bash
export AGENT_BROWSER_MAX_OUTPUT=50000
```

## Diff（验证变更）

执行操作后，使用 `diff snapshot` 验证其效果是否符合预期。它会把当前 accessibility tree 与当前会话中最近一次快照进行比较。

```bash
# 典型流程：snapshot -> action -> diff
agent-browser snapshot -i          # 生成基线快照
agent-browser click @e2            # 执行操作
agent-browser diff snapshot        # 查看发生了什么变化（自动对比最近一次 snapshot）
```

用于视觉回归测试或监控时：

```bash
# 先保存一张基线截图，稍后再比较
agent-browser screenshot baseline.png
# ... 时间流逝或页面发生变化 ...
agent-browser diff screenshot --baseline baseline.png

# 比较 staging 和 production
agent-browser diff url https://staging.example.com https://prod.example.com --screenshot
```

`diff snapshot` 输出中，`+` 表示新增，`-` 表示移除，类似 git diff。`diff screenshot` 会生成一张差异图，把变化像素标成红色，并附带不匹配百分比。

## 超时与慢页面

默认超时时间是 25 秒。可通过 `AGENT_BROWSER_DEFAULT_TIMEOUT` 环境变量覆盖（单位毫秒）。对于慢网站或超大页面，不要只依赖默认超时，而应显式等待：

```bash
# 等待网络活动稳定（慢页面最常用）
agent-browser wait --load networkidle

# 等待特定元素出现
agent-browser wait "#content"
agent-browser wait @e1

# 等待指定 URL 模式（适合重定向后）
agent-browser wait --url "**/dashboard"

# 等待某个 JavaScript 条件成立
agent-browser wait --fn "document.readyState === 'complete'"

# 最后手段：固定等待一段时间（毫秒）
agent-browser wait 5000
```

面对持续较慢的网站时，在 `open` 之后使用 `wait --load networkidle`，确保页面完全加载后再抓取快照。如果某个元素渲染很慢，则直接用 `wait <selector>` 或 `wait @ref` 等它出现。

## JavaScript 对话框（alert / confirm / prompt）

当页面打开 JavaScript 对话框（`alert()`、`confirm()` 或 `prompt()`）时，所有其他浏览器命令（snapshot、screenshot、click 等）都会被阻塞，直到该对话框被处理。如果命令开始莫名其妙超时，先检查是否有挂起的对话框：

```bash
# 检查是否有对话框在阻塞
agent-browser dialog status

# 接受对话框（关闭 alert / 点击 OK）
agent-browser dialog accept

# 接受 prompt 并输入文本
agent-browser dialog accept "my input"

# 取消对话框（点击 Cancel）
agent-browser dialog dismiss
```

当存在挂起对话框时，所有命令响应里都会包含 `warning` 字段，标明对话框类型和消息内容。在 `--json` 模式下，这会以响应对象中的 `"warning"` 键出现。

## 会话管理与清理

当同时运行多个 agent 或自动化任务时，始终使用命名会话，避免互相冲突：

```bash
# 每个 agent 使用自己的隔离会话
agent-browser --session agent1 open site-a.com
agent-browser --session agent2 open site-b.com

# 查看活动会话
agent-browser session list
```

完成后一定要关闭浏览器会话，避免泄漏后台进程：

```bash
agent-browser close                    # 关闭默认会话
agent-browser --session agent1 close   # 关闭指定会话
agent-browser close --all              # 关闭所有活动会话
```

如果之前的会话没有正确关闭，daemon 可能仍在运行。可用 `agent-browser close` 清理，或用 `agent-browser close --all` 一次性关闭所有会话。

如果希望在一段时间无活动后自动关闭 daemon（适合临时环境或 CI）：

```bash
AGENT_BROWSER_IDLE_TIMEOUT_MS=60000 agent-browser open example.com
```

## Ref 生命周期（重要）

Refs（`@e1`、`@e2` 等）会在页面发生变化后失效。遇到以下情况后必须重新抓取快照：

- 点击会导致导航的链接或按钮
- 提交表单
- 动态内容加载（如下拉框、模态框）

```bash
agent-browser click @e5              # 导航到新页面
agent-browser snapshot -i            # 必须重新 snapshot
agent-browser click @e1              # 使用新的 refs
```

## 标注截图（视觉模式）

使用 `--annotate` 可生成一张带编号标注的截图，编号会覆盖到可交互元素上。每个标签 `[N]` 对应 ref `@eN`。同时这也会缓存 refs，因此你可以不额外执行 snapshot，直接开始交互。

```bash
agent-browser screenshot --annotate
# 输出会包含图片路径和图例：
#   [1] @e1 button "Submit"
#   [2] @e2 link "Home"
#   [3] @e3 textbox "Email"
agent-browser click @e2              # 使用标注截图中的 ref 点击
```

以下情况适合使用标注截图：

- 页面里有未标注的图标按钮或纯视觉元素
- 需要验证视觉布局或样式
- 存在 Canvas 或图表元素（文本快照看不到）
- 需要依据元素空间位置做判断

## 语义定位器（Refs 的替代方案）

当 refs 不可用或不可靠时，使用语义定位器：

```bash
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
agent-browser find role button click --name "Submit"
agent-browser find placeholder "Search" type "query"
agent-browser find testid "submit-btn" click
```

## JavaScript 求值（eval）

使用 `eval` 在浏览器上下文里执行 JavaScript。**Shell 的引用规则会破坏复杂表达式**，请优先使用 `--stdin` 或 `-b` 避免出错。

```bash
# 简单表达式可以使用常规引用
agent-browser eval 'document.title'
agent-browser eval 'document.querySelectorAll("img").length'

# 复杂 JS：使用 --stdin + heredoc（推荐）
agent-browser eval --stdin <<'EVALEOF'
JSON.stringify(
  Array.from(document.querySelectorAll("img"))
    .filter(i => !i.alt)
    .map(i => ({ src: i.src.split("/").pop(), width: i.width }))
)
EVALEOF

# 另一种方式：base64 编码（彻底规避 shell 转义问题）
agent-browser eval -b "$(echo -n 'Array.from(document.querySelectorAll("a")).map(a => a.href)' | base64)"
```

**为什么这很重要：** Shell 在处理命令时，内部双引号、`!`（history expansion）、反引号、`$()` 等都可能在 JavaScript 传给 agent-browser 之前就把它破坏掉。`--stdin` 和 `-b` 会彻底绕过 shell 解释。

**经验法则：**

- 单行、无嵌套引号：使用普通 `eval 'expression'`，单引号即可
- 有嵌套引号、箭头函数、模板字符串或多行：使用 `eval --stdin <<'EVALEOF'`
- 程序生成的脚本：使用 `eval -b` 配合 base64

## 配置文件

在项目根目录创建 `agent-browser.json` 以保存持久配置：

```json
{
  "headed": true,
  "proxy": "http://localhost:8080",
  "profile": "./browser-data"
}
```

优先级（从低到高）：`~/.agent-browser/config.json` < `./agent-browser.json` < 环境变量 < CLI flags。使用 `--config <path>` 或 `AGENT_BROWSER_CONFIG` 环境变量可指定自定义配置文件（缺失或无效时会直接报错退出）。所有 CLI 选项都映射到 camelCase 键（例如 `--executable-path` -> `"executablePath"`）。布尔 flag 接受 `true` / `false`（例如 `--headed false` 可覆盖配置）。用户配置和项目配置中的 extensions 会合并，而不是替换。

## 深入文档

| 参考资料 | 适用场景 |
| -------------------------------------------------------------------- | --------------------------------------------------------- |
| [references/commands.md](references/commands.md)                     | 所有命令及其选项的完整参考 |
| [references/snapshot-refs.md](references/snapshot-refs.md)           | Ref 生命周期、失效规则、故障排查 |
| [references/session-management.md](references/session-management.md) | 并行会话、状态持久化、并发抓取 |
| [references/authentication.md](references/authentication.md)         | 登录流程、OAuth、2FA 处理、状态复用 |
| [references/video-recording.md](references/video-recording.md)       | 用于调试和文档的录制工作流 |
| [references/profiling.md](references/profiling.md)                   | Chrome DevTools profiling 性能分析 |
| [references/proxy-support.md](references/proxy-support.md)           | 代理配置、地理位置测试、轮换代理 |

## 浏览器引擎选择

使用 `--engine` 选择本地浏览器引擎。默认值为 `chrome`。

```bash
# 使用 Lightpanda（快速无头浏览器，需要单独安装）
agent-browser --engine lightpanda open example.com

# 通过环境变量指定
export AGENT_BROWSER_ENGINE=lightpanda
agent-browser open example.com

# 配合自定义二进制路径
agent-browser --engine lightpanda --executable-path /path/to/lightpanda open example.com
```

支持的引擎：
- `chrome`（默认）-- 通过 CDP 使用 Chrome/Chromium
- `lightpanda` -- 通过 CDP 使用 Lightpanda 无头浏览器（速度快 10 倍、内存占用少 10 倍）

Lightpanda 不支持 `--extension`、`--profile`、`--state` 或 `--allow-file-access`。安装方式见 https://lightpanda.io/docs/open-source/installation 。

## 可观测性 Dashboard

Dashboard 是一个独立的后台服务，用于展示所有会话的实时浏览器视口、命令活动和控制台输出。

```bash
# 先安装 dashboard
agent-browser dashboard install

# 启动 dashboard 服务（后台运行，端口 4848）
agent-browser dashboard start

# 所有会话都会自动出现在 dashboard 中
agent-browser open example.com

# 停止 dashboard
agent-browser dashboard stop
```

Dashboard 独立于浏览器会话运行，默认监听 4848 端口（可通过 `--port` 配置）。所有会话都会自动把流输出发送到 dashboard。

## 开箱即用模板

| 模板 | 说明 |
| ------------------------------------------------------------------------ | ----------------------------------- |
| [templates/form-automation.sh](templates/form-automation.sh)             | 带校验的表单填写 |
| [templates/authenticated-session.sh](templates/authenticated-session.sh) | 登录一次，后续复用状态 |
| [templates/capture-workflow.sh](templates/capture-workflow.sh)           | 带截图的内容提取流程 |

```bash
./templates/form-automation.sh https://example.com/form
./templates/authenticated-session.sh https://app.example.com/login
./templates/capture-workflow.sh https://example.com ./output
```
