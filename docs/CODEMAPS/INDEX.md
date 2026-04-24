<!-- 生成时间: 2026-04-24 | 扫描文件: 236 | Token 估算: ~3695 -->

# Codemap Index

**生成日期:** 2026-04-24
**扫描文件:** 236
**Token 估算:** ~3695

## Areas

| Area | Size | Key Directories |
|------|------|-----------------|
| [Skills](./skills.md) | 130 files | `skills`, `skills/agent-browser`, `skills/agent-browser/references` |
| [CLI](./cli.md) | 19 files | `.`, `install_skills`, `mcp-configs` |
| [Agents](./agents.md) | 11 files | `.agents/skills/dev-creating-subagents`, `.agents/skills/dev-creating-subagents/references`, `.agents/skills/setup` |
| [Docs](./docs.md) | 41 files | `.`, `docs`, `docs/plans` |
| [Scripts](./scripts.md) | 5 files | `.agents/skills/update-upstream-repos/scripts`, `scripts` |

## Upstream Submodules

| Name | Path | URL |
|------|------|-----|
| `upstream/superpowers` | `upstream/superpowers` | [link](https://github.com/obra/superpowers.git) |
| `upstream/everything-claude-code` | `upstream/everything-claude-code` | [link](https://github.com/affaan-m/everything-claude-code.git) |
| `upstream/ui-ux-pro-max-skill` | `upstream/ui-ux-pro-max-skill` | [link](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git) |
| `upstream/humanizer-zh` | `upstream/humanizer-zh` | [link](https://github.com/op7418/Humanizer-zh.git) |
| `upstream/product-manager-skills` | `upstream/product-manager-skills` | [link](https://github.com/deanpeters/Product-Manager-Skills.git) |
| `upstream/obsidian-skills` | `upstream/obsidian-skills` | [link](https://github.com/kepano/obsidian-skills.git) |
| `upstream/orbitos` | `upstream/orbitos` | [link](https://github.com/MarsWang42/OrbitOS.git) |
| `upstream/karpathy-llm-wiki` | `upstream/karpathy-llm-wiki` | [link](https://github.com/Astro-Han/karpathy-llm-wiki.git) |
| `upstream/karpathy-skills` | `upstream/karpathy-skills` | [link](https://github.com/forrestchang/andrej-karpathy-skills.git) |

## 如何重新生成

```bash
uv run scripts/generate_codemaps.py
uv run scripts/generate_codemaps.py --dry-run    # 仅输出到 stdout
uv run scripts/generate_codemaps.py --force       # 跳过差异确认
```

## 相关文档

- [Skills](./skills.md) — 共享 skill 清单
- [CLI](./cli.md) — ce CLI 架构
- [Agents](./agents.md) — 平台配置
- [Docs](./docs.md) — 文档目录
- [Scripts](./scripts.md) — 脚本清单
