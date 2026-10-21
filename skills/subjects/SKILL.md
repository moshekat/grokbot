---
name: subjects
description: "Use when the user talks about a subject (a person, project, admin matter, asset or place), or asks what they owe anyone, what's due, or what's next. Owns the spine, subject folders, tasks inside them, and the timeline."
---

# subjects

The spine. One folder per subject; every task belongs to exactly one subject.
Email, voice, calendar and lists are inputs to this, not separate features.

**Phase 2 status:** Markdown only. No index, no database, no `triage.py` writer.
You write the files yourself with your file tools.

## Where it lives

| Thing | Path |
|---|---|
| Spine root | `$SPINE_ROOT`, else `$HERMES_HOME/spine` (on the VM: `/opt/data/spine`) |
| Subjects | `<root>/subjects/<id>/SUBJECT.md` |
| Timeline | `<root>/subjects/<id>/timeline.md` |
| Docs | `<root>/subjects/<id>/docs/` |
| Mail | `<root>/subjects/<id>/mail/` |
| Lists | `<root>/lists/<name>.md` |

Work out the real root once with `echo "${SPINE_ROOT:-$HERMES_HOME/spine}"` and use
that absolute path for the rest of the conversation.

## Creating a subject

1. Propose the name to the user and wait. **A subject with the wrong name is worse
   than no subject.**
2. Create `<root>/subjects/<id>/` plus `timeline.md` with a first line.
3. Write `SUBJECT.md` by copying `EXAMPLE.md` from this skill's folder and
   replacing the values. Do not invent fields, do not reorder the frontmatter.
4. Run the validator (below). If it complains, fix the file and run it again.

`<id>` is lowercase, hyphenated, and matches the folder name: `medical-aid`,
`car`, `jane-doe`.

## Frontmatter

Required: `id`, `title`, `kind`, `status`, `updated`.
Optional: `next_action`, `due`, `people`, `tags`.

| Field | Values |
|---|---|
| `kind` | `person` · `project` · `admin` · `asset` · `place` |
| `status` | `active` · `waiting` · `dormant` · `done` |
| `next_action` | one imperative line, required while `status: active` |
| `due` | `YYYY-MM-DD`, the date the next action is due, not the project's |
| `people` | short tags for who is involved, `[spouse]`, `[broker]` |
| `tags` | free keywords used to match mail later, `[insurance, health]` |

Style: tabs are forbidden, two-space indents, dates unquoted, `updated` set to
today every time you touch the file.

## The operations

| Ask | What you do |
|---|---|
| "what's on my plate" / "what's due" | glob `<root>/subjects/*/SUBJECT.md`, read frontmatter, answer sorted by `due` (undated last) |
| "what's happening with X" | read `SUBJECT.md`, then the last ~10 lines of `timeline.md` |
| add a task | append a `- [ ]` line under `## Tasks` in `SUBJECT.md`, update `next_action`, `due`, `updated` |
| finish a task | tick it `- [x]` with `— done <date>`, append a timeline line, set the next `next_action` or ask what it should be |
| an event happened | append **one** line to `timeline.md` |
| status change | edit `status` in frontmatter; if it stops being `active`, drop `due` |

Answer questions from the files, not from memory of what you wrote earlier in the
conversation.

## timeline.md

Append-only, one line per event, newest at the bottom. Never rewrite or reorder it.

```
2026-10-21 — triage: accountant sent invoice #4471, due Friday
2026-10-20 — sent the signed claim form to the broker
```

Date, em dash, what happened. People and amounts stay in the line; no headings, no
bullet points, no sub-lists.

## Hard rules

- **Never delete a subject folder.** To retire one, set `status: dormant` or `done`.
- **Never rewrite `timeline.md`.** Append only. If it needs correcting, add a line
  saying so.
- **One subject, one task.** If a task fits two subjects, ask which, or split it.
- **Do not edit files under `mail/` or `docs/`** — they are dropped in, not authored.
- **Never write to `_index.db`.** It is derived and you cannot yet rebuild it; it
  does not exist in this phase.
- **Do not touch `triage.py`.** Triage labels mail on its own; it does not write
  here yet.

## Validating

After writing or editing any `SUBJECT.md`, run:

```bash
# Resolve the skill dir first; it is an external dir, not /opt/data/skills.
SKILLS=/opt/data/repo/skills/subjects          # or wherever skills.external_dirs points
/opt/hermes/.venv/bin/python "$SKILLS/validate.py"
/opt/hermes/.venv/bin/python "$SKILLS/validate.py" medical-aid
```

Exit 0 is `ok: N subject(s) valid`. Exit 1 lists every problem — fix them, don't
report success until it exits 0. Exit 2 means there is nothing to check yet.

Locally use `python3 validate.py --root /tmp/spine` instead of the container paths.

## Files

- `SKILL.md`: this file.
- `EXAMPLE.md`: the canonical subject. Copy its shape exactly.
- `validate.py`: frontmatter checker. Reads only, never writes.
