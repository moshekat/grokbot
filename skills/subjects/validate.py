#!/usr/bin/env python3
"""Validate a node against the spine schema.

Not a CLI for the data, just a guard rail: the model writes Markdown, this says
whether the frontmatter is well formed and whether the tree hangs together. It
never writes anything.

    validate.py                      # every node under the spine root
    validate.py home                 # one node and its subtree
    validate.py --root /tmp/spine    # a different tree

A "node" is one `SUBJECT.md` at any depth. Subjects, strands and tasks are the
same shape; depth is a `parent:` pointer. See docs/FRONT-PAGE.md.

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

SCHEMA = 1
MAX_DEPTH = 3  # subject -> strand -> task; deeper only warns

REQUIRED = ("id", "title", "status", "updated")
OPTIONAL = (
    "schema", "parent", "kind", "next_action",
    "due", "remind_at", "recur", "nag",
    "people", "tags", "attachments",
)
KINDS = {"person", "project", "admin", "asset", "place"}
STATUSES = {"active", "waiting", "dormant", "done"}
# "after 14d" = interval since completion; the others are calendar cadences.
RECUR_RE = re.compile(r"^(after \d+d|daily|weekly|monthly|yearly)$")
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)



def default_root() -> Path:
    """The spine root: $SPINE_ROOT, else next to Hermes' data dir."""
    env = os.environ.get("SPINE_ROOT")
    if env:
        return Path(env)
    home = os.environ.get("HERMES_HOME") or os.environ.get("HERMES_DATA") or "/opt/data"
    return Path(home) / "spine"


def check_one(path: Path, node_id: str | None = None) -> list[str]:
    """Return a list of problems for one node file. Empty means good.

    node_id is the node's `id`; it is the folder name for a subject and for a
    task, so the same check applies at every depth.
    """
    problems: list[str] = []
    expected = node_id or path.parent.name
    text = path.read_text(encoding="utf-8")

    m = FM_RE.match(text)
    if not m:
        return [f"{expected}: no YAML frontmatter block at the top of the file"]

    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        return [f"{expected}: frontmatter is not valid YAML: {exc}"]
    if not isinstance(data, dict):
        return [f"{expected}: frontmatter must be key/value pairs, got {type(data).__name__}"]

    label = expected  # problems are reported against the id we already know

    for key in REQUIRED:
        if key not in data or data[key] in (None, ""):
            problems.append(f"{label}: missing required field '{key}'")

    unknown = set(data) - set(REQUIRED) - set(OPTIONAL)
    if unknown:
        problems.append(f"{label}: unknown field(s) {sorted(unknown)}; allowed: "
                        f"{sorted(set(REQUIRED) | set(OPTIONAL))}")

    schema = data.get("schema")
    if schema is not None:
        if not isinstance(schema, int) or schema != SCHEMA:
            problems.append(f"{label}: schema is '{schema}', this validator reads {SCHEMA}")

    sid = data.get("id")
    if isinstance(sid, str) and not ID_RE.match(sid):
        problems.append(f"{label}: id '{sid}' must be lowercase-hyphenated, e.g. 'medical-aid'")
    if isinstance(sid, str) and sid != label:
        problems.append(f"{label}: id '{sid}' does not match the folder name '{label}'")

    # `kind` is no longer what says what a node is — depth does (has children =>
    # strand, none => task). It is kept as an optional tag for matching mail, so a
    # value outside the known words is a typo rather than a different kind of thing.
    kind = data.get("kind")
    if kind not in (None, "") and kind not in KINDS:
        problems.append(f"{label}: kind '{kind}' is not one of {sorted(KINDS)}")

    status = data.get("status")
    if status not in (None, "") and status not in STATUSES:
        problems.append(f"{label}: status '{status}' is not one of {sorted(STATUSES)}")

    # YAML turns an unquoted 2026-10-27 into a date; accept either, reject junk.
    for key in ("due", "updated"):
        val = data.get(key)
        if val in (None, ""):
            continue
        if isinstance(val, dt.datetime):
            problems.append(f"{label}: '{key}' has a time; use a bare date (YYYY-MM-DD)")
        elif isinstance(val, dt.date):
            pass
        elif isinstance(val, str):
            try:
                dt.date.fromisoformat(val)
            except ValueError:
                problems.append(f"{label}: '{key}' is '{val}', not a YYYY-MM-DD date")
        else:
            problems.append(f"{label}: '{key}' must be a YYYY-MM-DD date, got {type(val).__name__}")

    # remind_at is the only field that carries a time, because a clock needs one.
    remind = data.get("remind_at")
    if remind not in (None, ""):
        if isinstance(remind, dt.datetime):
            pass
        elif isinstance(remind, dt.date):
            problems.append(f"{label}: remind_at '{remind}' has no time; use YYYY-MM-DDTHH:MM "
                            f"(a bare date is what 'due' is for)")
        elif isinstance(remind, str):
            try:
                dt.datetime.fromisoformat(remind)
            except ValueError:
                problems.append(f"{label}: remind_at '{remind}' is not YYYY-MM-DDTHH:MM")
        else:
            problems.append(f"{label}: remind_at must be YYYY-MM-DDTHH:MM, "
                            f"got {type(remind).__name__}")

    recur = data.get("recur")
    if recur not in (None, ""):
        if not isinstance(recur, str) or not RECUR_RE.match(recur):
            problems.append(f"{label}: recur '{recur}' is not one of "
                            f"'after <n>d', 'daily', 'weekly', 'monthly', 'yearly'")

    nag = data.get("nag")
    if nag is not None and not isinstance(nag, bool):
        problems.append(f"{label}: nag must be true or false, got {nag!r}")

    for key, sample in (("people", "spouse"), ("tags", "insurance"),
                        ("attachments", "settlement-v3.pdf")):
        val = data.get(key)
        if val is not None and not isinstance(val, list):
            problems.append(f"{label}: '{key}' must be a list, e.g. {key}: [{sample}]")

    return problems


def discover(subjects: Path) -> dict[str, Path]:
    """Every node file under a subject, keyed by the id in its frontmatter.

    Subjects are `<root>/subjects/<id>/SUBJECT.md`; a node deeper down is
    `<root>/subjects/<top>/tasks/<id>.md` at any depth. The folder name is only a
    fallback id — the frontmatter wins, because that is what references point at.
    """
    found: dict[str, Path] = {}
    for path in sorted(subjects.rglob("SUBJECT.md")):
        found[path.parent.name] = path
    for path in sorted(subjects.rglob("tasks/*.md")):
        found[path.stem] = path
    return found


def read_fm(path: Path) -> dict:
    """Frontmatter as a dict, or {} if it cannot be read. Never raises."""
    try:
        m = FM_RE.match(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return {}
    if not m:
        return {}
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def check_tree(nodes: dict[str, Path], root_id: str | None = None) -> list[str]:
    """Parent links, cycles and the depth cap across the whole tree.

    node_id is the frontmatter `id` where there is one, so a rename does not break
    a parent pointer as long as the frontmatter still matches.
    """
    problems: list[str] = []
    ids = {nid: read_fm(p).get("id") or nid for nid, p in nodes.items()}
    by_id = {v: k for k, v in ids.items()}  # frontmatter id -> node key

    parents: dict[str, str | None] = {}
    for key, path in nodes.items():
        parent = read_fm(path).get("parent")
        if parent in (None, ""):
            parents[key] = None
            continue
        parent = str(parent)
        if parent not in by_id:
            problems.append(f"{key}: parent '{parent}' does not exist "
                            f"(no node declares that id)")
            parents[key] = None
            continue
        parents[key] = by_id[parent]

    # Cycles: walk up from each node; a repeat means the tree is not a tree.
    for key in nodes:
        seen = [key]
        cur = parents.get(key)
        while cur is not None:
            if cur in seen:
                loop = " -> ".join(seen[seen.index(cur):] + [cur])
                problems.append(f"{key}: parent chain is a cycle: {loop}")
                break
            seen.append(cur)
            cur = parents.get(cur)

    # Depth: a root is depth 0. Report only if it is reachable without a cycle.
    for key in nodes:
        depth, seen, cur = 0, {key}, parents.get(key)
        while cur is not None and cur not in seen:
            depth += 1
            seen.add(cur)
            cur = parents.get(cur)
        else:
            if cur is None and depth > MAX_DEPTH:
                problems.append(f"{key}: {depth} levels deep; the cap is {MAX_DEPTH} "
                                f"(subject -> strand -> task). Flatten it or confirm it.")

    if root_id:
        wanted = by_id.get(root_id, root_id)
        if wanted not in nodes:
            problems.append(f"{root_id}: no such node")
        else:
            # This node, anything reachable from it *and* anything that sits
            # inside its folder. Location matters: a node with a broken or cyclic
            # parent is still part of the subject it lives in, and filtering it
            # out would hide exactly the problems the user asked to see.
            keep = {wanted}
            changed = True
            while changed:
                changed = False
                for key, parent in parents.items():
                    if parent in keep and key not in keep:
                        keep.add(key)
                        changed = True
            container = nodes[wanted].parent
            is_subject = nodes[wanted].name == "SUBJECT.md"
            for key, path in nodes.items():
                if path == nodes[wanted]:
                    keep.add(key)
                elif is_subject and container in path.parents:
                    # A subject owns everything filed under its folder.
                    keep.add(key)
            problems = [p for p in problems
                        if p.split(":", 1)[0] in keep]
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate nodes in the spine.")
    ap.add_argument("node", nargs="?", help="node id; its subtree if given, all if omitted")
    ap.add_argument("--root", type=Path, default=None, help="spine root (default: $SPINE_ROOT)")
    ap.add_argument("--quiet-depth", action="store_true",
                    help="do not warn about trees deeper than the cap")
    args = ap.parse_args()

    root = args.root or default_root()
    subjects = root / "subjects"
    if not subjects.is_dir():
        print(f"no subjects directory at {subjects}", file=sys.stderr)
        return 2

    nodes = discover(subjects)
    if not nodes:
        print(f"no subjects in {subjects}", file=sys.stderr)
        return 2

    if args.node:
        match = [k for k, p in nodes.items()
                 if k == args.node or read_fm(p).get("id") == args.node]
        if not match:
            print(f"no such node: {args.node}", file=sys.stderr)
            return 2

    problems: list[str] = []
    for key, path in nodes.items():
        problems.extend(check_one(path, node_id=key))

    tree = check_tree(nodes, args.node)
    if args.quiet_depth:
        tree = [p for p in tree if "levels deep" not in p]
    problems.extend(tree)

    if problems:
        print(f"{len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print(f"ok: {len(nodes)} node(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
