---
name: dev-e2e-testing
description: 何时使用 Playwright Python 构建端到端测试套件，需要 Page Object Model、不稳定测试处理或浏览器测试配置时
---

# E2E 测试模式 (Playwright Python)

使用 Playwright Python 构建稳定、可维护的浏览器端到端测试套件。

## 何时使用

- 需要为 Web 应用编写浏览器自动化测试
- 测试出现不稳定（flaky）现象
- 配置多浏览器/多设备测试矩阵
- 需要 Python 生态的 E2E 测试方案

## 安装

```bash
pip install pytest-playwright
playwright install
```

## 目录结构

```
tests/
├── e2e/
│   ├── auth/           # 认证相关测试
│   │   ├── test_login.py
│   │   └── test_register.py
│   ├── features/       # 功能测试
│   │   ├── test_search.py
│   │   └── test_checkout.py
│   └── conftest.py     # pytest 配置和 fixtures
├── pages/              # Page Object Model
│   ├── __init__.py
│   ├── base_page.py
│   └── items_page.py
└── pytest.ini          # pytest 配置
```

## Page Object Model (POM)

### Base Page

```python
# pages/base_page.py
from playwright.sync_api import Page, Locator, expect

class BasePage:
    def __init__(self, page: Page):
        self.page = page
    
    def goto(self, url: str):
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
    
    def wait_for_response(self, url_pattern: str):
        return self.page.wait_for_response(lambda resp: url_pattern in resp.url)
```

### 具体 Page

```python
# pages/items_page.py
from playwright.sync_api import Page, Locator, expect
from .base_page import BasePage

class ItemsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input = page.locator('[data-testid="search-input"]')
        self.item_cards = page.locator('[data-testid="item-card"]')
        self.create_button = page.locator('[data-testid="create-btn"]')
    
    def goto(self):
        super().goto("/items")
    
    def search(self, query: str):
        self.search_input.fill(query)
        self.wait_for_response("/api/search")
        self.page.wait_for_load_state("networkidle")
    
    def get_item_count(self) -> int:
        return self.item_cards.count()
    
    def expect_item_contains_text(self, index: int, text: str):
        expect(self.item_cards.nth(index)).to_contain_text(text)
```

## pytest 配置

```ini
# pytest.ini
[pytest]
testpaths = tests/e2e
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --headed --tracing=retain-on-failure
```

```python
# conftest.py
import pytest
from playwright.sync_api import Page
from pages.items_page import ItemsPage

@pytest.fixture
def items_page(page: Page) -> ItemsPage:
    """提供已初始化的 ItemsPage"""
    return ItemsPage(page)

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """全局浏览器上下文配置"""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "record_video_dir": "./artifacts/videos/",
    }
```

## 测试结构

```python
# tests/e2e/features/test_search.py
import pytest
from playwright.sync_api import Page, expect
from pages.items_page import ItemsPage

class TestItemSearch:
    
    def test_search_by_keyword(self, page: Page, items_page: ItemsPage):
        items_page.goto()
        items_page.search("test")
        
        count = items_page.get_item_count()
        assert count > 0
        
        items_page.expect_item_contains_text(0, "test")
        page.screenshot(path="artifacts/search-results.png")
    
    def test_handle_no_results(self, page: Page, items_page: ItemsPage):
        items_page.goto()
        items_page.search("xyznonexistent123")
        
        no_results = page.locator('[data-testid="no-results"]')
        expect(no_results).to_be_visible()
        assert items_page.get_item_count() == 0
```

## Playwright 配置

```python
# conftest.py 高级配置
import pytest
from playwright.sync_api import sync_playwright

def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default="http://localhost:3000",
        help="Base URL for tests",
    )

@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base-url")

@pytest.fixture(scope="session")
def browser_type_launch_args():
    """浏览器启动参数"""
    return {
        "headless": True,
        "slow_mo": 50,
    }
```

## 不稳定测试处理

### 识别不稳定

```bash
# 重复运行 10 次检测不稳定
pytest tests/e2e/features/test_search.py --count=10

# 带重试运行
pytest tests/e2e/features/test_search.py --reruns=3 --reruns-delay=1
```

### 跳过不稳定测试

```python
import pytest
import os

@pytest.mark.skip(reason="Flaky - Issue #123")
def test_flaky_complex_search(items_page):
    pass

@pytest.mark.skipif(os.getenv("CI") == "true", reason="Flaky in CI - Issue #123")
def test_conditional_skip(items_page):
    pass
```

### 常见原因与修复

| 问题 | 错误做法 | 正确做法 |
|------|----------|----------|
| 竞态条件 | `page.click('[data-testid="btn"]')` | `page.locator('[data-testid="btn"]').click()` |
| 网络时序 | `page.wait_for_timeout(5000)` | `page.wait_for_response(lambda resp: "/api/data" in resp.url)` |
| 动画时序 | 直接点击 | `locator.wait_for(state="visible"); page.wait_for_load_state("networkidle")` |

## 多浏览器测试

```bash
# 测试特定浏览器
pytest --browser=chromium
pytest --browser=firefox
pytest --browser=webkit

# 同时测试多个浏览器
pytest --browser=chromium --browser=firefox

# 移动设备
pytest --device="Pixel 5"
pytest --device="iPhone 13"
```

```python
# conftest.py 中配置多浏览器
@pytest.fixture(params=["chromium", "firefox", "webkit"])
def browser_type(request):
    return request.param
```

## Artifacts 管理

```python
# conftest.py 自动截图和视频
import pytest
from playwright.sync_api import Page

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            page.screenshot(path=f"artifacts/failed-{item.name}.png")
```

## Web3 / 钱包测试

```python
# tests/e2e/web3/test_wallet.py
import pytest
from playwright.sync_api import Page, expect

def test_wallet_connection(page: Page, context):
    # Mock wallet provider
    context.add_init_script("""
        window.ethereum = {
            isMetaMask: true,
            request: async ({ method }) => {
                if (method === 'eth_requestAccounts')
                    return ['0x1234567890123456789012345678901234567890'];
                if (method === 'eth_chainId') return '0x1';
            }
        };
    """)
    
    page.goto("/")
    page.locator('[data-testid="connect-wallet"]').click()
    expect(page.locator('[data-testid="wallet-address"]')).to_contain_text("0x1234")
```

## 关键流程测试（金融/交易）

```python
import pytest
import os
from playwright.sync_api import Page, expect

class TestTradeExecution:
    
    @pytest.mark.skipif(
        os.getenv("NODE_ENV") == "production",
        reason="Skip on production - involves real money"
    )
    def test_trade_execution(self, page: Page):
        page.goto("/markets/test-market")
        page.locator('[data-testid="position-yes"]').click()
        page.locator('[data-testid="trade-amount"]').fill("1.0")
        
        # 确认预览
        preview = page.locator('[data-testid="trade-preview"]')
        expect(preview).to_contain_text("1.0")
        
        # 提交并等待确认
        page.locator('[data-testid="confirm-trade"]').click()
        page.wait_for_response(
            lambda resp: "/api/trade" in resp.url and resp.status == 200,
            timeout=30000
        )
        
        expect(page.locator('[data-testid="trade-success"]')).to_be_visible()
```

## 实用 Fixtures

```python
# conftest.py 常用 fixtures
import pytest
from playwright.sync_api import BrowserContext, Page

@pytest.fixture
def authenticated_context(browser) -> BrowserContext:
    """提供已登录的浏览器上下文"""
    context = browser.new_context()
    page = context.new_page()
    
    # 执行登录
    page.goto("/login")
    page.fill('[name="username"]', "testuser")
    page.fill('[name="password"]', "testpass")
    page.click('[type="submit"]')
    page.wait_for_url("/dashboard")
    
    # 保存存储状态
    context.storage_state(path="auth.json")
    page.close()
    
    # 使用存储状态创建新上下文
    return browser.new_context(storage_state="auth.json")

@pytest.fixture
def auth_page(authenticated_context) -> Page:
    """提供已登录的页面"""
    return authenticated_context.new_page()
```

## 命令行运行

```bash
# 基本运行
pytest tests/e2e/

# 带 UI 模式（调试）
pytest --headed

# 特定测试文件
pytest tests/e2e/auth/test_login.py -v

# 生成 HTML 报告
pytest --html=report.html --self-contained-html

# 生成 Playwright 追踪
pytest --tracing=on

# 使用特定 base URL
pytest --base-url=https://staging.example.com
```
