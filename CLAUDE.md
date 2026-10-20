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
| `docs/research/2026-10-20-landscape.md` | What Grok Bot is, its features and pricing, and the open-source alternatives (with sources) |
| `docs/PLAN.md` | Recommended plan and phases |
| `DECISIONS.md` | Decision log: append-only, dated |
| `PROGRESS.md` | What's done, what's next, open questions |
| `STARTER_PROMPT.md` | Paste-in prompt to start the next AI session |
| `.env.example` | Names of the secrets the project needs (no values) |

## Working rules for future sessions
- Read `PROGRESS.md` and `DECISIONS.md` first.
- After meaningful work, update `PROGRESS.md`, and record any decision in `DECISIONS.md` with the date and reason.
- This market moves weekly. Re-check prices, star counts and features before relying on the research doc.
- Security matters here: these agents get logins, email and shell access. Sandbox them, use dedicated
  accounts, and don't install unvetted community skills (see the research doc, section "Security").
