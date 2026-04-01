"""
Database layer — SQLite (local) + Oracle (cloud, optional).
"""
import json
import os
import re
import sqlite3
import uuid
from pathlib import Path

from .config import load_config, get_workspace_map_path


# ============================================================
# Workspace detection
# ============================================================

def detect_workspace() -> str:
    """Detect current workspace from cwd or env."""
    ws = os.environ.get("MEMORY_WORKSPACE")
    if ws:
        return ws

    cwd = Path(os.environ.get("INIT_CWD", os.getcwd()))
    config = load_config()

    # Check if inside wrapper/data dir
    wrapper_dir = config.get("wrapper_dir", "")
    if wrapper_dir and wrapper_dir in str(cwd):
        return "clawd-lobster"

    # Check workspace map
    map_path = get_workspace_map_path()
    try:
        with open(map_path) as f:
            registry = json.load(f)
        ws_root = Path(config["workspace_root"])
        workspaces = registry.get("workspaces", [])
        if isinstance(workspaces, list):
            for ws_entry in workspaces:
                ws_id = ws_entry.get("id", "")
                ws_path = ws_root / ws_entry.get("path", ws_id)
                try:
                    if cwd == ws_path or ws_path in cwd.parents or cwd in ws_path.parents:
                        return ws_id
                except (ValueError, OSError):
                    continue
        elif isinstance(workspaces, dict):
            # Legacy format: {"id": "display_path"}
            for ws_id, display_path in workspaces.items():
                ws_path = ws_root / display_path
                try:
                    if cwd == ws_path or ws_path in cwd.parents or cwd in ws_path.parents:
                        return ws_id
                except (ValueError, OSError):
                    continue
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Fallback: use directory name (sanitized)
    name = cwd.name.lower().replace(" ", "-") if cwd.name else "unknown"
    return re.sub(r'[^a-zA-Z0-9_-]', '-', name)


# ============================================================
# SQLite
# ============================================================

def get_sqlite(workspace_id: str = None) -> sqlite3.Connection:
    """Get SQLite connection for a workspace."""
    ws_id = workspace_id or detect_workspace()
    config = load_config()

    if ws_id == "clawd-lobster":
        db_path = Path(config["wrapper_dir"]) / ".claude-memory" / "memory.db"
    else:
        ws_root = Path(config["workspace_root"])
        map_path = get_workspace_map_path()
        try:
            with open(map_path) as f:
                registry = json.load(f)
            workspaces = registry.get("workspaces", [])
            display_path = None
            if isinstance(workspaces, list):
                for ws_entry in workspaces:
                    if ws_entry.get("id") == ws_id:
                        display_path = ws_entry.get("path", ws_id)
                        break
            elif isinstance(workspaces, dict):
                display_path = workspaces.get(ws_id)
            if display_path:
                db_path = ws_root / display_path / ".claude-memory" / "memory.db"
            else:
                # Security: reject workspace IDs with path traversal characters
                if not re.match(r'^[a-zA-Z0-9_-]+$', ws_id):
                    raise ValueError(f"Invalid workspace ID: contains illegal characters")
                db_path = ws_root / ws_id / ".claude-memory" / "memory.db"
        except (FileNotFoundError, json.JSONDecodeError):
            if not re.match(r'^[a-zA-Z0-9_-]+$', ws_id):
                raise ValueError(f"Invalid workspace ID: contains illegal characters")
            db_path = ws_root / ws_id / ".claude-memory" / "memory.db"

    if not db_path.exists():
        raise FileNotFoundError(f"Memory database not found for workspace '{ws_id}'. Run init_db.py first.")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def new_id() -> str:
    return str(uuid.uuid4())[:8]


def tags_to_json(tags: str) -> str:
    return json.dumps([t.strip() for t in tags.split(",") if t.strip()])


# ============================================================
# Oracle (optional L4)
# ============================================================

_oracle_conn = None


def get_oracle():
    """Get Oracle connection (cached). Returns None if not configured."""
    global _oracle_conn
    config = load_config()

    if not config["oracle"]["enabled"]:
        return None

    if _oracle_conn is not None:
        try:
            _oracle_conn.ping()
            return _oracle_conn
        except Exception:
            _oracle_conn = None

    try:
        import oracledb
        _oracle_conn = oracledb.connect(
            user=config["oracle"]["user"],
            password=config["oracle"]["password"],
            dsn=config["oracle"]["dsn"],
            config_dir=config["oracle"]["wallet_dir"],
            wallet_location=config["oracle"]["wallet_dir"],
            wallet_password=config["oracle"]["wallet_password"],
            tcp_connect_timeout=15,
        )
        return _oracle_conn
    except Exception:
        return None
