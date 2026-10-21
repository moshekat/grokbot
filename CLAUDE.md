# GrokBot project: context for future sessions

## What this project is
We're building our **own equivalent of Grok Bot** (SpaceXAI/xAI's paid "always-on AI teammate" product,
launched in beta on 2026-08-11) rather than buying it: self-hosted Hermes Agent on our own server, using DeepSeek.
The buy-versus-build research is in `docs/research/`, and `docs/PLAN.md` records the reasoning.

"GROC bot" in voice-dictated prompts means **Grok Bot**.

## Resources available
- Local Linux machine (this one). The hard drives get plugged in here.
- An online Proxmox server (VPS) we own. Host IP and hostname are deliberately kept out of this public repo;
  they're in the private ProxHetz repo. RAM and CPU still need recording in `PROGRESS.md`.

## This repo is public
https://github.com/moshekat/grokbot. Rule: no secrets, no host IPs or hostnames, no personal email addresses,
no client data. Infrastructure specifics belong in the private ProxHetz repo or the user's notes.

## Where things live
| File | Purpose |
|---|---|
| `docs/HANDOVER.md` | **Current state and the next concrete steps**, plus today's verified facts (Hermes version, Docker image, model names, prices) |
| `docs/TASK-SPINE.md` | **The product design**: subjects → tasks → calendar/reminders/lists; the files-first store and its derived SQLite index |
| `docs/research/2026-10-20-landscape.md` | What Grok Bot is, its features and pricing, and the open-source alternatives (with sources) |
| `docs/research/2026-10-21-market.md` | Demand evidence, competitor pricing and our running costs; why a generic assistant has no moat |
| `docs/PLAN.md` | Recommended plan and phases |
| `DECISIONS.md` | Decision log: append-only, dated |
| `PROGRESS.md` | What's done, what's next, open questions |
| `STARTER_PROMPT.md` | Paste-in prompt to start the next AI session |
| `.env.example` | Names of the secrets the project needs (no values) |
| `deploy/.env.example` | Variable names for the server-side Hermes container (no values) |
| `deploy/.env` | The real values. **Gitignored.** Never commit, never paste into a chat |
| `deploy/docker-compose.yml` | The Hermes container: pinned image, data mount, no published ports |
| `deploy/README.md` | VM bring-up, update, backup and security steps |
| `SOUL.md` | The bot's persona and rules (deployed to `/opt/data/SOUL.md`) |
| `skills/inbox-triage/` | Inbox triage: `SKILL.md` rules + `triage.py` (read-only stub for now) |
| `skills/subjects/` | The spine: `SKILL.md` rules, `EXAMPLE.md` canonical subject, `validate.py` frontmatter checker |
| `spine/` | Empty skeleton (`subjects/`, `lists/`) + `README.md` rules. Deployed to `/opt/data/spine` |

## Our code versus the agent's own state
- **We write:** skills (`skills/*/SKILL.md`), their Python scripts, `deploy/`, `SOUL.md`. All generic; anything
  per-installation (inbox address, OAuth client, schedule, targets) is an environment variable, never hardcoded.
- **Hermes writes:** its memory, sessions and self-authored skills, under `/srv/hermes/data` on the VM. Never in git.
- **DeepSeek** is stateless: it reads our skills and Hermes' memory and acts through them.
- Language: Python 3 + Markdown + YAML. Don't reach for an LLM SDK in our scripts; the model comes via Hermes.
- The private client platform monorepo (`greyonion-platform`) is **out of scope**. This project is not client code.

## Working rules for future sessions
- Read `PROGRESS.md` and `DECISIONS.md` first; `docs/HANDOVER.md` has the verified technical facts and the next steps.
- Re-check the Hermes release and DeepSeek model IDs before building: the docs move weekly. v0.22.2 and
  `deepseek-flash` / `deepseek-v4-pro` were correct on 2026-10-20.
- After meaningful work, update `PROGRESS.md`, and record any decision in `DECISIONS.md` with the date and reason.
- This market moves weekly. Re-check prices, star counts and features before relying on the research doc.
- Security matters here: these agents get logins, email and shell access. Sandbox them, use dedicated
  accounts, and don't install unvetted community skills (see the research doc, section "Security").
