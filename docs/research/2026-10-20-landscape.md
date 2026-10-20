# Grok Bot and open-source alternatives: research (2026-10-20)

## 1. What Grok Bot is
Grok Bot is a paid product from SpaceXAI (formerly xAI), built with Cursor. Early beta opened on **2026-08-11**.
It's a separate app from the Grok chatbot, and it's also separate from the `@grok` reply bot on X.
One report cites about 418k weekly users by mid-September (Bloomberg, via Paralect).

**The core idea:** you create named "Bots", and each Bot does one job and has its own chat and memory.
They run on an **always-on cloud computer** (Chrome, a filesystem and a terminal), so work continues after you close your laptop.

### Features
- **Persistent cloud computer:** one per account, shared by all your Bots, with each Bot on its own screen. This makes it *not* a security boundary between Bots.
- **Browser automation:** Bots use sites that have no API by clicking through them. Logins, 2FA and CAPTCHAs are handed back to you.
- **Connectors:** a marketplace of API integrations, plus support for MCP servers, plugins and Cursor skills. 1Password works for shared logins.
- **Approvals:** before a Bot sends, publishes, buys or deletes, it asks you: Allow once, Always allow, or Deny. Approvals inside routines expire after about 10 minutes.
- **Memory:** each Bot keeps corrections, writing style and approval rules, and Bots share what they learn.
- **Routines:** scheduled or event-triggered tasks (for example, a new Slack message or a GitHub notification), up to 50 per Bot.
- **Teach by demo:** you do a task once in the Bot's browser and it learns the routine. Still rolling out.
- **Group chats:** 2 to 6 Bots in one thread, handing work to each other.
- **Team Bots (2026-09-28):** you can publish a Bot to a team or to Slack.
- **Proactive Bots (2026-10-02):** Bots suggest tasks before you ask.
- **Own email address:** one `@mail.grokbot.com` address per account.
- **Other integrations:** native X search; Plaid (read-only bank data, late September); Stripe-based shopping (US).
- **Coding:** coding work is handed off to Cursor cloud agents.
- **Model:** you **can't choose the model**. A router picks among Grok 4.6/4.7, Claude Opus 5.5 and others.
- **Platforms:** desktop apps (macOS, Windows, Linux), iOS and Android. There's no web app.

### Pricing (X subscription plans from 2026-10-12, per Paralect)
| Plan | Price | Grok Bot? |
|---|---|---|
| Free / Plus | $0 / $8 | No |
| Premium | $30/mo ($300/yr) | Yes |
| Super | $100/mo | Yes, about 3.5x Premium usage |
| Ultra | $200/mo | Yes, about 12x Premium usage |
| Teams / Enterprise | per seat / custom | Yes |

Grok chat, Cursor and Grok Bot share one weekly usage pool. Routines consume usage continuously.
Non-Grok models are billed at API list price, and usage over the allowance is billed at token cost.
Reviewers describe the pricing as confusing and say it changes often.

### What reviewers say
- It's polished and "just works", but you can't tune the model or the setup.
- Good results: personal-assistant and recurring web jobs, such as news scraping and weekly analytics reviews.
- Weak results: open-ended jobs, such as a lead-generation bot that produced nothing in week one.
- Not good for work centred on local files.
- Main worry: the Bots sign in *as you* on a cloud machine you don't control.

### Can we get its code?
**No.** Grok Bot is proprietary and closed-source. A repo calling itself "open-grokbot" (ishandutta2007) has 9 stars and is abandoned. Ignore it.

## 2. Open-source alternatives (GitHub stats checked 2026-10-20)
| Project | Stars | License | Language | What it is |
|---|---|---|---|---|
| **OpenClaw** (`openclaw/openclaw`) | ~393k | MIT | TypeScript | The best-known self-hosted personal assistant. A "Gateway" daemon on your machine or server, reached through WhatsApp, Telegram, Slack, Discord, Signal, iMessage, Teams and 20+ more channels. Swappable models (Claude, OpenAI, local). Skills and plugins come from the ClawHub marketplace. Governed by the OpenClaw Foundation. |
| **Hermes Agent** (`NousResearch/hermes-agent`) | ~255k | MIT | Python | A self-improving agent: it creates and refines its own skills, has memory and session search, a cron scheduler, subagents, and a single gateway for Telegram, Discord, Slack, WhatsApp, Signal and email. Seven execution backends (local, Docker, SSH, Modal, Daytona, and others). Any model. Has `hermes claw migrate` to import from OpenClaw. |
| **Rakazo** (`elie222/rakazo`) | ~4.8k | Apache-2.0 | TypeScript | The **closest clone of Grok Bot's shape**: persistent named bots with memory and routines; a Docker "computer" per bot (browser, terminal, desktop); bot-to-bot delegation; web, desktop and mobile apps; integrations through Composio, Pipedream or MCP. Installs on a VPS with Docker Compose. **Beta.** |
| **OpenBot** (`CopilotKit/OpenBot`) | ~6.7k | MIT | TypeScript | A template for company "AI coworkers". Each coworker has an isolated browser and files, and every action goes through a policy and audit gateway. **Alpha.** Needs a CopilotKit Intelligence licence (a free tier exists). Best suited as a starting point for a business product. |

Hosted, closed alternatives mentioned by reviewers: ChatGPT "dots" (Pro and Business only, not in the EU or UK), Meta Muse (US only), Lindy, and Claude Cowork / Claude Tag.

### Typical self-hosting cost
- Server: we already have one. Otherwise expect $5–30/mo for a VPS.
- Model API usage: roughly **$20–60+/mo** for moderate personal use. Heavy browser automation costs more.
- Optional extras: a sandbox provider (E2B or Daytona), Composio or Pipedream, and text-to-speech keys.

## 3. Security (important)
OpenClaw's popularity has made it a target. In early 2026:
- **"ClawHavoc":** hundreds to more than a thousand malicious ClawHub skills, many of which installed infostealers. OpenClaw added VirusTotal scanning, and says the scanning is "not a silver bullet".
- **Tens of thousands of instances exposed on the internet:** older versions didn't require gateway authentication by default.
- **"ClawJacked":** a malicious website could hijack a local instance through its localhost WebSocket.
- By default, tools run **on the host** unless you configure sandboxing.

**Rules we'll follow:**
- Run the agent in Docker on the server, with gateway auth on, behind HTTPS or a VPN. Never expose it openly.
- Give the bot **dedicated accounts** and least-privilege API keys.
- Install no community skills without reading them first.
- Keep approvals on for sending, buying, deleting and publishing.
- Treat every inbound message and web page as untrusted (prompt injection).

## Sources
- https://www.paralect.com/stack/grok-bot (most detailed feature and pricing breakdown)
- https://christopheralarcon.com/blog/what-is-grok-bot (paying user's week-one review)
- https://www.therundown.ai/tools/grok-bot
- https://www.buildfastwithai.com/blogs/grok-bot-review-ai-teammates-pricing-is-it-worth-it-2026
- https://teslanorth.com/2026/10/10/elon-grok-bot-shopping/
- https://github.com/openclaw/openclaw · https://github.com/NousResearch/hermes-agent · https://github.com/elie222/rakazo · https://github.com/CopilotKit/OpenBot
- https://rakazo.com/alternatives/ · https://agenta.ai/blog/best-grok-bot-alternatives (vendor or comparison blogs, so treat them as biased)
- https://thehackernews.com/2026/02/openclaw-integrates-virustotal-scanning.html
- https://www.antiy.net/p/clawhavoc-analysis-of-large-scale-poisoning-campaign-targeting-the-openclaw-skill-market-for-ai-agents/
- https://blog.rankiteo.com/ope1772403877-openclaw-vulnerability-february-2026/

Caveat: most Grok Bot coverage comes from SEO-style blogs, and there's little official documentation. Pricing in particular has changed several times since launch.
