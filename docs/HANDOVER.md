# Where we are, and what happens next (2026-10-20)

This is the short version for a human reader. For the full plan, see `docs/PLAN.md`.

## State: repo-side build started; nothing exists on the server yet

- Research and planning are done. The repo is **public**: https://github.com/moshekat/grokbot
- The four Phase-1 blockers are **answered** (inbox, host size, go-ahead, Telegram steps). The remaining
  blockers are the user's to supply: the VM itself, and the values for `deploy/.env`.
- **Built in the repo (uncommitted at the time of writing):** `deploy/docker-compose.yml`, `deploy/.env`
  (gitignored, placeholders), `deploy/README.md`, `SOUL.md`, and the `skills/inbox-triage/` scaffold
  (`SKILL.md` plus a read-only `triage.py` stub).
- **Nothing exists on the server:** no VM 123, no Docker, no Hermes, no Telegram bot, no Google OAuth client.

## What was verified today

| Thing | Finding |
|---|---|
| Hermes Agent | Latest release **v0.22.2** (2026-10-15), MIT, still very active. |
| Official Docker image | **`nousresearch/hermes-agent:latest`** on Docker Hub, with pinned tags such as `v0.22.2`. |
| Install script | `curl -fsSL https://hermes-agent.nousresearch.com/install.sh \| bash` (needs git, curl, tar). |
| Data volume | `/opt/data` (`HERMES_HOME`). Mount it and the container keeps its config, keys and sessions. |
| Telegram | Native platform. Set `TELEGRAM_BOT_TOKEN` + `TELEGRAM_ALLOWED_USERS`; long polling, so **no public port**. Voice notes are transcribed. |
| DeepSeek | Built-in provider, provider name `deepseek`, env var `DEEPSEEK_API_KEY`. |
| DeepSeek models | **`deepseek-flash`** and **`deepseek-v4-pro`**. `deepseek-chat` and `deepseek-reasoner` are retired. |
| DeepSeek prices | flash: $0.15 in / $0.60 out per 1M (peak: $0.30 / $1.20); v4-pro: $0.66 / $1.98 (peak: $1.32 / $3.96). Cache hits are about 50× cheaper. |

## Corrections to the earlier docs

1. **"Local Whisper on the server" is redundant.** Hermes already transcribes voice notes itself (`stt`).
   Try the built-in path first, and only add our own Whisper later if quality is poor.
2. **Minimal VMs can break the install.** Hermes' image bundling links Node.js against `libatomic.so.1`.
   The installer asks for `libatomic1` if it is missing (needs sudo). It also runs on **Python 3.14**.
   Ubuntu 24.04 or Debian 13 is a safer base than an old minimal image.
3. **"4 vCPU / 8 GB" is generous.** On a host that is already crowded, 2 vCPU / 4 GB is enough for
   Telegram, cron and small API skills. Whisper on CPU is the only memory-hungry part.
4. **Disk: `vms` is 72% full.** Put the 30–50 GB VM disk on `FourTStorage` (ZFS), as `docs/PLAN.md` suggested.
5. **The DeepSeek spend cap is user-side.** Check the platform for "set a spend limit". If it turns out to
   only warn rather than block, the fallback is a monthly balance top-up and a Hermes cron job that reports
   spend from `--usage-file` JSON.

## VM 123 specification

A full **QEMU/KVM VM**, not an LXC container: Hermes runs in Docker, and the bot will hold mail and
calendar credentials plus shell access, so it belongs behind a VM boundary. This mirrors the existing
VM 199 pattern. **The user creates the VM** per the ProxHetz protocols; the install happens afterwards.

| Field | Value |
|---|---|
| ID / name | `123` / `ai-assistant` |
| Type | QEMU/KVM VM (not LXC) |
| OS | Ubuntu 24.04 LTS, cloud-init |
| CPU | 2 vCPU, host type |
| RAM | 4 GB |
| Disk | 30 GB on `FourTStorage` (ZFS). The `vms` pool is 72% full |
| Firmware / machine | OVMF (UEFI), q35 |
| Network | `vmbr0`, DHCP with a Kea reservation (address kept in the private ProxHetz notes, not here) |
| Cloud-init | enabled, standard SSH key injected |
| Admin user | `greyroot`, sole login; `PermitRootLogin no`, `AllowUsers greyroot`, passwordless sudo, default `ubuntu` user removed |
| Guest agent | `qemu-guest-agent` enabled |
| Boot | `onboot=1` |
| Timezone | `Africa/Johannesburg` |
| Network access | NetBird peer only; **no public ingress, no published ports** |
| Tags | `vm`, `ai`, `grokbot` |

Host headroom, recorded 2026-10-20: 62 GB RAM and 8 cores, about 15 GB in use. VM 123 is small by design:
the load is API calls and cron, not inference.

### Install order once the VM exists

1. SSH in as `greyroot`; confirm timezone, `docker` installed, and the `hermes` user created (non-root).
2. `/srv/hermes` owned by `hermes`, mode `750`; `.env` mode `600`, owned by `hermes`.
3. Copy `deploy/docker-compose.yml` and the filled `.env` there, then `docker compose up -d`.
4. Confirm the Telegram round-trip. **This is the Phase 1 finish line.**
5. Only then: Google OAuth client, the inbox skill, shadow mode.

## What we write, and what Hermes writes

The split matters because only one half belongs in git.

| Who writes it | What | Where it lives |
|---|---|---|
| **Us** | Skills (`SKILL.md` rules), Python scripts, compose config, persona | **This repo**, in git. Generic: nothing installation-specific is hardcoded |
| **Hermes** | Its memory (`MEMORY.md`, `USER.md`), session history, and any skills it writes for itself while working | `/srv/hermes/data` on the VM (`/opt/data` in the container). Never in git: back it up encrypted |
| **The model** | Nothing. DeepSeek holds no state; it reads our skills and Hermes' memory and acts through them | n/a |

Language: **Python 3, Markdown and YAML.** Python because Hermes itself is Python, so our scripts sit
alongside it and are easy to review. Judgment goes in `SKILL.md` so it can be changed without touching
code; mechanics go in Python so they can be tested without an LLM in the loop.

What is deliberately **not** here: the private client platform monorepo. The assistant is not a client app,
and mixing a personal-mail-holding bot with client production code would couple two unrelated release and
secrets lifecycles. Anything installation-specific (the inbox address, the OAuth client, schedules, targets)
is an environment variable in `/srv/hermes/.env`.
## What's next

Blocked on the user:

1. **Create VM 123** per the specification above, then say when `greyroot` is reachable.
2. **Fill `deploy/.env`**: `DEEPSEEK_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`. Values are typed
   into the file, never pasted into chat or committed.
3. **Confirm the five CAT run times** (08:00 / 10:30 / 13:00 / 15:30 / 17:30 proposed).

After that, the first working session runs the install order above: `docker compose up -d`, `hermes setup`
(DeepSeek + `deepseek-flash` + Telegram), then the Telegram round-trip, then the Google OAuth client and
the inbox skill in shadow mode (labels only).

## Repo layout

| Path | What it is |
|---|---|
| `deploy/docker-compose.yml` | Hermes container: pinned `v0.22.2`, `restart: unless-stopped`, data bind mount, no published ports |
| `deploy/.env.example` | Variable names only, tracked |
| `deploy/.env` | The values, **gitignored**, filled in by the user |
| `deploy/README.md` | Bring-up, update, backup and security steps for the VM |
| `SOUL.md` | The bot's persona and rules; deployed to `/opt/data/SOUL.md` |
| `skills/inbox-triage/` | Triage skill: `SKILL.md` rules plus a read-only `triage.py` stub |

- This repo is public: no IPs, hostnames, addresses, tokens or client data.
- Never commit `.env` or credentials. On the server, keep them at `/srv/hermes/.env` with mode `600`, owned by `hermes`.
- The private client platform repo is out of scope for this project.
- The server is production and hosts client websites. Confirm before every change there.
