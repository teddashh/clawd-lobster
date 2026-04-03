"""
Poller entrypoint for the Odoo connector.

Designed to be invoked with --once by cron / the runtime scheduler:
  python -m connect_odoo.poller --once

Connects to Odoo, checks for pending tasks (arp.task state='pending'),
prints them as JSON, and exits.
"""

from __future__ import annotations

import json
import sys

from .server import _execute_kw

try:
    import xmlrpc.client as _xmlrpc  # noqa: F401 — used for Fault type
except ImportError:
    pass


def poll_once() -> list[dict]:
    """Fetch pending tasks from Odoo and return them."""
    try:
        tasks = _execute_kw(
            "arp.task",
            "search_read",
            [[["state", "=", "pending"]]],
            {
                "fields": ["id", "name", "state", "description", "create_date"],
                "limit": 50,
            },
        )
    except Exception as exc:
        # If arp.task model doesn't exist, return empty
        msg = str(exc).lower()
        if "arp.task" in msg or "does not exist" in msg:
            tasks = []
        else:
            raise
    return tasks


def main() -> None:
    tasks = poll_once()
    print(json.dumps(tasks, default=str, ensure_ascii=False, indent=2))
    if tasks:
        print(f"\n[poller] Found {len(tasks)} pending task(s).", file=sys.stderr)
    else:
        print("[poller] No pending tasks.", file=sys.stderr)


if __name__ == "__main__":
    main()
