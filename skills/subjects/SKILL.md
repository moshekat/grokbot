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
| Strands and tasks | `<root>/subjects/<subject>/tasks/<id>.md`, nested freely — `tasks/geyser/quote.md` is a real node, not a subfolder to ignore |
| Log | `<root>/subjects/<id>/timeline.md` (the subject's log) |
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

## Adding a task or a strand

A task is its own file: `<root>/subjects/<subject>/tasks/<id>.md`, with `parent:`
set to the strand or subject it hangs under. Never add a `## Tasks` bullet to
`SUBJECT.md` — that was the old flat shape and it cannot hold a strand with several
live threads.

A strand is the same file with `parent:` pointing at the subject. Nesting is how
depth is expressed; there is no marker that says "this is a strand", because a
node with children *is* one.

Naming the files is a real decision, so propose it: `sign-letter`, not `task-4`.
The id is what parents, mail links and calendar events point at.

## Frontmatter

Required: `id`, `title`, `status`, `updated`.
Optional: `schema`, `parent`, `kind`, `due`, `remind_at`, `recur`, `nag`, `people`,
`tags`, `attachments`. (`next_action` is still accepted so old files validate, but it
is **deprecated**: the next action is computed from the open tasks, never stored.)

| Field | Values |
|---|---|
| `schema` | `1`. Write it. It is how a future format change gets migrated instead of misread |
| `parent` | the `id` of the node this one hangs under; **omit on a subject** |
| `kind` | `person` · `project` · `admin` · `asset` · `place` — a loose tag for matching mail, not what defines the node |
| `status` | `active` · `waiting` · `dormant` · `done` |
| `due` | `YYYY-MM-DD`, a bare date, no time |
| `remind_at` | `YYYY-MM-DDTHH:MM`, the clock. A date without a time is rejected — that is what `due` is for |
| `recur` | `after 14d` · `daily` · `weekly` · `monthly` · `yearly` |
| `nag` | `true` / `false`. Keep firing on the `recur` cadence until the node is closed |
| `people` | short tags for who is involved, `[spouse]`, `[broker]` |
| `tags` | free keywords used to match mail later, `[insurance, health]` |
| `attachments` | file names for documents this node owns, `[settlement-v3.pdf]`. Names or handles, never absolute paths |

Style: tabs are forbidden, two-space indents, dates unquoted, `updated` set to
today every time you touch the file.

### What a node is, and what a clock is

A **node is a node**: a subject, a strand and a task are the same file, and depth is
the `parent` pointer. A node with children is a strand; a node without is a task.
That is derived — never write it down.

A **task and a reminder are the same object.** The job is `status`, the children and
the log; the reminder is the clock:

- `remind_at` alone — fires once, on that date and time.
- `recur: after 14d` — fires 14 days after the node was last completed. Doing it
  resets the timer. Use this whenever the user says "every so often", "if I haven't
  spoken to her in a while", "when it's been too long". A calendar recurrence cannot
  express this.
- `recur: daily` (or weekly/monthly/yearly) + `nag: true` — keeps firing until closed.
  Use this when the user names no date but the thing must not be forgotten.

Never ask the user whether something is a task or a reminder. **They speak, you set
the fields.** The word "remind" is the cue to set a clock.

## The operations

| Ask | What you do |
|---|---|
| "what's on my plate" / "what's due" | walk every `.md` under `<root>/subjects/` except each `timeline.md` and the subjects' own body, read frontmatter, consider only `status: active`/`waiting`, answer sorted by `due` (undated last) |
| "where are we with X" | read `X`'s file, then its children, then the last ~10 lines of the log. **Answer in two lines: history, then current.** Never read a stored summary — there isn't one; compose it now from the open items and the log |
| add a task | write `<subject>/tasks/<id>.md` with `parent:`, one file per task. Do **not** append to a `## Tasks` bullet list any more |
| add a strand | a file with `parent:` pointing at its subject; tasks point at the strand |
| finish a task | set `status: done`, append a log line, set `updated` |
| snooze | move `remind_at` forward and append a log line. **Do not create a new node** — "remind me in two hours" is a snooze, not a new task |
| "call Steve again" | the existing node is still open: snooze it and log the attempt (`tried Thu, no answer`). One node accumulates attempts |
| an event happened | append **one** line to the log |
| status change | edit `status` in frontmatter; if it stops being `active`, drop `due` |

**`next_action` is not a field any more.** The next action of a strand is its hottest
open child (nearest `due`, then nearest `remind_at`, then oldest). Compute it when
asked; never store it. A stored next action goes stale and then gets read back as
current fact.

### An old `## Tasks` bullet is not a second task, and not yours to delete

Files written before this schema carry `- [ ] something — due DATE` bullets under
`## Tasks`, and a `next_action:` line. Both are **history**, and the file may say
something the new node file does not (here: the geyser check, due 2026-10-23, with no
task file at all).

- **Never delete them to remove a contradiction.** Deleting is how a real obligation
  disappears: nobody can then tell whether it was done or dropped. Both of these
  happened before `schema: 1`, so they are evidence, not clutter.
- **The task files are the truth about what is open.** A bullet with no matching
  task file means the thing was never migrated — say so, and offer to *create* the
  task file from it, preserving its `due`.
- **Migrating is a separate, explicit job.** Only when the user says "migrate home",
  do you: create one task file per open bullet (keeping `due`), append one log line
  per bullet you converted, then remove the bullet. Report each one as it goes.
- If asked to "clean up" a subject, propose the migration and wait. A subject whose
  history contradicts itself is honest; a subject whose history was quietly deleted
  is not.

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
- **Never state a fact you have not checked.** Before you say a file, folder or
  subject exists, read it. Before you say one is gone, look for it. If you did not
  look, say "I haven't checked" — do not reason from what ought to be there and
  present the conclusion as observation. A status update that blends verified
  facts with guesses is worse than no update.
- **When corrected, re-check before replying.** If the user says something is not
  there, look again and report what you actually see. Never explain the absence by
  inventing a cause ("something removed it") — you did not see that happen.

## Validating

After writing or editing any node file, run:

```bash
# Resolve the skill dir first; it is an external dir, not /opt/data/skills.
SKILLS=/opt/data/repo/skills/subjects          # or wherever skills.external_dirs points
/opt/hermes/.venv/bin/python "$SKILLS/validate.py"          # the whole spine
/opt/hermes/.venv/bin/python "$SKILLS/validate.py" divorce  # one subject and its subtree
```

Exit 0 is `ok: N node(s) valid`. Exit 1 lists every problem — fix them, don't
report success until it exits 0. Exit 2 means there is nothing to check yet.

It also checks the tree, not just the fields: a `parent` that does not exist, a
parent chain that loops, and nesting deeper than three levels (subject → strand →
task). The depth one is a warning about structure, not a broken file; say so rather
than deleting something.

Locally use `python3 validate.py --root /tmp/spine` instead of the container paths.

## Files

- `SKILL.md`: this file.
- `EXAMPLE.md`: the canonical subject. Copy its shape exactly.
- `validate.py`: frontmatter and tree checker. Reads only, never writes.
