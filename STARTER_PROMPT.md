# Starter prompt for the next AI session

Copy everything below the line into a new session opened in this repo.

---

You're picking up the **GrokBot** project: a self-hosted personal-assistant AI bot, our own alternative to SpaceXAI's paid "Grok Bot" product. The user dictates by voice, so "GROC bot" means Grok Bot.

**Working directory:** `/media/moshe/MKData/Repositories/GrokBot` (note the case: `MKData`, not `mosheKat`; this filesystem is case-sensitive).

## Read these first, in this order
1. `CLAUDE.md`: project context and working rules.
2. `PROGRESS.md`: what's done, what's next, and environment notes (server, email, model).
3. `DECISIONS.md`: the dated decision log. Respect decisions marked "decided". Items marked "proposed" still need the user's OK.
4. `docs/PLAN.md`: the current plan (jobs, architecture, costs, phases, open questions).
5. `docs/HANDOVER.md`: **verified technical facts and the exact next steps** (Hermes v0.22.2, Docker image, model names, prices).
6. `docs/research/2026-10-20-landscape.md`: background on Grok Bot and the open-source alternatives (only if needed).

## Where we are (as of 2026-10-20, after the repo-side build)
- Research and planning are done. The repo is at https://github.com/moshekat/grokbot (branch `main`, **public**).
- The repo-side build has started: `deploy/` (compose + env + README), `SOUL.md`, `skills/inbox-triage/`.
- **No infrastructure work has started.** Nothing is created on the Proxmox host: no VM, no Docker, no Hermes,
  no Telegram bot, no Google OAuth client.
- **Verified on 2026-10-20** (details in `docs/HANDOVER.md`):
  - Hermes Agent **v0.22.2**; official Docker image `nousresearch/hermes-agent` (tags `latest` / `stable` / `v0.22.2`); data volume `/opt/data`; Telegram uses long polling (no public port).
  - Install script alternative: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`, then `hermes gateway install`.
  - Hermes has a built-in DeepSeek provider (`DEEPSEEK_API_KEY`, base URL `https://api.deepseek.com`); models are **`deepseek-flash`** and **`deepseek-v4-pro`**.
  - No separate Whisper: Hermes transcribes Telegram voice notes itself.
- Git identity is set **locally only** (`moshekat` / `moshekat@users.noreply.github.com`), matching the ProxHetz repo. Pushing uses HTTPS with `gh` credentials (`gh auth setup-git`); `gh` is logged in as `moshekat`.
- Plan:
  - **Hermes Agent** (NousResearch, MIT licence) on a **new VM on the user's Proxmox server (Hetzner)**, reached only over the NetBird VPN.
  - Model: **DeepSeek** (`deepseek-flash` by default). Set a spend cap.
  - The bot talks to the user over **Telegram**, not WhatsApp.
  - Everything runs in **Africa/Johannesburg (CAT, UTC+2)**: the VM, the container's `TZ`, and cron.
    Inbox triage is five daytime runs at **08:00 / 10:30 / 13:00 / 15:30 / 17:30**; nothing overnight.
  - Language and layout: **Python 3 + Markdown + YAML**. Our generic code lives in this repo
    (`deploy/`, `SOUL.md`, `skills/*/SKILL.md` + a Python script per skill); the real values live in
    `/srv/hermes/.env` on the VM; the agent's own memory and self-written skills live in
    `/srv/hermes/data` and are never committed. The private client platform monorepo is not involved.
- Goal: the user's own productivity first, with an eye to selling it later. Keep our custom skills and tools portable and in this repo.
- The four jobs, in build order:
  1. Gmail inbox triage. Start in label-only "shadow mode". Deleting means Gmail Trash only.
  2. Voice note to drafted email. Always ask for approval before sending.
  3. Google Calendar and Tasks.
  4. A hard-drive dedup tool. This is a deterministic hash-index script that compares local drives against the Nextcloud data on VM 108. It isn't an LLM job.
- The server's infrastructure docs live in a separate repo: `/media/moshe/MKData/Repositories/ProxHetz/`.
  - Start with `Proxmox Hetxner Server Architecture/docs/ARCHITECTURE.md`.
  - **Don't read or copy anything from its `secrets-backup/` folder.**

## Waiting on the user before Phase 1
1. **Create VM 123 `ai-assistant`** per the specification in `docs/HANDOVER.md` (Ubuntu 24.04, 2 vCPU, 4 GB RAM,
   30 GB on `FourTStorage`, admin `greyroot`, NetBird only, timezone `Africa/Johannesburg`). Then say it is reachable.
2. **Fill `deploy/.env`** (gitignored): `DEEPSEEK_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`
   (numeric Telegram id from @userinfobot; handles are mutable and are not an allowlist).
3. **Confirm the five CAT run times**: 08:00 / 10:30 / 13:00 / 15:30 / 17:30 proposed.

Already answered (2026-10-20): the inbox (the work address, kept in the private notes and never in this public repo),
the host size (62 GB RAM / 8 cores, about 15 GB in use), the go-ahead to run on production, and the Telegram token steps.

## Two open housekeeping questions (asked, not yet answered)
- **Public or private repo?** It was pushed public, because that's where the user pointed and the research is shareable. It exposes the project's existence and architecture (no secrets, no host IP, no addresses). To flip it:
  `gh repo edit moshekat/grokbot --visibility private --accept-visibility-change-consequences`
- **Rewrite history to drop a personal work address?** The address was scrubbed from the working tree, but the **initial commit still contains it**, so it is retrievable from the public history. Rewriting means a force-push. The user has not asked for this yet; don't do it unprompted.

## Rules
- This is a **production server** hosting client websites. Confirm with the user before any change to the server, and never expose new services publicly.
- **Never commit secrets** (DeepSeek key, Telegram token, Google OAuth files). Keep them in `.env` or on the server, which `.gitignore` covers. `.env.example` lists the variable names, with no values.
- **This repo is public.** No secrets, no host IPs or hostnames, no personal email addresses, no client data. Infrastructure specifics belong in the private ProxHetz repo or the user's notes.
- Don't install community or ClawHub skills without reading their code first.
- After each piece of work:
  - Update `PROGRESS.md`.
  - Record new decisions in `DECISIONS.md` with the date and reason.
  - Re-check any prices or versions you rely on, because this space changes weekly.

**Your first step:** summarise the current state for the user in a few lines, then ask for the three items under "Waiting on the user" that are still outstanding.
