# The front page (designed 2026-10-24)

The spine described in `docs/TASK-SPINE.md` is a store of subjects and tasks. This
doc is about **how it is read**: what the assistant shows, at what depth, and how a
thing reaches the user without being asked for.

It supersedes nothing in `TASK-SPINE.md`; it replaces the flat task schema sketched
there. Decisions are recorded in `DECISIONS.md`.

## The problem this solves

The first version of the spine had one flat `## Tasks` list per subject and a single
`next_action` in frontmatter. That works for one person with three or four open
things. It fails at real life:

- a single matter has **several live strands at once** (divorce: three letters out,
  a lawyer we are waiting on, and a decision still to make) and frontmatter holds
  exactly one `next_action`;
- the user cannot decide whether something is a **task** or a **reminder**, because
  in their head they are partly the same and partly not;
- nothing **comes to the user**. A list you have to remember to open loses to a
  phone that taps you. This user has ADHD and said so plainly: managing this is
  hard, and the system must do the remembering.

The answer is not a better filing system. It is a **newspaper**: headlines on the
front page, detail behind them, and the hot ones pushed at the user.

## One node type, rendered as a newspaper

There are no separate "subject", "strand" and "task" formats. There is **one node**,
and depth is a `parent` pointer.

```
Subjects                    depth 0   (no parent)          war, divorce, home
  Strands                   depth 1   (parent: war)        logistics, ammunition
    Tasks                   depth 2   (parent: logistics)  book the truck
      Subtasks              depth 3   (rare)
```

Everything above a leaf is a **strand**; a leaf is a **task**. That is the only
distinction and it is *derived*: a node with children is a strand, a node without is
a task. It is never stored, so a strand whose children all close becomes a task by
itself, with no bookkeeping.

**Why this is the flexible shape.** The same file layout serves level 0 and level 3.
Moving a task between strands, splitting a strand out of a subject, or adding a
fourth level are all edits to a `parent:` line: not a schema change, not a
migration. When storage has to change (see "The storage seam"), the node does not.

### Cap: three levels

Past three levels a headline stops being scannable and becomes a filing cabinet. The
validator **warns** past depth 3 (subject → strand → task is two edges) but does not
refuse: the user may have a real reason.

## The three parts of every level

Every node renders the same way, at every depth:

| Part | What it is | Where it comes from |
|---|---|---|
| **Headline** | one line, the thing that grabs you | the node's `title` |
| **Subhead** | one or two lines: who is involved, what changed, what is blocked | rendered from the node's children and recent log |

## History and current: the two lines

When the user asks "where are we with X", the answer is exactly two lines.

- **History**: one line, past tense. *"Writing three letters; spoken to the lawyer;
  waiting for his reply."*
- **Current**: one line, the next thing. *"We should probably send him a reminder."*

Both are **rendered when asked, from live data**, and never stored:

- history = the node's closed children plus its most recent `## Log` entries,
  condensed;
- current = the node's hottest open child (nearest `due`, then nearest `remind_at`,
  then oldest open).

**Storing a summary is forbidden.** A stored one-line history is a cache with no
invalidation, and it will be read back a week later as though it were still true.
This is the same drift that already bit us in triage (identical input classified
`7/14/22`, then `5/15/23` an hour later). Anything the user reads is computed at
read time.

## Tasks and reminders are the same object

The user's own words: *"they're sort of the same thing, but sort of different"*.
They are right, and the difference is not in what the thing **is** but in how it
**reaches them**.

One node, two aspects:

- a **job** to finish (the task aspect): `status`, children, `## Log`;
- a **clock** that pokes the user (the reminder aspect): `remind_at`, `recur`, `nag`.

| The user says | What is created |
|---|---|
| "remind me to call Steve in two hours" | clock + job |
| "do my taxes" | job, no clock |
| "phone my sister, she gets sore after two weeks" | job + 14-day interval-since-completion |
| "take my pills" | trivial job + daily clock |
| "remind me in two hours, I'm busy" | **snooze** on an existing node |

**The user never files into a bucket.** They speak; the assistant sets the flags. The
word "remind" is the cue to set a clock.

### Three clock modes

1. **fixed**: `remind_at: 2026-10-24T15:00`. Fires once.
2. **interval since completion**: `recur: after 14d`, anchored on the node's last
   completion. Doing the three-minute call resets the timer. This is the sister case,
   and it cannot be expressed as a calendar recurrence, which is why it is our own
   field.
3. **nag until done**: `nag: true` with a `recur` cadence. Fires on the cadence until
   the node is closed. This is the taxes case: a job with no date the user will
   honour needs the system to keep asking.

Default is the daytime digest; overnight is silence unless the user set a time (same
rule as the five triage runs).

### Snooze is first-class

For someone who gets pulled off mid-task, "remind me in two hours" is the most-used
button in the system and must be the cheapest: one sentence, no ceremony, no new
node, no confirmation. It moves `remind_at` and logs the fact.

### "Call Steve again"

Not a new node and not a separate reminder. The existing node is still open; "again"
means: **snooze it, and append a line to its log** (*"tried Thu, no answer"*). One
node that accumulates attempts holds the story; three nodes called *call Steve*
fragment it.

| **Bulk** | the detail: context, children, documents, mail | `## Context`, children, `docs/`, `mail/` |

The user only ever sees the first two until they ask. "Remind me where we are with
war" reads the bulk. That is the drill-down loop:

```
front page   →  "Divorce: sign the letter"                      (headline)
push it      →  history + current, two lines                     (subhead)
push again   →  context, children, log, files                    (bulk)
```

## The four views

Four doors, each of which takes the user somewhere real. They are four **views over
one spine**, not four stores.

1. **Today**: the front page. Everything firing or overdue now, plus what today's
   mail changed. Headlines only.
2. **Subjects**: the sections, one headline each (war, divorce, home, cool-ideas).
   Push one to go deeper.
3. **Inbox**: what came in, and the reconciliation. Does it fit an existing task,
   does it change one, were we waiting for this receipt and it arrived.
4. **Say**: capture anything. "Remind me in two hours", "add to the pharmacy list".
   Zero ceremony, no subject required.

## Two background agents

Neither is a new store; both are the spine being read and written.

- **The reconciler**: on each triage run, folds that run's mail into the spine and
  prints the **deltas as headlines**. *"receipt arrived → loop closed"*, *"Cool Ideas
  suspended → the account strand just changed"*. This is the user's "were we waiting
  for a receipt and got the receipt": the spine notices the loop close and says so,
  instead of the user remembering to check.
- **The alarm**: pushes the headlines whose clocks fire. It reads `remind_at`,
  `recur` and `nag` across the tree and delivers per the channel table in
  `TASK-SPINE.md`.

## The node file

One file per node, the same shape at every depth:
`spine/subjects/<subject>/tasks/<id>.md`.

```yaml
---
schema: 1
id: sign-letter
title: Sign the settlement letter
parent: finalise-divorce        # omit for a subject (depth 0)
status: active                  # active | waiting | dormant | done
due: 2026-10-31                 # optional
remind_at: 2026-10-25T09:00     # optional; the clock
recur: ""                       # optional: "daily", "after 14d"
nag: false                      # optional
people: [lawyer]                # optional
attachments: [settlement-v3.pdf]  # optional; handles, not paths
updated: 2026-10-24
---

## Context

The bulk. Anything the user or the assistant needs to understand this node later:
what the lawyer said, why we chose this, what is blocked and on whom.

## Log

2026-10-22 — lawyer's PA said Wednesday is dead, call before 10
2026-10-20 — third letter drafted
```

`## Log` is append-only and is the raw material for the one-line history. `## Context`
is the "bulk" the user is talking about when they say *"keep track of all the context
in that task"*.

**This schema does not exist yet.** `validate.py` today accepts only
`id, title, kind, status, updated, next_action, due, people, tags`, and rejects any
unknown field. `schema`, `parent`, `remind_at`, `recur`, `nag` and `attachments` are
new in step 1, and `kind` becomes derived rather than required. Until that step lands,
writing any of these fields into a real subject fails validation by design — the
validator is doing its job.

## The storage seam

The user asked for the shape to be changeable later: specifically, if a node stops
being a Markdown file and needs to own PDFs and documents in a way that file paths
cannot express.

Four rules, each cheap now and expensive later:

1. **One seam.** All spine access goes through a single module (`spine/store.py` when
   it exists) exposing verbs: `list_nodes`, `get_node`, `save_node`, `children_of`,
   `attach`, `append_log`. Nothing else touches the filesystem. If a node later
   becomes a row, one file is rewritten.
2. **Identity is an id, never a path.** `sign-letter` is the reference held by
   parents, mail links and calendar events. The path is an implementation detail of
   the current backend. Paths leaking into references is the *cause* of the migration
   pain the user is worried about, so design them out now.
3. **Attachments are opaque handles.** A node records
   `attachments: [settlement-v3.pdf]` plus a resolver, never an absolute path. Today
   the resolver returns a filesystem path; tomorrow a Nextcloud URL or a blob key.
   The node file does not change shape.
4. **A schema version.** `schema: 1` in frontmatter, and the validator reads both
   versions during a change. Without a version marker a format change silently
   misreads every existing file, and `home` is already real data.

What this is **not**: an abstract store interface with swappable backends written
before a second backend exists. That is how a system becomes mediocre at two things
and debuggable at neither. The seam exists and has one implementation until a real
second one appears.

## What gets built, in order

1. **The node schema**: `tasks/<id>.md` under a subject, `schema: 1`, `parent`, kind
   derived, clocks optional. `EXAMPLE.md` and `validate.py` extended; the validator
   gains tree checks (orphan, cycle, missing parent, depth warning).
2. **The renderer**: one module that turns a node into headline / subhead /
   history+current. One place decides what is a headline and what is detail, so the
   front page and the drill-down cannot disagree.
3. **`Today`**: the front page, built on the renderer.
4. **`Say`**: quick capture, so all four doors do something real.
5. **The reconciler**: triage → deltas as headlines.
6. **The alarm**: last, because it needs 1–5 to have something to push.

`next_action` in frontmatter is **removed** by step 1, not kept in parallel: it is
the stored-cache mistake at subject level, and it already duplicates `## Tasks`. The
headline is computed instead.

## Open questions

- **The middle level's name.** "Strand" is the working word. Alternatives: "area",
  "line", "thread". It only matters because the user has to say it.
- **Where does "current" look when a strand has three equally hot children?** The
  order above (due, then `remind_at`, then oldest) is a guess and needs real data.
- **Does the reconciler propose spine changes or make them?** Proposing is safer, but
  a morning queue of proposals reintroduces the very thing that fails for this user.
  Leaning: make additive changes silently, propose only deletions and re-parenting.
- **Time zones and the alarm.** Everything is CAT today; a sold product is not.

