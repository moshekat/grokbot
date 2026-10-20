# Plan: own personal-assistant bot (revised 2026-10-20)

## Goal
Personal productivity first. Build it so it could later be packaged and sold.

## Recommendation
- **Self-host Hermes Agent** on our own Proxmox server (Hetzner), using our **DeepSeek** key.
- **Don't buy Grok Bot for now.** Our jobs are API-friendly (Gmail and Google Calendar) or about local files (hard drives). Those are Grok Bot's weak spots, and it can't reach a drive plugged into this PC.
- **Don't build the agent from scratch.** Build only our own *skills* or *tools* on top of Hermes. Those pieces are portable and could be sold later.

Why Hermes rather than the others:
- It has a messaging gateway (Telegram, WhatsApp, Slack, email) with **voice-note transcription**, a built-in cron scheduler, any-model support, and an MIT licence, so commercial use is fine.
- Rakazo's strength is a full browser or desktop "computer" per bot, which we don't need yet.
- OpenClaw has the worst security record.

## The jobs, and how each gets done
| # | Job | How | Needs an LLM? |
|---|---|---|---|
| 1 | **Inbox triage**: bin rubbish, flag what needs attention, send a daily digest | Gmail API skill. Classify each new email as rubbish, FYI or needs-you. Rubbish gets a label and goes to Trash, *not* permanent deletion: Gmail keeps Trash for 30 days. The bot sends a morning and afternoon "needs you" digest. | Yes (cheap) |
| 2 | **Voice-to-email**: "email Jo saying …" | Send a voice note to the bot. It transcribes it (local Whisper on the server, which is free), drafts the email in your style, shows you the draft, and **sends only after you approve**. | Yes |
| 3 | **Calendar and to-do** | Google Calendar plus Google Tasks API skills. Add, move and list items by voice or text, with a morning agenda. | Yes (cheap) |
| 4 | **Hard-drive dedup against the Nextcloud data server** | Mostly **not** an AI job. A deterministic script: (a) build a hash index of the Nextcloud data once, on the server; (b) for each drive you plug in, hash it locally and compare against the index; (c) report duplicates and unique files, then copy the unique files to Nextcloud. Hermes only runs it and reports back. We can't compare bytes over the internet; a hash index is the only practical approach. | No (≈$0) |

## Chat channel
- **Use Telegram for the bot, even though you use WhatsApp day to day.**
- WhatsApp bots need either the unofficial bridges, which risk getting the number banned, or Meta's paid Business API with template rules. Both are painful for machine-to-machine work.
- Telegram's bot API is free, official and built for this. Your personal chats can stay on WhatsApp.

## Where it runs
- New VM on the Proxmox host. IDs 123–198 are free. Suggested: **VM 123 `ai-assistant`**, Ubuntu, 4 vCPU, 8 GB RAM, 50 GB, with Docker. Whisper `small` runs fine on CPU for voice notes.
- Note that the `vms` pool is 72% full. Consider putting the disk on `FourTStorage`.
- **Reach it only over NetBird VPN, not through public Nginx Proxy Manager.** Telegram needs outbound connections only, so nothing has to be exposed publicly.
- The VM has its own Google OAuth client, scoped to Gmail, Calendar and Tasks. Approval is required for sending email and deleting calendar events.
- Install no community skills without reading them first.

## Model costs (DeepSeek, checked 2026-10-20)
`deepseek-flash`: $0.15 per 1M input tokens, $1.20 per 1M output tokens. Prices are half off-peak, and cached input is about 50 times cheaper.
`deepseek-v4-pro` costs about 4 times as much. Use it only for drafting replies, if Flash's quality isn't good enough.

| Workload | Estimate per month |
|---|---|
| Triage of about 100 emails a day | about $1–3 |
| Voice-drafted emails, about 10 a day | about $0.50–1 |
| Calendar, to-do and digests | under $1 |
| Agent overhead (each step resends about 10–30k tokens of context, mostly cached) | about $1–5 |
| **Total** | **about $3–10/month** |

The $20–60 quoted in reviews assumes Claude or GPT-class pricing ($3–15 per 1M tokens). Things that could blow up the cost: routines that poll too often, browser or screenshot automation, and an agent stuck in a loop. **Set a monthly spend cap on the DeepSeek account.**

**Privacy caveat:** DeepSeek is a China-based provider, and your email content would be sent to it. For a personal inbox that may be acceptable. For client data and a future product, plan to route through a provider with clearer data terms, or use a local model for classification.

## Phases
1. **Setup (one evening):** create the VM, install Docker and Hermes, connect DeepSeek and Telegram, and get it talking.
2. **Inbox triage in "shadow mode" (1–2 weeks):** the bot *labels only*, with no trashing, while we check its accuracy. Then turn on trashing.
3. **Voice-to-email, then calendar and to-do.**
4. **Drive dedup tool:** a standalone script first, then wrapped as a Hermes skill.
5. **Productise later:** document setup, keep our skills in their own repo, and assess a hosted version for clients.

## Open questions
- Which inbox or inboxes? The candidate address is on Account B, which is being consolidated into Account A. Pick the one that survives the migration, or plan for both. (The address itself is kept in the private notes, not in this public repo.)
- What are the Proxmox host's actual RAM and CPU? (The Fujitsu D3401-H2 isn't recorded in the docs.) Run `free -h; nproc` on the host.
- Where is the Nextcloud data the drives should be compared against? Probably the VM 108 data disk.
