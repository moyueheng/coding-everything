# MCP 安装集成 实施计划

> **给 Agent：** 必需子 skill：使用 `dev-executing-plans` 逐个任务实施此计划。

**目标：** 在现有 `make install` 流程中新增 MCP 服务器配置管理，自动将 4 个必装 MCP 写入 `~/.claude.json`。

**架构：** 在现有 `scripts/install_skills.py` 中新增 MCP 管理函数，通过 `mcp-configs/required.json` 模板驱动配置。Token 从现有 `~/.claude.json` 或环境变量读取，manifest 记录管理的 MCP 列表以支持卸载。

**技术栈：** Python 3.10+，标准库 (`json`, `pathlib`, `os`)，`unittest`

**设计文档：** `docs/plans/2026-03-31-mcp-install-design.md`

---

## 文件结构

| 文件 | 职责 | 操作 |
|------|------|------|
| `mcp-configs/required.json` | 4 个必装 MCP 模板定义 | 新建 |
| `scripts/install_skills.py` | 安装逻辑，新增 MCP 管理函数 | 修改 |
| `tests/test_install_skills.py` | 现有测试，扩展 MCP 相关测试 | 修改 |
| `docs/plans/2026-03-31-mcp-install-design.md` | 设计文档 | 已存在（修正 URL） |

---

## 任务 1：创建 `mcp-configs/required.json` 模板文件

**文件：**
- 创建：`mcp-configs/required.json`

> 此任务是纯配置文件创建，不需要 TDD。

**步骤 1：创建目录和文件**

创建 `mcp-configs/required.json`，内容如下：

```json
{
  "mcpServers": {
    "auggie-mcp": {
      "command": "auggie",
      "args": ["--mcp", "--mcp-auto-workspace"],
      "type": "stdio",
      "_install_note": "需要先安装 Auggie CLI 并执行 `auggie login` 完成浏览器 OAuth 认证。文档: https://docs.augmentcode.com/context-services/mcp/overview"
    },
    "zai-github-read": {
      "type": "http",
      "url": "https://open.bigmodel.cn/api/mcp/zread/mcp",
      "headers": {
        "Authorization": "Bearer {{ZAI_API_KEY}}"
      }
    },
    "zai-web-reader": {
      "type": "http",
      "url": "https://open.bigmodel.cn/api/mcp/web_reader/mcp",
      "headers": {
        "Authorization": "Bearer {{ZAI_API_KEY}}"
      }
    },
    "zai-web-search-prime": {
      "type": "http",
      "url": "https://open.bigmodel.cn/api/mcp/web_search_prime/mcp",
      "headers": {
        "Authorization": "Bearer {{ZAI_API_KEY}}"
      }
    }
  }
}
```

**注意：** URL 路径段使用下划线 (`web_reader`, `web_search_prime`)，这是智谱 API 的实际路径格式。

**步骤 2：验证 JSON 格式正确**

运行：`python3 -c "import json; json.load(open('mcp-configs/required.json'))"`
预期：无错误输出

**步骤 3：修正设计文档中的 URL**

修改 `docs/plans/2026-03-31-mcp-install-design.md` 中 `required.json` 示例，将 `web-reader` 改为 `web_reader`，`web-search-prime` 改为 `web_search_prime`。

**步骤 4：提交**

```bash
git add mcp-configs/required.json docs/plans/2026-03-31-mcp-install-design.md
git commit -m "feat(mcp): add required MCP server template"
```

---

## 任务 2：实现 `load_mcp_template` 和 `resolve_zai_api_key` 函数

**文件：**
- 修改：`scripts/install_skills.py`（在 `discover_skills` 函数后插入新函数）
- 修改：`tests/test_install_skills.py`（新增测试类 `McpTemplateTest`）

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1：RED - 编写失败的测试**

在 `tests/test_install_skills.py` 末尾（`if __name__` 之前）新增测试类：

```python
class McpTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name) / "repo"
        self.home = Path(self.temp_dir.name) / "home"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _create_required_json(self) -> None:
        mcp_dir = self.repo_root / "mcp-configs"
        mcp_dir.mkdir(parents=True)
        (mcp_dir / "required.json").write_text(
            json.dumps({
                "mcpServers": {
                    "auggie-mcp": {
                        "command": "auggie",
                        "args": ["--mcp", "--mcp-auto-workspace"],
                        "type": "stdio",
                        "_install_note": "需要先安装 Auggie CLI",
                    },
                    "zai-github-read": {
                        "type": "http",
                        "url": "https://open.bigmodel.cn/api/mcp/zread/mcp",
                        "headers": {"Authorization": "Bearer {{ZAI_API_KEY}}"},
                    },
                }
            }),
            encoding="utf-8",
        )

    def test_load_mcp_template_returns_parsed_json(self) -> None:
        self._create_required_json()
        result = install_skills.load_mcp_template(self.repo_root)
        self.assertIn("mcpServers", result)
        self.assertIn("auggie-mcp", result["mcpServers"])
        self.assertIn("zai-github-read", result["mcpServers"])

    def test_load_mcp_template_raises_when_file_missing(self) -> None:
        with self.assertRaises(FileNotFoundError):
            install_skills.load_mcp_template(self.repo_root)

    def test_resolve_zai_api_key_from_existing_config(self) -> None:
        claude_config = {
            "mcpServers": {
                "zai-github-read": {
                    "headers": {"Authorization": "Bearer my-token-123"},
                }
            }
        }
        result = install_skills.resolve_zai_api_key(claude_config)
        self.assertEqual(result, "my-token-123")

    def test_resolve_zai_api_key_from_env_var(self) -> None:
        claude_config = {"mcpServers": {}}
        with unittest.mock.patch.dict("os.environ", {"ZAI_API_KEY": "env-token-456"}):
            result = install_skills.resolve_zai_api_key(claude_config)
            self.assertEqual(result, "env-token-456")

    def test_resolve_zai_api_key_returns_none_when_unavailable(self) -> None:
        claude_config = {"mcpServers": {}}
        with unittest.mock.patch.dict("os.environ", {}, clear=True):
            result = install_skills.resolve_zai_api_key(claude_config)
            self.assertIsNone(result)

    def test_resolve_zai_api_key_prefers_existing_over_env(self) -> None:
        claude_config = {
            "mcpServers": {
                "zai-web-reader": {
                    "headers": {"Authorization": "Bearer config-token"},
                }
            }
        }
        with unittest.mock.patch.dict("os.environ", {"ZAI_API_KEY": "env-token"}):
            result = install_skills.resolve_zai_api_key(claude_config)
            self.assertEqual(result, "config-token")
```

**步骤 2：验证 RED - 看着它失败**

运行：`uv run python -m unittest tests.test_install_skills.McpTemplateTest -v`
预期：FAIL - `AttributeError: module 'scripts.install_skills' has no attribute 'load_mcp_template'`

**步骤 3：GREEN - 编写最小实现**

在 `scripts/install_skills.py` 中，在 `discover_skills` 函数之后（`remove_existing` 之前）插入：

```python
import os as _os

MCP_CONFIG_RELATIVE_PATH = Path("mcp-configs/required.json")

ZAI_MCP_NAMES = ("zai-github-read", "zai-web-reader", "zai-web-search-prime")


def load_mcp_template(repo_root: Path) -> dict:
    path = repo_root / MCP_CONFIG_RELATIVE_PATH
    if not path.is_file():
        raise FileNotFoundError(f"MCP config not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_zai_api_key(claude_config: dict) -> str | None:
    for name in ZAI_MCP_NAMES:
        server = claude_config.get("mcpServers", {}).get(name, {})
        auth = server.get("headers", {}).get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[len("Bearer "):]
    env_key = _os.environ.get("ZAI_API_KEY")
    if env_key:
        return env_key
    return None
```

同时在文件顶部 import 区域新增：

```python
import os as _os
```

**步骤 4：验证 GREEN - 看着它通过**

运行：`uv run python -m unittest tests.test_install_skills.McpTemplateTest -v`
预期：5 个测试全部 PASS

运行全部测试确保无回归：
运行：`uv run python -m unittest tests.test_install_skills -v`
预期：全部 PASS（原有 8 个 + 新增 5 个）

**步骤 5：REFACTOR**

检查：
- `ZAI_MCP_NAMES` 作为模块常量，避免硬编码散落
- `_os` 别名避免与可能的其他 `os` 冲突
- 函数签名简洁，职责单一

无需进一步重构。

**步骤 6：运行 ruff check**

运行：`uv run ruff check scripts/install_skills.py tests/test_install_skills.py`
预期：无错误

**步骤 7：提交**

```bash
git add scripts/install_skills.py tests/test_install_skills.py
git commit -m "feat(mcp): add load_mcp_template and resolve_zai_api_key"
```

---

## 任务 3：实现 `merge_mcp_config` 函数

**文件：**
- 修改：`scripts/install_skills.py`（新增 `merge_mcp_config` 函数）
- 修改：`tests/test_install_skills.py`（新增测试类 `MergeMcpConfigTest`）

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1：RED - 编写失败的测试**

```python
class MergeMcpConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name) / "repo"
        self.home = Path(self.temp_dir.name) / "home"
        self.claude_json = self.home / ".claude.json"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_required_json(self, servers: dict) -> None:
        mcp_dir = self.repo_root / "mcp-configs"
        mcp_dir.mkdir(parents=True, exist_ok=True)
        (mcp_dir / "required.json").write_text(
            json.dumps({"mcpServers": servers}), encoding="utf-8"
        )

    def _write_claude_json(self, data: dict) -> None:
        self.home.mkdir(parents=True, exist_ok=True)
        self.claude_json.write_text(json.dumps(data), encoding="utf-8")

    def _read_claude_json(self) -> dict:
        return json.loads(self.claude_json.read_text(encoding="utf-8"))

    def test_merge_adds_mcp_to_empty_claude_json(self) -> None:
        self._write_required_json({
            "auggie-mcp": {
                "command": "auggie",
                "args": ["--mcp"],
                "type": "stdio",
                "_install_note": "reminder",
            }
        })
        self._write_claude_json({"mcpServers": {}})

        installed = install_skills.merge_mcp_config(self.home, self.repo_root)

        self.assertEqual(installed, ["auggie-mcp"])
        config = self._read_claude_json()
        mcp = config["mcpServers"]["auggie-mcp"]
        self.assertEqual(mcp["command"], "auggie")
        self.assertEqual(mcp["type"], "stdio")
        self.assertNotIn("_install_note", mcp)

    def test_merge_substitutes_zai_api_key(self) -> None:
        self._write_required_json({
            "zai-github-read": {
                "type": "http",
                "url": "https://example.com/mcp",
                "headers": {"Authorization": "Bearer {{ZAI_API_KEY}}"},
            }
        })
        self._write_claude_json({"mcpServers": {}})

        with unittest.mock.patch.dict("os.environ", {"ZAI_API_KEY": "test-key"}):
            installed = install_skills.merge_mcp_config(self.home, self.repo_root)

        self.assertEqual(installed, ["zai-github-read"])
        config = self._read_claude_json()
        self.assertEqual(
            config["mcpServers"]["zai-github-read"]["headers"]["Authorization"],
            "Bearer test-key",
        )

    def test_merge_skips_zai_when_no_api_key(self) -> None:
        self._write_required_json({
            "zai-github-read": {
                "type": "http",
                "url": "https://example.com/mcp",
                "headers": {"Authorization": "Bearer {{ZAI_API_KEY}}"},
            }
        })
        self._write_claude_json({"mcpServers": {}})

        with unittest.mock.patch.dict("os.environ", {}, clear=True):
            installed = install_skills.merge_mcp_config(self.home, self.repo_root)

        self.assertEqual(installed, [])
        config = self._read_claude_json()
        self.assertNotIn("zai-github-read", config["mcpServers"])

    def test_merge_preserves_existing_mcp_servers(self) -> None:
        self._write_required_json({
            "auggie-mcp": {
                "command": "auggie",
                "args": ["--mcp"],
                "type": "stdio",
            }
        })
        self._write_claude_json({
            "mcpServers": {
                "user-custom": {"type": "http", "url": "https://user.com/mcp"}
            }
        })

        install_skills.merge_mcp_config(self.home, self.repo_root)

        config = self._read_claude_json()
        self.assertIn("user-custom", config["mcpServers"])
        self.assertIn("auggie-mcp", config["mcpServers"])

    def test_merge_creates_claude_json_when_missing(self) -> None:
        self._write_required_json({
            "auggie-mcp": {
                "command": "auggie",
                "args": ["--mcp"],
                "type": "stdio",
            }
        })
        self.home.mkdir(parents=True, exist_ok=True)

        installed = install_skills.merge_mcp_config(self.home, self.repo_root)

        self.assertEqual(installed, ["auggie-mcp"])
        self.assertTrue(self.claude_json.exists())
        config = self._read_claude_json()
        self.assertIn("auggie-mcp", config["mcpServers"])

    def test_merge_is_idempotent(self) -> None:
        self._write_required_json({
            "auggie-mcp": {
                "command": "auggie",
                "args": ["--mcp"],
                "type": "stdio",
            }
        })
        self._write_claude_json({"mcpServers": {}})

        install_skills.merge_mcp_config(self.home, self.repo_root)
        install_skills.merge_mcp_config(self.home, self.repo_root)

        config = self._read_claude_json()
        self.assertEqual(len(config["mcpServers"]), 1)
```

**步骤 2：验证 RED - 看着它失败**

运行：`uv run python -m unittest tests.test_install_skills.MergeMcpConfigTest -v`
预期：FAIL - `AttributeError: module 'scripts.install_skills' has no attribute 'merge_mcp_config'`

**步骤 3：GREEN - 编写最小实现**

在 `scripts/install_skills.py` 中，`resolve_zai_api_key` 之后插入：

```python
CLAUDE_JSON_FILENAME = ".claude.json"
PLACEHOLDER_ZAI_API_KEY = "{{ZAI_API_KEY}}"


def _deep_copy_without_internal_keys(data: dict) -> dict:
    return {k: v for k, v in data.items() if not k.startswith("_")}


def merge_mcp_config(home: Path, repo_root: Path) -> list[str]:
    template = load_mcp_template(repo_root)
    claude_json_path = home / CLAUDE_JSON_FILENAME

    if claude_json_path.exists():
        claude_config = json.loads(claude_json_path.read_text(encoding="utf-8"))
    else:
        claude_config = {}

    if "mcpServers" not in claude_config:
        claude_config = {**claude_config, "mcpServers": {}}

    zai_api_key = resolve_zai_api_key(claude_config)
    installed: list[str] = []

    for name, server_def in template["mcpServers"].items():
        clean_def = _deep_copy_without_internal_keys(server_def)

        needs_zai_key = PLACEHOLDER_ZAI_API_KEY in json.dumps(clean_def)
        if needs_zai_key and zai_api_key is None:
            continue

        if needs_zai_key:
            serialized = json.dumps(clean_def)
            serialized = serialized.replace(PLACEHOLDER_ZAI_API_KEY, zai_api_key)
            clean_def = json.loads(serialized)

        claude_config["mcpServers"] = {
            **claude_config["mcpServers"],
            name: clean_def,
        }
        installed.append(name)

    claude_json_path.parent.mkdir(parents=True, exist_ok=True)
    claude_json_path.write_text(
        json.dumps(claude_config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return sorted(installed)
```

**步骤 4：验证 GREEN - 看着它通过**

运行：`uv run python -m unittest tests.test_install_skills.MergeMcpConfigTest -v`
预期：6 个测试全部 PASS

运行全部测试确保无回归：
运行：`uv run python -m unittest tests.test_install_skills -v`
预期：全部 PASS

**步骤 5：REFACTOR**

检查：
- `_deep_copy_without_internal_keys` 过滤 `_install_note` 等元数据字段
- `PLACEHOLDER_ZAI_API_KEY` 常量避免魔术字符串
- 通过 JSON 序列化/反序列化替换占位符，保持不可变性
- `sorted(installed)` 保证输出顺序稳定

无需进一步重构。

**步骤 6：运行 ruff check**

运行：`uv run ruff check scripts/install_skills.py tests/test_install_skills.py`
预期：无错误

**步骤 7：提交**

```bash
git add scripts/install_skills.py tests/test_install_skills.py
git commit -m "feat(mcp): add merge_mcp_config with template substitution"
```

---

## 任务 4：实现 `remove_managed_mcps` 和 `collect_mcp_status` 函数

**文件：**
- 修改：`scripts/install_skills.py`（新增 2 个函数）
- 修改：`tests/test_install_skills.py`（新增测试类）

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1：RED - 编写失败的测试**

```python
class RemoveManagedMcpsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.home = Path(self.temp_dir.name) / "home"
        self.claude_json = self.home / ".claude.json"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_claude_json(self, servers: dict) -> None:
        self.home.mkdir(parents=True, exist_ok=True)
        self.claude_json.write_text(
            json.dumps({"mcpServers": servers}), encoding="utf-8"
        )

    def _read_claude_json(self) -> dict:
        return json.loads(self.claude_json.read_text(encoding="utf-8"))

    def test_removes_only_managed_mcp_names(self) -> None:
        self._write_claude_json({
            "auggie-mcp": {"type": "stdio", "command": "auggie"},
            "user-custom": {"type": "http", "url": "https://user.com/mcp"},
        })
        install_skills.remove_managed_mcps(self.home, ["auggie-mcp"])
        config = self._read_claude_json()
        self.assertNotIn("auggie-mcp", config["mcpServers"])
        self.assertIn("user-custom", config["mcpServers"])

    def test_noop_when_claude_json_missing(self) -> None:
        self.home.mkdir(parents=True, exist_ok=True)
        install_skills.remove_managed_mcps(self.home, ["auggie-mcp"])
        self.assertFalse(self.claude_json.exists())

    def test_removes_empty_mcp_servers_key(self) -> None:
        self._write_claude_json({
            "auggie-mcp": {"type": "stdio", "command": "auggie"},
        })
        install_skills.remove_managed_mcps(self.home, ["auggie-mcp"])
        config = self._read_claude_json()
        self.assertEqual(config["mcpServers"], {})


class CollectMcpStatusTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name) / "repo"
        self.home = Path(self.temp_dir.name) / "home"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_required_json(self, servers: dict) -> None:
        mcp_dir = self.repo_root / "mcp-configs"
        mcp_dir.mkdir(parents=True, exist_ok=True)
        (mcp_dir / "required.json").write_text(
            json.dumps({"mcpServers": servers}), encoding="utf-8"
        )

    def _write_claude_json(self, servers: dict) -> None:
        self.home.mkdir(parents=True, exist_ok=True)
        (self.home / ".claude.json").write_text(
            json.dumps({"mcpServers": servers}), encoding="utf-8"
        )

    def test_all_configured(self) -> None:
        self._write_required_json({
            "auggie-mcp": {"type": "stdio", "command": "auggie"},
            "zai-github-read": {
                "type": "http",
                "url": "https://example.com",
                "headers": {"Authorization": "Bearer {{ZAI_API_KEY}}"},
            },
        })
        self._write_claude_json({
            "auggie-mcp": {"type": "stdio", "command": "auggie"},
            "zai-github-read": {
                "type": "http",
                "url": "https://example.com",
                "headers": {"Authorization": "Bearer real-key"},
            },
        })
        status = install_skills.collect_mcp_status(self.home, self.repo_root)
        self.assertEqual(status["configured"], ["auggie-mcp", "zai-github-read"])
        self.assertEqual(status["missing"], [])

    def test_partial_configured(self) -> None:
        self._write_required_json({
            "auggie-mcp": {"type": "stdio", "command": "auggie"},
            "zai-github-read": {
                "type": "http",
                "url": "https://example.com",
                "headers": {"Authorization": "Bearer {{ZAI_API_KEY}}"},
            },
        })
        self._write_claude_json({
            "auggie-mcp": {"type": "stdio", "command": "auggie"},
        })
        status = install_skills.collect_mcp_status(self.home, self.repo_root)
        self.assertEqual(status["configured"], ["auggie-mcp"])
        self.assertEqual(status["missing"], ["zai-github-read"])

    def test_no_claude_json(self) -> None:
        self._write_required_json({
            "auggie-mcp": {"type": "stdio", "command": "auggie"},
        })
        self.home.mkdir(parents=True, exist_ok=True)
        status = install_skills.collect_mcp_status(self.home, self.repo_root)
        self.assertEqual(status["configured"], [])
        self.assertEqual(status["missing"], ["auggie-mcp"])
```

**步骤 2：验证 RED - 看着它失败**

运行：`uv run python -m unittest tests.test_install_skills.RemoveManagedMcpsTest tests.test_install_skills.CollectMcpStatusTest -v`
预期：FAIL

**步骤 3：GREEN - 编写最小实现**

在 `merge_mcp_config` 之后插入：

```python
def remove_managed_mcps(home: Path, managed_names: list[str]) -> None:
    claude_json_path = home / CLAUDE_JSON_FILENAME
    if not claude_json_path.exists():
        return

    claude_config = json.loads(claude_json_path.read_text(encoding="utf-8"))
    servers = claude_config.get("mcpServers", {})

    managed_set = set(managed_names)
    updated_servers = {k: v for k, v in servers.items() if k not in managed_set}

    claude_config = {**claude_config, "mcpServers": updated_servers}
    claude_json_path.write_text(
        json.dumps(claude_config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def collect_mcp_status(home: Path, repo_root: Path) -> dict:
    template = load_mcp_template(repo_root)
    claude_json_path = home / CLAUDE_JSON_FILENAME

    if claude_json_path.exists():
        claude_config = json.loads(claude_json_path.read_text(encoding="utf-8"))
        existing = set(claude_config.get("mcpServers", {}).keys())
    else:
        existing = set()

    configured: list[str] = []
    missing: list[str] = []

    for name in sorted(template["mcpServers"].keys()):
        if name in existing:
            configured.append(name)
        else:
            missing.append(name)

    return {"configured": configured, "missing": missing}
```

**步骤 4：验证 GREEN - 看着它通过**

运行：`uv run python -m unittest tests.test_install_skills.RemoveManagedMcpsTest tests.test_install_skills.CollectMcpStatusTest -v`
预期：6 个测试全部 PASS

运行全部测试：
运行：`uv run python -m unittest tests.test_install_skills -v`
预期：全部 PASS

**步骤 5：REFACTOR**

检查：
- `remove_managed_mcps` 使用字典推导创建新对象，不修改原对象
- `collect_mcp_status` 返回稳定排序的列表
- 两个函数都处理 `~/.claude.json` 不存在的情况

无需进一步重构。

**步骤 6：运行 ruff check**

运行：`uv run ruff check scripts/install_skills.py tests/test_install_skills.py`
预期：无错误

**步骤 7：提交**

```bash
git add scripts/install_skills.py tests/test_install_skills.py
git commit -m "feat(mcp): add remove_managed_mcps and collect_mcp_status"
```

---

## 任务 5：集成 MCP 到 install/update/uninstall/status 命令

**文件：**
- 修改：`scripts/install_skills.py`（修改 4 个 command 函数 + `manifest_payload`）
- 修改：`tests/test_install_skills.py`（扩展集成测试）

> **给 Agent：** 此任务使用 `dev-tdd` skill。遵循 RED-GREEN-REFACTOR。

**步骤 1：RED - 编写失败的测试**

在 `tests/test_install_skills.py` 的 `InstallSkillsTest` 类中新增测试方法：

```python
def test_install_writes_mcp_servers_to_claude_json(self) -> None:
    mcp_dir = self.repo_root / "mcp-configs"
    mcp_dir.mkdir(parents=True)
    (mcp_dir / "required.json").write_text(
        json.dumps({
            "mcpServers": {
                "auggie-mcp": {
                    "command": "auggie",
                    "args": ["--mcp"],
                    "type": "stdio",
                }
            }
        }),
        encoding="utf-8",
    )

    code = self.run_command("install")
    self.assertEqual(code, 0)

    claude_json = self.home / ".claude.json"
    self.assertTrue(claude_json.exists())
    config = json.loads(claude_json.read_text(encoding="utf-8"))
    self.assertIn("auggie-mcp", config["mcpServers"])

    manifest = json.loads(self.manifest_path().read_text(encoding="utf-8"))
    self.assertIn("auggie-mcp", manifest["managed_mcp_servers"])

def test_uninstall_removes_managed_mcp_servers(self) -> None:
    mcp_dir = self.repo_root / "mcp-configs"
    mcp_dir.mkdir(parents=True)
    (mcp_dir / "required.json").write_text(
        json.dumps({
            "mcpServers": {
                "auggie-mcp": {
                    "command": "auggie",
                    "args": ["--mcp"],
                    "type": "stdio",
                }
            }
        }),
        encoding="utf-8",
    )
    claude_json = self.home / ".claude.json"
    self.home.mkdir(parents=True, exist_ok=True)
    claude_json.write_text(
        json.dumps({
            "mcpServers": {
                "user-own": {"type": "http", "url": "https://user.com"},
            }
        }),
        encoding="utf-8",
    )

    self.run_command("install")
    self.run_command("uninstall")

    config = json.loads(claude_json.read_text(encoding="utf-8"))
    self.assertNotIn("auggie-mcp", config["mcpServers"])
    self.assertIn("user-own", config["mcpServers"])

def test_status_reports_mcp_state(self) -> None:
    mcp_dir = self.repo_root / "mcp-configs"
    mcp_dir.mkdir(parents=True)
    (mcp_dir / "required.json").write_text(
        json.dumps({
            "mcpServers": {
                "auggie-mcp": {
                    "command": "auggie",
                    "args": ["--mcp"],
                    "type": "stdio",
                }
            }
        }),
        encoding="utf-8",
    )

    self.run_command("install")
    self.stdout = io.StringIO()
    code = self.run_command("status")
    self.assertEqual(code, 0)
    output = self.stdout.getvalue()
    self.assertIn("mcp_configured=", output)
    self.assertIn("auggie-mcp", output)
```

**步骤 2：验证 RED - 看着它失败**

运行：`uv run python -m unittest tests.test_install_skills.InstallSkillsTest.test_install_writes_mcp_servers_to_claude_json -v`
预期：FAIL - manifest 中没有 `managed_mcp_servers` 字段

**步骤 3：GREEN - 编写最小实现**

修改 `manifest_payload` 函数，新增 `mcp_servers` 参数：

```python
def manifest_payload(
    repo_root: Path,
    targets: InstallTargets,
    skills: Iterable[str],
    installed_at: str | None = None,
    mcp_servers: Iterable[str] = (),
) -> dict:
    timestamp = now_iso()
    return {
        "repo_root": str(repo_root),
        "installed_at": installed_at or timestamp,
        "updated_at": timestamp,
        "targets": {
            "agents_skills_dir": str(targets.agents_skills_dir),
            "claude_skills_dir": str(targets.claude_skills_dir),
            "kimi_agent_dir": str(targets.kimi_agent_dir),
            "ks_path": str(targets.ks_path),
        },
        "skills": list(skills),
        "managed_mcp_servers": sorted(mcp_servers),
    }
```

修改 `command_install`：

```python
def command_install(repo_root: Path, home: Path, stdout: TextIO = sys.stdout) -> int:
    targets = build_targets(home)
    ensure_parent_dirs(targets)
    skills = discover_skills(repo_root)
    install_skill_links(repo_root, targets, skills)
    install_kimi_agent_and_ks(repo_root, targets)
    installed_at = None
    existing = load_manifest(targets)
    if existing:
        installed_at = existing.get("installed_at")
    mcp_servers = merge_mcp_config(home, repo_root)
    _print_mcp_status(home, repo_root, mcp_servers, stdout)
    write_manifest(repo_root, targets, skills, installed_at=installed_at, mcp_servers=mcp_servers)
    print(f"installed {len(skills)} skills", file=stdout)
    return 0
```

修改 `command_update`：

```python
def command_update(repo_root: Path, home: Path, stdout: TextIO = sys.stdout) -> int:
    targets = build_targets(home)
    manifest = load_manifest(targets)
    if manifest is None:
        print("manifest missing; running install", file=stdout)
        return command_install(repo_root, home, stdout=stdout)

    ensure_parent_dirs(targets)
    skills = discover_skills(repo_root)
    install_skill_links(repo_root, targets, skills)
    install_kimi_agent_and_ks(repo_root, targets)
    mcp_servers = merge_mcp_config(home, repo_root)
    _print_mcp_status(home, repo_root, mcp_servers, stdout)
    write_manifest(repo_root, targets, skills, installed_at=manifest.get("installed_at"), mcp_servers=mcp_servers)
    print(f"updated {len(skills)} skills", file=stdout)
    return 0
```

修改 `command_uninstall`，在 `remove_existing(targets.manifest_path)` 之前插入：

```python
    managed_mcps = manifest.get("managed_mcp_servers", [])
    if managed_mcps:
        remove_managed_mcps(home, managed_mcps)
```

修改 `command_status`，在 `return 0` 之前插入 MCP 状态输出：

```python
    mcp_status = collect_mcp_status(home, repo_root)
    configured = mcp_status["configured"]
    missing = mcp_status["missing"]
    if configured:
        print("mcp_configured=" + ",".join(configured), file=stdout)
    if missing:
        print("mcp_missing=" + ",".join(missing), file=stdout)
```

新增辅助函数 `_print_mcp_status`（放在 `command_install` 之前）：

```python
def _print_mcp_status(home: Path, repo_root: Path, installed: list[str], stdout: TextIO) -> None:
    if not installed:
        return
    template = load_mcp_template(repo_root)
    print("MCP servers:", file=stdout)
    for name in installed:
        server = template["mcpServers"][name]
        note = server.get("_install_note")
        if note:
            print(f"  ✓ {name} → configured ({note})", file=stdout)
        else:
            print(f"  ✓ {name} → configured", file=stdout)
    all_names = set(template["mcpServers"].keys())
    skipped = sorted(all_names - set(installed))
    for name in skipped:
        print(f"  ⚠ {name} → skipped (set ZAI_API_KEY or configure any zai service in ~/.claude.json first)", file=stdout)
```

同时需要修改 `write_manifest` 签名以传递 `mcp_servers`：

```python
def write_manifest(
    repo_root: Path,
    targets: InstallTargets,
    skills: Iterable[str],
    installed_at: str | None = None,
    mcp_servers: Iterable[str] = (),
) -> None:
    payload = manifest_payload(repo_root, targets, skills, installed_at=installed_at, mcp_servers=mcp_servers)
    targets.manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
```

**步骤 4：验证 GREEN - 看着它通过**

运行：`uv run python -m unittest tests.test_install_skills -v`
预期：全部 PASS

**步骤 5：REFACTOR**

检查：
- `_print_mcp_status` 输出格式与设计文档一致
- `manifest_payload` 保持向后兼容（`mcp_servers` 默认空元组）
- 4 个 command 函数的调用链清晰

无需进一步重构。

**步骤 6：运行 ruff check**

运行：`uv run ruff check scripts/install_skills.py tests/test_install_skills.py`
预期：无错误

**步骤 7：提交**

```bash
git add scripts/install_skills.py tests/test_install_skills.py
git commit -m "feat(mcp): integrate MCP management into install/update/uninstall/status"
```

---

## 任务 6：端到端验证

**文件：** 无修改

> 此任务是验证性任务，不需要 TDD。

**步骤 1：运行全部测试**

运行：`uv run python -m unittest tests.test_install_skills -v`
预期：全部 PASS，包含所有原有和新增测试

**步骤 2：运行 ruff check**

运行：`uv run ruff check scripts/install_skills.py tests/test_install_skills.py`
预期：无错误

**步骤 3：用真实仓库做 dry-run（不实际执行，仅验证 import 和函数可调用）**

运行：`uv run python -c "from scripts import install_skills; print('OK')"`
预期：`OK`

**步骤 4：验证 `make test` 通过**

运行：`make test`
预期：全部 PASS

---

## 任务 7：更新文档

**文件：**
- 修改：`CLAUDE.md`（在项目结构中新增 `mcp-configs/` 目录，更新 skill 列表说明）
- 修改：`docs/plans/2026-03-31-mcp-install-design.md`（修正 URL，标记已实现）

> 此任务是文档更新，不需要 TDD。

**步骤 1：更新 CLAUDE.md 项目结构**

在项目结构树中的 `scripts/` 之前新增：

```
├── mcp-configs/                # MCP 服务器配置模板
│   └── required.json           # 必装 MCP 定义（auggie-mcp + 3 个 zai 服务）
```

在快速安装章节后新增 MCP 配置说明段落，描述：
- `make install` 自动配置 4 个必装 MCP 到 `~/.claude.json`
- zai 服务需要 `ZAI_API_KEY` 环境变量或现有配置中的 Bearer token
- auggie-mcp 需要先执行 `auggie login`
- `make uninstall` 仅删除本工具管理的 MCP

**步骤 2：修正设计文档中的 URL**

将 `docs/plans/2026-03-31-mcp-install-design.md` 中的 `web-reader` 改为 `web_reader`，`web-search-prime` 改为 `web_search_prime`。

**步骤 3：提交**

```bash
git add CLAUDE.md docs/plans/2026-03-31-mcp-install-design.md
git commit -m "docs: add MCP installation to project documentation"
```

---

## 计划自审

### 1. Spec 覆盖度

| Spec 需求 | 对应任务 |
|-----------|---------|
| `mcp-configs/required.json` 模板 | 任务 1 |
| `load_mcp_template` 函数 | 任务 2 |
| `resolve_zai_api_key` 函数（3 级优先级） | 任务 2 |
| `merge_mcp_config` 函数（ADD-ONLY、占位符替换） | 任务 3 |
| `remove_managed_mcps` 函数 | 任务 4 |
| `collect_mcp_status` 函数 | 任务 4 |
| Manifest 扩展 `managed_mcp_servers` | 任务 5 |
| `command_install` 集成 + 输出 | 任务 5 |
| `command_update` 集成 | 任务 5 |
| `command_uninstall` 集成 | 任务 5 |
| `command_status` 集成 + MCP 状态 | 任务 5 |
| auggie-mcp 登录提醒 + 文档链接 | 任务 1（`_install_note`）、任务 5（`_print_mcp_status`） |
| URL 使用下划线格式 | 任务 1、步骤 3 修正设计文档 |
| 文档更新 | 任务 7 |

全部覆盖，无遗漏。

### 2. 占位符扫描

无 "TBD"、"TODO"、"稍后实现" 等红旗。所有代码完整可运行。

### 3. 类型一致性

- `merge_mcp_config` 返回 `list[str]`，`command_install` 中赋值给 `mcp_servers`，传入 `write_manifest` 的 `mcp_servers` 参数类型 `Iterable[str]` — 兼容。
- `remove_managed_mcps` 接受 `list[str]`，从 manifest 的 `managed_mcp_servers`（`list[str]`）传入 — 一致。
- `collect_mcp_status` 返回 `dict` 包含 `configured`/`missing`（`list[str]`），`command_status` 中直接使用 — 一致。

无类型不一致。
