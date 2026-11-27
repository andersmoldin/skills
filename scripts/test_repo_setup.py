#!/usr/bin/env python3
"""Tests for github-repo-setup's repo-setup.sh audit on an advisory repo (private on GitHub Free). GitHub is
faked (fakegh.py). Run: python3 -m unittest discover -s scripts"""
import pathlib
import subprocess
import unittest

from fakegh import FakeGh

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "github" / "github-repo-setup" / "scripts" / "repo-setup.sh"
REPO = "o/r"


def advisory_repo() -> dict:
    """An advisory repo whose settings and files are what the skill sets up."""
    return {"api": {
        f"GET repos/{REPO}": {"body": {
            "visibility": "private", "default_branch": "main", "allow_squash_merge": True, "allow_merge_commit": False,
            "allow_rebase_merge": False, "allow_auto_merge": False, "delete_branch_on_merge": True,
            "squash_merge_commit_title": "PR_TITLE", "squash_merge_commit_message": "PR_BODY"}},
        f"GET repos/{REPO}/rulesets": {"status": 403, "body": {
            "message": "Upgrade to GitHub Pro or make this repository public to enable this feature."}},
        f"GET repos/{REPO}/actions/permissions/workflow": {"body": {
            "default_workflow_permissions": "read", "can_approve_pull_request_reviews": False}},
        f"GET repos/{REPO}/actions/permissions": {"body": {"enabled": True, "sha_pinning_required": True}},
        f"GET repos/{REPO}/labels/needs-captain": {"body": {"name": "needs-captain"}},
        f"GET repos/{REPO}/contents/.github/workflows?ref=main": {"body": []},
        f"GET repos/{REPO}/contents/*": {"body": {"type": "file"}},
    }}


class AdvisoryAudit(unittest.TestCase):
    def audit(self, scenario: dict) -> subprocess.CompletedProcess:
        self.gh = FakeGh(scenario)
        self.addCleanup(self.gh.cleanup)
        return subprocess.run(["bash", str(SCRIPT), "audit", REPO, "--checks", "ci,pr-title"],
                              env=self.gh.env, capture_output=True, text=True)

    def test_a_repo_set_up_as_the_skill_says_has_no_drift(self):
        result = self.audit(advisory_repo())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("main not protected (advisory)", result.stdout)
        self.assertIn("no drift", result.stdout)

    def test_flags_auto_merge_turned_on(self):
        scenario = advisory_repo()
        scenario["api"][f"GET repos/{REPO}"]["body"]["allow_auto_merge"] = True
        result = self.audit(scenario)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("DRIFT: merge settings", result.stdout)
        self.assertIn('"allow_auto_merge":true', result.stdout)

    def test_flags_a_missing_merge_script(self):
        scenario = advisory_repo()
        scenario["api"][f"GET repos/{REPO}/contents/.github/pr-review/merge.sh?ref=main"] = {
            "status": 404, "body": {"message": "Not Found"}}
        result = self.audit(scenario)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("file missing: .github/pr-review/merge.sh", result.stdout)


if __name__ == "__main__":
    unittest.main()
