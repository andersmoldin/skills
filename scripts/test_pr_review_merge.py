#!/usr/bin/env python3
"""Tests for github-pr-review's merge.sh: when the review app merges what it approved. GitHub is faked
(fakegh.py). Run: python3 -m unittest discover -s scripts"""
import copy
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from fakegh import FakeGh

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "github" / "github-pr-review" / "templates" / "merge.sh"
REPO, PR, SHA = "o/r", "7", "a" * 40
SINCE = "2026-11-27T10:00:00Z"
BOT, CAPTAIN = "r-pr-review[bot]", "o"
ADVISORY = {"status": 403, "body": {"message": "Upgrade to GitHub Pro or make this repository public to enable this feature."}}


def approved_pr() -> dict:
    """An approved PR on an advisory repo whose checks have passed: the case that merges."""
    return {
        "api": {
            f"GET repos/{REPO}/pulls/{PR}": {"body": {
                "state": "open", "merged": False, "draft": False, "changed_files": 1, "labels": [],
                "head": {"sha": SHA, "ref": "fix/thing"}, "base": {"ref": "main"}}},
            f"GET repos/{REPO}/rules/branches/main": ADVISORY,
            f"GET repos/{REPO}/pulls/{PR}/reviews?per_page=100": {"body": [
                {"user": {"login": BOT}, "state": "APPROVED", "commit_id": SHA, "submitted_at": "2026-11-27T10:05:00Z"}]},
            f"GET repos/{REPO}/issues/{PR}/comments?since={SINCE}&per_page=100": {"body": []},
            f"GET repos/{REPO}/pulls/{PR}/files?per_page=100": {"body": [{"filename": "src/app.py"}]},
        },
        "checks": {"body": [
            {"name": "ci", "bucket": "pass", "workflow": "ci"},
            {"name": "gitleaks", "bucket": "pass", "workflow": "guard"},
            {"name": "merge", "bucket": "pending", "workflow": "pr-review"},
        ]},
    }


class Merge(unittest.TestCase):
    def setUp(self):
        self.work = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.work)
        (self.work / ".github").mkdir()
        self.codeowners("/.github/   @o\n/VISION.md  @o\n")
        self.mode = "enforce"

    def codeowners(self, text: str) -> None:
        (self.work / ".github" / "CODEOWNERS").write_text(text, encoding="utf-8")

    def run_merge(self, scenario: dict, **env: str) -> subprocess.CompletedProcess:
        self.gh = FakeGh(scenario)
        self.addCleanup(self.gh.cleanup)
        environment = {**self.gh.env, "HOME": str(self.work), "GH_REPO": REPO, "PR": PR, "SHA": SHA,
                       "SINCE": SINCE, "BOT": BOT, "CAPTAIN": CAPTAIN, "MODE": self.mode,
                       "GITHUB_WORKFLOW": "pr-review", "WAIT_SECONDS": "0", "POLL_SECONDS": "0", **env}
        return subprocess.run(["bash", str(SCRIPT)], cwd=self.work, env=environment, capture_output=True, text=True)

    def merges(self) -> list[list[str]]:
        return [c for c in self.gh.calls() if c[:2] == ["pr", "merge"]]

    def comments(self) -> list[str]:
        return [c[c.index("--body") + 1] for c in self.gh.calls() if c[:2] == ["pr", "comment"]]

    def assert_held(self, result: subprocess.CompletedProcess, reason: str) -> None:
        """Approved but not merged, and the PR says why: the captain has to act."""
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(self.merges(), [])
        self.assertEqual(len(self.comments()), 1, self.gh.calls())
        self.assertIn(reason, self.comments()[0])

    def assert_skipped(self, result: subprocess.CompletedProcess) -> None:
        """Nothing for the merge job to do, and nothing to say on the PR."""
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.merges(), [])
        self.assertEqual(self.comments(), [])

    def test_merges_an_approved_pr_once_its_checks_pass(self):
        result = self.run_merge(approved_pr())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.merges(), [["pr", "merge", PR, "--squash", "--match-head-commit", SHA]])
        self.assertEqual(self.comments(), [])

    def test_observe_mode_never_merges(self):
        for mode in ("observe", ""):
            with self.subTest(mode=mode):
                self.mode = mode
                self.assert_skipped(self.run_merge(approved_pr()))

    def test_leaves_the_merge_to_auto_merge_where_github_enforces_the_review(self):
        scenario = approved_pr()
        scenario["api"][f"GET repos/{REPO}/rules/branches/main"] = {"body": [
            {"type": "deletion"},
            {"type": "pull_request", "parameters": {"required_approving_review_count": 1}}]}
        self.assert_skipped(self.run_merge(scenario))

    def test_merges_on_a_public_repo_whose_rules_require_no_review(self):
        scenario = approved_pr()
        scenario["api"][f"GET repos/{REPO}/rules/branches/main"] = {"body": [
            {"type": "pull_request", "parameters": {"required_approving_review_count": 0}}]}
        self.assertEqual(self.run_merge(scenario).returncode, 0)
        self.assertEqual(len(self.merges()), 1)

    def test_holds_when_it_cannot_tell_whether_github_enforces_the_review(self):
        for answer in ({"status": 502, "body": {"message": "Bad Gateway"}},
                       {"status": 403, "body": {"message": "Resource not accessible by integration"}},
                       {"body": {"message": "not a list of rules"}}):
            with self.subTest(answer=answer):
                scenario = approved_pr()
                scenario["api"][f"GET repos/{REPO}/rules/branches/main"] = answer
                self.assert_held(self.run_merge(scenario), "cannot tell whether GitHub enforces")

    def test_does_not_merge_commits_pushed_after_the_review(self):
        scenario = approved_pr()
        scenario["api"][f"GET repos/{REPO}/pulls/{PR}"]["body"]["head"]["sha"] = "b" * 40
        self.assert_skipped(self.run_merge(scenario))

    def test_leaves_a_closed_or_merged_pr_alone(self):
        for change in ({"state": "closed"}, {"state": "closed", "merged": True}):
            with self.subTest(change=change):
                scenario = approved_pr()
                scenario["api"][f"GET repos/{REPO}/pulls/{PR}"]["body"].update(change)
                self.assert_skipped(self.run_merge(scenario))

    def test_merges_only_an_approval_from_this_run_of_the_reviewed_commit(self):
        approval = {"user": {"login": BOT}, "state": "APPROVED", "commit_id": SHA, "submitted_at": "2026-11-27T10:05:00Z"}
        for name, review in (("older commit", {"commit_id": "c" * 40}),
                             ("earlier run", {"submitted_at": "2026-11-27T09:59:59Z"}),
                             ("someone else", {"user": {"login": "mallory"}}),
                             ("dismissed", {"state": "DISMISSED"}),
                             ("comment only", {"state": "COMMENTED"})):
            with self.subTest(name):
                scenario = approved_pr()
                scenario["api"][f"GET repos/{REPO}/pulls/{PR}/reviews?per_page=100"]["body"] = [{**approval, **review}]
                self.assert_skipped(self.run_merge(scenario))

    def test_holds_while_any_reviewer_requests_changes(self):
        scenario = approved_pr()
        reviews = scenario["api"][f"GET repos/{REPO}/pulls/{PR}/reviews?per_page=100"]["body"]
        reviews.insert(0, {"user": {"login": CAPTAIN}, "state": "CHANGES_REQUESTED", "commit_id": "c" * 40,
                           "submitted_at": "2026-11-27T09:00:00Z"})
        reviews.append({"user": {"login": CAPTAIN}, "state": "COMMENTED", "commit_id": SHA,
                        "submitted_at": "2026-11-27T10:06:00Z"})
        self.assert_held(self.run_merge(scenario), f"changes requested by {CAPTAIN}")

    def test_a_later_approval_lifts_a_request_for_changes(self):
        scenario = approved_pr()
        reviews = scenario["api"][f"GET repos/{REPO}/pulls/{PR}/reviews?per_page=100"]["body"]
        reviews.insert(0, {"user": {"login": BOT}, "state": "CHANGES_REQUESTED", "commit_id": "c" * 40,
                           "submitted_at": "2026-11-27T09:00:00Z"})
        self.assertEqual(self.run_merge(scenario).returncode, 0)
        self.assertEqual(len(self.merges()), 1)

    def test_holds_a_pr_that_waits_for_the_captain(self):
        scenario = approved_pr()
        scenario["api"][f"GET repos/{REPO}/pulls/{PR}"]["body"]["labels"] = [{"name": "needs-captain"}]
        self.assert_held(self.run_merge(scenario), "needs-captain")

    def test_stops_when_the_captain_says_stop(self):
        scenario = approved_pr()
        scenario["api"][f"GET repos/{REPO}/issues/{PR}/comments?since={SINCE}&per_page=100"]["body"] = [
            {"user": {"login": CAPTAIN}, "body": "@agent stop, I am rethinking this"}]
        self.assert_skipped(self.run_merge(scenario))

    def test_a_stop_word_quoted_by_someone_else_changes_nothing(self):
        scenario = approved_pr()
        scenario["api"][f"GET repos/{REPO}/issues/{PR}/comments?since={SINCE}&per_page=100"]["body"] = [
            {"user": {"login": "mallory"}, "body": "@agent stop"}]
        self.assertEqual(self.run_merge(scenario).returncode, 0)
        self.assertEqual(len(self.merges()), 1)

    def test_holds_a_draft(self):
        scenario = approved_pr()
        scenario["api"][f"GET repos/{REPO}/pulls/{PR}"]["body"]["draft"] = True
        self.assert_held(self.run_merge(scenario), "draft")

    def test_holds_beta_into_main_which_takes_a_merge_commit(self):
        scenario = approved_pr()
        scenario["api"][f"GET repos/{REPO}/pulls/{PR}"]["body"]["head"]["ref"] = "beta"
        self.assert_held(self.run_merge(scenario), "merge commit")

    def test_a_failed_read_never_merges(self):
        for endpoint in (f"GET repos/{REPO}/pulls/{PR}/reviews?per_page=100",
                         f"GET repos/{REPO}/issues/{PR}/comments?since={SINCE}&per_page=100",
                         f"GET repos/{REPO}/pulls/{PR}/files?per_page=100"):
            with self.subTest(endpoint):
                scenario = approved_pr()
                scenario["api"][endpoint] = {"status": 500, "body": {"message": "Server Error"}}
                result = self.run_merge(scenario)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.merges(), [])

    def test_holds_a_pr_that_touches_a_protected_path(self):
        for name, owners, files in (
                ("directory", "/.github/ @o\n", [{"filename": ".github/workflows/ci.yml"}]),
                ("file", "/VISION.md @o\n", [{"filename": "VISION.md"}]),
                ("glob", "/github/*/scripts/ @o\n", [{"filename": "github/x/scripts/run.sh"}]),
                ("directory without slash", "/scripts @o\n", [{"filename": "scripts/run.sh"}]),
                ("at any depth", "secrets/ @o\n", [{"filename": "app/secrets/key.txt"}]),
                ("last line without newline", "/README.md @o\n/VISION.md @o", [{"filename": "VISION.md"}]),
                ("indented, with a comment after it", "  /VISION.md  @o  # the vision\n", [{"filename": "VISION.md"}]),
                ("moved out of it", "/.github/ @o\n", [{"filename": "ci.yml", "previous_filename": ".github/workflows/ci.yml"}])):
            with self.subTest(name):
                self.codeowners("# protected\n\n" + owners)
                scenario = approved_pr()
                scenario["api"][f"GET repos/{REPO}/pulls/{PR}/files?per_page=100"]["body"] = files
                self.assert_held(self.run_merge(scenario), "protected path")

    def test_a_path_that_only_resembles_a_protected_one_merges(self):
        self.codeowners("/.github/ @o\n/VISION.md @o\n")
        scenario = approved_pr()
        scenario["api"][f"GET repos/{REPO}/pulls/{PR}/files?per_page=100"]["body"] = [
            {"filename": "docs/VISION.md"}, {"filename": "github/README.md"}]
        scenario["api"][f"GET repos/{REPO}/pulls/{PR}"]["body"]["changed_files"] = 2
        self.assertEqual(self.run_merge(scenario).returncode, 0)
        self.assertEqual(len(self.merges()), 1)

    def test_holds_when_codeowners_is_missing_or_empty(self):
        for text in (None, "# nothing here\n"):
            with self.subTest(text=text):
                if text is None:
                    (self.work / ".github" / "CODEOWNERS").unlink(missing_ok=True)
                else:
                    self.codeowners(text)
                self.assert_held(self.run_merge(approved_pr()), "CODEOWNERS")

    def test_holds_when_github_lists_fewer_files_than_the_pr_changes(self):
        scenario = approved_pr()
        scenario["api"][f"GET repos/{REPO}/pulls/{PR}"]["body"]["changed_files"] = 3001
        self.assert_held(self.run_merge(scenario), "file list")

    def test_holds_when_a_check_fails_or_is_cancelled(self):
        for bucket in ("fail", "cancel"):
            with self.subTest(bucket=bucket):
                scenario = approved_pr()
                scenario["checks"]["body"][0]["bucket"] = bucket
                self.assert_held(self.run_merge(scenario), "ci")

    def test_ignores_the_checks_of_its_own_workflow(self):
        scenario = approved_pr()
        scenario["checks"]["body"] += [{"name": "review", "bucket": "fail", "workflow": "pr-review"},
                                       {"name": "escalate-untrusted", "bucket": "skipping", "workflow": "pr-review"}]
        self.assertEqual(self.run_merge(scenario).returncode, 0)
        self.assertEqual(len(self.merges()), 1)

    def test_counts_commit_statuses_and_skipped_checks(self):
        scenario = approved_pr()
        scenario["checks"]["body"] += [{"name": "deploy-preview", "bucket": "pass", "workflow": ""},
                                       {"name": "optional", "bucket": "skipping", "workflow": "ci"}]
        self.assertEqual(self.run_merge(scenario).returncode, 0)
        self.assertEqual(len(self.merges()), 1)
        scenario["checks"]["body"][-2]["bucket"] = "fail"
        self.assert_held(self.run_merge(scenario), "deploy-preview")

    def test_waits_for_pending_checks_then_merges(self):
        scenario = approved_pr()
        pending = copy.deepcopy(scenario["checks"])
        pending["body"][0]["bucket"] = "pending"
        pending["exit"] = 8
        scenario["checks"] = [pending, {"status": 500, "body": {"message": "flaky"}}, scenario["checks"]]
        result = self.run_merge(scenario, WAIT_SECONDS="60")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(self.merges()), 1)

    def test_holds_when_checks_are_still_pending_at_the_deadline(self):
        for name, checks in (("pending", [{"name": "ci", "bucket": "pending", "workflow": "ci"}]),
                             ("none reported", []),
                             ("only its own", [{"name": "merge", "bucket": "pending", "workflow": "pr-review"}])):
            with self.subTest(name):
                scenario = approved_pr()
                scenario["checks"] = {"body": checks}
                self.assert_held(self.run_merge(scenario), "checks")

    def test_stops_waiting_when_new_commits_arrive(self):
        scenario = approved_pr()
        open_pr = scenario["api"][f"GET repos/{REPO}/pulls/{PR}"]
        pushed = copy.deepcopy(open_pr)
        pushed["body"]["head"]["sha"] = "b" * 40
        scenario["api"][f"GET repos/{REPO}/pulls/{PR}"] = [open_pr, open_pr, pushed]
        scenario["checks"] = {"body": [{"name": "ci", "bucket": "pending", "workflow": "ci"}]}
        self.assert_skipped(self.run_merge(scenario, WAIT_SECONDS="60"))

    def test_says_so_when_github_refuses_the_merge(self):
        scenario = approved_pr()
        scenario["merge"] = {"status": 405, "body": {"message": "Pull Request is not mergeable"}}
        result = self.run_merge(scenario)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(self.comments()), 1)
        self.assertIn("Pull Request is not mergeable", self.comments()[0])


if __name__ == "__main__":
    unittest.main()
