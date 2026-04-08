"""Load skill onboarding metadata from skill.json manifests.

Reads the `onboarding` section from each skill.json and converts
them into state items for the onboarding workflow.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _skills_dir() -> Path:
    """Locate the skills/ directory relative to the package."""
    return Path(__file__).resolve().parent.parent.parent / "skills"


def load_skill_manifests() -> list[dict]:
    """Load all skill.json files that have onboarding sections.

    Returns list of skill manifests (the full skill.json content)
    that contain an `onboarding` key.
    """
    skills_dir = _skills_dir()
    if not skills_dir.exists():
        return []

    manifests = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        manifest_path = skill_dir / "skill.json"
        if not manifest_path.exists():
            continue
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            if "onboarding" in data:
                manifests.append(data)
        except (json.JSONDecodeError, OSError):
            continue

    return manifests


def manifests_to_items(manifests: list[dict]) -> list[dict]:
    """Convert skill manifests into onboarding state items.

    Each manifest's `onboarding` section becomes an item in the state.
    """
    items = []
    for m in manifests:
        ob = m.get("onboarding", {})
        skill_id = m.get("id", m.get("name", "unknown"))

        item = {
            "id": skill_id,
            "tier": ob.get("tier", "optional"),
            "kind": m.get("kind", m.get("category", "prompt-pattern")),
            "status": "pending",
            "depends_on": ob.get("depends_on", []),
            "started_at": None,
            "completed_at": None,
            "last_actor": None,
            "retry_count": 0,
            "error": None,
            "facts": {k: False for k in ob.get("facts_schema", {})},
            # Display metadata
            "title": ob.get("title", m.get("name", skill_id)),
            "summary": ob.get("summary", ""),
            "why_it_matters": ob.get("why_it_matters", ""),
            "estimated_minutes": ob.get("estimated_minutes", 5),
            "steps": ob.get("steps", []),
        }
        items.append(item)

    # Sort by tier priority then order
    tier_order = {"required": 0, "optional": 1, "onetime": 2}
    items.sort(key=lambda i: (
        tier_order.get(i["tier"], 9),
        next((m.get("onboarding", {}).get("order", 99)
              for m in manifests if m.get("id") == i["id"]), 99),
    ))

    return items


def get_skill_display(manifests: list[dict]) -> list[dict]:
    """Get display-friendly skill catalog for the API.

    Returns a simplified list suitable for the dashboard skills tab.
    """
    catalog = []
    for m in manifests:
        ob = m.get("onboarding", {})
        catalog.append({
            "id": m.get("id", ""),
            "name": m.get("name", ""),
            "kind": m.get("kind", m.get("category", "")),
            "version": m.get("version", ""),
            "tier": ob.get("tier", "optional"),
            "title": ob.get("title", m.get("name", "")),
            "summary": ob.get("summary", ""),
            "why_it_matters": ob.get("why_it_matters", ""),
            "estimated_minutes": ob.get("estimated_minutes", 5),
            "always_on": m.get("alwaysOn", False),
            "default_enabled": m.get("defaultEnabled", False),
            "steps_count": len(ob.get("steps", [])),
        })
    return catalog
