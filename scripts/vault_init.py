"""
vault_init.py — Initialize The Vault (Oracle L3 Deep Brain) schema.

Creates 9 vault tables + indexes + views in an Oracle Autonomous Database.
Non-destructive: skips tables that already exist.

Usage:
    # Using clawd-lobster config (reads ~/.clawd-lobster/config.json):
    python vault_init.py

    # With explicit connection params:
    python vault_init.py --wallet-dir /path/to/wallet --dsn mydb_tp --user VAULT_USER --password secret

    # Dry run (print DDL without executing):
    python vault_init.py --dry-run

    # Verify existing schema:
    python vault_init.py --doctor

Requires: oracledb (pip install oracledb)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Schema version — bump when DDL changes
# ---------------------------------------------------------------------------
SCHEMA_VERSION = "11.0.0"

# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def _load_config() -> dict:
    """Load Oracle config from clawd-lobster config.json."""
    config_file = Path.home() / ".clawd-lobster" / "config.json"
    if not config_file.exists():
        return {}
    with open(config_file, encoding="utf-8") as f:
        return json.load(f).get("oracle", {})


def get_connection(args: argparse.Namespace):
    """Get Oracle connection from CLI args or config."""
    try:
        import oracledb
    except ImportError:
        print("ERROR: oracledb not installed. Run: pip install oracledb")
        sys.exit(1)

    cfg = _load_config()

    wallet_dir = args.wallet_dir or cfg.get("wallet_dir", "")
    dsn = args.dsn or cfg.get("dsn", "")
    user = args.user or cfg.get("user", "")
    password = args.password or cfg.get("password", "") or os.environ.get("CLAWD_ORACLE_PASSWORD", "")
    wallet_password = args.wallet_password or cfg.get("wallet_password", "") or os.environ.get("CLAWD_ORACLE_WALLET_PASSWORD", "")

    if not all([wallet_dir, dsn, user, password]):
        missing = []
        if not wallet_dir:
            missing.append("wallet_dir")
        if not dsn:
            missing.append("dsn")
        if not user:
            missing.append("user")
        if not password:
            missing.append("password")
        print(f"ERROR: Missing Oracle config: {', '.join(missing)}")
        print("Set in ~/.clawd-lobster/config.json under 'oracle' key, or pass as CLI args.")
        sys.exit(1)

    connect_kwargs = {
        "user": user,
        "password": password,
        "dsn": dsn,
    }
    if wallet_dir:
        connect_kwargs["config_dir"] = wallet_dir
        connect_kwargs["wallet_location"] = wallet_dir
        if wallet_password:
            connect_kwargs["wallet_password"] = wallet_password

    return oracledb.connect(**connect_kwargs)


# ---------------------------------------------------------------------------
# DDL definitions
# ---------------------------------------------------------------------------

TABLES: list[tuple[str, str]] = [
    # 1. SOURCES
    (
        "vault_sources",
        """CREATE TABLE vault_sources (
            id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            source_type     VARCHAR2(50) NOT NULL,
            source_uri      VARCHAR2(2048) NOT NULL,
            source_uri_hash VARCHAR2(64) NOT NULL,
            display_name    VARCHAR2(512),
            trust_level     NUMBER(3,2) DEFAULT 0.80,
            metadata_json   CLOB CHECK (metadata_json IS JSON),
            created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
            CONSTRAINT uq_source_uri UNIQUE (source_type, source_uri_hash)
        )""",
    ),
    # 2. DOCUMENTS (v11: +ownership, email fields, versioning, fidelity, redaction)
    (
        "vault_documents",
        """CREATE TABLE vault_documents (
            id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            source_id       NUMBER NOT NULL REFERENCES vault_sources(id),
            doc_type        VARCHAR2(50) NOT NULL,
            title           VARCHAR2(1000),
            content         CLOB,
            content_hash    VARCHAR2(64),
            occurred_at     TIMESTAMP NOT NULL,
            ingested_at     TIMESTAMP DEFAULT SYSTIMESTAMP,
            metadata_json   CLOB CHECK (metadata_json IS JSON),
            taxonomy_id     NUMBER,
            privacy_level   VARCHAR2(20) DEFAULT 'internal',
            language        VARCHAR2(10) DEFAULT 'en',
            embedding       VECTOR(1536, FLOAT32),
            embedding_model VARCHAR2(128),
            lifecycle       VARCHAR2(20) DEFAULT 'raw',
            ownership       VARCHAR2(20) DEFAULT 'self',
            email_from      VARCHAR2(500),
            email_importance VARCHAR2(10),
            email_direction VARCHAR2(10),
            threat_score    NUMBER(3,2),
            parent_doc_id   NUMBER,
            version         NUMBER DEFAULT 1,
            is_latest       NUMBER(1) DEFAULT 1,
            fidelity        VARCHAR2(15) DEFAULT 'high',
            redacted_at     TIMESTAMP,
            original_path   VARCHAR2(2048),
            CONSTRAINT uq_doc_content UNIQUE (source_id, content_hash)
        )""",
    ),
    # 3. CHUNKS
    (
        "vault_chunks",
        """CREATE TABLE vault_chunks (
            id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            document_id     NUMBER NOT NULL REFERENCES vault_documents(id),
            chunk_index     NUMBER NOT NULL,
            text_content    CLOB NOT NULL,
            token_count     NUMBER,
            char_start      NUMBER,
            char_end        NUMBER,
            summary         VARCHAR2(2000),
            embedding       VECTOR(1536, FLOAT32),
            embedding_model VARCHAR2(128),
            created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
            CONSTRAINT uq_chunk UNIQUE (document_id, chunk_index)
        )""",
    ),
    # 4. ENTITIES (v11: +ownership, +merged_into_id)
    (
        "vault_entities",
        """CREATE TABLE vault_entities (
            id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            entity_type     VARCHAR2(50) NOT NULL,
            canonical_name  VARCHAR2(500) NOT NULL,
            metadata_json   CLOB CHECK (metadata_json IS JSON),
            contact_id      NUMBER,
            taxonomy_id     NUMBER,
            embedding       VECTOR(1536, FLOAT32),
            first_seen_at   TIMESTAMP,
            last_seen_at    TIMESTAMP,
            confidence      NUMBER(3,2) DEFAULT 0.80,
            lifecycle       VARCHAR2(20) DEFAULT 'extracted',
            ownership       VARCHAR2(20) DEFAULT 'external',
            merged_into_id  NUMBER,
            created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
            updated_at      TIMESTAMP DEFAULT SYSTIMESTAMP
        )""",
    ),
    # 5. ENTITY ALIASES (v11: +confidence, +verified_by)
    (
        "vault_entity_aliases",
        """CREATE TABLE vault_entity_aliases (
            id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            entity_id       NUMBER NOT NULL REFERENCES vault_entities(id),
            alias_text      VARCHAR2(500) NOT NULL,
            alias_normalized VARCHAR2(500) NOT NULL,
            source          VARCHAR2(64) DEFAULT 'extraction',
            confidence      NUMBER(3,2) DEFAULT 1.0,
            verified_by     VARCHAR2(50) DEFAULT 'auto_extracted',
            created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
            CONSTRAINT uq_alias UNIQUE (entity_id, alias_normalized)
        )""",
    ),
    # 6. FACTS (v11: +fact_type, +subject, +predicate, +object, +valid_from/to)
    (
        "vault_facts",
        """CREATE TABLE vault_facts (
            id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            claim           VARCHAR2(4000) NOT NULL,
            fact_type       VARCHAR2(30) DEFAULT 'claim',
            subject         VARCHAR2(500),
            predicate       VARCHAR2(200),
            object_value    CLOB,
            confidence      NUMBER(3,2) DEFAULT 0.80,
            source_doc_id   NUMBER REFERENCES vault_documents(id),
            source_chunk_id NUMBER REFERENCES vault_chunks(id),
            source_agent    VARCHAR2(50),
            extraction_method VARCHAR2(50),
            taxonomy_id     NUMBER,
            fact_date       TIMESTAMP,
            valid_from      TIMESTAMP,
            valid_to        TIMESTAMP,
            created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
            lifecycle       VARCHAR2(20) DEFAULT 'extracted',
            superseded_by   NUMBER,
            embedding       VECTOR(1536, FLOAT32)
        )""",
    ),
    # 7. RELATIONS
    (
        "vault_relations",
        """CREATE TABLE vault_relations (
            id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            subject_type    VARCHAR2(20) NOT NULL,
            subject_id      NUMBER NOT NULL,
            relation_type   VARCHAR2(100) NOT NULL,
            object_type     VARCHAR2(20) NOT NULL,
            object_id       NUMBER NOT NULL,
            confidence      NUMBER(3,2) DEFAULT 1.0,
            source_doc_id   NUMBER REFERENCES vault_documents(id),
            metadata_json   CLOB CHECK (metadata_json IS JSON),
            created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
            CONSTRAINT chk_rel_subject CHECK (subject_type IN ('entity','document','fact','chunk')),
            CONSTRAINT chk_rel_object CHECK (object_type IN ('entity','document','fact','chunk'))
        )""",
    ),
    # 8. EVENTS (immutable lifecycle log)
    (
        "vault_events",
        """CREATE TABLE vault_events (
            id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            target_type     VARCHAR2(50) NOT NULL,
            target_id       NUMBER NOT NULL,
            from_state      VARCHAR2(30),
            to_state        VARCHAR2(30) NOT NULL,
            reason          VARCHAR2(2000),
            actor           VARCHAR2(64),
            created_at      TIMESTAMP DEFAULT SYSTIMESTAMP
        )""",
    ),
    # 9. SYNC LOG
    (
        "vault_sync_log",
        """CREATE TABLE vault_sync_log (
            id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            source_layer    VARCHAR2(10) NOT NULL,
            source_id       VARCHAR2(200) NOT NULL,
            source_hash     VARCHAR2(64),
            vault_table     VARCHAR2(50) NOT NULL,
            vault_id        NUMBER NOT NULL,
            synced_at       TIMESTAMP DEFAULT SYSTIMESTAMP,
            sync_agent      VARCHAR2(50),
            CONSTRAINT uq_sync UNIQUE (source_layer, source_id, vault_table)
        )""",
    ),
    # 10. AUDIT TRAIL (v11 — operational audit log)
    (
        "vault_audit_trail",
        """CREATE TABLE vault_audit_trail (
            id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            action          VARCHAR2(50) NOT NULL,
            actor           VARCHAR2(100),
            target_type     VARCHAR2(50),
            target_id       NUMBER,
            details         CLOB CHECK (details IS JSON),
            created_at      TIMESTAMP DEFAULT SYSTIMESTAMP
        )""",
    ),
    # 11. METRICS (v11 — quantified self-awareness)
    (
        "vault_metrics",
        """CREATE TABLE vault_metrics (
            id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            metric_type     VARCHAR2(50) NOT NULL,
            metric_value    NUMBER,
            metric_json     CLOB CHECK (metric_json IS JSON),
            measured_at     TIMESTAMP DEFAULT SYSTIMESTAMP
        )""",
    ),
    # 12. DOC TYPES (v11 — advisory registry, no FK from vault_documents)
    (
        "vault_doc_types",
        """CREATE TABLE vault_doc_types (
            doc_type        VARCHAR2(50) PRIMARY KEY,
            description     VARCHAR2(500),
            parent_type     VARCHAR2(50),
            created_at      TIMESTAMP DEFAULT SYSTIMESTAMP
        )""",
    ),
]

# ---------------------------------------------------------------------------
# ALTER TABLE statements for upgrading existing v4 schema to v11
# Each statement is (description, SQL). Safe to re-run: ORA-01430 = column exists.
# ---------------------------------------------------------------------------
ALTER_STATEMENTS: list[tuple[str, str]] = [
    # vault_documents new columns
    ("vault_documents.ownership", "ALTER TABLE vault_documents ADD ownership VARCHAR2(20) DEFAULT 'self'"),
    ("vault_documents.email_from", "ALTER TABLE vault_documents ADD email_from VARCHAR2(500)"),
    ("vault_documents.email_importance", "ALTER TABLE vault_documents ADD email_importance VARCHAR2(10)"),
    ("vault_documents.email_direction", "ALTER TABLE vault_documents ADD email_direction VARCHAR2(10)"),
    ("vault_documents.threat_score", "ALTER TABLE vault_documents ADD threat_score NUMBER(3,2)"),
    ("vault_documents.parent_doc_id", "ALTER TABLE vault_documents ADD parent_doc_id NUMBER"),
    ("vault_documents.version", "ALTER TABLE vault_documents ADD version NUMBER DEFAULT 1"),
    ("vault_documents.is_latest", "ALTER TABLE vault_documents ADD is_latest NUMBER(1) DEFAULT 1"),
    ("vault_documents.fidelity", "ALTER TABLE vault_documents ADD fidelity VARCHAR2(15) DEFAULT 'high'"),
    ("vault_documents.redacted_at", "ALTER TABLE vault_documents ADD redacted_at TIMESTAMP"),
    ("vault_documents.original_path", "ALTER TABLE vault_documents ADD original_path VARCHAR2(2048)"),
    # vault_entities new columns
    ("vault_entities.ownership", "ALTER TABLE vault_entities ADD ownership VARCHAR2(20) DEFAULT 'external'"),
    ("vault_entities.merged_into_id", "ALTER TABLE vault_entities ADD merged_into_id NUMBER"),
    # vault_entity_aliases new columns
    ("vault_entity_aliases.confidence", "ALTER TABLE vault_entity_aliases ADD confidence NUMBER(3,2) DEFAULT 1.0"),
    ("vault_entity_aliases.verified_by", "ALTER TABLE vault_entity_aliases ADD verified_by VARCHAR2(50) DEFAULT 'auto_extracted'"),
    # vault_facts new columns
    ("vault_facts.fact_type", "ALTER TABLE vault_facts ADD fact_type VARCHAR2(30) DEFAULT 'claim'"),
    ("vault_facts.subject", "ALTER TABLE vault_facts ADD subject VARCHAR2(500)"),
    ("vault_facts.predicate", "ALTER TABLE vault_facts ADD predicate VARCHAR2(200)"),
    ("vault_facts.object_value", "ALTER TABLE vault_facts ADD object_value CLOB"),
    ("vault_facts.valid_from", "ALTER TABLE vault_facts ADD valid_from TIMESTAMP"),
    ("vault_facts.valid_to", "ALTER TABLE vault_facts ADD valid_to TIMESTAMP"),
]

INDEXES: list[str] = [
    # Documents
    "CREATE INDEX idx_vdoc_type ON vault_documents(doc_type)",
    "CREATE INDEX idx_vdoc_occurred ON vault_documents(occurred_at)",
    "CREATE INDEX idx_vdoc_source ON vault_documents(source_id)",
    "CREATE INDEX idx_vdoc_taxonomy ON vault_documents(taxonomy_id)",
    "CREATE INDEX idx_vdoc_hash ON vault_documents(content_hash)",
    "CREATE INDEX idx_vdoc_lifecycle ON vault_documents(lifecycle)",
    # v11: new document indexes
    "CREATE INDEX idx_vdoc_ownership ON vault_documents(ownership)",
    "CREATE INDEX idx_vdoc_email_from ON vault_documents(email_from)",
    "CREATE INDEX idx_vdoc_parent ON vault_documents(parent_doc_id)",
    "CREATE INDEX idx_vdoc_latest ON vault_documents(is_latest)",
    "CREATE INDEX idx_vdoc_fidelity ON vault_documents(fidelity)",
    "CREATE INDEX idx_vdoc_original_path ON vault_documents(original_path)",
    # Chunks
    "CREATE INDEX idx_vchunk_doc ON vault_chunks(document_id)",
    # Entities
    "CREATE INDEX idx_ventity_type ON vault_entities(entity_type)",
    "CREATE INDEX idx_ventity_name ON vault_entities(canonical_name)",
    "CREATE INDEX idx_ventity_contact ON vault_entities(contact_id)",
    # v11: entity merge tracking
    "CREATE INDEX idx_ventity_merged ON vault_entities(merged_into_id)",
    # Aliases
    "CREATE INDEX idx_valias_norm ON vault_entity_aliases(alias_normalized)",
    "CREATE INDEX idx_valias_entity ON vault_entity_aliases(entity_id)",
    # Facts
    "CREATE INDEX idx_vfact_source ON vault_facts(source_doc_id)",
    "CREATE INDEX idx_vfact_lifecycle ON vault_facts(lifecycle)",
    "CREATE INDEX idx_vfact_date ON vault_facts(fact_date)",
    "CREATE INDEX idx_vfact_agent ON vault_facts(source_agent)",
    # v11: fact_type index
    "CREATE INDEX idx_vfact_type ON vault_facts(fact_type)",
    # Relations
    "CREATE INDEX idx_vrel_subject ON vault_relations(subject_type, subject_id)",
    "CREATE INDEX idx_vrel_object ON vault_relations(object_type, object_id)",
    "CREATE INDEX idx_vrel_type ON vault_relations(relation_type)",
    # Events
    "CREATE INDEX idx_vevent_target ON vault_events(target_type, target_id)",
    "CREATE INDEX idx_vevent_time ON vault_events(created_at)",
    # Sync log
    "CREATE INDEX idx_vsync_source ON vault_sync_log(source_layer, source_id)",
    # v11: Audit trail
    "CREATE INDEX idx_vaudit_action ON vault_audit_trail(action)",
    "CREATE INDEX idx_vaudit_actor ON vault_audit_trail(actor)",
    "CREATE INDEX idx_vaudit_created ON vault_audit_trail(created_at)",
    # v11: Metrics
    "CREATE INDEX idx_vmetrics_type ON vault_metrics(metric_type)",
    "CREATE INDEX idx_vmetrics_measured ON vault_metrics(measured_at)",
]

VIEWS: list[tuple[str, str]] = [
    (
        "v_document_summary",
        """CREATE OR REPLACE VIEW v_document_summary AS
        SELECT d.id, d.doc_type, d.title, d.occurred_at, d.lifecycle,
               d.privacy_level, d.language, d.ownership, d.fidelity, d.is_latest,
               s.source_type, s.display_name AS source_name,
               (SELECT COUNT(*) FROM vault_chunks c WHERE c.document_id = d.id) AS chunk_count,
               (SELECT COUNT(*) FROM vault_facts f WHERE f.source_doc_id = d.id) AS fact_count
        FROM vault_documents d
        JOIN vault_sources s ON s.id = d.source_id""",
    ),
    (
        "v_entity_profile",
        """CREATE OR REPLACE VIEW v_entity_profile AS
        SELECT e.id, e.entity_type, e.canonical_name, e.confidence, e.lifecycle,
               e.ownership, e.merged_into_id, e.first_seen_at, e.last_seen_at,
               (SELECT LISTAGG(a.alias_text, ', ') WITHIN GROUP (ORDER BY a.alias_text)
                FROM vault_entity_aliases a WHERE a.entity_id = e.id) AS aliases,
               (SELECT COUNT(*) FROM vault_relations r
                WHERE (r.subject_type = 'entity' AND r.subject_id = e.id)
                   OR (r.object_type = 'entity' AND r.object_id = e.id)) AS relation_count
        FROM vault_entities e""",
    ),
    # v11: current documents view (non-retracted, latest version)
    (
        "v_current_documents",
        """CREATE OR REPLACE VIEW v_current_documents AS
        SELECT d.id, d.doc_type, d.title, d.occurred_at, d.lifecycle,
               d.privacy_level, d.ownership, d.fidelity, d.version,
               d.email_from, d.email_direction, d.original_path,
               s.source_type, s.display_name AS source_name
        FROM vault_documents d
        JOIN vault_sources s ON s.id = d.source_id
        WHERE d.is_latest = 1 AND d.redacted_at IS NULL""",
    ),
]

# Schema version metadata table
SCHEMA_META_DDL = """CREATE TABLE vault_schema_meta (
    key     VARCHAR2(100) PRIMARY KEY,
    value   VARCHAR2(1000),
    updated_at TIMESTAMP DEFAULT SYSTIMESTAMP
)"""

# ---------------------------------------------------------------------------
# Seed data for vault_doc_types (25 initial types)
# ---------------------------------------------------------------------------
DOC_TYPE_SEEDS: list[tuple[str, str, str | None]] = [
    ("email", "Electronic mail message", None),
    ("conversation", "Chat/messaging conversation", None),
    ("social_post", "Social media post", None),
    ("daily_report", "Daily work summary report", "report"),
    ("report", "Generic report", None),
    ("note", "Personal or work note", None),
    ("sop", "Standard operating procedure", None),
    ("pdf", "PDF document", None),
    ("image", "Photograph or image", None),
    ("voice_memo", "Audio recording with transcription", None),
    ("meeting_transcript", "Meeting recording transcript", None),
    ("action_log", "Agent or human action log entry", None),
    ("debate_transcript", "AI roundtable debate record", None),
    ("code_artifact", "Source code file or snippet", None),
    ("webpage", "Archived web page", None),
    ("file", "Generic file", None),
    ("financial_record", "Invoice, receipt, statement", None),
    ("health_record", "Medical or health document", None),
    ("legal_document", "Contract, agreement, legal filing", None),
    ("news_article", "News or press article", None),
    ("scan", "Scanned document or handwritten note", None),
    ("research_paper", "Academic or research publication", "pdf"),
    ("presentation", "Slide deck or presentation", "file"),
    ("spreadsheet", "Excel or data spreadsheet", "file"),
    ("knowledge", "Knowledge base article", "note"),
]


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def _table_exists(cursor, table_name: str) -> bool:
    cursor.execute(
        "SELECT COUNT(*) FROM user_tables WHERE table_name = :1",
        [table_name.upper()],
    )
    return cursor.fetchone()[0] > 0


def _index_exists(cursor, index_name: str) -> bool:
    cursor.execute(
        "SELECT COUNT(*) FROM user_indexes WHERE index_name = :1",
        [index_name.upper()],
    )
    return cursor.fetchone()[0] > 0


def create_tables(cursor, dry_run: bool = False) -> dict:
    """Create all vault tables. Returns {created: [], skipped: [], errors: []}."""
    result = {"created": [], "skipped": [], "errors": []}

    for name, ddl in TABLES:
        if dry_run:
            print(f"[DRY RUN] Would create: {name}")
            print(f"  {ddl[:120]}...")
            result["created"].append(name)
            continue
        if _table_exists(cursor, name):
            result["skipped"].append(name)
            continue
        try:
            cursor.execute(ddl)
            result["created"].append(name)
            print(f"  [OK] Created: {name}")
        except Exception as e:
            err = str(e)
            if "ORA-00955" in err:
                result["skipped"].append(name)
            else:
                result["errors"].append(f"{name}: {err}")
                print(f"  [ERR] {name}: {err}")

    return result


def create_indexes(cursor, dry_run: bool = False) -> dict:
    """Create all indexes. Returns {created: [], skipped: [], errors: []}."""
    result = {"created": [], "skipped": [], "errors": []}

    for ddl in INDEXES:
        # Extract index name from "CREATE INDEX idx_name ON ..."
        parts = ddl.split()
        idx_name = parts[2] if len(parts) > 2 else "unknown"

        if dry_run:
            print(f"[DRY RUN] Would create index: {idx_name}")
            result["created"].append(idx_name)
            continue
        if _index_exists(cursor, idx_name):
            result["skipped"].append(idx_name)
            continue
        try:
            cursor.execute(ddl)
            result["created"].append(idx_name)
        except Exception as e:
            err = str(e)
            if "ORA-00955" in err or "ORA-01408" in err:
                result["skipped"].append(idx_name)
            else:
                result["errors"].append(f"{idx_name}: {err}")

    return result


def apply_alters(cursor, dry_run: bool = False) -> dict:
    """Apply ALTER TABLE statements for upgrading v4 to v11. Safe to re-run."""
    result = {"applied": [], "skipped": [], "errors": []}
    for desc, ddl in ALTER_STATEMENTS:
        if dry_run:
            print(f"[DRY RUN] Would alter: {desc}")
            result["applied"].append(desc)
            continue
        try:
            cursor.execute(ddl)
            result["applied"].append(desc)
        except Exception as e:
            err = str(e)
            if "ORA-01430" in err:  # column already exists
                result["skipped"].append(desc)
            else:
                result["errors"].append(f"{desc}: {err}")
    return result


def seed_doc_types(cursor, dry_run: bool = False) -> dict:
    """Seed vault_doc_types with initial 25 types. Safe to re-run (MERGE)."""
    result = {"seeded": 0, "skipped": 0, "errors": []}
    for doc_type, description, parent_type in DOC_TYPE_SEEDS:
        if dry_run:
            result["seeded"] += 1
            continue
        try:
            # M8 fix: use named binds for clarity (doc_type appears in both USING and INSERT)
            cursor.execute("""
                MERGE INTO vault_doc_types t
                USING (SELECT :dt_match AS doc_type FROM dual) s
                ON (t.doc_type = s.doc_type)
                WHEN NOT MATCHED THEN INSERT (doc_type, description, parent_type)
                    VALUES (:dt_val, :desc, :parent)
            """, {"dt_match": doc_type, "dt_val": doc_type,
                  "desc": description, "parent": parent_type})
            result["seeded"] += 1
        except Exception as e:
            err = str(e)
            if "ORA-00001" in err:  # unique constraint = already exists
                result["skipped"] += 1
            else:
                result["errors"].append(f"{doc_type}: {err}")
    return result


def create_views(cursor, dry_run: bool = False) -> dict:
    """Create or replace views. Returns {created: [], errors: []}."""
    result = {"created": [], "errors": []}

    for name, ddl in VIEWS:
        if dry_run:
            print(f"[DRY RUN] Would create view: {name}")
            result["created"].append(name)
            continue
        try:
            cursor.execute(ddl)
            result["created"].append(name)
        except Exception as e:
            result["errors"].append(f"{name}: {str(e)}")

    return result


def update_schema_version(cursor, dry_run: bool = False) -> None:
    """Store schema version in vault_schema_meta."""
    if dry_run:
        print(f"[DRY RUN] Would set schema_version = {SCHEMA_VERSION}")
        return

    if not _table_exists(cursor, "vault_schema_meta"):
        try:
            cursor.execute(SCHEMA_META_DDL)
        except Exception:
            pass  # already exists

    cursor.execute("""
        MERGE INTO vault_schema_meta m
        USING (SELECT 'schema_version' AS key FROM dual) s
        ON (m.key = s.key)
        WHEN MATCHED THEN UPDATE SET value = :1, updated_at = SYSTIMESTAMP
        WHEN NOT MATCHED THEN INSERT (key, value) VALUES ('schema_version', :2)
    """, [SCHEMA_VERSION, SCHEMA_VERSION])


def doctor(cursor) -> dict:
    """Check schema health. Returns diagnostic dict."""
    diag = {
        "connection": "ok",
        "schema_version": None,
        "vector_support": False,
        "tables": {},
        "missing_tables": [],
        "missing_indexes": [],
    }

    # Schema version
    if _table_exists(cursor, "vault_schema_meta"):
        cursor.execute("SELECT value FROM vault_schema_meta WHERE key = 'schema_version'")
        row = cursor.fetchone()
        diag["schema_version"] = row[0] if row else None

    # Check VECTOR support
    try:
        cursor.execute("SELECT VECTOR('[1.0, 2.0, 3.0]', 3, FLOAT32) FROM dual")
        diag["vector_support"] = True
    except Exception:
        diag["vector_support"] = False

    # Check tables + row counts (C2 fix: names come from TABLES constant, not user input)
    _ALLOWED_TABLES = frozenset(n for n, _ in TABLES)
    for name, _ in TABLES:
        if name not in _ALLOWED_TABLES:
            continue
        if _table_exists(cursor, name):
            cursor.execute(f"SELECT COUNT(*) FROM {name}")
            diag["tables"][name] = cursor.fetchone()[0]
        else:
            diag["missing_tables"].append(name)

    # Check indexes
    for ddl in INDEXES:
        parts = ddl.split()
        idx_name = parts[2] if len(parts) > 2 else "unknown"
        if not _index_exists(cursor, idx_name):
            diag["missing_indexes"].append(idx_name)

    return diag


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Initialize The Vault (Oracle L3) schema.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Reads config from ~/.clawd-lobster/config.json if CLI args not provided.",
    )
    parser.add_argument("--wallet-dir", help="Oracle wallet directory path")
    parser.add_argument("--wallet-password", help="Oracle wallet password")
    parser.add_argument("--dsn", help="Oracle DSN (e.g., mydb_tp)")
    parser.add_argument("--user", help="Oracle username")
    parser.add_argument("--password", help="Oracle password")
    parser.add_argument("--dry-run", action="store_true", help="Print DDL without executing")
    parser.add_argument("--doctor", action="store_true", help="Check schema health and exit")
    args = parser.parse_args()

    print(f"The Vault — Schema v{SCHEMA_VERSION}")
    print("=" * 50)

    if args.dry_run:
        print("[DRY RUN MODE — no changes will be made]\n")
        print("--- Tables ---")
        create_tables(None, dry_run=True)
        print("\n--- ALTER (v4 to v11 upgrades) ---")
        apply_alters(None, dry_run=True)
        print("\n--- Indexes ---")
        create_indexes(None, dry_run=True)
        print("\n--- Views ---")
        create_views(None, dry_run=True)
        print("\n--- Seed doc types ---")
        seed_doc_types(None, dry_run=True)
        print(f"\n--- Schema version: {SCHEMA_VERSION} ---")
        return

    conn = get_connection(args)
    cursor = conn.cursor()
    print(f"Connected as: {conn.username}@{conn.dsn}\n")

    if args.doctor:
        diag = doctor(cursor)
        print("--- Vault Doctor ---")
        print(f"  Connection:     {diag['connection']}")
        print(f"  Schema version: {diag['schema_version'] or 'NOT SET'}")
        print(f"  VECTOR support: {'YES' if diag['vector_support'] else 'NO'}")
        print()
        if diag["tables"]:
            print("  Tables:")
            for t, count in diag["tables"].items():
                print(f"    {t:30s} {count:>8,} rows")
        if diag["missing_tables"]:
            print(f"\n  Missing tables: {', '.join(diag['missing_tables'])}")
        if diag["missing_indexes"]:
            print(f"  Missing indexes: {', '.join(diag['missing_indexes'])}")
        conn.close()
        return

    # --- Preflight: check VECTOR support ---
    print("--- Preflight ---")
    try:
        cursor.execute("SELECT VECTOR('[1.0, 2.0, 3.0]', 3, FLOAT32) FROM dual")
        print("  [OK] VECTOR column support detected")
    except Exception:
        print("  [WARN] VECTOR columns not supported — tables with VECTOR will fail.")
        print("         Upgrade to Oracle 23ai or later for vector search.")

    # --- Init ---
    print("\n--- Creating tables ---")
    t_result = create_tables(cursor, dry_run=False)
    conn.commit()

    print("\n--- Applying ALTER statements (v4 to v11) ---")
    a_result = apply_alters(cursor, dry_run=False)
    conn.commit()

    print("\n--- Creating indexes ---")
    i_result = create_indexes(cursor, dry_run=False)
    conn.commit()

    print("\n--- Creating views ---")
    v_result = create_views(cursor, dry_run=False)
    conn.commit()

    print("\n--- Seeding doc types ---")
    s_result = seed_doc_types(cursor, dry_run=False)
    conn.commit()

    all_errors = t_result["errors"] + a_result["errors"] + i_result["errors"] + v_result["errors"] + s_result["errors"]

    # Only stamp schema version if no errors occurred
    if not all_errors:
        print("\n--- Setting schema version ---")
        update_schema_version(cursor, dry_run=False)
        conn.commit()
    else:
        print("\n--- Skipping schema version stamp (errors detected) ---")

    # --- Summary ---
    print("\n" + "=" * 50)
    print("SUMMARY")
    print(f"  Tables:  {len(t_result['created'])} created, {len(t_result['skipped'])} skipped, {len(t_result['errors'])} errors")
    print(f"  Alters:  {len(a_result['applied'])} applied, {len(a_result['skipped'])} skipped, {len(a_result['errors'])} errors")
    print(f"  Indexes: {len(i_result['created'])} created, {len(i_result['skipped'])} skipped, {len(i_result['errors'])} errors")
    print(f"  Views:   {len(v_result['created'])} created, {len(v_result['errors'])} errors")
    print(f"  Seeds:   {s_result['seeded']} doc types seeded, {s_result['skipped']} skipped")

    if all_errors:
        print(f"  Schema:  NOT STAMPED (errors)")
        print(f"\n  ERRORS ({len(all_errors)}):")
        for err in all_errors:
            print(f"    - {err}")
    else:
        print(f"  Schema:  v{SCHEMA_VERSION}")

    conn.close()

    if all_errors:
        print("\n[WARN] Schema initialized with errors. Run --doctor to check.")
        sys.exit(1)
    else:
        print("\n[OK] Vault schema initialized successfully.")


if __name__ == "__main__":
    main()
