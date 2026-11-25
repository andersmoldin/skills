#!/usr/bin/env python3
"""Tests for check_skills.py, run against a throwaway repo layout: python3 -m unittest discover -s scripts"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent / "check_skills.py"


class CheckSkills(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        (self.root / "scripts").mkdir()
        shutil.copy(SCRIPT, self.root / "scripts" / "check_skills.py")

    def skill(self, path: str) -> None:
        folder = self.root / path
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text(f"---\nname: {folder.name}\ndescription: Does a thing.\n---\n", encoding="utf-8")

    def manifest(self, manifest: dict, marketplace_entry: dict | None = None) -> None:
        (self.root / ".claude-plugin").mkdir(exist_ok=True)
        (self.root / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
        entry = marketplace_entry or {"name": manifest.get("name"), "source": "./"}
        marketplace = {"name": "m", "owner": {"name": "o"}, "plugins": [entry]}
        (self.root / ".claude-plugin" / "marketplace.json").write_text(json.dumps(marketplace), encoding="utf-8")

    def check(self) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-I", str(self.root / "scripts" / "check_skills.py")],
                              capture_output=True, text=True)

    def test_every_skill_listed_passes(self):
        self.skill("github/one")
        self.skill("research/two")
        self.manifest({"name": "p", "skills": ["./github/one/", "./research/two"]})
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("2 skills checked, 0 problems", result.stdout)

    def test_single_skill_path_as_string_passes(self):
        self.skill("github/one")
        self.manifest({"name": "p", "skills": "./github/one"})
        self.assertEqual(self.check().returncode, 0)

    def test_skill_not_listed_in_plugin_json_fails(self):
        self.skill("github/listed")
        self.skill("research/forgotten")
        self.manifest({"name": "p", "skills": ["./github/listed"]})
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("research/forgotten", result.stdout)
        self.assertIn("not listed", result.stdout)

    def test_listed_path_without_skill_md_fails(self):
        self.skill("github/real")
        (self.root / "github" / "renamed-away").mkdir()
        self.manifest({"name": "p", "skills": ["./github/real", "./github/renamed-away", "./research/gone"]})
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("./github/renamed-away: listed", result.stdout)
        self.assertIn("./research/gone: listed", result.stdout)

    def test_two_skills_with_the_same_name_fail(self):
        self.skill("github/twin")
        self.skill("research/twin")
        self.manifest({"name": "p", "skills": ["./github/twin", "./research/twin"]})
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("twin", result.stdout)
        self.assertIn("same name", result.stdout)

    def test_skill_listed_twice_fails(self):
        self.skill("github/one")
        self.manifest({"name": "p", "skills": ["./github/one", "./github/one/"]})
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("listed more than once", result.stdout)

    def test_version_in_plugin_json_fails(self):
        self.skill("github/real")
        self.manifest({"name": "p", "version": "1.0.0", "skills": ["./github/real"]})
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("version", result.stdout)

    def test_version_in_marketplace_entry_fails(self):
        self.skill("github/real")
        self.manifest({"name": "p", "skills": ["./github/real"]}, {"name": "p", "source": "./", "version": "1.0.0"})
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("marketplace.json", result.stdout)
        self.assertIn("version", result.stdout)

    def test_marketplace_without_an_entry_for_the_plugin_fails(self):
        self.skill("github/real")
        self.manifest({"name": "p", "skills": ["./github/real"]}, {"name": "renamed", "source": "./"})
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("no entry for plugin 'p'", result.stdout)

    def test_unusable_plugin_json_fails_with_a_message(self):
        cases = {
            "missing": None,
            "not JSON": "{",
            "not an object": "[]",
            "skills not a list": '{"name": "p", "skills": 3}',
            "path without ./": '{"name": "p", "skills": ["github/real"]}',
            "path outside the repo": '{"name": "p", "skills": ["./../real"]}',
        }
        for case, text in cases.items():
            with self.subTest(case):
                shutil.rmtree(self.root / ".claude-plugin", ignore_errors=True)
                shutil.rmtree(self.root / "github", ignore_errors=True)
                self.skill("github/real")
                if text is not None:
                    (self.root / ".claude-plugin").mkdir()
                    (self.root / ".claude-plugin" / "plugin.json").write_text(text, encoding="utf-8")
                result = self.check()
                self.assertEqual(result.returncode, 1)
                self.assertIn(".claude-plugin/plugin.json", result.stdout)
                self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
