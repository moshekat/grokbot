# Starter prompt for the next AI session

Copy everything below the line into a new session opened in this repo.

---

You're picking up the **GrokBot** project: a self-hosted personal-assistant AI bot, our own alternative to SpaceXAI's paid "Grok Bot" product. The user dictates by voice, so "GROC bot" means Grok Bot.

## Read these first, in this order
1. `CLAUDE.md`: project context and working rules.
2. `PROGRESS.md`: what's done, what's next, and environment notes (server, email, model).
3. `DECISIONS.md`: the dated decision log. Respect decisions marked "decided". Items marked "proposed" still need the user's OK.
4. `docs/PLAN.md`: the current plan (jobs, architecture, costs, phases, open questions).
5. `docs/research/2026-10-20-landscape.md`: background on Grok Bot and the open-source alternatives (only if needed).

## Where we are (as of 2026-10-20)
- Research and planning are done. Nothing has been installed or created yet.
- Plan:
  - **Hermes Agent** (NousResearch, MIT licence) on a **new VM on the user's Proxmox server (Hetzner)**, reached only over the NetBird VPN.
  - Model: **DeepSeek** (`deepseek-flash` by default). Set a spend cap.
  - The bot talks to the user over **Telegram**, not WhatsApp.
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
1. **Which inbox the bot should manage.** Google Workspace accounts are being consolidated, and one address sits on the account that will be cancelled. (It's kept in the private notes, not here.)
2. **The Proxmox host's actual RAM and CPU** (`free -h; nproc` on the host).
3. **Explicit go-ahead to create the VM** (suggested: VM 123 `ai-assistant`, Ubuntu, 4 vCPU, 8 GB RAM, 50 GB disk, Docker) **and to install Hermes on the live server.**
4. **A Telegram bot token** from @BotFather. The user creates this.

## Rules
- This is a **production server** hosting client websites. Confirm with the user before any change to the server, and never expose new services publicly.
- **Never commit secrets** (DeepSeek key, Telegram token, Google OAuth files). Keep them in `.env` or on the server, which `.gitignore` covers.
- Don't install community or ClawHub skills without reading their code first.
- After each piece of work:
  - Update `PROGRESS.md`.
  - Record new decisions in `DECISIONS.md` with the date and reason.
  - Re-check any prices or versions you rely on, because this space changes weekly.

**Your first step:** summarise the current state for the user in a few lines, then ask for the four items under "Waiting on the user" that are still outstanding.
