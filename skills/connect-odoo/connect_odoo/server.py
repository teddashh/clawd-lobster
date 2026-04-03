"""
MCP server for Odoo ERP integration via XML-RPC.

Exposes tools: odoo_search, odoo_read, odoo_create, odoo_write,
odoo_execute, odoo_poll_tasks.

All connection details come from environment variables:
  ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD
"""

from __future__ import annotations

import json
import os
import sys
import xmlrpc.client
from typing import Any

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Odoo XML-RPC helpers
# ---------------------------------------------------------------------------

_uid_cache: int | None = None


def _env(key: str) -> str:
    """Return an env var or raise a clear error."""
    val = os.environ.get(key)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return val


def _common_proxy() -> xmlrpc.client.ServerProxy:
    return xmlrpc.client.ServerProxy(f"{_env('ODOO_URL')}/xmlrpc/2/common")


def _object_proxy() -> xmlrpc.client.ServerProxy:
    return xmlrpc.client.ServerProxy(f"{_env('ODOO_URL')}/xmlrpc/2/object")


def _authenticate() -> int:
    """Authenticate and cache the uid."""
    global _uid_cache
    if _uid_cache is not None:
        return _uid_cache
    uid = _common_proxy().authenticate(
        _env("ODOO_DB"), _env("ODOO_USER"), _env("ODOO_PASSWORD"), {}
    )
    if not uid:
        raise RuntimeError("Odoo authentication failed — check credentials")
    _uid_cache = uid
    return uid


def _execute_kw(model: str, method: str, args: list, kwargs: dict | None = None) -> Any:
    """Call execute_kw on the Odoo object endpoint."""
    uid = _authenticate()
    return _object_proxy().execute_kw(
        _env("ODOO_DB"), uid, _env("ODOO_PASSWORD"),
        model, method, args, kwargs or {},
    )


# ---------------------------------------------------------------------------
# MCP server & tools
# ---------------------------------------------------------------------------

mcp = FastMCP("odoo")


@mcp.tool()
def odoo_search(
    model: str,
    domain: list[list] | None = None,
    fields: list[str] | None = None,
    limit: int = 80,
) -> str:
    """Search Odoo records.

    Args:
        model: Odoo model name, e.g. 'res.partner', 'crm.lead'.
        domain: Odoo domain filter, e.g. [['is_company','=',True]].
        fields: List of field names to return. None = all fields.
        limit: Max records to return (default 80).

    Returns:
        JSON array of matching records.
    """
    kwargs: dict[str, Any] = {"limit": limit}
    if fields:
        kwargs["fields"] = fields
    records = _execute_kw(model, "search_read", [domain or []], kwargs)
    return json.dumps(records, default=str, ensure_ascii=False)


@mcp.tool()
def odoo_read(
    model: str,
    ids: list[int],
    fields: list[str] | None = None,
) -> str:
    """Read specific Odoo records by ID.

    Args:
        model: Odoo model name.
        ids: List of record IDs to read.
        fields: Fields to return. None = all.

    Returns:
        JSON array of records.
    """
    kwargs: dict[str, Any] = {}
    if fields:
        kwargs["fields"] = fields
    records = _execute_kw(model, "read", [ids], kwargs)
    return json.dumps(records, default=str, ensure_ascii=False)


@mcp.tool()
def odoo_create(model: str, values: dict) -> str:
    """Create a new Odoo record.

    Args:
        model: Odoo model name.
        values: Field values for the new record.

    Returns:
        JSON with the new record ID.
    """
    new_id = _execute_kw(model, "create", [values])
    return json.dumps({"id": new_id})


@mcp.tool()
def odoo_write(model: str, ids: list[int], values: dict) -> str:
    """Update existing Odoo records.

    Args:
        model: Odoo model name.
        ids: Record IDs to update.
        values: Field values to write.

    Returns:
        JSON with success status.
    """
    result = _execute_kw(model, "write", [ids, values])
    return json.dumps({"success": bool(result)})


@mcp.tool()
def odoo_execute(model: str, method: str, args: list | None = None) -> str:
    """Execute an arbitrary Odoo method.

    Args:
        model: Odoo model name.
        method: Method name to call.
        args: Positional arguments for the method.

    Returns:
        JSON-encoded result.
    """
    result = _execute_kw(model, method, args or [])
    return json.dumps(result, default=str, ensure_ascii=False)


@mcp.tool()
def odoo_poll_tasks() -> str:
    """Poll Odoo for pending tasks assigned to this agent.

    Searches arp.task model for records with state='pending'.
    Returns JSON array of tasks, or an empty array if the model
    does not exist.
    """
    try:
        tasks = _execute_kw(
            "arp.task",
            "search_read",
            [[["state", "=", "pending"]]],
            {"fields": ["id", "name", "state", "description", "create_date"], "limit": 50},
        )
    except xmlrpc.client.Fault as exc:
        # Model may not exist on this Odoo instance
        if "arp.task" in str(exc) or "does not exist" in str(exc).lower():
            tasks = []
        else:
            raise
    return json.dumps(tasks, default=str, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def _health_check() -> None:
    """Test the Odoo connection and print version info, then exit."""
    try:
        version = _common_proxy().version()
        uid = _authenticate()
        print(json.dumps({
            "status": "ok",
            "server_version": version.get("server_version", "unknown"),
            "uid": uid,
        }))
        sys.exit(0)
    except Exception as exc:
        print(json.dumps({"status": "error", "detail": str(exc)}))
        sys.exit(1)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    if "--health" in sys.argv:
        _health_check()
    mcp.run()


if __name__ == "__main__":
    main()
