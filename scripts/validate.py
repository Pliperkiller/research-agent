#!/usr/bin/env python3
"""Validate the research-agent plugin before committing.

Checks:
  1. Manifests parse and carry the required fields.
  2. Every skill has a SKILL.md with name and description frontmatter, and the
     name matches its directory.
  3. Bundled scripts compile.
  4. The figure linter flags the known-bad fixture and clears the known-good one.

Usage:
    python scripts/validate.py
"""
from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILURES: list[str] = []


def check(condition: bool, message: str) -> None:
    if condition:
        print(f"  ok   {message}")
    else:
        print(f"  FAIL {message}")
        FAILURES.append(message)


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    block = text.split("---", 2)[1]
    out, key = {}, None
    for line in block.splitlines():
        if line and not line[0].isspace() and ":" in line:
            key, _, value = line.partition(":")
            out[key.strip()] = value.strip()
        elif key and line.strip():
            out[key] += " " + line.strip()
    return out


def main() -> int:
    print("manifests")
    mk = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    pl = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    check("name" in mk and "owner" in mk and "plugins" in mk,
          "marketplace.json has name, owner and plugins")
    check(any(p.get("name") == pl["name"] for p in mk["plugins"]),
          f"marketplace lists the plugin '{pl['name']}'")
    check(pl["name"] == pl["name"].lower().replace(" ", "-"),
          "plugin name is kebab-case")

    print("skills")
    skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
    check(bool(skills), "at least one skill is present")
    for skill in skills:
        md = skill / "SKILL.md"
        check(md.exists(), f"{skill.name}/SKILL.md exists")
        if not md.exists():
            continue
        fm = frontmatter(md)
        check(fm.get("name") == skill.name,
              f"{skill.name}: frontmatter name matches the directory")
        check(len(fm.get("description", "")) > 40,
              f"{skill.name}: description is substantive enough to trigger")
        check((skill / "references" / "checklist.md").exists(),
              f"{skill.name}: ships an audit checklist")

    print("scripts compile")
    for py in sorted(ROOT.rglob("*.py")):
        try:
            py_compile.compile(str(py), doraise=True)
            print(f"  ok   {py.relative_to(ROOT)}")
        except py_compile.PyCompileError as exc:
            print(f"  FAIL {py.relative_to(ROOT)}: {exc}")
            FAILURES.append(str(py))

    print("figure linter against fixtures")
    lint = ROOT / "skills" / "scientific-figures" / "scripts" / "figure_lint.py"
    if lint.exists():
        for name, expect_findings in (("bad_figure.py", True),
                                      ("good_figure.py", False)):
            fixture = ROOT / "tests" / "fixtures" / name
            out = subprocess.run(
                [sys.executable, str(lint), str(fixture), "--json"],
                capture_output=True, text=True)
            found = json.loads(out.stdout or "{}")
            n = len(next(iter(found.values()), []))
            check((n > 0) == expect_findings,
                  f"{name}: {n} findings "
                  f"({'expected some' if expect_findings else 'expected none'})")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} check(s) failed")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
