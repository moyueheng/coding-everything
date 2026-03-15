#!/usr/bin/env python3
"""
Validate the update-upstream-repos skill without external Python dependencies.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/report-template.md",
    "scripts/generate_upstream_report.py",
]


def fail(message: str) -> int:
    print(f"[ERROR] {message}", file=sys.stderr)
    return 1


def parse_frontmatter(skill_md: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", skill_md, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md 缺少合法 frontmatter")

    data: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        if ":" not in raw_line:
            raise ValueError(f"frontmatter 行格式错误: {raw_line}")
        key, value = raw_line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def validate_openai_yaml(content: str) -> None:
    if not content.startswith("interface:\n"):
        raise ValueError("agents/openai.yaml 缺少 interface 顶层键")
    required_keys = ["display_name:", "short_description:", "default_prompt:"]
    for key in required_keys:
        if key not in content:
            raise ValueError(f"agents/openai.yaml 缺少 {key}")


def main() -> int:
    skill_dir = Path(__file__).resolve().parents[1]

    for rel_path in REQUIRED_FILES:
        path = skill_dir / rel_path
        if not path.exists():
            return fail(f"缺少文件: {path}")

    skill_md_path = skill_dir / "SKILL.md"
    skill_md = skill_md_path.read_text()
    if "[TODO:" in skill_md:
        return fail("SKILL.md 仍包含 TODO")

    try:
        frontmatter = parse_frontmatter(skill_md)
    except ValueError as exc:
        return fail(str(exc))

    if frontmatter.get("name") != "update-upstream-repos":
        return fail("frontmatter.name 必须是 update-upstream-repos")
    if not frontmatter.get("description"):
        return fail("frontmatter.description 不能为空")

    openai_yaml = (skill_dir / "agents/openai.yaml").read_text()
    try:
        validate_openai_yaml(openai_yaml)
    except ValueError as exc:
        return fail(str(exc))

    report_template = (skill_dir / "references/report-template.md").read_text()
    if "值得关注" not in report_template or "更新范围" not in report_template:
        return fail("报告模板缺少关键章节")

    generate_script = (skill_dir / "scripts/generate_upstream_report.py").read_text()
    if "--range" not in generate_script or "--output" not in generate_script:
        return fail("generate_upstream_report.py 缺少关键参数支持")

    print("[OK] update-upstream-repos skill 校验通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
