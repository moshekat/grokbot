#!/usr/bin/env python3
"""Create the AI/* triage labels in Gmail. Idempotent.

The google-workspace skill can list and apply labels but not create them, so
this small script fills that gap using the skill's own auth helpers. Running it
twice is safe: existing labels are reported and left alone.

Usage:
    /opt/hermes/.venv/bin/python create_labels.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Reuse the skill's authentication and service construction rather than
# duplicating OAuth handling.
SCRIPTS = Path("/opt/data/skills/productivity/google-workspace/scripts")
sys.path.insert(0, str(SCRIPTS))

from google_api import build_service  # noqa: E402

# name -> (background, text) colours as Gmail accepts them.
LABELS = {
    "AI/NeedsYou": ("#fb4c2f", "#ffffff"),
    "AI/FYI": ("#4986e7", "#ffffff"),
    "AI/Rubbish": ("#cccccc", "#000000"),
}


def main() -> int:
    service = build_service("gmail", "v1")
    existing = {
        label["name"]: label["id"]
        for label in service.users().labels().list(userId="me").execute().get("labels", [])
    }

    created, skipped, failed = [], [], []

    for name, (background, text) in LABELS.items():
        if name in existing:
            skipped.append(name)
            continue
        body = {
            "name": name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
            "color": {"backgroundColor": background, "textColor": text},
        }
        try:
            result = (
                service.users()
                .labels()
                .create(userId="me", body=body)
                .execute()
            )
            created.append((result["name"], result["id"]))
        except Exception as exc:  # noqa: BLE001 - report and continue
            failed.append(f"{name}: {exc}")

    print(
        json.dumps(
            {
                "created": created,
                "already_existed": skipped,
                "failed": failed,
                "total_labels_now": len(existing) + len(created),
            },
            indent=2,
        )
    )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
