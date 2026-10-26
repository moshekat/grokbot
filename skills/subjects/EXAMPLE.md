---
schema: 1
id: medical-aid
title: Medical aid
status: active
kind: admin
due: 2026-10-27
people: [spouse]
tags: [insurance, health]
updated: 2026-10-21
---

# Medical aid

The family policy, claim submissions and the annual review.

## Context

- Claims go through the member portal; the reference prefix is `CLM`.
- The 2026 rate increase lands in January; the review happens in November.

## Log

2026-10-21 — claim for the physio visit still to submit; broker emailed the dependant list
2026-10-14 — emailed the broker the updated dependant list

## Open questions

- Is the dental limit shared across the family, or per member?

---

Tasks hang off this subject as their own files, never as bullets here. Two shapes:

`tasks/submit-physio-claim.md` — the user holds it:

```
---
schema: 1
id: submit-physio-claim
title: Submit the 2026 claim for the physio visit
parent: medical-aid
status: active
due: 2026-10-27
updated: 2026-10-21
---
```

`tasks/dependant-list-confirmed.md` — someone else holds it, so it has a chase date:

```
---
schema: 1
id: dependant-list-confirmed
title: Broker to confirm the dependant list was loaded
parent: medical-aid
status: waiting
waiting_on: the broker
remind_at: 2026-10-26T09:00
updated: 2026-10-21
---
```

The second one is the one that used to get lost: the mail was sent, so the work
looked finished, and nothing brought it back when the broker stayed quiet.

