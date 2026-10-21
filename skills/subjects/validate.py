#!/usr/bin/env python3
"""Validate a subject folder against the spine schema.

Not a CLI for the data, just a guard rail: the model writes Markdown, this says
whether the frontmatter is well formed. It never writes anything.

    validate.py                      # every subject under the spine root
    validate.py medical-aid          # one subject
    validate.py --root /tmp/spine    # a different tree

Exit codes: 0 clean, 1 problems found, 2 nothing to check.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - yaml ships with Hermes
    sys.exit("yaml is missing: run this with /opt/hermes/.venv/bin/python")

REQUIRED = ("id", "title", "kind", "status", "updated")
OPTIONAL = ("next_action", "due", "people", "tags")
KINDS = {"person", "project", "admin", "asset", "place"}
STATUSES = {"active", "waiting", "dormant", "done"}
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def default_root() -> Path:
    """The spine root: $SPINE_ROOT, else next to Hermes' data dir."""
    env = os.environ.get("SPINE_ROOT")
    if env:
        return Path(env)
    home = os.environ.get("HERMES_HOME") or os.environ.get("HERMES_DATA") or "/opt/data"
    return Path(home) / "spine"


def check_one(path: Path) -> list[str]:
    """Return a list of problems for one SUBJECT.md. Empty means good."""
    problems: list[str] = []
    name = path.parent.name
    text = path.read_text(encoding="utf-8")

    m = FM_RE.match(text)
    if not m:
        return [f"{name}: no YAML frontmatter block at the top of the file"]

    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        return [f"{name}: frontmatter is not valid YAML: {exc}"]
    if not isinstance(data, dict):
        return [f"{name}: frontmatter must be key/value pairs, got {type(data).__name__}"]

    for key in REQUIRED:
        if key not in data or data[key] in (None, ""):
            problems.append(f"{name}: missing required field '{key}'")

    unknown = set(data) - set(REQUIRED) - set(OPTIONAL)
    if unknown:
        problems.append(f"{name}: unknown field(s) {sorted(unknown)}; allowed: "
                        f"{sorted(set(REQUIRED) | set(OPTIONAL))}")

    sid = data.get("id")
    if isinstance(sid, str) and not ID_RE.match(sid):
        problems.append(f"{name}: id '{sid}' must be lowercase-hyphenated, e.g. 'medical-aid'")
    if isinstance(sid, str) and sid != name:
        problems.append(f"{name}: id '{sid}' does not match the folder name '{name}'")

    kind = data.get("kind")
    if kind not in (None, "") and kind not in KINDS:
        problems.append(f"{name}: kind '{kind}' is not one of {sorted(KINDS)}")

    status = data.get("status")
    if status not in (None, "") and status not in STATUSES:
        problems.append(f"{name}: status '{status}' is not one of {sorted(STATUSES)}")

    # YAML turns an unquoted 2026-10-27 into a date; accept either, reject junk.
    for key in ("due", "updated"):
        val = data.get(key)
        if val in (None, ""):
            continue
        if isinstance(val, dt.datetime):
            problems.append(f"{name}: '{key}' has a time; use a bare date (YYYY-MM-DD)")
        elif isinstance(val, dt.date):
            pass
        elif isinstance(val, str):
            try:
                dt.date.fromisoformat(val)
            except ValueError:
                problems.append(f"{name}: '{key}' is '{val}', not a YYYY-MM-DD date")
        else:
            problems.append(f"{name}: '{key}' must be a YYYY-MM-DD date, got {type(val).__name__}")

    for key, sample in (("people", "spouse"), ("tags", "insurance")):
        val = data.get(key)
        if val is not None and not isinstance(val, list):
            problems.append(f"{name}: '{key}' must be a list, e.g. {key}: [{sample}]")

    if data.get("status") == "active" and not data.get("next_action"):
        problems.append(f"{name}: status is 'active' but there is no next_action")

    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate subject folders for the spine.")
    ap.add_argument("subject", nargs="?", help="subject id (folder name); all if omitted")
    ap.add_argument("--root", type=Path, default=None, help="spine root (default: $SPINE_ROOT)")
    args = ap.parse_args()

    root = args.root or default_root()
    subjects = root / "subjects"
    if not subjects.is_dir():
        print(f"no subjects directory at {subjects}", file=sys.stderr)
        return 2

    if args.subject:
        targets = [subjects / args.subject / "SUBJECT.md"]
        missing = [t for t in targets if not t.is_file()]
        if missing:
            print(f"no such subject: {args.subject} (looked for {targets[0]})", file=sys.stderr)
            return 2
    else:
        targets = sorted(subjects.glob("*/SUBJECT.md"))
        if not targets:
            print(f"no subjects in {subjects}", file=sys.stderr)
            return 2

    problems: list[str] = []
    for path in targets:
        problems.extend(check_one(path))

    if problems:
        print(f"{len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print(f"ok: {len(targets)} subject(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
