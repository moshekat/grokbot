# GrokBot project: context for future sessions

## What this project is
We're deciding whether to **buy Grok Bot** (SpaceXAI/xAI's paid "always-on AI teammate" product,
launched in beta on 2026-08-11) or **run our own equivalent**, either with an existing open-source
agent on our own server or with our own build.

"GROC bot" in voice-dictated prompts means **Grok Bot**.

## Resources available
- Local Linux machine (this one).
- An online server (VPS) we own. Specs still need recording in `PROGRESS.md`.

## Where things live
| File | Purpose |
|---|---|
| `docs/research/2026-10-20-landscape.md` | What Grok Bot is, its features and pricing, and the open-source alternatives (with sources) |
| `docs/PLAN.md` | Recommended plan and phases |
| `DECISIONS.md` | Decision log: append-only, dated |
| `PROGRESS.md` | What's done, what's next, open questions |
| `STARTER_PROMPT.md` | Paste-in prompt to start the next AI session |

## Working rules for future sessions
- Read `PROGRESS.md` and `DECISIONS.md` first.
- After meaningful work, update `PROGRESS.md`, and record any decision in `DECISIONS.md` with the date and reason.
- This market moves weekly. Re-check prices, star counts and features before relying on the research doc.
- Security matters here: these agents get logins, email and shell access. Sandbox them, use dedicated
  accounts, and don't install unvetted community skills (see the research doc, section "Security").
