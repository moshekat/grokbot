# Decision log
Append-only. Newest entries go at the bottom. Format: date, decision, reason, status.

## 2026-10-20: "GROC bot" means SpaceXAI's Grok Bot
- Reason: the folder name and the user's dictation match the product launched 2026-08-11.
- Status: assumed; the user should confirm.

## 2026-10-20: don't write a Grok Bot clone from scratch
- Reason: Grok Bot is closed-source. Mature open-source equivalents already exist (OpenClaw ~393k stars, Hermes ~255k, Rakazo ~4.8k).
- Status: proposed; waiting on the user.

## 2026-10-20: run a buy-versus-self-host bake-off on 3–5 real jobs before committing
- Reason: the right choice depends on our use cases, cost tolerance and how much we trust Grok Bot with our logins.
- Status: proposed; waiting on the user.

## 2026-10-20: the goal is personal productivity, with an eye to selling later
- Source: the user.
- Status: decided.

## 2026-10-20: self-host Hermes Agent on the Proxmox server; no Grok Bot trial for now
- Reason: the jobs (Gmail, Calendar, voice-to-email, local hard-drive dedup) suit API skills and local scripts, not Grok Bot's cloud browser. Hermes has a gateway with voice transcription, cron, any-model support and an MIT licence.
- Supersedes: the "bake-off" proposal above.
- Status: proposed; waiting on the user's go-ahead.

## 2026-10-20: model = DeepSeek (the user's existing key); default deepseek-flash
- Reason: estimated $3–10/month for the planned jobs.
- Caveat: privacy. Revisit before handling client data.
- Status: decided.

## 2026-10-20: bot channel = Telegram, not WhatsApp
- Reason: the user dislikes WhatsApp for machine-to-machine use. WhatsApp bots need unofficial bridges (ban risk) or the paid Business API.
- Status: proposed.

## 2026-10-20: the drive-dedup job is a deterministic hash-index script, not an LLM task
- Reason: accuracy, near-zero cost, and the drives are local while Nextcloud is remote.
- Status: proposed.

## 2026-10-20: email deletion = Gmail Trash only (recoverable for 30 days); shadow mode first; sending always needs approval
- Status: proposed.

## 2026-10-20: this repo is on GitHub, public, as `moshekat/grokbot`
- Reason: the user asked for it to be pushed there. It holds research, planning and (later) our skills and tools, so it can be shared and sold from.
- Consequence: infrastructure specifics (Proxmox host IP and hostname, personal email addresses) were stripped from `PROGRESS.md` and `docs/PLAN.md` before the first push. Those details stay in the private ProxHetz repo and the user's own notes.
- Rule: keep it that way. No secrets, no host details, no client data in this repo.
- Status: decided.

## 2026-10-20: install Hermes from the official Docker image, pinned by tag
- Reason: `nousresearch/hermes-agent` is published on Docker Hub with version tags (current release `v0.22.2`) and keeps all state in a `/opt/data` volume. A pinned image makes updates deliberate and rollback a tag change, and keeps the agent off the VM's host OS on a production server.
- Alternative kept: the install script plus `hermes gateway install` (a systemd service), if the container's isolation blocks a skill.
- Status: proposed; execute only after the user's go-ahead for Phase 1.

## 2026-10-20: no separate Whisper; use Hermes' built-in voice transcription first
- Reason: the Telegram gateway transcribes voice notes itself, so installing Whisper on the VM adds cost and maintenance for no gain until its quality is proven poor.
- Status: proposed.

## 2026-10-20: VM size 2–4 vCPU / 4–8 GB, Ubuntu 24.04, disk on `FourTStorage`
- Reason: no local model, no GPU, no browser work; the load is API calls and cron. The `vms` pool is 72% full.
- Supersedes: the earlier "4 vCPU / 8 GB, 50 GB" suggestion, which stays the ceiling.
- Status: superseded by the VM 123 spec below (settled at 2 vCPU / 4 GB / 30 GB).

## 2026-10-20: VM 123 `ai-assistant` is a full QEMU/KVM VM, not an LXC container
- Spec: Ubuntu 24.04, 2 vCPU, 4 GB RAM, 30 GB disk on `FourTStorage`, OVMF/q35, cloud-init with the standard key, admin `greyroot` (sole login, passwordless sudo, `PermitRootLogin no`), QEMU agent, `onboot=1`, timezone `Africa/Johannesburg`, a Kea DHCP reservation in the server's guest range (the exact address is in the private ProxHetz notes, not here), NetBird peer, no public ingress. The user creates the VM per the ProxHetz protocols; the container work happens after that.
- Reason: Hermes runs in Docker, which needs a real kernel/namespace stack on this host; and the bot holds mail and calendar credentials plus shell access, so it belongs behind a VM boundary rather than in a shared container host. Mirrors the existing VM 199 pattern.
- Status: decided. The VM does not exist yet.

## 2026-10-20: the inbox runs 5× per day, daytime only, in CAT
- Times: **08:00, 10:30, 13:00, 15:30, 17:30 Africa/Johannesburg** (UTC+2, no DST). Nothing overnight.
- Reason: the user's own working hours; a digest at 3 a.m. is noise, and an overnight run only creates stale labels by morning.
- Status: proposed; the times are the user's to change.

## 2026-10-20: container clock and cron in `Africa/Johannesburg`
- Reason: `TZ=Africa/Johannesburg` in the compose file, and the Hermes host runs the same zone. Cron expressions then mean what they read, and there is no mental arithmetic between UTC and CAT when reading logs.
- Status: decided (implemented in `deploy/docker-compose.yml`).

## 2026-10-20: our code lives in this repo; configuration and secrets live on the VM; the client platform repo is not involved
- Split:
  - **This repo (`grokbot`, public):** the generic, portable skills, scripts and deploy config. Nothing instance-specific is hardcoded; the inbox address, OAuth client, targets and schedule arrive as environment variables.
  - **The VM (`/srv/hermes`):** `/srv/hermes/.env` (mode 600) with the real values, plus `/srv/hermes/data`, which holds Hermes' own memory, sessions and any skills it writes for itself.
  - **`greyonion-platform` (private):** untouched by this project. It is the client platform monorepo (Java: banking, DocBot, Wholesome, Grit); the assistant is neither a client app nor buildable with it.
- Reason: the assistant holds the user's personal mail and calendar. Mixing that with client production code would couple two very different release and secrets lifecycles, and would sink a potentially sellable tool into a private client repo. Keeping the code generic in public and the instance values private is also exactly what makes it reusable by someone else later.
- Rule: if a value differs per installation, it goes in `.env`; if it is a generic rule or behaviour, it goes in the repo.
- Status: decided.

## 2026-10-20: skills are Markdown instructions plus, where needed, a Python script
- Reason: Hermes is Python, so our scripts sit alongside it with no extra runtime (the `.gitignore` already covers `.venv/` and `requirements.txt`). The split keeps the *judgment* (the `SKILL.md` rules) editable by someone who doesn't read Python, and the *mechanics* (API calls, hashing) testable without an LLM in the loop.
- Libraries: `google-auth` + `google-api-python-client` for Gmail, Calendar and Tasks; the standard library (`hashlib`, `sqlite3`, `pathlib`) for drive dedup. No LLM SDK: the model is reached through Hermes, not through our code.
- Status: decided.

## 2026-10-21: one assistant with a task spine; email, voice, calendar and lists are inputs to it
- Shape: **subjects → tasks → calendar / reminders / lists**. A subject is a person, project, admin matter, asset or place; a task belongs to a subject; email triage, voice notes and calendar invites all land in the same store. Design in `docs/TASK-SPINE.md`.
- Reason: the four jobs in `docs/PLAN.md` were listed as separate features. In practice every one of them produces the same two things — an **open task** and a **fact about a subject** — and without a shared spine triage dead-ends in a Gmail label and each new feature grows its own storage.
- Consequence: `triage.py`'s needs-you bucket upserts a task instead of only labelling. The digest reads from the spine.
- Status: decided.

## 2026-10-21: the subject store is files first (Markdown + YAML), with a derived SQLite FTS5 index; no MySQL
- Layout: one folder per subject under the profile data dir, each with `SUBJECT.md` (frontmatter: `id`, `title`, `kind`, `status`, `next_action`, `due`, `people`, `tags`), an append-only `timeline.md`, `docs/` and `mail/`. A sibling `lists/` folder holds named lists. A bounded "hot snapshot" of active subjects and due tasks is injected each session, mirroring how Hermes injects its own `MEMORY.md`.
- Index: `spine/_index.db`, SQLite **FTS5** — the engine Hermes already uses for `session_search` — and **derived**: it may be deleted and rebuilt (`spine reindex`) and must never hold a fact the files don't.
- Reason: Markdown is readable by the model without an ORM, fixable by the user in a text editor, and survives `grep`, git, rsync, Nextcloud and tar. Export to a future customer is a folder copy. MySQL would add a daemon, credentials and migrations to buy concurrency a single-tenant assistant doesn't use.
- Revisit: only if a hosted many-tenant version makes the case.
- Status: decided.

## 2026-10-21: lists are first-class, but we build no list feature
- What we use instead: Hermes' native **`todo_list`** tool for flat todos, the `google-workspace` skill (Google Tasks) when a list should live on a phone, `product-price-monitor` for "watch until the price drops", `weekly-review-planning` for the weekly reset.
- What we add: one Markdown file per **named** list (`pharmacy`, `hardware`, `movies`) under `spine/lists/`, so a name always resolves to one file and the list inherits search, backup and export.
- Reason: a name like "the pharmacy list" needs one unambiguous home; a flat todo tool has no names.
- Status: decided.

## 2026-10-21: single-tenant first, multi-tenant-ready
- Rules: the data path comes from an env var (never a hardcoded `/opt/data`); no fact is stored as "the user's X" — facts hang off a subject id; one profile = one assistant = one spine, so a second person is a second profile, not a row; per-installation values stay env vars; export is a folder copy.
- Reason: building for one user now is the fastest path to something that works, but a second family member or a customer is the likely next step (`docs/research/2026-10-21-market.md`), and these are cheap constraints now and an expensive rewrite later.
- Status: decided.

## 2026-10-21: reminders use three channels by importance
- **Telegram digest** (default, batched, working hours), **ntfy** push for time-sensitive items, **real calendar alarm** for things that must not be missed (medication, flights). Nothing fires overnight unless the user asked for it.
- Reason: one channel either under- or over-alerts. A digest is right for most tasks; a calendar alarm is the only thing a phone will actually wake you for.
- Status: proposed.

## 2026-10-21: the spine ships as Markdown rules first, no CLI yet
- First slice: `skills/subjects/` with `SKILL.md` rules, a canonical `EXAMPLE.md` the model copies, and a read-only `validate.py` that checks frontmatter. No `spine.py`, no index, no `triage.py` writer.
- Reason: the operations that deserve code aren't known yet. A week of real use names them; writing the CLI now would be guessing at an API. The one thing that *does* warrant code is validation, because a malformed `SUBJECT.md` is silent otherwise.
- Graduate to `spine.py` when either: the model gets frontmatter wrong more than once in ~10 subjects, or a computed view is wanted (e.g. "everything due in the next 7 days across all subjects"). The second will come first.
- Ship skills via `skills.external_dirs` in `config.yaml`, not a copy into `/opt/data/skills`, so the repo stays the source of truth and a `git pull` + restart is the whole update.
- Status: decided.

## 2026-10-21: deploy-time corrections (verified on `ai-assistant`)
- External skill dirs are **read-only** (the container's own `config.yaml` says so), so the "git pull plus restart" update path above is wrong: an update is a tar copy into `/opt/data/repo/skills` plus a restart. The upside stands — the agent cannot edit the checkout.
- The container runs as **root**, not as `HERMES_UID`. Anything it writes is root-owned, so `chown 1002:1002` is an explicit step, not something the image handles.
- `/opt/data` **is** a bind mount of `/srv/hermes/data` (the compose file was right). `docker exec grep /proc/mounts` is misleading: the container sees the host's mount table and reports the host root device.
- The config lives at `/srv/hermes/data/config.yaml` (inside `data/`), not beside `docker-compose.yml`. A backup step pointed at the wrong path failed silently — always check the backup exists.
- Status: decided.

## 2026-10-24: one recursive node type; the spine is read as a newspaper
- The flat `## Tasks` list plus a single `next_action` cannot hold a real matter: the divorce has three letters out and a lawyer we are waiting on, and frontmatter holds exactly one next action.
- Replaced by **one node type** whose depth is a `parent:` pointer. Subject, strand and task are the same file at different depths; strand-versus-task is *derived* (has children ⇒ strand), so it is never stored and never goes stale. Depths: subject → strand → task, with the validator warning past three.
- Every level renders as **headline → subhead → bulk**. The user sees headlines only; detail is behind a push.
- The one-line **history** and one-line **current** the user asked for are **rendered at read time and never stored**. A stored summary is a cache with no invalidation and would be read back as current fact a week later — the same drift already observed in triage (`7/14/22` then `5/15/23` on identical input, an hour apart).
- `next_action` is therefore removed rather than kept alongside: it is the stored-cache mistake at subject level and already duplicates `## Tasks`.
- Reason: the user's own model is a newspaper, and a flat checklist forces a real matter to be flattened into something that cannot answer "where are we with X".
- Design: `docs/FRONT-PAGE.md`. Status: decided; not yet built.

## 2026-10-24: a task and a reminder are one object with two aspects
- The user cannot (and should not have to) classify a thing as a task or a reminder. They are the same node: a **job** (`status`, children, `## Log`) plus an optional **clock** (`remind_at`, `recur`, `nag`).
- The user speaks; the assistant sets the flags. "Remind me…" is the cue to set a clock. Nothing is filed by the user into a bucket.
- Three clock modes: **fixed**, **interval since completion** (phone my sister within 14 days of the last time I did it — a calendar recurrence cannot express this), and **nag until done** (taxes).
- "Call Steve again" is **not** a new node and **not** a separate reminder: it is a snooze plus a log line on the existing node, so one node accumulates the attempts instead of three fragmenting the story.
- **Snooze is first-class** and must be the cheapest action in the system: one sentence, no confirmation, no new node.
- Reason: the user has ADHD and said managing this is hard. The governing principle is that the system comes to the user; they never have to remember to check a list.
- Status: decided; not yet built.

## 2026-10-24: keep the storage shape changeable, but write no abstraction early
- The user intends to sell this eventually and wants the data shape changeable (e.g. a task that must own PDFs, where file paths stop being an adequate reference).
- Four rules instead of a swappable-backend interface: (1) **one seam** — all spine access through `store.py` verbs; (2) **identity is an id, never a path** — parents, mail and calendar reference `sign-letter`, not a file location; (3) **attachments are opaque handles plus a resolver**, never absolute paths; (4) **`schema: 1`** in frontmatter so a later format change can be read and migrated rather than silently misread.
- Explicitly **not** doing: an abstract store with pluggable backends written before a second backend exists. That produces a system mediocre at two things and debuggable at neither. The seam exists with one implementation until a real second one appears.
- Reason: the migration pain the user is worried about is caused by *paths leaking into references*, not by Markdown. Rules 2 and 3 remove the cause; rule 1 makes the eventual swap one file.
- Status: decided; rules 1–4 land with the node schema.
