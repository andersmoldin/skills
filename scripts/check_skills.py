#!/usr/bin/env python3
"""Validate every SKILL.md in the repo: frontmatter present, name is kebab-case and matches its folder,
description present and within Claude Code's limit. Exits non-zero listing every problem."""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_DESCRIPTION = 1024


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
    for p in problems:
        print(p)
    print(f"{len(skills)} skills checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
