#!/usr/bin/env python3
"""A stand-in for the gh CLI, so tests can run the repo's shell scripts without GitHub.

FakeGh(scenario) writes a `gh` executable into a temporary bin directory. Every call is logged; the
answer comes from the scenario:

    {"api": {"GET repos/o/r/pulls/7": response, "GET repos/o/r/contents/*": response, ...},
     "checks": response, "merge": response}

A response is {"status": 200, "body": <JSON>, "exit": <code>} (all optional), or a list of responses
returned one per call, the last one repeating. API keys are "METHOD path" with the leading slash
dropped; an exact key wins over an fnmatch pattern. --jq runs through the real jq, as gh would.
A call the scenario does not answer fails loudly."""
import fnmatch
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile


class FakeGh:
    def __init__(self, scenario: dict):
        self.dir = pathlib.Path(tempfile.mkdtemp())
        self.scenario = self.dir / "scenario.json"
        self.scenario.write_text(json.dumps(scenario), encoding="utf-8")
        self.log = self.dir / "calls.jsonl"
        self.log.touch()
        bin_dir = self.dir / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(f'#!/bin/sh\nexec "{sys.executable}" -I "{pathlib.Path(__file__).resolve()}" "$@"\n',
                      encoding="utf-8")
        gh.chmod(0o755)
        self.env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                    "FAKE_GH_SCENARIO": str(self.scenario), "FAKE_GH_LOG": str(self.log),
                    "FAKE_GH_STATE": str(self.dir)}

    def cleanup(self) -> None:
        shutil.rmtree(self.dir)

    def calls(self) -> list[list[str]]:
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]


def respond(key: str, response, state_dir: pathlib.Path, jq: str | None) -> int:
    if isinstance(response, list):
        counter = state_dir / ("count-" + "".join(c if c.isalnum() else "_" for c in key))
        n = int(counter.read_text()) if counter.exists() else 0
        counter.write_text(str(n + 1))
        response = response[min(n, len(response) - 1)]
    status = response.get("status", 200)
    body = json.dumps(response.get("body", {}))
    if status >= 400:
        print(body)
        message = response.get("body", {}).get("message", "error")
        print(f"gh: {message} (HTTP {status})", file=sys.stderr)
        return 1
    if jq is None:
        print(body)
    else:
        result = subprocess.run(["jq", "-r", "-c", jq], input=body, capture_output=True, text=True)
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        if result.returncode:
            return result.returncode
    return response.get("exit", 0)


def option(args: list[str], *names: str) -> str | None:
    for i, a in enumerate(args):
        if a in names and i + 1 < len(args):
            return args[i + 1]
    return None


def main() -> int:
    args = sys.argv[1:]
    with open(os.environ["FAKE_GH_LOG"], "a", encoding="utf-8") as log:
        log.write(json.dumps(args) + "\n")
    scenario = json.loads(pathlib.Path(os.environ["FAKE_GH_SCENARIO"]).read_text(encoding="utf-8"))
    state = pathlib.Path(os.environ["FAKE_GH_STATE"])
    jq = option(args, "--jq", "-q")

    if args[:1] == ["api"]:
        method = (option(args, "-X", "--method") or "GET").upper()
        takes_value = {"-X", "--method", "--jq", "-q", "-f", "-F", "--field", "--raw-field", "-H", "--header",
                       "--input"}
        path, skip = None, False
        for a in args[1:]:
            if skip:
                skip = False
            elif a in takes_value:
                skip = True
            elif not a.startswith("-"):
                path = a
                break
        key = f"{method} {(path or '').lstrip('/')}"
        api = scenario.get("api", {})
        if key in api:
            return respond(key, api[key], state, jq)
        for pattern, response in api.items():
            if fnmatch.fnmatchcase(key, pattern):
                return respond(key, response, state, jq)
    elif args[:2] == ["pr", "checks"] and "checks" in scenario:
        return respond("checks", scenario["checks"], state, jq)
    elif args[:2] == ["pr", "merge"]:
        return respond("merge", scenario.get("merge", {}), state, jq)
    elif args[:2] == ["pr", "comment"]:
        return 0
    print(f"fake gh: the scenario has no answer for: gh {' '.join(args)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
