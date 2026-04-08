"""
vault_mcp_server.py — MCP server wrapping vault_api for Agent SDK consumption.

⚠️  DRAFT — NOT WORKING
The claude_agent_sdk imports below (tool, create_sdk_mcp_server) use an API
that has NOT been verified. Do NOT rely on this module until confirmed.

Exposes Vault operations as MCP tools so any Claude agent (via Agent SDK)
can ingest, search, query, and manage the Oracle Vault.

Usage (standalone):
    python scripts/vault_mcp_server.py          # stdio MCP server

Usage (in-process with Agent SDK):
    from vault_mcp_server import create_vault_mcp
    server = create_vault_mcp()
    # Pass to ClaudeAgentOptions(mcp_servers={"vault": server})
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure vault_api is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from claude_agent_sdk import tool, create_sdk_mcp_server


def _vault():
    """Lazy-load Vault singleton."""
    from vault_api import Vault
    if not hasattr(_vault, "_instance"):
        _vault._instance = Vault()
    return _vault._instance


def _text(s: str) -> dict:
    return {"content": [{"type": "text", "text": s}]}


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool(
    "vault_ingest",
    "Ingest a document into the Oracle Vault. Returns the new document ID. Only content and doc_type are required.",
    {"content": str, "doc_type": str, "title": str, "occurred_at": str,
     "ownership": str, "privacy_level": str, "language": str, "fidelity": str,
     "original_path": str, "email_from": str},
)
async def vault_ingest(args: dict) -> dict:
    import asyncio
    content = args.get("content", "")
    doc_type = args.get("doc_type", "note")
    if not content:
        return _text(json.dumps({"error": "content is required"}))
    kwargs = {}
    for k in ("title", "occurred_at", "ownership", "privacy_level",
              "language", "fidelity", "original_path",
              "email_from", "email_importance", "email_direction"):
        v = args.get(k)
        if v:
            kwargs[k] = v
    try:
        doc_id = await asyncio.to_thread(_vault().ingest, content, doc_type, **kwargs)
        return _text(json.dumps({"doc_id": doc_id}, ensure_ascii=False))
    except Exception as e:
        return _text(json.dumps({"error": str(e)}))


@tool(
    "vault_search",
    "Search the Vault for documents matching a query. Returns up to 10 results.",
    {"query": str, "doc_type": str, "limit": int},
)
async def vault_search(args: dict) -> dict:
    import asyncio
    q = args.get("query", "")
    if not q:
        return _text(json.dumps({"error": "query is required"}))
    kwargs = {}
    if args.get("doc_type"):
        kwargs["doc_type"] = args["doc_type"]
    if args.get("limit"):
        kwargs["limit"] = args["limit"]
    try:
        results = await asyncio.to_thread(_vault().search, q, **kwargs)
        return _text(json.dumps(results, default=str, ensure_ascii=False))
    except Exception as e:
        return _text(json.dumps({"error": str(e)}))


@tool(
    "vault_about",
    "Get a comprehensive profile for a named entity (person, company, project).",
    {"entity_name": str},
)
async def vault_about(args: dict) -> dict:
    import asyncio
    name = args.get("entity_name", "")
    if not name:
        return _text(json.dumps({"error": "entity_name is required"}))
    try:
        profile = await asyncio.to_thread(_vault().about, name)
        if profile:
            return _text(json.dumps(profile, default=str, ensure_ascii=False))
        return _text(json.dumps({"error": f"No entity found: {name}"}))
    except Exception as e:
        return _text(json.dumps({"error": str(e)}))


@tool(
    "vault_timeline",
    "Get a chronological timeline of events for an entity or topic.",
    {"entity": str, "topic": str, "start": str, "end": str, "limit": int},
)
async def vault_timeline(args: dict) -> dict:
    import asyncio
    kwargs = {}
    for k in ("entity", "topic", "start", "end", "limit"):
        v = args.get(k)
        if v:
            kwargs[k] = v
    try:
        events = await asyncio.to_thread(_vault().timeline, **kwargs)
        return _text(json.dumps(events, default=str, ensure_ascii=False))
    except Exception as e:
        return _text(json.dumps({"error": str(e)}))


@tool(
    "vault_stats",
    "Get current Vault database statistics (table counts, schema version).",
    {},
)
async def vault_stats(args: dict) -> dict:
    import asyncio
    try:
        stats = await asyncio.to_thread(_vault().stats)
        return _text(json.dumps(stats, default=str, ensure_ascii=False))
    except Exception as e:
        return _text(json.dumps({"error": str(e)}))


@tool(
    "vault_add_entity",
    "Add a new entity (person, company, project, concept) to the Vault.",
    {"entity_type": str, "canonical_name": str, "aliases": str},
)
async def vault_add_entity(args: dict) -> dict:
    import asyncio
    entity_type = args.get("entity_type", "person")
    name = args.get("canonical_name", "")
    if not name:
        return _text(json.dumps({"error": "canonical_name is required"}))
    aliases_str = args.get("aliases", "")
    aliases = [a.strip() for a in aliases_str.split(",") if a.strip()] if aliases_str else []
    try:
        entity_id = await asyncio.to_thread(_vault().add_entity, entity_type, name, aliases)
        return _text(json.dumps({"entity_id": entity_id}, ensure_ascii=False))
    except Exception as e:
        return _text(json.dumps({"error": str(e)}))


@tool(
    "vault_merge_entities",
    "Merge two entities (move aliases and relations from source to target).",
    {"source_id": int, "target_id": int, "reason": str},
)
async def vault_merge_entities(args: dict) -> dict:
    import asyncio
    source_id = args.get("source_id")
    target_id = args.get("target_id")
    if not source_id or not target_id:
        return _text(json.dumps({"error": "source_id and target_id are required"}))
    reason = args.get("reason", "manual merge")
    try:
        result = await asyncio.to_thread(
            _vault().merge_entities, int(source_id), int(target_id), reason)
        return _text(json.dumps(result, default=str, ensure_ascii=False))
    except Exception as e:
        return _text(json.dumps({"error": str(e)}))


# ---------------------------------------------------------------------------
# MCP server factory
# ---------------------------------------------------------------------------

ALL_TOOLS = [
    vault_ingest, vault_search, vault_about, vault_timeline,
    vault_stats, vault_add_entity, vault_merge_entities,
]


def create_vault_mcp():
    """Create an in-process MCP server for the Vault. Use with Agent SDK."""
    return create_sdk_mcp_server("vault", tools=ALL_TOOLS)


if __name__ == "__main__":
    # Standalone stdio mode (for external MCP clients)
    print("vault_mcp_server: Use create_vault_mcp() for in-process Agent SDK usage.")
    print(f"Available tools: {[t.name for t in ALL_TOOLS]}")
