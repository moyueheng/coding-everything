from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from install_skills import cli, installer


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
        self._create_mcp_required_json()
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()

    def _create_mcp_required_json(self) -> None:
        mcp_dir = self.repo_root / "mcp-configs"
        mcp_dir.mkdir(parents=True, exist_ok=True)
        (mcp_dir / "required.json").write_text(
            json.dumps(
                {
                    "mcpServers": {
                        "auggie-mcp": {
                            "command": "auggie",
                            "args": ["--mcp"],
                            "type": "stdio",
                        }
                    }
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_command(self, command: str) -> int:
        return installer.main(
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
            self.assertEqual(
                agents_link.resolve(), (self.repo_root / "skills" / skill).resolve()
            )
            self.assertTrue(claude_link.is_symlink())
            self.assertEqual(
                claude_link.resolve(), (self.repo_root / "skills" / skill).resolve()
            )

        kimi_link = self.home / ".kimi/agents/superpower"
        ks_link = self.home / ".local/bin/ks"
        self.assertTrue(kimi_link.is_symlink())
        self.assertEqual(
            kimi_link.resolve(), (self.repo_root / "kimi/agents/superpower").resolve()
        )
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
        self.assertEqual(
            missing_link.resolve(),
            (self.repo_root / "skills" / "alpha-skill").resolve(),
        )
        self.assertEqual(
            drifted_link.resolve(), (self.repo_root / "skills" / "beta-skill").resolve()
        )

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
        self.assertIn("alpha-skill", output)
        self.assertNotIn(".agents/skills/alpha-skill", output)
        self.assertIn("drifted=", output)
        self.assertIn("beta-skill", output)
        self.assertNotIn(".claude/skills/beta-skill", output)
        self.assertIn("untracked_new_skills=gamma-skill", output)

    def test_discover_skills_ignores_self_referencing_symlink(self) -> None:
        skills_dir = self.repo_root / "skills"
        (skills_dir / "skills").symlink_to(skills_dir)

        discovered = installer.discover_skills(self.repo_root)
        self.assertNotIn("skills", discovered)

    def test_discover_skills_ignores_self_referencing_symlink_even_with_skill_md(
        self,
    ) -> None:
        skills_dir = self.repo_root / "skills"
        (skills_dir / "skills").symlink_to(skills_dir)
        (skills_dir / "SKILL.md").write_text("# skills root\n", encoding="utf-8")

        discovered = installer.discover_skills(self.repo_root)
        self.assertNotIn("skills", discovered)

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

    def test_install_writes_mcp_servers_to_manifest(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            code = self.run_command("install")
        self.assertEqual(code, 0)
        manifest = json.loads(self.manifest_path().read_text(encoding="utf-8"))
        self.assertIn("mcp_servers", manifest)
        self.assertEqual(manifest["mcp_servers"], ["auggie-mcp"])

    def test_install_outputs_mcp_result(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            code = self.run_command("install")
        self.assertEqual(code, 0)
        output = self.stdout.getvalue()
        self.assertIn("mcp_servers=", output)
        self.assertIn("auggie-mcp", output)

    def test_install_merges_mcp_into_claude_json(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            code = self.run_command("install")
        self.assertEqual(code, 0)
        claude_json_path = self.home / ".claude.json"
        self.assertTrue(claude_json_path.exists())
        config = json.loads(claude_json_path.read_text(encoding="utf-8"))
        self.assertIn("auggie-mcp", config["mcpServers"])

    def test_update_writes_mcp_servers_to_manifest(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            self.run_command("install")
        self.stdout = io.StringIO()
        with mock.patch.dict("os.environ", {}, clear=True):
            code = self.run_command("update")
        self.assertEqual(code, 0)
        manifest = json.loads(self.manifest_path().read_text(encoding="utf-8"))
        self.assertIn("mcp_servers", manifest)
        self.assertEqual(manifest["mcp_servers"], ["auggie-mcp"])

    def test_update_outputs_mcp_result(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            self.run_command("install")
        self.stdout = io.StringIO()
        with mock.patch.dict("os.environ", {}, clear=True):
            code = self.run_command("update")
        self.assertEqual(code, 0)
        output = self.stdout.getvalue()
        self.assertIn("mcp_servers=", output)
        self.assertIn("auggie-mcp", output)

    def test_uninstall_removes_managed_mcp_servers(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            self.run_command("install")
        claude_json_path = self.home / ".claude.json"
        config = json.loads(claude_json_path.read_text(encoding="utf-8"))
        self.assertIn("auggie-mcp", config["mcpServers"])

        code = self.run_command("uninstall")
        self.assertEqual(code, 0)
        config = json.loads(claude_json_path.read_text(encoding="utf-8"))
        self.assertNotIn("auggie-mcp", config["mcpServers"])

    def test_uninstall_preserves_user_mcp_servers(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            self.run_command("install")
        claude_json_path = self.home / ".claude.json"
        config = json.loads(claude_json_path.read_text(encoding="utf-8"))
        config["mcpServers"]["user-custom"] = {
            "type": "http",
            "url": "https://user.com",
        }
        claude_json_path.write_text(json.dumps(config), encoding="utf-8")

        code = self.run_command("uninstall")
        self.assertEqual(code, 0)
        config = json.loads(claude_json_path.read_text(encoding="utf-8"))
        self.assertNotIn("auggie-mcp", config["mcpServers"])
        self.assertIn("user-custom", config["mcpServers"])

    def test_status_outputs_mcp_state(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            self.run_command("install")
        self.stdout = io.StringIO()
        with mock.patch.dict("os.environ", {}, clear=True):
            code = self.run_command("status")
        self.assertEqual(code, 0)
        output = self.stdout.getvalue()
        self.assertIn("mcp_configured=", output)
        self.assertIn("auggie-mcp", output)

    def test_status_outputs_mcp_missing_when_not_installed(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            self.run_command("install")
        claude_json_path = self.home / ".claude.json"
        config = json.loads(claude_json_path.read_text(encoding="utf-8"))
        del config["mcpServers"]["auggie-mcp"]
        claude_json_path.write_text(json.dumps(config), encoding="utf-8")

        self.stdout = io.StringIO()
        with mock.patch.dict("os.environ", {}, clear=True):
            code = self.run_command("status")
        self.assertEqual(code, 0)
        output = self.stdout.getvalue()
        self.assertIn("mcp_missing=", output)
        self.assertIn("auggie-mcp", output)


class ManifestPayloadMcpTest(unittest.TestCase):
    def test_manifest_payload_includes_mcp_servers(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        repo_root = root / "repo"
        home = root / "home"
        targets = installer.build_targets(home)
        result = installer.manifest_payload(
            repo_root, targets, ["skill-a"], mcp_servers=["mcp-1", "mcp-2"]
        )
        self.assertIn("mcp_servers", result)
        self.assertEqual(result["mcp_servers"], ["mcp-1", "mcp-2"])

    def test_manifest_payload_defaults_mcp_servers_to_empty(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        repo_root = root / "repo"
        home = root / "home"
        targets = installer.build_targets(home)
        result = installer.manifest_payload(repo_root, targets, ["skill-a"])
        self.assertIn("mcp_servers", result)
        self.assertEqual(result["mcp_servers"], [])


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
            json.dumps(
                {
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
                }
            ),
            encoding="utf-8",
        )

    def test_load_mcp_template_returns_parsed_json(self) -> None:
        self._create_required_json()
        result = installer.load_mcp_template(self.repo_root)
        self.assertIn("mcpServers", result)
        self.assertIn("auggie-mcp", result["mcpServers"])
        self.assertIn("zai-github-read", result["mcpServers"])

    def test_load_mcp_template_raises_when_file_missing(self) -> None:
        with self.assertRaises(FileNotFoundError):
            installer.load_mcp_template(self.repo_root)

    def test_resolve_zai_api_key_from_existing_config(self) -> None:
        claude_config = {
            "mcpServers": {
                "zai-github-read": {
                    "headers": {"Authorization": "Bearer my-token-123"},
                }
            }
        }
        result = installer.resolve_zai_api_key(claude_config)
        self.assertEqual(result, "my-token-123")

    def test_resolve_zai_api_key_from_env_var(self) -> None:
        claude_config = {"mcpServers": {}}
        with mock.patch.dict("os.environ", {"ZAI_API_KEY": "env-token-456"}):
            result = installer.resolve_zai_api_key(claude_config)
            self.assertEqual(result, "env-token-456")

    def test_resolve_zai_api_key_returns_none_when_unavailable(self) -> None:
        claude_config = {"mcpServers": {}}
        with mock.patch.dict("os.environ", {}, clear=True):
            result = installer.resolve_zai_api_key(claude_config)
            self.assertIsNone(result)

    def test_resolve_zai_api_key_prefers_existing_over_env(self) -> None:
        claude_config = {
            "mcpServers": {
                "zai-web-reader": {
                    "headers": {"Authorization": "Bearer config-token"},
                }
            }
        }
        with mock.patch.dict("os.environ", {"ZAI_API_KEY": "env-token"}):
            result = installer.resolve_zai_api_key(claude_config)
            self.assertEqual(result, "config-token")


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
        self._write_required_json(
            {
                "auggie-mcp": {
                    "command": "auggie",
                    "args": ["--mcp"],
                    "type": "stdio",
                    "_install_note": "reminder",
                }
            }
        )
        self._write_claude_json({"mcpServers": {}})

        installed = installer.merge_mcp_config(self.home, self.repo_root)

        self.assertEqual(installed, ["auggie-mcp"])
        config = self._read_claude_json()
        mcp = config["mcpServers"]["auggie-mcp"]
        self.assertEqual(mcp["command"], "auggie")
        self.assertEqual(mcp["type"], "stdio")
        self.assertNotIn("_install_note", mcp)

    def test_merge_substitutes_zai_api_key(self) -> None:
        self._write_required_json(
            {
                "zai-github-read": {
                    "type": "http",
                    "url": "https://example.com/mcp",
                    "headers": {"Authorization": "Bearer {{ZAI_API_KEY}}"},
                }
            }
        )
        self._write_claude_json({"mcpServers": {}})

        with unittest.mock.patch.dict("os.environ", {"ZAI_API_KEY": "test-key"}):
            installed = installer.merge_mcp_config(self.home, self.repo_root)

        self.assertEqual(installed, ["zai-github-read"])
        config = self._read_claude_json()
        self.assertEqual(
            config["mcpServers"]["zai-github-read"]["headers"]["Authorization"],
            "Bearer test-key",
        )

    def test_merge_skips_zai_when_no_api_key(self) -> None:
        self._write_required_json(
            {
                "zai-github-read": {
                    "type": "http",
                    "url": "https://example.com/mcp",
                    "headers": {"Authorization": "Bearer {{ZAI_API_KEY}}"},
                }
            }
        )
        self._write_claude_json({"mcpServers": {}})

        with unittest.mock.patch.dict("os.environ", {}, clear=True):
            installed = installer.merge_mcp_config(self.home, self.repo_root)

        self.assertEqual(installed, [])
        config = self._read_claude_json()
        self.assertNotIn("zai-github-read", config["mcpServers"])

    def test_merge_preserves_existing_mcp_servers(self) -> None:
        self._write_required_json(
            {
                "auggie-mcp": {
                    "command": "auggie",
                    "args": ["--mcp"],
                    "type": "stdio",
                }
            }
        )
        self._write_claude_json(
            {
                "mcpServers": {
                    "user-custom": {"type": "http", "url": "https://user.com/mcp"}
                }
            }
        )

        installer.merge_mcp_config(self.home, self.repo_root)

        config = self._read_claude_json()
        self.assertIn("user-custom", config["mcpServers"])
        self.assertIn("auggie-mcp", config["mcpServers"])

    def test_merge_creates_claude_json_when_missing(self) -> None:
        self._write_required_json(
            {
                "auggie-mcp": {
                    "command": "auggie",
                    "args": ["--mcp"],
                    "type": "stdio",
                }
            }
        )
        self.home.mkdir(parents=True, exist_ok=True)

        installed = installer.merge_mcp_config(self.home, self.repo_root)

        self.assertEqual(installed, ["auggie-mcp"])
        self.assertTrue(self.claude_json.exists())
        config = self._read_claude_json()
        self.assertIn("auggie-mcp", config["mcpServers"])

    def test_merge_is_idempotent(self) -> None:
        self._write_required_json(
            {
                "auggie-mcp": {
                    "command": "auggie",
                    "args": ["--mcp"],
                    "type": "stdio",
                }
            }
        )
        self._write_claude_json({"mcpServers": {}})

        installer.merge_mcp_config(self.home, self.repo_root)
        installer.merge_mcp_config(self.home, self.repo_root)

        config = self._read_claude_json()
        self.assertEqual(len(config["mcpServers"]), 1)


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
        self._write_claude_json(
            {
                "auggie-mcp": {"type": "stdio", "command": "auggie"},
                "user-custom": {"type": "http", "url": "https://user.com/mcp"},
            }
        )
        installer.remove_managed_mcps(self.home, ["auggie-mcp"])
        config = self._read_claude_json()
        self.assertNotIn("auggie-mcp", config["mcpServers"])
        self.assertIn("user-custom", config["mcpServers"])

    def test_noop_when_claude_json_missing(self) -> None:
        self.home.mkdir(parents=True, exist_ok=True)
        installer.remove_managed_mcps(self.home, ["auggie-mcp"])
        self.assertFalse(self.claude_json.exists())

    def test_removes_empty_mcp_servers_key(self) -> None:
        self._write_claude_json(
            {
                "auggie-mcp": {"type": "stdio", "command": "auggie"},
            }
        )
        installer.remove_managed_mcps(self.home, ["auggie-mcp"])
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
        self._write_required_json(
            {
                "auggie-mcp": {"type": "stdio", "command": "auggie"},
                "zai-github-read": {
                    "type": "http",
                    "url": "https://example.com",
                    "headers": {"Authorization": "Bearer {{ZAI_API_KEY}}"},
                },
            }
        )
        self._write_claude_json(
            {
                "auggie-mcp": {"type": "stdio", "command": "auggie"},
                "zai-github-read": {
                    "type": "http",
                    "url": "https://example.com",
                    "headers": {"Authorization": "Bearer real-key"},
                },
            }
        )
        status = installer.collect_mcp_status(self.home, self.repo_root)
        self.assertEqual(status["configured"], ["auggie-mcp", "zai-github-read"])
        self.assertEqual(status["missing"], [])

    def test_partial_configured(self) -> None:
        self._write_required_json(
            {
                "auggie-mcp": {"type": "stdio", "command": "auggie"},
                "zai-github-read": {
                    "type": "http",
                    "url": "https://example.com",
                    "headers": {"Authorization": "Bearer {{ZAI_API_KEY}}"},
                },
            }
        )
        self._write_claude_json(
            {
                "auggie-mcp": {"type": "stdio", "command": "auggie"},
            }
        )
        status = installer.collect_mcp_status(self.home, self.repo_root)
        self.assertEqual(status["configured"], ["auggie-mcp"])
        self.assertEqual(status["missing"], ["zai-github-read"])

    def test_no_claude_json(self) -> None:
        self._write_required_json(
            {
                "auggie-mcp": {"type": "stdio", "command": "auggie"},
            }
        )
        self.home.mkdir(parents=True, exist_ok=True)
        status = installer.collect_mcp_status(self.home, self.repo_root)
        self.assertEqual(status["configured"], [])
        self.assertEqual(status["missing"], ["auggie-mcp"])


class CliArgParseTest(unittest.TestCase):
    def test_parse_install_command(self) -> None:
        args = cli.parse_args(["install"])
        self.assertEqual(args.command, "install")
        self.assertIsNone(args.group)

    def test_parse_install_with_group(self) -> None:
        args = cli.parse_args(["install", "--group", "obsidian"])
        self.assertEqual(args.command, "install")
        self.assertEqual(args.group, "obsidian")

    def test_parse_status(self) -> None:
        args = cli.parse_args(["status"])
        self.assertEqual(args.command, "status")

    def test_parse_update_with_group(self) -> None:
        args = cli.parse_args(["update", "--group", "global"])
        self.assertEqual(args.command, "update")
        self.assertEqual(args.group, "global")

    def test_parse_uninstall(self) -> None:
        args = cli.parse_args(["uninstall"])
        self.assertEqual(args.command, "uninstall")
        self.assertIsNone(args.group)


class GroupInstallTest(unittest.TestCase):
    """分组安装逻辑的测试。"""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.repo_root = root / "repo"
        self.home = root / "home"

        # 创建 global 组的 skills
        skills_dir = self.repo_root / "skills"
        for skill in ("dev-tdd", "dev-debug"):
            skill_path = skills_dir / skill
            skill_path.mkdir(parents=True)
            (skill_path / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")

        # 创建 obsidian 组的 skills
        for skill in ("obsidian-markdown", "obsidian-bases"):
            skill_path = skills_dir / skill
            skill_path.mkdir(parents=True)
            (skill_path / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")

        # kimi agent
        kimi_agent = self.repo_root / "kimi" / "agents" / "superpower"
        kimi_agent.mkdir(parents=True)
        (kimi_agent / "agent.yaml").write_text("name: superpower\n", encoding="utf-8")

        # ks
        ks = self.repo_root / "ks"
        ks.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")

        # MCP 配置
        mcp_dir = self.repo_root / "mcp-configs"
        mcp_dir.mkdir(parents=True, exist_ok=True)
        (mcp_dir / "required.json").write_text(
            json.dumps(
                {
                    "mcpServers": {
                        "auggie-mcp": {
                            "command": "auggie",
                            "args": ["--mcp"],
                            "type": "stdio",
                        }
                    }
                }
            ),
            encoding="utf-8",
        )

        # skills-install.yaml -- 使用绝对路径（测试 home 是临时目录）
        self.config_path = self.repo_root / "skills-install.yaml"
        self.config_path.write_text(
            "\n".join(
                [
                    "groups:",
                    "  global:",
                    "    skills:",
                    "      - dev-tdd",
                    "      - dev-debug",
                    "    targets:",
                    f"      - {self.home}/.agents/skills",
                    f"      - {self.home}/.claude/skills",
                    "  obsidian:",
                    "    skills:",
                    "      - obsidian-markdown",
                    "      - obsidian-bases",
                    "    targets:",
                    f"      - {self.home}/obsidian-vault/.obsidian/scripts/skills",
                ]
            ),
            encoding="utf-8",
        )

        self.stdout = io.StringIO()
        self.stderr = io.StringIO()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _v2_manifest_path(self) -> Path:
        return installer._ce_manifest_path(self.home)

    def _run_install_grouped(self, *, group: str | None = None) -> int:
        return installer.command_install_grouped(
            self.repo_root,
            self.home,
            self.config_path,
            group=group,
            stdout=self.stdout,
        )

    def _run_uninstall_grouped(self, *, group: str | None = None) -> int:
        return installer.command_uninstall_grouped(
            self.repo_root,
            self.home,
            self.config_path,
            group=group,
            stdout=self.stdout,
            stderr=self.stderr,
        )

    def _run_status_grouped(self, *, group: str | None = None) -> int:
        return installer.command_status_grouped(
            self.repo_root,
            self.home,
            self.config_path,
            group=group,
            stdout=self.stdout,
        )

    # ---- tests ----

    def test_install_all_groups(self) -> None:
        """ce install 安装所有组：global skills 在全局 targets，obsidian skills 在项目 targets，kimi+ks 也被安装。"""  # noqa: E501
        with mock.patch.dict("os.environ", {}, clear=True):
            code = self._run_install_grouped()

        self.assertEqual(code, 0)

        # global 组：dev-tdd, dev-debug 在 .agents/skills 和 .claude/skills
        for skill in ("dev-tdd", "dev-debug"):
            for target_dir in (".agents/skills", ".claude/skills"):
                link = self.home / target_dir / skill
                self.assertTrue(
                    link.is_symlink(),
                    f"{link} should be a symlink",
                )
                self.assertEqual(
                    link.resolve(),
                    (self.repo_root / "skills" / skill).resolve(),
                )

        # obsidian 组：obsidian-markdown, obsidian-bases 在 ~/obsidian-vault/.obsidian/scripts/skills
        # 但 targets 中 ~/obsidian-vault/... 展开后是 home/obsidian-vault/...
        obsidian_target = self.home / "obsidian-vault/.obsidian/scripts/skills"
        for skill in ("obsidian-markdown", "obsidian-bases"):
            link = obsidian_target / skill
            self.assertTrue(
                link.is_symlink(),
                f"{link} should be a symlink",
            )
            self.assertEqual(
                link.resolve(),
                (self.repo_root / "skills" / skill).resolve(),
            )

        # kimi agent + ks
        kimi_link = self.home / ".kimi/agents/superpower"
        ks_link = self.home / ".local/bin/ks"
        self.assertTrue(kimi_link.is_symlink())
        self.assertTrue(ks_link.is_symlink())

    def test_install_single_group(self) -> None:
        """ce install --group obsidian 只安装 obsidian 组。"""
        with mock.patch.dict("os.environ", {}, clear=True):
            code = self._run_install_grouped(group="obsidian")

        self.assertEqual(code, 0)

        # obsidian skills 已安装
        obsidian_target = self.home / "obsidian-vault/.obsidian/scripts/skills"
        for skill in ("obsidian-markdown", "obsidian-bases"):
            link = obsidian_target / skill
            self.assertTrue(link.is_symlink())

        # global skills 未安装
        for skill in ("dev-tdd", "dev-debug"):
            self.assertFalse((self.home / ".agents/skills" / skill).exists())

        # kimi/ks 也未安装（只有 global 组才处理）
        self.assertFalse((self.home / ".kimi/agents/superpower").exists())

    def test_install_writes_v2_manifest(self) -> None:
        """安装后写入 v2 格式 manifest（有 version=2 和 groups 键）。"""
        with mock.patch.dict("os.environ", {}, clear=True):
            self._run_install_grouped()

        manifest_path = self._v2_manifest_path()
        self.assertTrue(manifest_path.exists())

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], 2)
        self.assertIn("groups", manifest)
        self.assertIn("global", manifest["groups"])
        self.assertIn("obsidian", manifest["groups"])

        # global 组应有 mcp_servers
        global_group = manifest["groups"]["global"]
        self.assertIn("mcp_servers", global_group)
        self.assertEqual(global_group["mcp_servers"], ["auggie-mcp"])

    def test_uninstall_single_group(self) -> None:
        """只卸载 obsidian 组，global 组不受影响。"""
        with mock.patch.dict("os.environ", {}, clear=True):
            self._run_install_grouped()

        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        with mock.patch.dict("os.environ", {}, clear=True):
            code = self._run_uninstall_grouped(group="obsidian")

        self.assertEqual(code, 0)

        # obsidian skills 被卸载
        obsidian_target = self.home / "obsidian-vault/.obsidian/scripts/skills"
        for skill in ("obsidian-markdown", "obsidian-bases"):
            self.assertFalse(
                (obsidian_target / skill).exists(),
                f"{obsidian_target / skill} should be removed",
            )

        # global skills 仍然存在
        for skill in ("dev-tdd", "dev-debug"):
            self.assertTrue((self.home / ".agents/skills" / skill).is_symlink())

        # manifest 仍然存在且只包含 global
        manifest_path = self._v2_manifest_path()
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertIn("global", manifest["groups"])
        self.assertNotIn("obsidian", manifest["groups"])

    def test_status_shows_all_groups(self) -> None:
        """status 输出包含 [global] 和 [obsidian]。"""
        with mock.patch.dict("os.environ", {}, clear=True):
            self._run_install_grouped()

        self.stdout = io.StringIO()
        with mock.patch.dict("os.environ", {}, clear=True):
            code = self._run_status_grouped()

        self.assertEqual(code, 0)
        output = self.stdout.getvalue()
        self.assertIn("[global]", output)
        self.assertIn("[obsidian]", output)
        self.assertIn("installed=2", output)

    def test_status_single_group(self) -> None:
        """status --group global 只显示 global。"""
        with mock.patch.dict("os.environ", {}, clear=True):
            self._run_install_grouped()

        self.stdout = io.StringIO()
        with mock.patch.dict("os.environ", {}, clear=True):
            code = self._run_status_grouped(group="global")

        self.assertEqual(code, 0)
        output = self.stdout.getvalue()
        self.assertIn("[global]", output)
        self.assertNotIn("[obsidian]", output)

    def test_install_skips_when_target_dir_symlinks_to_source_skills(
        self,
    ) -> None:
        """当 target 目录是 source skills 目录的 symlink 时，不应创建自引用 symlink。"""
        # 让 ~/.claude/skills 成为 repo skills 目录的 symlink
        claude_skills = self.home / ".claude/skills"
        claude_skills.parent.mkdir(parents=True, exist_ok=True)
        claude_skills.symlink_to(self.repo_root / "skills")

        with mock.patch.dict("os.environ", {}, clear=True):
            code = self._run_install_grouped()

        self.assertEqual(code, 0)

        # ~/.claude/skills/dev-tdd 不应该是 symlink（否则就是自引用）
        for skill in ("dev-tdd", "dev-debug"):
            link = self.home / ".claude/skills" / skill
            # 如果 is_symlink() 为 True，说明创建了自引用 symlink
            self.assertFalse(
                link.is_symlink(),
                f"{skill} should NOT be a symlink (target dir symlinks to source)",
            )
            # 但目录本身应该存在（因为是 source 目录的直接子目录）
            self.assertTrue(
                link.is_dir(),
                f"{skill} should still be a real directory",
            )

        # .agents/skills 应该正常创建 symlink（因为它不指向 source）
        for skill in ("dev-tdd", "dev-debug"):
            link = self.home / ".agents/skills" / skill
            self.assertTrue(link.is_symlink())

    def test_install_no_config_falls_back_to_legacy(self) -> None:
        """配置文件不存在时走旧版 command_install 路径。"""
        # 删除配置文件
        self.config_path.unlink()

        with mock.patch.dict("os.environ", {}, clear=True):
            code = self._run_install_grouped()

        self.assertEqual(code, 0)
        # 旧版 manifest 路径应被使用
        legacy_manifest = installer._legacy_manifest_path(self.home)
        self.assertTrue(legacy_manifest.exists())


if __name__ == "__main__":
    unittest.main()
