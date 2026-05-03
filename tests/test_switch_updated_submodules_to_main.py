from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def load_script() -> ModuleType:
    path = (
        Path(__file__).resolve().parents[1]
        / ".agents"
        / "skills"
        / "update-upstream-repos"
        / "scripts"
        / "switch_updated_submodules_to_main.py"
    )
    spec = importlib.util.spec_from_file_location("switch_updated_submodules_to_main", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_parse_all_upstream_submodules_includes_initialized_unchanged_paths(
    monkeypatch,
    tmp_path: Path,
) -> None:
    script = load_script()
    repo_root = tmp_path
    (repo_root / "upstream" / "changed" / ".git").mkdir(parents=True)
    (repo_root / "upstream" / "unchanged" / ".git").mkdir(parents=True)
    (repo_root / "other" / "ignored" / ".git").mkdir(parents=True)

    def fake_run_git(args: list[str], cwd: Path) -> str:
        if args[:4] == ["config", "--file", ".gitmodules", "--get-regexp"]:
            return "\n".join(
                [
                    "submodule.upstream/changed.path upstream/changed",
                    "submodule.upstream/unchanged.path upstream/unchanged",
                    "submodule.other/ignored.path other/ignored",
                    "submodule.upstream/not-initialized.path upstream/not-initialized",
                ]
            )
        if args == ["rev-parse", "HEAD"] and cwd == repo_root / "upstream" / "changed":
            return "changed-sha"
        if args == ["rev-parse", "HEAD"] and cwd == repo_root / "upstream" / "unchanged":
            return "unchanged-sha"
        raise AssertionError(f"unexpected git call: {args} cwd={cwd}")

    monkeypatch.setattr(script, "run_git", fake_run_git)

    targets = script.parse_all_upstream_submodules(repo_root)

    assert targets == [
        script.SubmoduleTarget(path="upstream/changed", target_sha="changed-sha"),
        script.SubmoduleTarget(path="upstream/unchanged", target_sha="unchanged-sha"),
    ]


def test_changed_only_parser_still_filters_gitlink_diffs(
    monkeypatch,
    tmp_path: Path,
) -> None:
    script = load_script()
    repo_root = tmp_path
    (repo_root / "upstream" / "changed" / ".git").mkdir(parents=True)

    def fake_run_git(args: list[str], cwd: Path) -> str:
        if args == ["diff", "--raw", "HEAD", "--"]:
            return ":160000 160000 old new M\tupstream/changed\n:100644 100644 old new M\tREADME.md"
        if args == ["rev-parse", "HEAD"] and cwd == repo_root / "upstream" / "changed":
            return "changed-sha"
        raise AssertionError(f"unexpected git call: {args} cwd={cwd}")

    monkeypatch.setattr(script, "run_git", fake_run_git)

    targets = script.parse_changed_submodules(repo_root, "HEAD")

    assert targets == [script.SubmoduleTarget(path="upstream/changed", target_sha="changed-sha")]
