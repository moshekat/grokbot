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

## The shape: one assistant, one spine
Everything below is an **input to a single task spine** (design:
`docs/TASK-SPINE.md`): **subjects → tasks → calendar / reminders / lists**. A
subject is a person, project, admin matter, asset or place; a task belongs to it;
email, voice notes and calendar invites all land in the same store. Triage
produces tasks, not just labels.

Built **single-tenant first, multi-tenant-ready**: everything under the profile
data dir, facts hanging off subject ids, one profile per person. That way a
second family member or a future customer is a second profile, not a rewrite.

## The inputs, and how each gets done
| # | Input | How | Needs an LLM? |
|---|---|---|---|
| 1 | **Inbox triage**: bin rubbish, flag what needs attention, send a daily digest | Gmail API skill. Classify each new email as rubbish, FYI or needs-you. Rubbish gets a label and goes to Trash, *not* permanent deletion: Gmail keeps Trash for 30 days. The bot sends a morning and afternoon "needs you" digest. **Needs-you upserts a task against the matching subject.** | Yes (cheap) |
| 2 | **Voice-to-email**: "email Jo saying …" | Send a voice note to the bot. Hermes' built-in speech-to-text transcribes it (voice notes in Telegram are supported out of the box), it drafts the email in your style, shows you the draft, and **sends only after you approve**. Only add a separate local Whisper if the built-in quality is poor. | Yes |
| 3 | **Calendar and to-do** | Google Calendar plus Google Tasks API skills. Add, move and list items by voice or text, with a morning agenda. Tasks live on subjects in the spine. | Yes (cheap) |
| 4 | **Lists** (pharmacy, hardware, movies) | **Nothing new to build.** Hermes has a native `todo_list` tool; Google Tasks covers the phone case. We only give each named list one Markdown file in the spine. | Cheap |
| 5 | **Reminders** | Telegram digest by default, ntfy push for time-sensitive, a real calendar alarm for what mustn't be missed. | Free–cheap |
| 6 | **Hard-drive dedup against the Nextcloud data server** | Mostly **not** an AI job. A deterministic script: (a) build a hash index of the Nextcloud data once, on the server; (b) for each drive you plug in, hash it locally and compare against the index; (c) report duplicates and unique files, then copy the unique files to Nextcloud. Hermes only runs it and reports back. We can't compare bytes over the internet; a hash index is the only practical approach. | No (≈$0) |

## Chat channel
- **Use Telegram for the bot, even though you use WhatsApp day to day.**
- WhatsApp bots need either the unofficial bridges, which risk getting the number banned, or Meta's paid Business API with template rules. Both are painful for machine-to-machine work.
- Telegram's bot API is free, official and built for this. Your personal chats can stay on WhatsApp.

## Where it runs
- New VM on the Proxmox host. IDs 123–198 are free. Suggested: **VM 123 `ai-assistant`**, Ubuntu 24.04 LTS, **2–4 vCPU, 4–8 GB RAM, 30–50 GB**, with Docker. Sizing is modest because the work is API calls, cron and small scripts; check it against the host's real RAM before creating it.
- Hermes needs **Python 3.14** and, on minimal images, the system package **`libatomic1`** (its Node.js dependency links against it). A current Ubuntu or Debian 13 base avoids the problem.
- Note that the `vms` pool is 72% full. Put the VM disk on `FourTStorage` (ZFS), which has room.
- **Reach it only over NetBird VPN, not through public Nginx Proxy Manager.** Telegram needs outbound connections only, so nothing has to be exposed publicly.
- The VM has its own Google OAuth client, scoped to Gmail, Calendar and Tasks. Approval is required for sending email and deleting calendar events.
- Install no community skills without reading them first.

## How it gets installed (checked 2026-10-20)
Hermes publishes an official Docker image: `nousresearch/hermes-agent`, with `latest`, `stable` and pinned version tags (current release `v0.22.2`). One container runs the gateway; the data lives in a volume mounted at `/opt/data`. Pin the tag and bump it deliberately.
- The alternative is the install script (`curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`) plus `hermes gateway install`, which registers a systemd service. Use this if the container's isolation gets in the way.
- Telegram needs only outbound connections (long polling), so no port is published.

## Model costs (DeepSeek, checked 2026-10-20)
Current model IDs are `deepseek-flash` and `deepseek-v4-pro`; the old `deepseek-chat` and `deepseek-reasoner` names are retired.

| Per 1M tokens | `deepseek-flash` (peak / off-peak) | `deepseek-v4-pro` (peak / off-peak) |
|---|---|---|
| Input, cache miss | $0.30 / $0.15 | $1.32 / $0.66 |
| Input, cache hit | $0.006 / $0.003 | $0.044 / $0.022 |
| Output | $1.20 / $0.60 | $3.96 / $1.98 |

Off-peak is half price: 01:00–04:00 and 06:00–10:00 UTC on weekdays are peak (excluding Chinese public holidays); everything else, including weekends, is off-peak. Context is 1M tokens on both models.

`deepseek-v4-pro` costs about 4× `deepseek-flash`. Use it only for drafting replies, if Flash's quality isn't good enough; the estimates below assume Flash.

| Workload | Estimate per month |
|---|---|
| Triage of about 100 emails a day | about $1–3 |
| Voice-drafted emails, about 10 a day | about $0.50–1 |
| Calendar, to-do and digests | under $1 |
| Agent overhead (each step resends about 10–30k tokens of context, mostly cached) | about $1–5 |
| **Total** | **about $3–10/month** |

The estimates above assume Flash. The $20–60 quoted in reviews assumes Claude or GPT-class pricing ($3–15 per 1M tokens). Things that could blow up the cost: routines that poll too often, browser or screenshot automation, and an agent stuck in a loop. **Set a monthly spend limit on the DeepSeek account.** If the platform only warns instead of blocking, keep the balance topped up monthly and have Hermes cron a monthly spend report.

**Privacy caveat:** DeepSeek is a China-based provider, and your email content would be sent to it. For a personal inbox that may be acceptable. For client data and a future product, plan to route through a provider with clearer data terms, or use a local model for classification.

## Phases
1. **Setup (one evening):** create the VM, add it to NetBird, run the Hermes container (`deploy/.env.example` lists the server-side variables), connect DeepSeek and Telegram, and get it talking.
2. **Spine, then triage in "shadow mode" (1–2 weeks):** lay out `spine/` and the `subjects` skill first (Markdown only — no index, no database yet); then run triage so that needs-you *becomes a task on a subject*. The bot labels only, with no trashing, while we check its accuracy. Then turn on trashing.
3. **Calendar, lists and reminders:** Google Calendar write, named lists via `todo_list` / Google Tasks, and the three reminder channels.
4. **Voice-to-email**, so drafts arrive as tasks against the person.
5. **Drive dedup tool:** a standalone script first, then wrapped as a Hermes skill.
6. **Productise later:** document setup, keep our skills in their own repo, and assess a hosted version for clients. The market and pricing assessment is in `docs/research/2026-10-21-market.md`; the short version is that the platform layer is free, so a generic assistant has no moat — a turnkey, self-hosted, vertical one does.

## Open questions
- Which inbox or inboxes? The candidate address is on Account B, which is being consolidated into Account A. Pick the one that survives the migration, or plan for both. (The address itself is kept in the private notes, not in this public repo.)
- What are the Proxmox host's actual RAM and CPU? (The Fujitsu D3401-H2 isn't recorded in the docs.) Run `free -h; nproc` on the host.
- Does the DeepSeek platform offer a hard spend cap (blocking), or only warnings? Check when logging in to set it up.
- Where is the Nextcloud data the drives should be compared against? Probably the VM 108 data disk.
