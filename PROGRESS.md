# Progress

## Done
- **2026-10-20:** Researched the landscape (`docs/research/2026-10-20-landscape.md`).
- **2026-10-20:** Got the user's answers: personal use first, possibly sold later; jobs are inbox, voice-to-email, calendar/to-do and drive dedup; WhatsApp disliked; has a DeepSeek key.
- **2026-10-20:** Reviewed the server docs at `/media/moshe/MKData/Repositories/ProxHetz/` and revised `docs/PLAN.md` to the self-hosted Hermes plan.
- **2026-10-20:** Added `STARTER_PROMPT.md` (a handover prompt for the next AI session) and a `.gitignore`. The user is moving this folder into a git repo.

## Next
- [ ] User gives the go-ahead on the plan and answers the open questions in `docs/PLAN.md`.
- [ ] Phase 1: create VM 123 `ai-assistant`, install Docker and Hermes, connect DeepSeek and Telegram (access over NetBird only).
- [ ] Create a Google OAuth client (Gmail, Calendar and Tasks scopes) for the bot.

## Environment notes
- Server: Proxmox VE on Hetzner (Fujitsu D3401-H2, Debian 13, kernel 7.0). Host IP and hostname are deliberately
  kept out of this **public** repo; see the private ProxHetz repo's `Proxmox Hetxner Server Architecture/docs/ARCHITECTURE.md`.
  - Free guest IDs: 123–198. The `vms` storage pool is 72% full; `FourTStorage` (ZFS) has 2.37 TB free.
  - VPN: NetBird in container 102. Nextcloud: VM 108 (3 TB data disk).
  - Host RAM and CPU: not yet recorded.
- Email and calendar: Google Workspace. Two accounts, with a consolidation in progress (see ProxHetz `GoogleDrive_Nextcloud/plans/`).
- Model: DeepSeek API key, held by the user. Never commit it.
- Local machine: Linux. The hard drives get plugged in here.
