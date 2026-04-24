<!-- 生成时间: 2026-04-24 | 扫描文件: 19 | Token 估算: ~968 -->

# CLI Codemap

**文件数:** 19

## 架构数据流

```
~/.ce/config.yaml              (用户配置)
        │
        ▼
install_skills/cli.py           argparse 命令路由
        │
        ▼
install_skills/installer.py     symlink / manifest / MCP
        │
        ├─► ~/.agents/skills/   symlink
        ├─► ~/.claude/skills/   symlink
        └─► ~/.ce/install-manifest.json
```

## 关键模块

| File | Lines |
|------|-------|
| `AGENTS.md` | 141 |
| `CLAUDE.md` | 141 |
| `__init__.py` | 3 |
| `cli.py` | 433 |
| `config.py` | 88 |
| `installer.py` | 1131 |
| `models.py` | 50 |
| `required.json` | 37 |
| `pyproject.toml` | 27 |
| `__init__.py` | 1 |
| `conftest.py` | 9 |
| `test_cli_add.py` | 67 |
| `test_cli_init.py` | 86 |
| `test_cli_repo_root_repair.py` | 78 |
| `test_config.py` | 46 |
| `test_generate_codemaps.py` | 459 |
| `test_install_skills.py` | 1007 |
| `test_installer_v2.py` | 44 |
| `test_models.py` | 26 |

## 相关

- [INDEX](./INDEX.md) — 总览
- `install_skills/models.py` — frozen dataclass 定义
