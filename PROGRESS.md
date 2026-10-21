# Progress

## Done
- **2026-10-20:** Researched the landscape (`docs/research/2026-10-20-landscape.md`).
- **2026-10-20:** Got the user's answers: personal use first, possibly sold later; jobs are inbox, voice-to-email, calendar/to-do and drive dedup; WhatsApp disliked; has a DeepSeek key.
- **2026-10-20:** Reviewed the server docs at `/media/moshe/MKData/Repositories/ProxHetz/` and revised `docs/PLAN.md` to the self-hosted Hermes plan.
- **2026-10-20:** Added `STARTER_PROMPT.md` (a handover prompt for the next AI session) and a `.gitignore`.
- **2026-10-20:** Moved the folder into a git repo and pushed it to https://github.com/moshekat/grokbot (branch `main`).
  The repo is **public**, so infrastructure specifics (host IP, hostname, personal addresses) were removed from these docs;
  they stay in the private ProxHetz repo and the user's own notes.
- **2026-10-20:** Made the handover complete so a new session can resume without re-discovery: refreshed `STARTER_PROMPT.md`
  (current commit, working directory casing, no infrastructure built yet, open housekeeping questions), corrected `CLAUDE.md`
  from "deciding" to "building", added `.env.example` (names only), and listed the open questions in `PROGRESS.md`.
- **2026-10-20:** Re-verified the moving parts a week before any build, and wrote it up in `docs/HANDOVER.md`:
  - Hermes is on release **v0.22.2** with an official Docker Hub image (`nousresearch/hermes-agent`, tags `latest` / `stable` / `v0.22.2`).
    Data lives in `/opt/data`; the gateway runs with no published port (Telegram long polling).
  - Hermes has a **built-in DeepSeek provider** (`DEEPSEEK_API_KEY`, base `https://api.deepseek.com`), so `DEEPSEEK_API_KEY` in
    `.env.example` is correct as written.
  - DeepSeek's current models are **`deepseek-flash`** and **`deepseek-v4-pro`**; `deepseek-chat`/`deepseek-reasoner` are retired.
    Prices in `docs/PLAN.md` were corrected to the exact peak/off-peak table.
  - Hermes runs on **Python 3.14** and wants `libatomic1` on minimal images; the earlier "install Whisper locally" note was
    dropped because transcription is built in.
  - Added `deploy/.env.example` (server-side variable names) and revised the VM sizing recommendation.

- **2026-10-21:** Design session; captured in `DECISIONS.md` and `docs/TASK-SPINE.md`:
  the product is **one assistant with a task spine** (subjects → tasks → calendar/reminders/lists), not four jobs;
  the store is files-first with a derived SQLite FTS5 index; lists use Hermes' native `todo_list` plus one file per named list;
  single-tenant first but multi-tenant-ready.
- **2026-10-21:** Wrote `docs/research/2026-10-21-market.md` (demand evidence, competitor pricing, our running costs).
  `SOUL.md` and `docs/PLAN.md` were reframed to match; `CLAUDE.md`'s file table updated.
- **2026-10-21:** Built and deployed spine step 1. `skills/subjects/` (`SKILL.md`, `EXAMPLE.md`, read-only `validate.py`)
  and the empty `spine/` tree are on `ai-assistant` at `/srv/hermes/data/{repo/skills,spine}`, registered through
  `skills.external_dirs` and verified as `external / enabled` in `hermes skills list`. Nothing touches `triage.py`.
  Also recorded what the box actually looks like, in `deploy/README.md` — several of our assumptions were wrong:
  the container runs as **root** (`HERMES_UID=1002`), the config is at `/srv/hermes/data/config.yaml` (not beside
  `docker-compose.yml`), and external dirs are **read-only**, so a skill update is a copy plus a restart, not a `git pull`.

## Next
- [ ] **User: create VM 123 `ai-assistant`** (spec in `docs/HANDOVER.md` → "VM 123 specification"). Tell me when `greyroot` is reachable.
- [ ] **User: fill `deploy/.env`** (gitignored) with `DEEPSEEK_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`. Values never go into chat or git.
- [ ] **User: confirm the five CAT run times** (08:00 / 10:30 / 13:00 / 15:30 / 17:30 proposed).
- [ ] Phase 1 install, once the VM exists: copy `deploy/` to `/srv/hermes`, `docker compose up -d`, `hermes setup` (DeepSeek + `deepseek-flash` + Telegram), verify the Telegram round-trip (`deploy/README.md`).
- [ ] **Build the spine, step 1** — **done and deployed 2026-10-21** (see above). Remaining: the Telegram smoke test
      (create a subject, add a task with a due date, ask "what's due?", confirm files on the VM).
- [ ] Then upgrade `triage.py` so needs-you **upserts a task** on a subject instead of only labelling.
- [ ] Create a Google OAuth client (Gmail, Calendar and Tasks scopes) for the bot.
- [ ] Finish `skills/inbox-triage/triage.py` against the Gmail API, then run it in shadow mode for a week.
- [ ] Check whether the DeepSeek platform has a blocking spend limit; set it, or cron a monthly spend report.
- [ ] **Two housekeeping questions for the user** (asked 2026-10-20, no answer yet):
  - [ ] Keep the repo **public** or make it private? (`gh repo edit moshekat/grokbot --visibility private --accept-visibility-change-consequences`)
  - [ ] Rewrite git history to remove the personal work address left in the initial commit? Needs a force-push; don't do it unprompted.
- [x] ~~Confirm the Hermes install method and DeepSeek model names~~ — done 2026-10-20: Docker image `nousresearch/hermes-agent`
  (pinned tag), models `deepseek-flash` / `deepseek-v4-pro`. See `docs/HANDOVER.md`.
- [x] ~~Answer the four Phase-1 blockers~~ — done 2026-10-20: inbox chosen (the work address; kept out of this public repo
  like every other address); host is 62 GB RAM / 8 cores
  (about 15 GB in use); go-ahead granted to create VM 123 and run Hermes on production; Telegram token steps given.
- [x] ~~VM size~~ — settled at 2 vCPU / 4 GB / 30 GB on `FourTStorage` (guest 123, see `DECISIONS.md`).

## Repo layout (what exists now)

| Path | What it is |
|---|---|
| `deploy/docker-compose.yml` | The Hermes container: pinned `v0.22.2`, `restart: unless-stopped`, `/srv/hermes/data` → `/opt/data`, **no published ports** |
| `deploy/.env.example` | Variable names only (tracked) |
| `deploy/.env` | The real values (**gitignored**), user fills it in |
| `deploy/README.md` | First bring-up, updates, backup, and the security notes for the VM |
| `SOUL.md` | The bot's persona and rules (deployed to `/opt/data/SOUL.md`) |
| `skills/inbox-triage/SKILL.md` | Triage rules: three buckets, shadow mode, digest format, CAT schedule |
| `skills/inbox-triage/triage.py` | Phase-2 stub; `--dry-run` only, `--apply` refuses to run |
| `skills/subjects/SKILL.md` | Spine rules: create/list/show/update subjects, tasks inside them, append-only timeline |
| `skills/subjects/EXAMPLE.md` | The canonical subject; the model copies its shape |
| `skills/subjects/validate.py` | Frontmatter checker. Read-only. 0 clean, 1 problems, 2 nothing to check |
| `docs/TASK-SPINE.md` | Product design: subjects → tasks → calendar/reminders/lists (not built yet) |
| `docs/research/2026-10-21-market.md` | Demand, pricing and our running costs |

## Design decisions taken 2026-10-21 (details in `DECISIONS.md`)
- The four "jobs" are now **one assistant with a task spine**: subjects → tasks → calendar / reminders / lists. Triage's needs-you bucket upserts a task on a subject.
- The subject store is **files first** (Markdown + YAML per subject, append-only `timeline.md`, `docs/`, `mail/`, and a sibling `lists/`) with a **derived SQLite FTS5 index**. Not MySQL.
- **Lists are first-class but we build no list feature**: native `todo_list`, Google Tasks, and one Markdown file per named list.
- **Single-tenant first, multi-tenant-ready**: profile data dir from an env var, facts hang off subject ids, one profile per person.
- Reminders: Telegram digest by default, ntfy for time-sensitive, calendar alarm for must-not-miss.
- Market: demand is real (Hermes' 395 user stories; Personal Assistant is the third-largest category), but the platform layer is free, so the sellable thing is a turnkey self-hosted vertical assistant, not another general one.

## Timezone and schedule
- Everything is **Africa/Johannesburg (CAT, UTC+2, no DST)**: the VM, the container's `TZ`, and the cron entries.
- Inbox triage: **08:00 · 10:30 · 13:00 · 15:30 · 17:30** — five runs in the working day, nothing overnight.

## Where our code goes, and where it does not
- **This repo:** the generic skills, scripts and deploy config. No installation-specific values: the inbox address, OAuth client and schedule come in as environment variables.
- **The VM (`/srv/hermes`):** `.env` (mode 600) and `data/` (Hermes' memory, sessions and the skills it writes for itself). A backup of `data/` therefore contains credentials: encrypt it.
- **`greyonion-platform`:** not involved. That is the private client platform monorepo (Java: banking, DocBot, Wholesome, Grit) and the assistant has no business in it.
- Language: **Python + Markdown + YAML**. Judgment lives in `SKILL.md`; mechanics live in Python; the model is reached through Hermes, never through our own SDK code.

## Open questions before Phase 1 (from `docs/PLAN.md` and `STARTER_PROMPT.md`)
1. ~~Which inbox the bot manages~~ — answered: the work address, recorded in the private notes only (this repo is public).
2. ~~The Proxmox host's RAM and CPU~~ — answered: 62 GB RAM, 8 cores, about 15 GB in use.
3. ~~Go-ahead to create the VM and run Hermes~~ — granted.
4. ~~A Telegram bot token~~ — steps given (@BotFather `/newbot`, numeric id from @userinfobot); the values are still outstanding.
5. **DeepSeek:** does the platform offer a hard blocking spend cap, or only warnings? Unanswered.
6. **Privacy:** the assistant's mail content goes to DeepSeek, a China-based provider. Not yet discussed with the user.
7. **Housekeeping:** repo public or private; rewrite history to drop the work address.

## Environment notes
- Server: Proxmox VE on Hetzner (Fujitsu D3401-H2, Debian 13, kernel 7.0). Host IP and hostname are deliberately
  kept out of this **public** repo; see the private ProxHetz repo's `Proxmox Hetxner Server Architecture/docs/ARCHITECTURE.md`.
  - Free guest IDs: 123–198. The `vms` storage pool is 72% full; `FourTStorage` (ZFS) has 2.37 TB free.
  - VPN: NetBird in container 102. Nextcloud: VM 108 (3 TB data disk).
  - Host RAM and CPU: **62 GB RAM, 8 cores** (about 15 GB in use) — recorded 2026-10-20. VM 123 fits comfortably.
  - VM for this project: **123 `ai-assistant`**, spec in `docs/HANDOVER.md`. Not created yet.
- Email and calendar: Google Workspace. Two accounts, with a consolidation in progress (see ProxHetz `GoogleDrive_Nextcloud/plans/`).
  - Model: **DeepSeek** (`deepseek-flash` by default), API key held by the user. The keys go in `deploy/.env` (gitignored) only.
  - Schedule and timezone: **Africa/Johannesburg (CAT)**, inbox triage at **08:00 / 10:30 / 13:00 / 15:30 / 17:30**, nothing overnight.
  - Language: **Python + Markdown + YAML**. Skills are `SKILL.md` instructions plus Python scripts; the model is reached through Hermes, not our own SDK code.
  - Boundaries: our code lives in this repo (generic), values live in `/srv/hermes/.env` on the VM, and the private `greyonion-platform` repo is not used for any of this.
- Hermes: release v0.22.2 (checked 2026-10-20), Docker image `nousresearch/hermes-agent`, data in a volume at `/opt/data`.
  Telegram uses long polling, so the VM needs no public port. Re-check the version before the build.
- Local machine: Linux. The hard drives get plugged in here.
- Git: remote `origin` → https://github.com/moshekat/grokbot, branch `main`, **public**. Identity is set locally only
  (`moshekat` / `moshekat@users.noreply.github.com`). Push over HTTPS with `gh` credentials.
