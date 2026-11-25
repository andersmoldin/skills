#!/usr/bin/env python3
"""Validate every SKILL.md in the repo: frontmatter present, name is kebab-case and matches its folder,
description present and within Claude Code's limit. Validate .claude-plugin/plugin.json: it lists exactly
the skill folders, and has no version. Exits non-zero listing every problem."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_DESCRIPTION = 1024
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"


def frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fields = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fields[key.strip()] = value.strip()
    return fields


def manifest_problems(skill_dirs: list[pathlib.Path]) -> list[str]:
    """The plugin manifest lists exactly the skill folders in the repo, so none is silently left out."""
    rel = MANIFEST.relative_to(ROOT)
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"{rel}: missing"]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        return [f"{rel}: unreadable ({e})"]
    if not isinstance(manifest, dict):
        return [f"{rel}: not a JSON object"]
    entries = manifest.get("skills", [])
    if isinstance(entries, str):
        entries = [entries]
    if not isinstance(entries, list) or not all(isinstance(e, str) for e in entries):
        return [f"{rel}: 'skills' must be a path or a list of paths"]

    problems = []
    if "version" in manifest:
        problems.append(f"{rel}: remove 'version'; without it every commit is a new version, "
                        "with it installs stop updating until someone bumps it")
    listed = set()
    for entry in entries:
        path = (ROOT / entry).resolve()
        if not entry.startswith("./"):
            problems.append(f"{rel}: skill path {entry!r} must start with './'")
        elif not path.is_relative_to(ROOT):
            problems.append(f"{rel}: skill path {entry!r} is outside the repo")
        elif not (path / "SKILL.md").is_file():
            problems.append(f"{entry}: listed in {rel} but has no SKILL.md")
        else:
            listed.add(path)
    problems += [f"{d.relative_to(ROOT)}: skill not listed in {rel}"
                 for d in skill_dirs if d.resolve() not in listed]
    return problems


def main() -> int:
    problems = []
    skills = sorted(p for p in ROOT.rglob("SKILL.md") if ".git" not in p.parts and "node_modules" not in p.parts)
    for path in skills:
        rel = path.relative_to(ROOT)
        fm = frontmatter(path.read_text(encoding="utf-8"))
        if fm is None:
            problems.append(f"{rel}: no YAML frontmatter")
            continue
        name, description = fm.get("name", ""), fm.get("description", "")
        if not NAME.match(name):
            problems.append(f"{rel}: name {name!r} is not kebab-case")
        if name != path.parent.name:
            problems.append(f"{rel}: name {name!r} does not match folder {path.parent.name!r}")
        if not description:
            problems.append(f"{rel}: description missing")
        elif len(description) > MAX_DESCRIPTION:
            problems.append(f"{rel}: description is {len(description)} chars (max {MAX_DESCRIPTION})")
    problems += manifest_problems([p.parent for p in skills])
    for p in problems:
        print(p)
    print(f"{len(skills)} skills checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
