# The task spine (designed 2026-10-21)

One assistant, organised around **subjects → tasks → (calendar, reminders, lists)**.
Email triage, voice notes, calendar and lists are all *inputs* to that spine, not
separate features that happen to share a Telegram bot.

This doc is the design. Decisions are recorded in `DECISIONS.md`; phases in
`docs/PLAN.md`.

## Why a spine

A personal assistant that only reacts is a search box. What makes an assistant
feel like one is that it knows:

- **what is on my plate** (open tasks, sorted by when they matter),
- **who/what they are about** (a subject: a person, a project, a house, a car),
- **what happened before** (the timeline and the documents).

Every request — an email needing an answer, a voice note "remind me to phone the
pharmacy", a calendar invite — lands in the same place. That is the spine.
Without it, triage dead-ends in a Gmail label and every new feature invents its
own little database.

## Three layers

Hermes' own memory is proof the layering works: a tiny bounded Markdown file
(`MEMORY.md`, 2,200 chars; `USER.md`, 1,375 chars) that is injected into every
session, plus `session_search` over SQLite FTS5 for everything else. We use the
same shape, but for subjects and tasks.

### 1. Core: the hot snapshot

A small, bounded file the assistant reads at the start of every session —
injected through `SOUL.md` or a skill preamble, the same way `MEMORY.md` is.

- Active subjects, one line each, with `next_action` and `due`.
- Open tasks that are due or overdue.
- Standing preferences already in `USER.md`.

Rule: **bounded**. If it grows past a screen, it is no longer a snapshot and has
started competing with the transcript for context. Detail belongs in the subject
file, not here.

### 2. Subject store: files first

One folder per subject, under the profile's data directory:

```
spine/
  _index.db                 # generated; safe to delete and rebuild
  subjects/
    medical-aid/
      SUBJECT.md            # YAML frontmatter + prose
      timeline.md           # append-only, one dated line per event
      docs/                 # PDFs, scans, and their OCR text
      mail/                 # linked emails, by message-id
    house/
      SUBJECT.md
      timeline.md
      ...
  lists/
    pharmacy.md
    hardware.md
    movies.md
```

`SUBJECT.md` frontmatter:

```yaml
---
id: medical-aid
title: Medical aid
kind: admin            # person | project | admin | asset | place
status: active         # active | waiting | dormant | done
next_action: "Submit the 2026 claim for the physio visit"
due: 2026-10-27
people: [spouse]
tags: [insurance, health]
updated: 2026-10-21
---
```

Why files and not a database:

- **Grep, `cat`, git, `rsync`, Nextcloud, zip.** A folder of Markdown is the only
  format that survives every tool and every decade.
- **An LLM reads Markdown natively.** No ORM, no schema migration, no "export"
  step. The model opens the file.
- **Portability is the multi-tenant story.** Handing a customer their data is
  `tar czf`. Selling the product later is a folder copy.
- **Reviewable.** The user can fix a wrong fact in a text editor.

`timeline.md` is append-only and is the audit trail: triage results, decisions,
emails sent, things the user said. One line per event, newest at the bottom.

### 3. Index: SQLite FTS5, derived and disposable

`spine/_index.db` holds a full-text index of every `SUBJECT.md`, `timeline.md`,
OCR'd document and linked email, so `session_search`-style lookup stays fast once
the store outgrows one `grep`.

Hard rule: **the index is derived.** It carries no fact the files don't have.
If it is corrupted, deleted or stale, `spine reindex` rebuilds it from the tree.
Nothing in the assistant may write to the index first and the file second.

## Why SQLite and not MySQL

- It is what Hermes already uses for sessions and `session_search` (FTS5), so
  there is one storage engine, one backup story, zero new services.
- FTS5 gives the full-text search we need with no server, no tuning, no port.
- The whole store is under one directory that is already backed up.
- MySQL/MariaDB would add a daemon, credentials and a migration path to buy
  features (concurrency, replication) that a single-tenant assistant does not
  use. Revisit only if a hosted, many-tenant version makes the case.

## How inbox triage feeds the spine

Today's triage ends at a Gmail label. It should end at a **task**.

| Triage bucket | What happens now | What happens with the spine |
|---|---|---|
| rubbish | label + Trash (shadow mode first) | unchanged |
| FYI | label | optionally append a line to the subject's `timeline.md` |
| **needs-you** | label + digest | **upsert a task** against the matched subject, with the message-id in `mail/` |

Matching is by sender address and keywords against `people`/`tags`; no match
means the assistant proposes a new subject rather than inventing one. The digest
then reads from the spine ("3 tasks due this week") instead of re-scanning Gmail.

This is the change that makes triage worth doing: the email stops being a thing
to read and becomes a thing to do.

## Lists

Lists are **first-class**, a folder next to `subjects/`, one Markdown file per
named list (pharmacy, hardware, movies). Hermes already ships what a list needs:

- a native **`todo_list`** tool for flat, unnamed todos;
- **Google Tasks** via the `google-workspace` skill, if the list should live on a
  phone;
- `product-price-monitor` for "watch this until the price drops";
- `weekly-review-planning` for the Sunday reset.

We do **not** build a list feature. We give lists a home in the spine so they
inherit search, backup, the timeline and multi-tenant export for free, and use
the native tool where a flat list is all that's asked for. The phrase "pharmacy
list" must resolve to one clearly named file, not to a scattering of todos.

## Reminders

Three channels, chosen by how much the reminder matters:

| Channel | Use | Cost |
|---|---|---|
| **Telegram digest** | batched, during working hours | free, already wired |
| **ntfy** (push to phone) | time-sensitive, quiet hours | free/self-hostable |
| **Real alarm** | must not be missed (medication, flights) | platform calendar alert |

Default is the digest; a task may ask for a channel. Nothing fires overnight
unless the user set it (same rule as the 5 daytime triage runs).

## Multi-tenant-ready, single-tenant first

Built for one person now, structured so a second person is not a rewrite.

- **Everything under the profile data dir.** The path comes from an env var, never
  a hardcoded `/opt/data`. One profile = one assistant = one spine.
- **No "user" in the data.** Facts live in files, addressed by subject id, never
  by "the user's medical aid". A second person gets a second profile, not a row
  flag.
- **Files first, config over code.** Anything that differs per installation is an
  env var (same rule as `DECISIONS.md`, 2026-10-20).
- **Export is a folder copy.** Encryption and access control belong to the VPS
  and the profile, not to the store format.
- **Hermes' own profile scoping does the heavy lifting.** Multi-profile is already
  supported upstream; we must not assume a single profile in any skill.

## What gets built, in order

1. `spine` layout + a `subjects` skill (create, list, show, update status/next
   action, append to timeline) — Markdown only, no index yet.
2. Task schema inside `SUBJECT.md` plus an inbox-wide "what's due" view.
3. `triage.py` upgraded: needs-you upserts a task with a message-id link.
4. FTS5 index + `reindex`; wire into `session_search`.
5. Calendar write (Google Calendar) and the reminder channels.
6. Lists: named-list files, then `todo_list` and Google Tasks where they fit.

## Open questions

- One `timeline.md` per subject, or per-year files once a subject gets long?
- Do linked emails store the full body (privacy, size) or just headers plus a
  pointer to Gmail (needs Gmail to stay the source of truth)?
- Does the snapshot live inside `SOUL.md`, or a separate `CORE.md` the skill
  loads? Editing `SOUL.md` on the server is the current deploy path, which
  argues for a separate file.
