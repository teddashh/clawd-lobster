"""
vault_migrate.py — Migrate legacy 'knowledge' table into The Vault (9-table schema).

Phase 1-2 of the VAULT-ARCHITECTURE.md migration plan:
  1. Create a 'legacy_import' source in vault_sources
  2. Copy each knowledge row → vault_documents with proper type mapping
  3. Preserve taxonomy_id, privacy_level, embeddings (if any)
  4. Log sync in vault_sync_log for traceability
  5. Log events in vault_events

Usage:
    python vault_migrate.py                  # dry-run (default)
    python vault_migrate.py --execute        # actually migrate
    python vault_migrate.py --status         # show migration status
    python vault_migrate.py --rollback       # remove migrated docs (reversible)

Requires: oracledb
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def _load_oracle_config() -> dict:
    config_file = Path.home() / ".clawd-lobster" / "config.json"
    if not config_file.exists():
        return {}
    with open(config_file, encoding="utf-8") as f:
        return json.load(f).get("oracle", {})


def _connect():
    import oracledb
    cfg = _load_oracle_config()
    return oracledb.connect(
        user=cfg.get("user", ""),
        password=cfg.get("password", "") or os.environ.get("CLAWD_ORACLE_PASSWORD", ""),
        dsn=cfg.get("dsn", ""),
        config_dir=cfg.get("wallet_dir", ""),
        wallet_location=cfg.get("wallet_dir", ""),
        wallet_password=cfg.get("wallet_password", "") or os.environ.get("CLAWD_ORACLE_WALLET_PASSWORD", ""),
    )


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Category → doc_type mapping
# ---------------------------------------------------------------------------

CATEGORY_TO_DOCTYPE = {
    "scripts": "note",
    "working": "note",
    "architecture": "note",
    "compliance-sop": "sop",
    "compliance": "sop",
    "compliance-iso": "sop",
    "compliance-nist": "sop",
    "development": "note",
    "system-index": "note",
    "system": "note",
    "decision": "note",
    "sop": "sop",
    "research": "note",
    "action-log": "note",
    "learnings": "note",
    "incident": "note",
    "memory": "note",
    "general": "note",
    "session": "conversation",
    "project": "note",
    "documentation": "note",
    "idea": "note",
    "guideline": "sop",
    "corporate": "note",
    "identity": "note",
}


# ---------------------------------------------------------------------------
# Migration logic
# ---------------------------------------------------------------------------

def get_or_create_source(cur, source_type: str, source_uri: str,
                         display_name: str) -> int:
    """Get or create a vault_sources entry. Returns source ID."""
    uri_hash = _sha256(source_uri)
    cur.execute(
        "SELECT id FROM vault_sources WHERE source_type = :1 AND source_uri_hash = :2",
        [source_type, uri_hash],
    )
    row = cur.fetchone()
    if row:
        return row[0]

    id_var = cur.var(int)
    cur.execute("""
        INSERT INTO vault_sources (source_type, source_uri, source_uri_hash,
            display_name, trust_level, metadata_json)
        VALUES (:1, :2, :3, :4, :5, :6)
        RETURNING id INTO :7
    """, [source_type, source_uri, uri_hash, display_name, 0.90,
          json.dumps({"migration": "vault_migrate.py", "original_table": "knowledge"}),
          id_var])
    return id_var.getvalue()[0]


def migrate_row(cur, row: dict, source_id: int, dry_run: bool) -> str:
    """Migrate one knowledge row. Returns 'created', 'skipped', or 'error:...'."""
    knowledge_id = row["id"]
    content = str(row["content"]) if row["content"] else ""
    title = row["title"] or "Untitled"
    category = row["category"] or "general"
    doc_type = CATEGORY_TO_DOCTYPE.get(category, "note")
    privacy = row["privacy_level"] or "internal"
    taxonomy_id = row["taxonomy_id"]
    created_at = row["created_at"] or datetime.now(timezone.utc)
    tags = row["tags"] or ""
    source_path = row["source_path"] or ""
    agent_scope = row["agent_scope"] or ""

    if not content.strip():
        return "skipped"  # empty content

    content_hash = _sha256(content)

    if dry_run:
        return "created"

    # Check if already migrated (via sync log)
    cur.execute("""
        SELECT vault_id FROM vault_sync_log
        WHERE source_layer = 'legacy' AND source_id = :1 AND vault_table = 'vault_documents'
    """, [str(knowledge_id)])
    if cur.fetchone():
        return "skipped"  # already migrated

    # Check for duplicate by content hash
    cur.execute(
        "SELECT id FROM vault_documents WHERE source_id = :1 AND content_hash = :2",
        [source_id, content_hash],
    )
    if cur.fetchone():
        return "skipped"

    # Build metadata
    meta = {
        "legacy_id": knowledge_id,
        "legacy_category": category,
        "legacy_tags": tags,
        "legacy_source_path": source_path,
        "legacy_agent_scope": agent_scope,
    }

    # Insert document
    doc_var = cur.var(int)
    cur.execute("""
        INSERT INTO vault_documents (source_id, doc_type, title, content,
            content_hash, occurred_at, metadata_json, taxonomy_id,
            privacy_level, language, lifecycle)
        VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, 'accepted')
        RETURNING id INTO :11
    """, [source_id, doc_type, title, content, content_hash,
          created_at, json.dumps(meta), taxonomy_id,
          privacy, "en", doc_var])
    doc_id = doc_var.getvalue()[0]

    # Log event
    cur.execute("""
        INSERT INTO vault_events (target_type, target_id, to_state, reason, actor)
        VALUES ('document', :1, 'accepted', :2, 'vault_migrate')
    """, [doc_id, f"Migrated from knowledge.id={knowledge_id}"])

    # Log sync
    cur.execute("""
        INSERT INTO vault_sync_log (source_layer, source_id, source_hash,
            vault_table, vault_id, sync_agent)
        VALUES ('legacy', :1, :2, 'vault_documents', :3, 'vault_migrate')
    """, [str(knowledge_id), content_hash, doc_id])

    return "created"


def run_migration(execute: bool = False):
    """Run the migration."""
    dry_run = not execute
    mode = "EXECUTE" if execute else "DRY-RUN"
    print(f"\n{'='*60}")
    print(f"  Vault Migration — {mode}")
    print(f"{'='*60}\n")

    conn = _connect()
    cur = conn.cursor()

    # Count legacy rows
    cur.execute("SELECT COUNT(*) FROM knowledge")
    total = cur.fetchone()[0]
    print(f"Legacy knowledge table: {total} rows")

    # Check already migrated
    cur.execute("""
        SELECT COUNT(*) FROM vault_sync_log
        WHERE source_layer = 'legacy' AND vault_table = 'vault_documents'
    """)
    already = cur.fetchone()[0]
    print(f"Already migrated: {already}")
    print(f"Remaining: {total - already}\n")

    if total - already == 0 and not dry_run:
        print("Nothing to migrate. All rows already in Vault.")
        conn.close()
        return

    # Create source
    if not dry_run:
        source_id = get_or_create_source(
            cur, "legacy_import", "oracle://knowledge_table",
            "Legacy knowledge table migration"
        )
    else:
        source_id = -1

    # Fetch all knowledge rows
    import oracledb
    cur.execute("""
        SELECT id, title, category, tags, privacy_level, content,
               source_path, created_at, taxonomy_id, agent_scope
        FROM knowledge
        ORDER BY id
    """)
    cols = [c[0].lower() for c in cur.description]
    rows = []
    for raw in cur.fetchall():
        row = {}
        for i, val in enumerate(raw):
            if isinstance(val, oracledb.LOB):
                row[cols[i]] = val.read()
            else:
                row[cols[i]] = val
        rows.append(row)

    stats = {"created": 0, "skipped": 0, "errors": []}

    for i, row in enumerate(rows):
        try:
            result = migrate_row(cur, row, source_id, dry_run)
            if result == "created":
                stats["created"] += 1
            elif result == "skipped":
                stats["skipped"] += 1
            else:
                stats["errors"].append(f"id={row['id']}: {result}")
        except Exception as e:
            stats["errors"].append(f"id={row['id']}: {e}")

        if (i + 1) % 25 == 0:
            print(f"  Progress: {i+1}/{len(rows)}")
            if not dry_run:
                conn.commit()

    if not dry_run:
        conn.commit()

    print(f"\n{'='*60}")
    print(f"  Results ({mode})")
    print(f"{'='*60}")
    print(f"  Created:  {stats['created']}")
    print(f"  Skipped:  {stats['skipped']}")
    print(f"  Errors:   {len(stats['errors'])}")
    if stats["errors"]:
        for err in stats["errors"][:10]:
            print(f"    - {err}")
        if len(stats["errors"]) > 10:
            print(f"    ... and {len(stats['errors'])-10} more")
    print()

    conn.close()
    return stats


def show_status():
    """Show migration status."""
    conn = _connect()
    cur = conn.cursor()

    print("\n=== Vault Migration Status ===\n")

    cur.execute("SELECT COUNT(*) FROM knowledge")
    total_legacy = cur.fetchone()[0]
    print(f"Legacy knowledge rows: {total_legacy}")

    cur.execute("""
        SELECT COUNT(*) FROM vault_sync_log
        WHERE source_layer = 'legacy' AND vault_table = 'vault_documents'
    """)
    migrated = cur.fetchone()[0]
    print(f"Migrated to Vault:     {migrated}")
    print(f"Not yet migrated:      {total_legacy - migrated}")

    if migrated > 0:
        cur.execute("""
            SELECT d.doc_type, COUNT(*)
            FROM vault_documents d
            JOIN vault_sync_log s ON s.vault_id = d.id
                AND s.source_layer = 'legacy' AND s.vault_table = 'vault_documents'
            GROUP BY d.doc_type
            ORDER BY COUNT(*) DESC
        """)
        print("\n  Migrated by type:")
        for row in cur.fetchall():
            print(f"    {row[0]:20s} {row[1]}")

    # Overall vault stats
    for table in ["vault_sources", "vault_documents", "vault_chunks",
                   "vault_entities", "vault_facts", "vault_relations",
                   "vault_events", "vault_sync_log"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        cnt = cur.fetchone()[0]
        print(f"  {table:30s} {cnt:>6} rows")

    conn.close()


def rollback_migration():
    """Remove all legacy-migrated documents (reversible)."""
    conn = _connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) FROM vault_sync_log
        WHERE source_layer = 'legacy' AND vault_table = 'vault_documents'
    """)
    count = cur.fetchone()[0]

    if count == 0:
        print("Nothing to rollback.")
        conn.close()
        return

    print(f"\nRolling back {count} migrated documents...")

    # Delete events for migrated docs
    cur.execute("""
        DELETE FROM vault_events WHERE target_type = 'document'
        AND target_id IN (
            SELECT vault_id FROM vault_sync_log
            WHERE source_layer = 'legacy' AND vault_table = 'vault_documents'
        )
    """)
    print(f"  Deleted {cur.rowcount} events")

    # Delete documents
    cur.execute("""
        DELETE FROM vault_documents WHERE id IN (
            SELECT vault_id FROM vault_sync_log
            WHERE source_layer = 'legacy' AND vault_table = 'vault_documents'
        )
    """)
    print(f"  Deleted {cur.rowcount} documents")

    # Delete sync log entries
    cur.execute("""
        DELETE FROM vault_sync_log
        WHERE source_layer = 'legacy' AND vault_table = 'vault_documents'
    """)
    print(f"  Deleted {cur.rowcount} sync log entries")

    # Clean up source if no docs left
    cur.execute("""
        DELETE FROM vault_sources WHERE source_type = 'legacy_import'
        AND id NOT IN (SELECT DISTINCT source_id FROM vault_documents)
    """)

    conn.commit()
    conn.close()
    print("Rollback complete.\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    args = sys.argv[1:]

    if "--status" in args:
        show_status()
    elif "--rollback" in args:
        rollback_migration()
    elif "--execute" in args:
        run_migration(execute=True)
    else:
        print("Running in DRY-RUN mode (add --execute to actually migrate)\n")
        run_migration(execute=False)
