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

## Next
- [ ] **Two housekeeping questions for the user** (asked 2026-10-20, no answer yet):
  - [ ] Keep the repo **public** or make it private? (`gh repo edit moshekat/grokbot --visibility private --accept-visibility-change-consequences`)
  - [ ] Rewrite git history to remove the personal work address left in the initial commit? Needs a force-push; don't do it unprompted.
- [ ] User gives the go-ahead on the plan and answers the open questions in `docs/PLAN.md` (inbox, host RAM and CPU, Nextcloud data location).
- [ ] Phase 1: create VM 123 `ai-assistant`, install Docker and Hermes, connect DeepSeek and Telegram (access over NetBird only).
- [ ] Create a Google OAuth client (Gmail, Calendar and Tasks scopes) for the bot.
- [ ] Confirm the Hermes install method (Docker image vs. supported install script) and the current DeepSeek model names before relying on the prices in `docs/PLAN.md`.

## Open questions before Phase 1 (from `docs/PLAN.md` and `STARTER_PROMPT.md`)
1. Which inbox the bot manages. The address is on the account being cancelled, so pick the one that survives the migration.
2. The Proxmox host's RAM and CPU (`free -h; nproc` on the host). Still not recorded.
3. Explicit go-ahead to create the VM **and** install Hermes on the live server.
4. A Telegram bot token from @BotFather. The user creates this.

## Environment notes
- Server: Proxmox VE on Hetzner (Fujitsu D3401-H2, Debian 13, kernel 7.0). Host IP and hostname are deliberately
  kept out of this **public** repo; see the private ProxHetz repo's `Proxmox Hetxner Server Architecture/docs/ARCHITECTURE.md`.
  - Free guest IDs: 123–198. The `vms` storage pool is 72% full; `FourTStorage` (ZFS) has 2.37 TB free.
  - VPN: NetBird in container 102. Nextcloud: VM 108 (3 TB data disk).
  - Host RAM and CPU: not yet recorded.
- Email and calendar: Google Workspace. Two accounts, with a consolidation in progress (see ProxHetz `GoogleDrive_Nextcloud/plans/`).
- Model: DeepSeek API key, held by the user. Never commit it. Env var names are in `.env.example`; values go in `.env` only.
- Local machine: Linux. The hard drives get plugged in here.
- Git: remote `origin` → https://github.com/moshekat/grokbot, branch `main`, **public**. Identity is set locally only
  (`moshekat` / `moshekat@users.noreply.github.com`). Push over HTTPS with `gh` credentials.
