from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import install_skills


class InstallSkillsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.repo_root = root / "repo"
        self.home = root / "home"
        (self.repo_root / "skills").mkdir(parents=True)
        for skill in ("alpha-skill", "beta-skill"):
            skill_dir = self.repo_root / "skills" / skill
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")
        kimi_agent = self.repo_root / "kimi/agents/superpower"
        kimi_agent.mkdir(parents=True)
        (kimi_agent / "agent.yaml").write_text("name: superpower\n", encoding="utf-8")
        ks = self.repo_root / "ks"
        ks.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_command(self, command: str) -> int:
        return install_skills.main(
            [command],
            repo_root=self.repo_root,
            home=self.home,
            stdout=self.stdout,
            stderr=self.stderr,
        )

    def manifest_path(self) -> Path:
        return self.home / ".local/share/coding-everything/install-manifest.json"

    def test_install_creates_skill_links_kimi_agent_ks_and_manifest(self) -> None:
        code = self.run_command("install")
        self.assertEqual(code, 0)

        for skill in ("alpha-skill", "beta-skill"):
            agents_link = self.home / ".agents/skills" / skill
            claude_link = self.home / ".claude/skills" / skill
            self.assertTrue(agents_link.is_symlink())
            self.assertEqual(agents_link.resolve(), (self.repo_root / "skills" / skill).resolve())
            self.assertTrue(claude_link.is_symlink())
            self.assertEqual(claude_link.resolve(), (self.repo_root / "skills" / skill).resolve())

        kimi_link = self.home / ".kimi/agents/superpower"
        ks_link = self.home / ".local/bin/ks"
        self.assertTrue(kimi_link.is_symlink())
        self.assertEqual(kimi_link.resolve(), (self.repo_root / "kimi/agents/superpower").resolve())
        self.assertTrue(ks_link.is_symlink())
        self.assertEqual(ks_link.resolve(), (self.repo_root / "ks").resolve())

        manifest = json.loads(self.manifest_path().read_text(encoding="utf-8"))
        self.assertEqual(manifest["skills"], ["alpha-skill", "beta-skill"])

    def test_update_repairs_missing_and_drifted_entries(self) -> None:
        self.run_command("install")
        missing_link = self.home / ".agents/skills" / "alpha-skill"
        drifted_link = self.home / ".claude/skills" / "beta-skill"
        missing_link.unlink()
        drifted_link.unlink()
        replacement = self.home / "replacement"
        replacement.mkdir(parents=True)
        drifted_link.symlink_to(replacement)

        code = self.run_command("update")
        self.assertEqual(code, 0)
        self.assertEqual(missing_link.resolve(), (self.repo_root / "skills" / "alpha-skill").resolve())
        self.assertEqual(drifted_link.resolve(), (self.repo_root / "skills" / "beta-skill").resolve())

    def test_update_without_manifest_falls_back_to_install(self) -> None:
        code = self.run_command("update")
        self.assertEqual(code, 0)
        self.assertTrue(self.manifest_path().exists())
        self.assertIn("manifest missing; running install", self.stdout.getvalue())

    def test_status_reports_install_state(self) -> None:
        self.run_command("install")
        (self.home / ".agents/skills" / "alpha-skill").unlink()
        drifted_link = self.home / ".claude/skills" / "beta-skill"
        drifted_link.unlink()
        drifted_target = self.home / "other"
        drifted_target.mkdir()
        drifted_link.symlink_to(drifted_target)
        gamma_dir = self.repo_root / "skills" / "gamma-skill"
        gamma_dir.mkdir()
        (gamma_dir / "SKILL.md").write_text("# gamma\n", encoding="utf-8")

        self.stdout = io.StringIO()
        code = self.run_command("status")
        self.assertEqual(code, 0)
        output = self.stdout.getvalue()
        self.assertIn("missing=", output)
        self.assertIn(".agents/skills/alpha-skill", output)
        self.assertIn("drifted=", output)
        self.assertIn(".claude/skills/beta-skill", output)
        self.assertIn("untracked_new_skills=gamma-skill", output)

    def test_install_ignores_directories_without_skill_md(self) -> None:
        ignored_dir = self.repo_root / "skills" / "not-a-skill"
        ignored_dir.mkdir()
        (ignored_dir / "README.md").write_text("ignore me\n", encoding="utf-8")

        code = self.run_command("install")
        self.assertEqual(code, 0)
        self.assertFalse((self.home / ".agents/skills" / "not-a-skill").exists())
        self.assertFalse((self.home / ".claude/skills" / "not-a-skill").exists())

        manifest = json.loads(self.manifest_path().read_text(encoding="utf-8"))
        self.assertNotIn("not-a-skill", manifest["skills"])

    def test_uninstall_removes_only_manifest_managed_entries(self) -> None:
        self.run_command("install")
        third_party_agents = self.home / ".agents/skills" / "third-party"
        third_party_claude = self.home / ".claude/skills" / "third-party"
        third_party_agents.parent.mkdir(parents=True, exist_ok=True)
        third_party_claude.parent.mkdir(parents=True, exist_ok=True)
        third_party_agents.mkdir()
        third_party_claude.mkdir()

        code = self.run_command("uninstall")
        self.assertEqual(code, 0)
        self.assertFalse((self.home / ".agents/skills" / "alpha-skill").exists())
        self.assertFalse((self.home / ".claude/skills" / "beta-skill").exists())
        self.assertTrue(third_party_agents.exists())
        self.assertTrue(third_party_claude.exists())
        self.assertFalse((self.home / ".kimi/agents/superpower").exists())
        self.assertFalse((self.home / ".local/bin/ks").exists())
        self.assertFalse(self.manifest_path().exists())

    def test_uninstall_refuses_when_manifest_is_missing(self) -> None:
        code = self.run_command("uninstall")
        self.assertEqual(code, 1)
        self.assertIn("manifest missing; refusing uninstall", self.stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
