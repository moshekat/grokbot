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
