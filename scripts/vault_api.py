"""
vault_api.py — The Vault (Oracle L3) Python API.

Agents and skills call these functions to interact with the Vault.
No agent should ever write SQL directly — this is the only gateway.

Usage:
    from vault_api import Vault

    v = Vault()                          # reads config from ~/.clawd-lobster/config.json
    v = Vault(wallet_dir=..., dsn=...)   # explicit params

    doc_id = v.ingest("email content", "email", {"from": "user@example.com", "to": ["colleague@example.com"]},
                       source_info={"type": "email_account", "uri": "outlook://inbox"})
    results = v.search("What did David say about the project?")
    profile = v.about("David Chen")
    timeline = v.timeline(entity="David Chen", start="2023-01-01", end="2023-12-31")

Requires: oracledb (pip install oracledb)
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__all__ = ["Vault"]


# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------

_pool = None


def _load_oracle_config() -> dict:
    """Load Oracle config from ~/.clawd-lobster/config.json."""
    config_file = Path.home() / ".clawd-lobster" / "config.json"
    if not config_file.exists():
        return {}
    with open(config_file, encoding="utf-8") as f:
        return json.load(f).get("oracle", {})


def _get_pool(wallet_dir: str = "", dsn: str = "", user: str = "",
              password: str = "", wallet_password: str = ""):
    """Get or create a connection pool."""
    global _pool
    if _pool is not None:
        return _pool

    import oracledb

    cfg = _load_oracle_config()
    wallet_dir = wallet_dir or cfg.get("wallet_dir", "")
    dsn = dsn or cfg.get("dsn", "")
    user = user or cfg.get("user", "")
    password = password or cfg.get("password", "") or os.environ.get("CLAWD_ORACLE_PASSWORD", "")
    wallet_password = wallet_password or cfg.get("wallet_password", "") or os.environ.get("CLAWD_ORACLE_WALLET_PASSWORD", "")

    pool_kwargs: dict[str, Any] = {
        "user": user, "password": password, "dsn": dsn,
        "min": 1, "max": 5, "increment": 1,
    }
    if wallet_dir:
        pool_kwargs["config_dir"] = wallet_dir
        pool_kwargs["wallet_location"] = wallet_dir
        if wallet_password:
            pool_kwargs["wallet_password"] = wallet_password

    _pool = oracledb.create_pool(**pool_kwargs)
    return _pool


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _fetchone_dict(cursor) -> dict | None:
    cols = [c[0].lower() for c in cursor.description]
    row = cursor.fetchone()
    if row is None:
        return None
    import oracledb
    return dict(zip(cols, [str(v) if isinstance(v, oracledb.LOB) else v for v in row]))


def _fetchall_dict(cursor) -> list[dict]:
    cols = [c[0].lower() for c in cursor.description]
    import oracledb
    return [
        dict(zip(cols, [str(v) if isinstance(v, oracledb.LOB) else v for v in row]))
        for row in cursor.fetchall()
    ]


# ---------------------------------------------------------------------------
# Vault class
# ---------------------------------------------------------------------------

class Vault:
    """API gateway to The Vault (Oracle L3 Deep Brain)."""

    def __init__(self, wallet_dir: str = "", dsn: str = "", user: str = "",
                 password: str = "", wallet_password: str = ""):
        self._pool = _get_pool(wallet_dir, dsn, user, password, wallet_password)

    # === INGEST ===

    def ingest(self, content: str, doc_type: str, meta: dict | None = None,
               source_info: dict | None = None, title: str = "",
               occurred_at: str | datetime | None = None,
               taxonomy_id: int | None = None,
               privacy_level: str = "internal",
               language: str = "en",
               ownership: str = "self",
               email_from: str | None = None,
               email_importance: str | None = None,
               email_direction: str | None = None,
               fidelity: str = "high",
               original_path: str | None = None,
               parent_doc_id: int | None = None,
               version: int = 1) -> int:
        """Ingest a document into the Vault. Returns the new document ID.

        Args:
            content: The document text content.
            doc_type: Type of document (email, note, file, conversation, etc.)
            meta: Type-specific metadata as dict (stored as JSON).
            source_info: Source info dict with 'type' and 'uri' keys.
            title: Document title (auto-generated from content if empty).
            occurred_at: When the content happened (ISO string or datetime).
            taxonomy_id: Optional taxonomy classification ID.
            privacy_level: One of: public, internal, restricted, secret.
            language: ISO language code (default 'en').

        Returns:
            The vault_documents.id of the created document.
        """
        source_info = source_info or {"type": "manual", "uri": f"manual://{_sha256(content)[:16]}"}
        meta = meta or {}

        if not title:
            title = content[:200].split("\n")[0].strip() or "Untitled"

        if occurred_at is None:
            occurred_at = datetime.now(timezone.utc)
        elif isinstance(occurred_at, str):
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    occurred_at = datetime.strptime(occurred_at, fmt)
                    break
                except ValueError:
                    continue
            else:
                occurred_at = datetime.now(timezone.utc)

        content_hash = _sha256(content)
        source_uri = source_info.get("uri", f"unknown://{content_hash[:16]}")
        source_type = source_info.get("type", "manual")
        source_uri_hash = _sha256(source_uri)

        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                # 1. Get or create source
                cur.execute(
                    "SELECT id FROM vault_sources WHERE source_type = :1 AND source_uri_hash = :2",
                    [source_type, source_uri_hash],
                )
                row = cur.fetchone()
                if row:
                    source_id = row[0]
                else:
                    id_var = cur.var(int)
                    cur.execute("""
                        INSERT INTO vault_sources (source_type, source_uri, source_uri_hash,
                            display_name, metadata_json)
                        VALUES (:1, :2, :3, :4, :5)
                        RETURNING id INTO :6
                    """, [source_type, source_uri, source_uri_hash,
                          source_info.get("display_name", source_uri[:200]),
                          json.dumps(source_info) if source_info else None,
                          id_var])
                    source_id = id_var.getvalue()[0]

                # 2. Check for duplicate document
                cur.execute(
                    "SELECT id FROM vault_documents WHERE source_id = :1 AND content_hash = :2",
                    [source_id, content_hash],
                )
                existing = cur.fetchone()
                if existing:
                    return existing[0]  # already ingested

                # 3. Insert document (v11: includes ownership, email, fidelity, versioning, original_path)
                doc_var = cur.var(int)
                # Extract promoted fields from meta if passed via PreDocument.to_ingest_kwargs()
                _ownership = ownership or (meta or {}).pop("ownership", "self")
                _email_from = email_from or (meta or {}).pop("email_from", None)
                _email_importance = email_importance or (meta or {}).pop("email_importance", None)
                _email_direction = email_direction or (meta or {}).pop("email_direction", None)
                _fidelity = fidelity or (meta or {}).pop("fidelity", "high")
                _original_path = original_path or (meta or {}).pop("original_path", None)
                _is_latest = 1
                # If this is a version update, mark previous as not latest
                if parent_doc_id:
                    cur.execute(
                        "UPDATE vault_documents SET is_latest = 0 WHERE id = :1",
                        [parent_doc_id],
                    )
                cur.execute("""
                    INSERT INTO vault_documents (source_id, doc_type, title, content,
                        content_hash, occurred_at, metadata_json, taxonomy_id,
                        privacy_level, language, lifecycle,
                        ownership, email_from, email_importance, email_direction,
                        fidelity, original_path, parent_doc_id, version, is_latest)
                    VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, 'raw',
                        :11, :12, :13, :14, :15, :16, :17, :18, :19)
                    RETURNING id INTO :20
                """, [source_id, doc_type, title, content, content_hash,
                      occurred_at, json.dumps(meta) if meta else None,
                      taxonomy_id, privacy_level, language,
                      _ownership, _email_from, _email_importance, _email_direction,
                      _fidelity, _original_path, parent_doc_id, version, _is_latest,
                      doc_var])
                doc_id = doc_var.getvalue()[0]

                # 4. Log event
                cur.execute("""
                    INSERT INTO vault_events (target_type, target_id, to_state, reason, actor)
                    VALUES ('document', :1, 'raw', 'Ingested via vault_api', 'vault_api')
                """, [doc_id])

                conn.commit()
                return doc_id

    def bulk_ingest(self, items: list[dict]) -> dict:
        """Ingest multiple documents. Each item is a dict with ingest() params.

        Returns: {created: int, skipped: int, errors: list[str]}
        """
        result = {"created": 0, "skipped": 0, "errors": []}
        for i, item in enumerate(items):
            try:
                self.ingest(**item)
                result["created"] += 1
            except Exception as e:
                if "uq_doc_content" in str(e).lower() or "unique constraint" in str(e).lower():
                    result["skipped"] += 1
                else:
                    result["errors"].append(f"item[{i}]: {e}")
        return result

    # === FIND (for dedup) ===

    def find_by_hash(self, content_hash: str) -> dict | None:
        """Find a document by content hash. Used for dedup layer 1."""
        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, doc_type, title, version, is_latest
                    FROM vault_documents
                    WHERE content_hash = :1 AND is_latest = 1
                    FETCH FIRST 1 ROWS ONLY
                """, [content_hash])
                return _fetchone_dict(cur)

    def find_by_path(self, original_path: str) -> dict | None:
        """Find latest document by original_path. Used for dedup layer 2 (versioning)."""
        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, doc_type, title, version, is_latest, content_hash
                    FROM vault_documents
                    WHERE original_path = :1 AND is_latest = 1
                    ORDER BY version DESC
                    FETCH FIRST 1 ROWS ONLY
                """, [original_path])
                return _fetchone_dict(cur)

    # === CHUNKS ===

    def add_chunk(self, document_id: int, chunk_index: int, content: str,
                  token_count: int | None = None) -> int:
        """Add a text chunk to a document. Returns chunk ID."""
        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                cid_var = cur.var(int)
                cur.execute("""
                    INSERT INTO vault_chunks (document_id, chunk_index, text_content, token_count)
                    VALUES (:1, :2, :3, :4)
                    RETURNING id INTO :5
                """, [document_id, chunk_index, content, token_count, cid_var])
                chunk_id = cid_var.getvalue()[0]
                conn.commit()
                return chunk_id

    # === SEARCH ===

    def search(self, query: str, doc_type: str | None = None,
               limit: int = 10) -> list[dict]:
        """Search the Vault by keyword across documents, chunks, and facts.

        Returns list of {id, type, title, excerpt, occurred_at, score}.
        """
        results = []
        q_like = f"%{query}%"
        q_lower = query.lower()

        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                # Search documents — M7 fix: use DBMS_LOB.INSTR for CLOB (safe for >32K)
                binds: dict[str, Any] = {"q_like": q_like, "q_lower": q_lower, "row_limit": limit}
                type_filter = ""
                if doc_type:
                    type_filter = "AND d.doc_type = :doc_type"
                    binds["doc_type"] = doc_type

                cur.execute(f"""
                    SELECT d.id, d.doc_type, d.title, d.occurred_at, d.lifecycle,
                           DBMS_LOB.SUBSTR(d.content, 300, 1) AS excerpt,
                           s.display_name AS source_name
                    FROM vault_documents d
                    JOIN vault_sources s ON s.id = d.source_id
                    WHERE (LOWER(d.title) LIKE LOWER(:q_like)
                           OR DBMS_LOB.INSTR(LOWER(d.content), :q_lower) > 0)
                        {type_filter}
                    ORDER BY d.occurred_at DESC
                    FETCH FIRST :row_limit ROWS ONLY
                """, binds)

                for row in _fetchall_dict(cur):
                    row["type"] = "document"
                    results.append(row)

                # Search facts
                cur.execute("""
                    SELECT f.id, f.claim, f.confidence, f.fact_date, f.lifecycle,
                           f.source_agent
                    FROM vault_facts f
                    WHERE LOWER(f.claim) LIKE LOWER(:fact_q)
                    ORDER BY f.confidence DESC, f.created_at DESC
                    FETCH FIRST :fact_limit ROWS ONLY
                """, {"fact_q": q_like, "fact_limit": limit})

                for row in _fetchall_dict(cur):
                    row["type"] = "fact"
                    results.append(row)

        return results

    # === ENTITY RESOLUTION ===

    def entity_resolve(self, name_or_alias: str) -> dict | None:
        """Resolve a name or alias to a canonical entity.

        Returns entity dict or None if not found.
        """
        norm = name_or_alias.strip().lower()

        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                # Try aliases first (most common path)
                cur.execute("""
                    SELECT e.id, e.entity_type, e.canonical_name, e.metadata_json,
                           e.confidence, e.lifecycle, e.first_seen_at, e.last_seen_at
                    FROM vault_entities e
                    JOIN vault_entity_aliases a ON a.entity_id = e.id
                    WHERE a.alias_normalized = :1
                    FETCH FIRST 1 ROWS ONLY
                """, [norm])
                result = _fetchone_dict(cur)
                if result:
                    return result

                # Fallback: try canonical name
                cur.execute("""
                    SELECT id, entity_type, canonical_name, metadata_json,
                           confidence, lifecycle, first_seen_at, last_seen_at
                    FROM vault_entities
                    WHERE LOWER(canonical_name) = :1
                    FETCH FIRST 1 ROWS ONLY
                """, [norm])
                return _fetchone_dict(cur)

    # === ABOUT (entity profile) ===

    def about(self, entity_name: str) -> dict | None:
        """Everything we know about an entity.

        Returns: {entity, aliases, documents, facts, relations} or None.
        """
        entity = self.entity_resolve(entity_name)
        if not entity:
            return None

        eid = entity["id"]
        profile: dict[str, Any] = {"entity": entity}

        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                # Aliases
                cur.execute(
                    "SELECT alias_text FROM vault_entity_aliases WHERE entity_id = :1 ORDER BY alias_text",
                    [eid],
                )
                profile["aliases"] = [r[0] for r in cur.fetchall()]

                # Related documents (via relations)
                cur.execute("""
                    SELECT d.id, d.doc_type, d.title, d.occurred_at
                    FROM vault_relations r
                    JOIN vault_documents d ON d.id = r.object_id AND r.object_type = 'document'
                    WHERE r.subject_type = 'entity' AND r.subject_id = :1
                    ORDER BY d.occurred_at DESC
                    FETCH FIRST 20 ROWS ONLY
                """, [eid])
                profile["documents"] = _fetchall_dict(cur)

                # Related facts
                cur.execute("""
                    SELECT f.id, f.claim, f.confidence, f.fact_date, f.lifecycle
                    FROM vault_relations r
                    JOIN vault_facts f ON f.id = r.object_id AND r.object_type = 'fact'
                    WHERE r.subject_type = 'entity' AND r.subject_id = :1
                    ORDER BY f.confidence DESC
                    FETCH FIRST 20 ROWS ONLY
                """, [eid])
                profile["facts"] = _fetchall_dict(cur)

                # Related entities — M6 fix: wrap UNION in subquery for overall limit
                cur.execute("""
                    SELECT * FROM (
                        SELECT e.id, e.entity_type, e.canonical_name, r.relation_type
                        FROM vault_relations r
                        JOIN vault_entities e ON e.id = r.object_id AND r.object_type = 'entity'
                        WHERE r.subject_type = 'entity' AND r.subject_id = :1
                        UNION
                        SELECT e.id, e.entity_type, e.canonical_name, r.relation_type
                        FROM vault_relations r
                        JOIN vault_entities e ON e.id = r.subject_id AND r.subject_type = 'entity'
                        WHERE r.object_type = 'entity' AND r.object_id = :2
                    ) FETCH FIRST 50 ROWS ONLY
                """, [eid, eid])
                profile["relations"] = _fetchall_dict(cur)

        return profile

    # === TIMELINE ===

    def timeline(self, entity: str | None = None, topic: str | None = None,
                 start: str | None = None, end: str | None = None,
                 limit: int = 50) -> list[dict]:
        """Chronological view of documents, optionally filtered by entity/topic/date range."""
        # Resolve entity once (avoid triple DB call from original code)
        entity_id = None
        if entity:
            resolved = self.entity_resolve(entity)
            if resolved:
                entity_id = resolved["id"]

        # Build query with clean named binds
        conditions = []
        binds: dict[str, Any] = {"row_limit": limit}
        join = ""

        if start:
            conditions.append("d.occurred_at >= TO_TIMESTAMP(:start_date, 'YYYY-MM-DD')")
            binds["start_date"] = start
        if end:
            conditions.append("d.occurred_at <= TO_TIMESTAMP(:end_date, 'YYYY-MM-DD')")
            binds["end_date"] = end
        if entity_id:
            join = """JOIN vault_relations r ON r.object_type = 'document' AND r.object_id = d.id
                        AND r.subject_type = 'entity' AND r.subject_id = :entity_id"""
            binds["entity_id"] = entity_id
        if topic:
            conditions.append("(LOWER(d.title) LIKE LOWER(:topic_q) OR DBMS_LOB.INSTR(LOWER(d.content), LOWER(:topic_q2)) > 0)")
            binds["topic_q"] = f"%{topic}%"
            binds["topic_q2"] = topic.lower()

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        query = f"""
            SELECT d.id, d.doc_type, d.title, d.occurred_at, d.lifecycle,
                   DBMS_LOB.SUBSTR(d.content, 200, 1) AS excerpt,
                   s.display_name AS source_name
            FROM vault_documents d
            JOIN vault_sources s ON s.id = d.source_id
            {join}
            {where}
            ORDER BY d.occurred_at DESC
            FETCH FIRST :row_limit ROWS ONLY
        """

        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                cur.execute(query, binds)
                return _fetchall_dict(cur)

    # === GRAPH ===

    def relations(self, entity_id: int, depth: int = 1) -> dict:
        """Return relationship graph around an entity.

        Returns: {nodes: [{id, type, name}], edges: [{from, to, type}]}
        """
        nodes: dict[str, dict] = {}
        edges: list[dict] = []
        visited: set[int] = set()
        queue = [entity_id]

        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                for _level in range(depth):
                    next_queue: list[int] = []
                    for eid in queue:
                        if eid in visited:
                            continue
                        visited.add(eid)

                        # Get entity info
                        cur.execute(
                            "SELECT id, entity_type, canonical_name FROM vault_entities WHERE id = :1",
                            [eid],
                        )
                        erow = _fetchone_dict(cur)
                        if erow:
                            nodes[str(eid)] = erow

                        # Get outgoing relations
                        cur.execute("""
                            SELECT r.relation_type, r.object_type, r.object_id, r.confidence,
                                   e.canonical_name AS target_name, e.entity_type AS target_type
                            FROM vault_relations r
                            LEFT JOIN vault_entities e ON r.object_type = 'entity' AND e.id = r.object_id
                            WHERE r.subject_type = 'entity' AND r.subject_id = :1
                        """, [eid])
                        for rel in _fetchall_dict(cur):
                            edges.append({
                                "from": eid,
                                "to": rel["object_id"],
                                "type": rel["relation_type"],
                                "target_type": rel["object_type"],
                                "target_name": rel.get("target_name"),
                                "confidence": rel["confidence"],
                            })
                            if rel["object_type"] == "entity" and rel["object_id"] not in visited:
                                next_queue.append(rel["object_id"])

                        # Get incoming relations
                        cur.execute("""
                            SELECT r.relation_type, r.subject_type, r.subject_id, r.confidence,
                                   e.canonical_name AS source_name, e.entity_type AS source_type
                            FROM vault_relations r
                            LEFT JOIN vault_entities e ON r.subject_type = 'entity' AND e.id = r.subject_id
                            WHERE r.object_type = 'entity' AND r.object_id = :1
                        """, [eid])
                        for rel in _fetchall_dict(cur):
                            edges.append({
                                "from": rel["subject_id"],
                                "to": eid,
                                "type": rel["relation_type"],
                                "target_type": rel["subject_type"],
                                "target_name": rel.get("source_name"),
                                "confidence": rel["confidence"],
                            })
                            if rel["subject_type"] == "entity" and rel["subject_id"] not in visited:
                                next_queue.append(rel["subject_id"])

                    queue = next_queue

        return {"nodes": list(nodes.values()), "edges": edges}

    # === LIFECYCLE ===

    def accept(self, fact_id: int) -> dict:
        """Mark a fact as accepted."""
        return self._update_lifecycle("fact", "vault_facts", fact_id, "accepted", "Accepted by user/agent")

    def supersede(self, fact_id: int, new_fact_id: int, reason: str = "") -> dict:
        """Mark a fact as superseded by another."""
        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE vault_facts SET lifecycle = 'superseded', superseded_by = :1 WHERE id = :2",
                    [new_fact_id, fact_id],
                )
                cur.execute("""
                    INSERT INTO vault_events (target_type, target_id, from_state, to_state, reason, actor)
                    VALUES ('fact', :1, 'accepted', 'superseded', :2, 'vault_api')
                """, [fact_id, reason or f"Superseded by fact #{new_fact_id}"])
                conn.commit()
        return {"ok": True, "fact_id": fact_id, "superseded_by": new_fact_id}

    def retract(self, fact_id: int, reason: str = "") -> dict:
        """Retract a fact (mark as retracted)."""
        return self._update_lifecycle("fact", "vault_facts", fact_id, "retracted", reason or "Retracted")

    # Whitelist of tables allowed in dynamic SQL (C1/C2 audit fix)
    _LIFECYCLE_TABLES = frozenset({"vault_documents", "vault_entities", "vault_facts"})

    def _update_lifecycle(self, target_type: str, table: str, record_id: int,
                          new_state: str, reason: str) -> dict:
        if table not in self._LIFECYCLE_TABLES:
            return {"ok": False, "error": f"Table '{table}' not in allowed lifecycle tables"}
        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT lifecycle FROM {table} WHERE id = :1", [record_id])
                row = cur.fetchone()
                if not row:
                    return {"ok": False, "error": "Record not found"}
                old_state = row[0]

                cur.execute(f"UPDATE {table} SET lifecycle = :1 WHERE id = :2", [new_state, record_id])
                cur.execute("""
                    INSERT INTO vault_events (target_type, target_id, from_state, to_state, reason, actor)
                    VALUES (:1, :2, :3, :4, :5, 'vault_api')
                """, [target_type, record_id, old_state, new_state, reason])
                conn.commit()
        return {"ok": True, "id": record_id, "from": old_state, "to": new_state}

    # === ENTITY MANAGEMENT ===

    def add_entity(self, entity_type: str, canonical_name: str,
                   aliases: list[str] | None = None,
                   metadata: dict | None = None,
                   contact_id: int | None = None,
                   taxonomy_id: int | None = None) -> int:
        """Create an entity with optional aliases. Returns entity ID.
        M5 fix: resolve + insert in same connection, catch constraint violation for race."""
        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                # Check if entity already exists (same connection — reduces TOCTOU window)
                norm = canonical_name.strip().lower()
                cur.execute("""
                    SELECT e.id FROM vault_entities e
                    JOIN vault_entity_aliases a ON a.entity_id = e.id
                    WHERE a.alias_normalized = :1
                    FETCH FIRST 1 ROWS ONLY
                """, [norm])
                row = cur.fetchone()
                if row:
                    return row[0]

                # Also check canonical name directly
                cur.execute("""
                    SELECT id FROM vault_entities WHERE LOWER(canonical_name) = :1
                    FETCH FIRST 1 ROWS ONLY
                """, [norm])
                row = cur.fetchone()
                if row:
                    return row[0]

                eid_var = cur.var(int)
                try:
                    cur.execute("""
                        INSERT INTO vault_entities (entity_type, canonical_name, metadata_json,
                            contact_id, taxonomy_id, first_seen_at, last_seen_at)
                        VALUES (:1, :2, :3, :4, :5, SYSTIMESTAMP, SYSTIMESTAMP)
                        RETURNING id INTO :6
                    """, [entity_type, canonical_name,
                          json.dumps(metadata) if metadata else None,
                          contact_id, taxonomy_id, eid_var])
                    entity_id = eid_var.getvalue()[0]
                except Exception as e:
                    # Race condition: another process created it between check and insert
                    if "unique constraint" in str(e).lower():
                        conn.rollback()
                        resolved = self.entity_resolve(canonical_name)
                        return resolved["id"] if resolved else -1
                    raise

                # Add canonical name as alias
                all_aliases = [canonical_name] + (aliases or [])
                for alias in all_aliases:
                    norm = alias.strip().lower()
                    try:
                        cur.execute("""
                            INSERT INTO vault_entity_aliases (entity_id, alias_text, alias_normalized)
                            VALUES (:1, :2, :3)
                        """, [entity_id, alias, norm])
                    except Exception:
                        pass  # duplicate alias, skip

                conn.commit()
                return entity_id

    def add_relation(self, subject_type: str, subject_id: int,
                     relation_type: str,
                     object_type: str, object_id: int,
                     confidence: float = 1.0,
                     source_doc_id: int | None = None,
                     metadata: dict | None = None) -> int:
        """Create a relation between vault objects. Returns relation ID."""
        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                rid_var = cur.var(int)
                cur.execute("""
                    INSERT INTO vault_relations (subject_type, subject_id, relation_type,
                        object_type, object_id, confidence, source_doc_id, metadata_json)
                    VALUES (:1, :2, :3, :4, :5, :6, :7, :8)
                    RETURNING id INTO :9
                """, [subject_type, subject_id, relation_type,
                      object_type, object_id, confidence, source_doc_id,
                      json.dumps(metadata) if metadata else None,
                      rid_var])
                rel_id = rid_var.getvalue()[0]
                conn.commit()
                return rel_id

    def add_fact(self, claim: str, source_doc_id: int | None = None,
                 source_chunk_id: int | None = None,
                 source_agent: str = "vault_api",
                 confidence: float = 0.8,
                 fact_date: str | None = None,
                 taxonomy_id: int | None = None) -> int:
        """Create a fact/assertion. Returns fact ID."""
        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                fid_var = cur.var(int)
                cur.execute("""
                    INSERT INTO vault_facts (claim, confidence, source_doc_id, source_chunk_id,
                        source_agent, extraction_method, taxonomy_id, fact_date, lifecycle)
                    VALUES (:1, :2, :3, :4, :5, 'manual', :6, TO_TIMESTAMP(:7, 'YYYY-MM-DD'), 'extracted')
                    RETURNING id INTO :8
                """, [claim, confidence, source_doc_id, source_chunk_id,
                      source_agent, taxonomy_id, fact_date,
                      fid_var])
                fact_id = fid_var.getvalue()[0]

                cur.execute("""
                    INSERT INTO vault_events (target_type, target_id, to_state, reason, actor)
                    VALUES ('fact', :1, 'extracted', 'Created via vault_api', :2)
                """, [fact_id, source_agent])

                conn.commit()
                return fact_id

    # === ENTITY MERGE / SPLIT ===

    def merge_entities(self, source_id: int, target_id: int,
                       reason: str = "") -> dict:
        """Merge source entity into target. Source gets merged_into_id = target.
        All aliases from source are copied to target. Relations are re-pointed."""
        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                # Verify both exist
                cur.execute("SELECT id, canonical_name FROM vault_entities WHERE id = :1", [source_id])
                src = _fetchone_dict(cur)
                cur.execute("SELECT id, canonical_name FROM vault_entities WHERE id = :1", [target_id])
                tgt = _fetchone_dict(cur)
                if not src or not tgt:
                    return {"ok": False, "error": "Entity not found"}

                # Copy aliases from source → target
                cur.execute("""
                    SELECT alias_text, alias_normalized, source, confidence
                    FROM vault_entity_aliases WHERE entity_id = :1
                """, [source_id])
                for alias in _fetchall_dict(cur):
                    try:
                        cur.execute("""
                            INSERT INTO vault_entity_aliases
                                (entity_id, alias_text, alias_normalized, source, confidence, verified_by)
                            VALUES (:1, :2, :3, :4, :5, 'entity_merge')
                        """, [target_id, alias["alias_text"], alias["alias_normalized"],
                              alias.get("source", "merge"), alias.get("confidence", 0.8)])
                    except Exception:
                        pass  # duplicate alias

                # Re-point relations
                cur.execute("""
                    UPDATE vault_relations SET subject_id = :1
                    WHERE subject_type = 'entity' AND subject_id = :2
                """, [target_id, source_id])
                cur.execute("""
                    UPDATE vault_relations SET object_id = :1
                    WHERE object_type = 'entity' AND object_id = :2
                """, [target_id, source_id])

                # Mark source as merged
                cur.execute("""
                    UPDATE vault_entities SET merged_into_id = :1, lifecycle = 'merged',
                        updated_at = SYSTIMESTAMP
                    WHERE id = :2
                """, [target_id, source_id])

                # Log event
                cur.execute("""
                    INSERT INTO vault_events (target_type, target_id, from_state, to_state, reason, actor)
                    VALUES ('entity', :1, 'extracted', 'merged', :2, 'vault_api')
                """, [source_id, reason or f"Merged into entity #{target_id}"])

                # Audit trail (must succeed — no silent swallowing)
                cur.execute("""
                    INSERT INTO vault_audit_trail (action, actor, target_type, target_id, details)
                    VALUES ('merge_entity', 'vault_api', 'entity', :1, :2)
                """, [source_id, json.dumps({
                    "source_id": source_id, "source_name": src["canonical_name"],
                    "target_id": target_id, "target_name": tgt["canonical_name"],
                    "reason": reason,
                })])

                conn.commit()
                return {
                    "ok": True,
                    "merged": src["canonical_name"],
                    "into": tgt["canonical_name"],
                }

    def gdpr_erase(self, entity_id: int, reason: str = "GDPR erasure request") -> dict:
        """Privacy deletion: redact all content associated with an entity.
        Does NOT physically delete — sets redacted_at tombstone on documents,
        removes entity content, logs the operation."""
        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                # 1. Find entity
                cur.execute("SELECT id, canonical_name FROM vault_entities WHERE id = :1", [entity_id])
                entity = _fetchone_dict(cur)
                if not entity:
                    return {"ok": False, "error": "Entity not found"}

                report = {
                    "entity": entity["canonical_name"],
                    "documents_redacted": 0,
                    "chunks_cleared": 0,
                    "facts_retracted": 0,
                    "relations_removed": 0,
                    "aliases_removed": 0,
                }

                # 2. Find all related documents — via relations AND email_from match
                #    (audit found: H2 — unlinked docs were missed)
                cur.execute("""
                    SELECT DISTINCT id FROM (
                        SELECT d.id FROM vault_documents d
                        JOIN vault_relations r ON r.object_type = 'document' AND r.object_id = d.id
                        WHERE r.subject_type = 'entity' AND r.subject_id = :1
                        UNION
                        SELECT d.id FROM vault_documents d
                        WHERE d.email_from IS NOT NULL AND LOWER(d.email_from) LIKE '%' || LOWER(:2) || '%'
                    )
                """, [entity_id, entity["canonical_name"]])
                doc_ids = [r[0] for r in cur.fetchall()]

                # 3. Redact documents + clear their chunks
                for doc_id in doc_ids:
                    cur.execute("""
                        UPDATE vault_documents SET redacted_at = SYSTIMESTAMP,
                            content = '[REDACTED]', title = '[REDACTED]',
                            metadata_json = NULL, is_latest = 0
                        WHERE id = :1
                    """, [doc_id])
                    report["documents_redacted"] += 1
                    # Clear chunk content (audit H2: chunks retained original text)
                    cur.execute("""
                        UPDATE vault_chunks SET text_content = '[REDACTED]',
                            summary = NULL, embedding = NULL
                        WHERE document_id = :1
                    """, [doc_id])
                    report["chunks_cleared"] += cur.rowcount

                # 4. Retract all facts linked to these documents
                if doc_ids:
                    # Use IN clause with bind list
                    placeholders = ",".join(f":{i+1}" for i in range(len(doc_ids)))
                    cur.execute(f"""
                        UPDATE vault_facts SET lifecycle = 'retracted'
                        WHERE source_doc_id IN ({placeholders})
                    """, doc_ids)
                    report["facts_retracted"] = cur.rowcount

                # 5. Remove relations
                cur.execute("""
                    DELETE FROM vault_relations
                    WHERE (subject_type = 'entity' AND subject_id = :1)
                       OR (object_type = 'entity' AND object_id = :2)
                """, [entity_id, entity_id])
                report["relations_removed"] = cur.rowcount

                # 6. Remove aliases
                cur.execute("DELETE FROM vault_entity_aliases WHERE entity_id = :1", [entity_id])
                report["aliases_removed"] = cur.rowcount

                # 7. Anonymize entity
                cur.execute("""
                    UPDATE vault_entities SET canonical_name = '[REDACTED]',
                        metadata_json = NULL, embedding = NULL,
                        lifecycle = 'retracted', updated_at = SYSTIMESTAMP
                    WHERE id = :1
                """, [entity_id])

                # 8. Log event
                cur.execute("""
                    INSERT INTO vault_events (target_type, target_id, to_state, reason, actor)
                    VALUES ('entity', :1, 'retracted', :2, 'vault_api.gdpr_erase')
                """, [entity_id, reason])

                # 9. Audit trail (must succeed — legally required for GDPR)
                cur.execute("""
                    INSERT INTO vault_audit_trail (action, actor, target_type, target_id, details)
                    VALUES ('gdpr_erase', 'vault_api', 'entity', :1, :2)
                """, [entity_id, json.dumps(report)])

                conn.commit()
                return {"ok": True, **report}

    # === ADMIN ===

    # Hardcoded table list for stats — safe from SQL injection (C1 audit note)
    _STATS_TABLES = [
        "vault_sources", "vault_documents", "vault_chunks",
        "vault_entities", "vault_entity_aliases", "vault_facts",
        "vault_relations", "vault_events", "vault_sync_log",
        "vault_audit_trail", "vault_metrics", "vault_doc_types",
    ]

    def stats(self) -> dict:
        """Get table row counts and schema info."""
        tables = self._STATS_TABLES
        result: dict[str, Any] = {"tables": {}, "schema_version": None}

        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                for t in tables:
                    try:
                        cur.execute(f"SELECT COUNT(*) FROM {t}")
                        result["tables"][t] = cur.fetchone()[0]
                    except Exception:
                        result["tables"][t] = "ERROR"

                try:
                    cur.execute("SELECT value FROM vault_schema_meta WHERE key = 'schema_version'")
                    row = cur.fetchone()
                    result["schema_version"] = row[0] if row else None
                except Exception:
                    pass

        return result

    def doctor(self) -> dict:
        """Check Vault health."""
        diag: dict[str, Any] = {"connection": "ok", "vector_support": False}
        with self._pool.acquire() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("SELECT VECTOR('[1.0, 2.0, 3.0]', 3, FLOAT32) FROM dual")
                    diag["vector_support"] = True
                except Exception:
                    pass
        diag.update(self.stats())
        return diag


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    print("=== Vault API Smoke Test ===\n")
    v = Vault()

    print("1. Stats:")
    s = v.stats()
    for table, count in s["tables"].items():
        print(f"   {table:30s} {count}")
    print(f"   Schema: {s['schema_version']}\n")

    print("2. Ingest test document:")
    doc_id = v.ingest(
        content="Test document from vault_api smoke test. This is a test email from David about Project Alpha.",
        doc_type="note",
        title="Vault API Smoke Test",
        meta={"test": True},
        source_info={"type": "manual", "uri": "test://vault_api_smoke"},
    )
    print(f"   Created document ID: {doc_id}\n")

    print("3. Search for 'David':")
    results = v.search("David", limit=5)
    for r in results:
        print(f"   [{r['type']}] {r.get('title') or r.get('claim', '')[:60]}")
    print()

    print("4. Add entity:")
    eid = v.add_entity("person", "David Chen", aliases=["David", "陳大衛"])
    print(f"   Entity ID: {eid}\n")

    print("5. Entity resolve:")
    e = v.entity_resolve("david")
    print(f"   Resolved: {e['canonical_name'] if e else 'NOT FOUND'}\n")

    print("6. About entity:")
    profile = v.about("David Chen")
    if profile:
        print(f"   Entity: {profile['entity']['canonical_name']}")
        print(f"   Aliases: {profile['aliases']}")
        print(f"   Documents: {len(profile['documents'])}")
        print(f"   Facts: {len(profile['facts'])}")
        print(f"   Relations: {len(profile['relations'])}")
    print()

    print("7. Final stats:")
    s = v.stats()
    for table, count in s["tables"].items():
        print(f"   {table:30s} {count}")

    print("\n=== Smoke test complete ===")
