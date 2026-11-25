#!/usr/bin/env python3
"""Validate every SKILL.md in the repo: frontmatter present, name is kebab-case and matches its folder,
description present and within Claude Code's limit. Validate the plugin manifests in .claude-plugin/:
plugin.json lists exactly the skill folders, marketplace.json has an entry for the plugin, and neither sets a
version, since a version nobody bumps stops installs from updating. Exits non-zero listing every problem."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_DESCRIPTION = 1024
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
NO_VERSION = "remove 'version'; without it every commit is a new version, with it installs stop updating"


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


def load_object(path: pathlib.Path) -> tuple[dict | None, str | None]:
    """A JSON object from path, or None and the problem that stops it from being read."""
    rel = path.relative_to(ROOT)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"{rel}: missing"
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        return None, f"{rel}: unreadable ({e})"
    if not isinstance(value, dict):
        return None, f"{rel}: not a JSON object"
    return value, None


def manifest_problems(skill_dirs: list[pathlib.Path]) -> list[str]:
    """plugin.json lists exactly the skill folders in the repo, so none is silently left out."""
    rel = MANIFEST.relative_to(ROOT)
    manifest, problem = load_object(MANIFEST)
    if manifest is None:
        return [problem]
    entries = manifest.get("skills", [])
    if isinstance(entries, str):
        entries = [entries]
    if not isinstance(entries, list) or not all(isinstance(e, str) for e in entries):
        return [f"{rel}: 'skills' must be a path or a list of paths"]

    problems = marketplace_problems(manifest.get("name"))
    if "version" in manifest:
        problems.append(f"{rel}: {NO_VERSION}")
    listed = set()
    for entry in entries:
        path = (ROOT / entry).resolve()
        if not entry.startswith("./"):
            problems.append(f"{rel}: skill path {entry!r} must start with './'")
        elif not path.is_relative_to(ROOT):
            problems.append(f"{rel}: skill path {entry!r} is outside the repo")
        elif not (path / "SKILL.md").is_file():
            problems.append(f"{entry}: listed in {rel} but has no SKILL.md")
        elif path in listed:
            problems.append(f"{entry}: listed more than once in {rel}")
        else:
            listed.add(path)
    problems += [f"{d.relative_to(ROOT)}: skill not listed in {rel}"
                 for d in skill_dirs if d.resolve() not in listed]
    by_name: dict[str, list[str]] = {}
    for d in skill_dirs:
        by_name.setdefault(d.name, []).append(str(d.relative_to(ROOT)))
    problems += [f"{', '.join(dirs)}: skills with the same name collide in the plugin"
                 for dirs in by_name.values() if len(dirs) > 1]
    return problems


def marketplace_problems(plugin_name: object) -> list[str]:
    """marketplace.json offers the plugin, and no entry pins a version."""
    rel = MARKETPLACE.relative_to(ROOT)
    marketplace, problem = load_object(MARKETPLACE)
    if marketplace is None:
        return [problem]
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not all(isinstance(p, dict) for p in plugins):
        return [f"{rel}: 'plugins' must be a list of objects"]
    problems = [f"{rel}: plugin entry {p.get('name')!r}: {NO_VERSION}" for p in plugins if "version" in p]
    if not any(p.get("name") == plugin_name for p in plugins):
        problems.append(f"{rel}: no entry for plugin {plugin_name!r} from {MANIFEST.relative_to(ROOT)}")
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
