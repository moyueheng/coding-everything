#!/usr/bin/env python3
"""
scripts/generate_codemaps.py

Codemap 生成器 — 扫描 coding-everything 仓库并生成 token-lean 架构文档。

用法：
    uv run scripts/generate_codemaps.py [--force] [--dry-run] [--repo-root PATH]

输出（docs/CODEMAPS/）：
    INDEX.md   — 总览索引 + submodule 列表 + 重新生成命令
    skills.md  — 按前缀分组统计 + skill 清单表
    cli.md     — CLI 架构图 + 数据流 + 关键模块表
    agents.md  — 平台配置概览
    docs.md    — 文档目录
    scripts.md — 脚本清单
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        "out",
        ".next",
        ".turbo",
        "coverage",
        ".cache",
        "upstream",
    }
)

AREA_LABELS: dict[str, str] = {
    "skills": "Skills",
    "cli": "CLI",
    "agents": "Agents",
    "docs": "Docs",
    "scripts": "Scripts",
}

# classify_file() 的前缀映射
_CLASSIFY_RULES: list[tuple[str, str]] = [
    ("skills/", "skills"),
    ("install_skills/", "cli"),
    ("tests/", "cli"),
    ("mcp-configs/", "cli"),
    ("pyproject.toml", "cli"),
    ("kimi/", "agents"),
    (".agents/skills/", "agents"),
    ("opencode/", "agents"),
    ("scripts/", "scripts"),
]

# classify_file() 的脚本子规则（.agents 下的 scripts/ 子目录）
_CLASSIFY_SCRIPTS_PREFIX = ".agents/"

# 根目录文档文件名
_ROOT_DOC_FILES: frozenset[str] = frozenset({"CLAUDE.md", "AGENTS.md", "README.md"})

# docs/ 前缀
_DOCS_PREFIX = "docs/"

# Token 估算常量
_CHARS_PER_TOKEN_EN = 4
_CHARS_PER_TOKEN_ZH = 1.5

# 差异阈值
_DIFF_THRESHOLD = 0.3


# ---------------------------------------------------------------------------
# 数据结构（frozen dataclass）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SkillMeta:
    """从 SKILL.md frontmatter 提取的元数据。"""

    name: str
    description: str
    path: Path


@dataclass(frozen=True)
class SubmoduleEntry:
    """.gitmodules 中的一条记录。"""

    name: str
    path: str
    url: str


@dataclass(frozen=True)
class AreaInfo:
    """一个区域的扫描结果。"""

    name: str
    files: list[Path]
    directories: list[str]
    entry_points: list[str]


@dataclass(frozen=True)
class ScanResult:
    """完整扫描结果，包含各区域和生成的 markdown。"""

    areas: dict[str, AreaInfo]
    metas: list[SkillMeta]
    submodules: list[SubmoduleEntry]
    markdowns: dict[str, str]
    total_tokens: int


# ---------------------------------------------------------------------------
# 文件扫描
# ---------------------------------------------------------------------------


def walk_files(root: Path) -> list[Path]:
    """递归收集 root 下所有文件，跳过 SKIP_DIRS 中的目录。"""
    results: list[Path] = []
    _walk_recursive(root, root, results)
    return sorted(results)


def _walk_recursive(current: Path, root: Path, results: list[Path]) -> None:
    try:
        entries = list(current.iterdir())
    except PermissionError:
        return
    for entry in entries:
        if entry.is_dir():
            if entry.name in SKIP_DIRS:
                continue
            _walk_recursive(entry, root, results)
        elif entry.is_file():
            results.append(entry)


# ---------------------------------------------------------------------------
# 分类
# ---------------------------------------------------------------------------


def classify_file(rel_path: Path) -> str | None:
    """根据相对路径将文件映射到区域键（skills/cli/agents/docs/scripts）。

    返回 None 表示不分类（如 upstream/、无匹配）。
    """
    path_str = rel_path.as_posix()

    # 排除 upstream/
    if path_str.startswith("upstream/"):
        return None

    # 根目录文档文件
    if path_str in _ROOT_DOC_FILES:
        return "docs"

    # docs/ 前缀
    if path_str.startswith(_DOCS_PREFIX):
        return "docs"

    # .agents/ 下的 scripts/ 子目录归入 scripts
    if path_str.startswith(_CLASSIFY_SCRIPTS_PREFIX) and "/scripts/" in path_str:
        return "scripts"

    # 前缀映射规则
    for prefix, area_key in _CLASSIFY_RULES:
        if path_str.startswith(prefix):
            return area_key

    return None


def classify_all(files: list[Path], root: Path) -> dict[str, AreaInfo]:
    """将所有文件分类到区域。"""
    area_files: dict[str, list[Path]] = {k: [] for k in AREA_LABELS}

    for f in files:
        rel = f.relative_to(root)
        area_key = classify_file(rel)
        if area_key is not None and area_key in area_files:
            area_files[area_key].append(f)

    areas: dict[str, AreaInfo] = {}
    for key, files_list in area_files.items():
        rel_paths = [f.relative_to(root).as_posix() for f in files_list]
        dirs = sorted({p.rsplit("/", 1)[0] if "/" in p else "." for p in rel_paths})
        entry_points = [
            p
            for p in rel_paths
            if p.endswith(("index.py", "main.py", "__main__.py", "cli.py"))
        ]
        areas[key] = AreaInfo(
            name=AREA_LABELS[key],
            files=files_list,
            directories=dirs,
            entry_points=entry_points[:10],
        )
    return areas


# ---------------------------------------------------------------------------
# 元数据提取
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(
    r"^---\s*\n(?P<yaml>.*?)\n---",
    re.DOTALL,
)


def parse_skill_frontmatter(content: str) -> SkillMeta | None:
    """从 SKILL.md 内容解析 YAML frontmatter，返回 SkillMeta 或 None。

    支持多行值（YAML 行延续：下一行缩进即追加到上一个值）。
    """
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return None

    yaml_block = match.group("yaml").strip()
    if not yaml_block:
        return None

    name = ""
    description = ""
    current_key = ""
    for raw_line in yaml_block.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        # 行延续：如果缩进比第一个键深，则追加到上一个值
        if raw_line.startswith("  ") or raw_line.startswith("\t"):
            if current_key == "name":
                name += " " + stripped
            elif current_key == "description":
                description += " " + stripped
            continue
        if stripped.startswith("name:"):
            name = stripped[len("name:") :].strip()
            current_key = "name"
        elif stripped.startswith("description:"):
            description = stripped[len("description:") :].strip()
            current_key = "description"
        else:
            current_key = ""

    if not name:
        return None

    return SkillMeta(name=name, description=description, path=Path())


def extract_skill_metas(skills_dir: Path) -> list[SkillMeta]:
    """扫描 skills_dir 下所有子目录的 SKILL.md，提取元数据。"""
    metas: list[SkillMeta] = []
    if not skills_dir.is_dir():
        return metas

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        try:
            content = skill_md.read_text(encoding="utf-8")
        except OSError:
            continue
        meta = parse_skill_frontmatter(content)
        if meta is None:
            continue
        # 使用 frozen dataclass 的替换方式：创建新实例
        metas.append(
            SkillMeta(name=meta.name, description=meta.description, path=skill_md)
        )

    return metas


def parse_submodules(gitmodules_path: Path) -> list[SubmoduleEntry]:
    """从 .gitmodules 文件解析 submodule 列表。"""
    if not gitmodules_path.is_file():
        return []

    content = gitmodules_path.read_text(encoding="utf-8")
    entries: list[SubmoduleEntry] = []

    for block in re.split(r"(?=\[submodule )", content):
        block = block.strip()
        if not block.startswith("[submodule"):
            continue
        name_match = re.search(r'\[submodule "([^"]+)"\]', block)
        path_match = re.search(r"^\s*path\s*=\s*(.+)$", block, re.MULTILINE)
        url_match = re.search(r"^\s*url\s*=\s*(.+)$", block, re.MULTILINE)
        if name_match and path_match and url_match:
            entries.append(
                SubmoduleEntry(
                    name=name_match.group(1),
                    path=path_match.group(1).strip(),
                    url=url_match.group(1).strip(),
                )
            )

    return entries


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


def estimate_tokens(text: str) -> int:
    """粗略估算文本的 token 数。

    中文字符约 1 token/字符，英文约 4 字符/token。
    """
    if not text:
        return 0
    chinese_chars = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    other_chars = len(text) - chinese_chars
    return max(
        1, int(chinese_chars / _CHARS_PER_TOKEN_ZH + other_chars / _CHARS_PER_TOKEN_EN)
    )


def count_lines(file_path: Path) -> int:
    """统计文件行数，出错返回 0。"""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        return len(content.splitlines()) or (1 if not content else 0)
    except OSError:
        return 0


def compute_diff_ratio(old_text: str, new_text: str) -> float:
    """计算两个文本之间的差异比例（0.0 ~ 1.0）。"""
    if not old_text and not new_text:
        return 0.0
    if not old_text or not new_text:
        return 1.0

    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    diff = list(difflib.unified_diff(old_lines, new_lines, n=0))
    changed = sum(
        1
        for line in diff
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    )
    total = max(len(old_lines), len(new_lines))
    return changed / total if total > 0 else 0.0


def show_diff_summary(old_text: str, new_text: str, file_name: str) -> None:
    """显示差异摘要。"""
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    diff = list(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{file_name} (old)",
            tofile=f"{file_name} (new)",
        )
    )
    # 显示前 50 行 diff
    for line in diff[:50]:
        print(line, end="")
    if len(diff) > 50:
        print(f"  ... (共 {len(diff)} 行差异)")


# ---------------------------------------------------------------------------
# Markdown 生成
# ---------------------------------------------------------------------------

_TODAY = date.today().isoformat()


def _metadata_header(file_count: int, token_est: int) -> str:
    return f"<!-- 生成时间: {_TODAY} | 扫描文件: {file_count} | Token 估算: ~{token_est} -->"


def _build_area_tree(area: AreaInfo, root: Path, max_depth: int = 2) -> str:
    """为区域构建 ASCII 目录树（最大深度 max_depth）。"""
    dirs_with_files: dict[str, list[str]] = {}
    for f in area.files:
        rel = f.relative_to(root).as_posix()
        parts = rel.split("/")
        if len(parts) > 1:
            dir_key = "/".join(parts[:-1])
        else:
            dir_key = "."
        dirs_with_files.setdefault(dir_key, []).append(parts[-1])

    lines: list[str] = []
    sorted_dirs = sorted(dirs_with_files.keys())
    for i, d in enumerate(sorted_dirs):
        prefix = "└── " if i == len(sorted_dirs) - 1 else "├── "
        lines.append(f"{prefix}{d}/")
        files = sorted(dirs_with_files[d])
        for j, fname in enumerate(files[:8]):
            fp = "    " if i == len(sorted_dirs) - 1 else "│   "
            fc = "└── " if j == len(files[:8]) - 1 and j >= len(files) - 8 else "├── "
            lines.append(f"{fp}{fc}{fname}")
        if len(files) > 8:
            fp = "    " if i == len(sorted_dirs) - 1 else "│   "
            lines.append(f"{fp}    ... (+{len(files) - 8} more)")

    return "\n".join(lines)


def generate_index(
    areas: dict[str, AreaInfo],
    all_files: list[Path],
    submodules: list[SubmoduleEntry],
    total_tokens: int,
) -> str:
    """生成 INDEX.md。"""
    total_files = len(all_files)
    header = _metadata_header(total_files, total_tokens)

    area_rows: list[str] = []
    for key in ("skills", "cli", "agents", "docs", "scripts"):
        area = areas.get(key)
        if area is None:
            continue
        dirs_str = ", ".join(f"`{d}`" for d in area.directories[:3]) or "—"
        area_rows.append(
            f"| [{area.name}](./{key}.md) | {len(area.files)} files | {dirs_str} |"
        )

    area_table = "\n".join(area_rows) if area_rows else "| — | — | — |"

    sub_section = ""
    if submodules:
        sub_rows = [
            f"| `{s.name}` | `{s.path}` | [link]({s.url}) |" for s in submodules
        ]
        sub_section = (
            "\n## Upstream Submodules\n"
            "\n| Name | Path | URL |\n|------|------|-----|\n" + "\n".join(sub_rows)
        )

    return f"""\
{header}

# Codemap Index

**生成日期:** {_TODAY}
**扫描文件:** {total_files}
**Token 估算:** ~{total_tokens}

## Areas

| Area | Size | Key Directories |
|------|------|-----------------|
{area_table}
{sub_section}

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
"""


def generate_skills_codemap(metas: list[SkillMeta]) -> str:
    """生成 skills.md。"""
    token_est = (
        estimate_tokens(" ".join(f"{m.name} {m.description}" for m in metas))
        if metas
        else 0
    )
    header = _metadata_header(len(metas), token_est)

    if not metas:
        return f"{header}\n\n# Skills Codemap\n\n_No skills found._\n"

    # 按前缀分组
    groups: dict[str, list[SkillMeta]] = {}
    for m in metas:
        prefix = m.name.split("-", 1)[0] if "-" in m.name else "other"
        groups.setdefault(prefix, []).append(m)

    group_stats: list[str] = []
    for prefix in sorted(groups.keys()):
        group_stats.append(f"| `{prefix}-` | {len(groups[prefix])} |")

    group_table = "\n".join(group_stats)

    skill_rows: list[str] = []
    for m in metas:
        desc_preview = (
            (m.description[:80] + "...") if len(m.description) > 80 else m.description
        )
        skill_rows.append(f"| `{m.name}` | {desc_preview} |")

    skill_table = "\n".join(skill_rows)

    return f"""\
{header}

# Skills Codemap

**Total Skills:** {len(metas)}
**Prefix Groups:** {len(groups)}

## 按前缀分组

| Prefix | Count |
|--------|-------|
{group_table}

## Skill 清单

| Name | Description |
|------|-------------|
{skill_table}
"""


def generate_cli_codemap(area: AreaInfo) -> str:
    """生成 cli.md。"""
    file_count = len(area.files)
    token_est = sum(count_lines(f) for f in area.files) // 4
    header = _metadata_header(file_count, token_est)

    # 构建文件表
    file_rows: list[str] = []
    for f in sorted(area.files):
        name = f.name
        lines = count_lines(f)
        file_rows.append(f"| `{name}` | {lines} |")
    file_table = "\n".join(file_rows) if file_rows else "| — | — |"

    return f"""\
{header}

# CLI Codemap

**文件数:** {file_count}

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
{file_table}

## 相关

- [INDEX](./INDEX.md) — 总览
- `install_skills/models.py` — frozen dataclass 定义
"""


def generate_generic_codemap(
    area_key: str,
    area: AreaInfo,
    root: Path | None = None,
) -> str:
    """生成通用区域 codemap（agents/docs/scripts）。"""
    file_count = len(area.files)
    token_est = sum(count_lines(f) for f in area.files) // 4
    header = _metadata_header(file_count, token_est)
    label = area.name if area.name else AREA_LABELS.get(area_key, area_key)

    if not area.files:
        return f"{header}\n\n# {label} Codemap\n\n_No files found in this area._\n"

    # 文件表（最多 40 条）
    file_rows: list[str] = []
    for f in sorted(area.files)[:40]:
        if root is not None:
            try:
                rel_name = f.relative_to(root).as_posix()
            except ValueError:
                rel_name = str(f)
        else:
            rel_name = f.name
        lines = count_lines(f)
        file_rows.append(f"| `{rel_name}` | {lines} |")
    more = f"\n*...+{len(area.files) - 40} more*" if len(area.files) > 40 else ""
    file_table = "\n".join(file_rows)

    # 目录树
    tree_lines = area.directories[:10]
    tree = "\n".join(f"- `{d}/`" for d in tree_lines)

    return f"""\
{header}

# {label} Codemap

**文件数:** {file_count}

## 目录

{tree}

## 文件清单

| File | Lines |
|------|-------|
{file_table}{more}

## 相关

- [INDEX](./INDEX.md) — 总览
"""


# ---------------------------------------------------------------------------
# 写入与差异检测
# ---------------------------------------------------------------------------


def write_codemap(
    output_dir: Path,
    filename: str,
    content: str,
    *,
    force: bool = False,
) -> bool:
    """写入 codemap 文件。返回 True 表示成功写入。

    如果已有文件差异 >30%，且非 force 模式，显示差异并返回 False。
    """
    target = output_dir / filename
    if target.exists() and not force:
        old_content = target.read_text(encoding="utf-8")
        ratio = compute_diff_ratio(old_content, content)
        if ratio > _DIFF_THRESHOLD:
            print(f"\n[WARN] {filename} 变更比例 {ratio:.0%} > {_DIFF_THRESHOLD:.0%}")
            show_diff_summary(old_content, content, filename)
            print(f"\n使用 --force 覆盖，或手动检查 {target}")
            return False

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# 扫描入口
# ---------------------------------------------------------------------------


def run_scan(repo_root: Path) -> ScanResult:
    """执行完整扫描，返回 ScanResult。"""
    all_files = walk_files(repo_root)
    areas = classify_all(all_files, repo_root)

    # 提取 skill 元数据
    skills_dir = repo_root / "skills"
    metas = extract_skill_metas(skills_dir)

    # 解析 submodules
    gitmodules = repo_root / ".gitmodules"
    submodules = parse_submodules(gitmodules)

    # 生成 markdown
    total_tokens = 0
    markdowns: dict[str, str] = {}

    index_md = generate_index(areas, all_files, submodules, 0)
    markdowns["index"] = index_md
    total_tokens += estimate_tokens(index_md)

    skills_md = generate_skills_codemap(metas)
    markdowns["skills"] = skills_md
    total_tokens += estimate_tokens(skills_md)

    if "cli" in areas:
        cli_md = generate_cli_codemap(areas["cli"])
        markdowns["cli"] = cli_md
        total_tokens += estimate_tokens(cli_md)

    for key in ("agents", "docs", "scripts"):
        if key in areas:
            md = generate_generic_codemap(key, areas[key], root=repo_root)
            markdowns[key] = md
            total_tokens += estimate_tokens(md)

    # 重新生成 index 带正确的 token 估算
    markdowns["index"] = generate_index(areas, all_files, submodules, total_tokens)

    return ScanResult(
        areas=areas,
        metas=metas,
        submodules=submodules,
        markdowns=markdowns,
        total_tokens=total_tokens,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="扫描 coding-everything 仓库并生成 codemap 文档。",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="跳过差异确认，直接覆盖。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅扫描并输出到 stdout，不写入文件。",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="仓库根目录路径。默认为当前目录。",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """主入口。"""
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()

    if not (repo_root / ".git").exists() and not (repo_root / "CLAUDE.md").exists():
        print(f"[ERROR] 看起来不是仓库根目录: {repo_root}", file=sys.stderr)
        return 1

    print(f"[codemaps] 扫描: {repo_root}")

    result = run_scan(repo_root)

    print(f"[codemaps] 扫描到 {sum(len(a.files) for a in result.areas.values())} 文件")
    print(f"[codemaps] Skill: {len(result.metas)} 个")
    print(f"[codemaps] Submodule: {len(result.submodules)} 个")
    print(f"[codemaps] Token 估算: ~{result.total_tokens}")

    if args.dry_run:
        print("\n--- INDEX.md ---")
        print(result.markdowns.get("index", ""))
        for key, md in result.markdowns.items():
            if key != "index":
                print(f"\n--- {key}.md ---")
                print(md)
        return 0

    output_dir = repo_root / "docs" / "CODEMAPS"
    filename_map: dict[str, str] = {
        "index": "INDEX.md",
        "skills": "skills.md",
        "cli": "cli.md",
        "agents": "agents.md",
        "docs": "docs.md",
        "scripts": "scripts.md",
    }

    skipped: list[str] = []
    for key, filename in filename_map.items():
        content = result.markdowns.get(key)
        if content is None:
            continue
        ok = write_codemap(output_dir, filename, content, force=args.force)
        if ok:
            print(f"[codemaps] 写入: {filename}")
        else:
            skipped.append(filename)

    if skipped:
        print("\n[WARN] 以下文件因差异过大未覆盖（使用 --force 跳过确认）:")
        for s in skipped:
            print(f"  - {s}")
        return 1

    print("\n[codemaps] 完成！文档已写入 docs/CODEMAPS/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
