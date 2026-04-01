"""
Configuration management for MCP Memory Server.
Reads from ~/.clawd-lobster/config.json, env vars, or install-time defaults.
"""
import copy
import json
import os
import stat
from pathlib import Path

CONFIG_DIR = Path.home() / ".clawd-lobster"
CONFIG_FILE = CONFIG_DIR / "config.json"

_DEFAULT = {
    "wrapper_dir": "",
    "data_dir": "",
    "workspace_root": str(Path.home() / "Documents" / "Workspace"),
    "knowledge_dir": "",
    "oracle": {
        "enabled": False,
        "wallet_dir": "",
        "wallet_password": "",
        "dsn": "",
        "user": "CLAUDE_MEMORY",
        "password": "",
    },
    "embedding": {
        "provider": "none",
        "model": "text-embedding-3-small",
        "api_key": "",
    },
    "l4_provider": "github",
}


def load_config() -> dict:
    """Load config from file, merge with defaults."""
    config = copy.deepcopy(_DEFAULT)

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            user_config = json.load(f)
        _deep_merge(config, user_config)

    # Derive paths if not set
    if not config["wrapper_dir"]:
        config["wrapper_dir"] = str(Path.home() / "Documents" / "clawd-lobster")
    if not config["data_dir"]:
        config["data_dir"] = config["wrapper_dir"]
    if not config["knowledge_dir"]:
        config["knowledge_dir"] = os.path.join(config["data_dir"], "knowledge")

    # Env overrides
    if os.environ.get("CLAWD_WRAPPER_DIR"):
        config["wrapper_dir"] = os.environ["CLAWD_WRAPPER_DIR"]
    if os.environ.get("CLAWD_DATA_DIR"):
        config["data_dir"] = os.environ["CLAWD_DATA_DIR"]
    if os.environ.get("CLAWD_WORKSPACE_ROOT"):
        config["workspace_root"] = os.environ["CLAWD_WORKSPACE_ROOT"]
    if os.environ.get("CLAWD_ORACLE_PASSWORD"):
        config["oracle"]["password"] = os.environ["CLAWD_ORACLE_PASSWORD"]
    if os.environ.get("OPENAI_API_KEY"):
        config["embedding"]["api_key"] = os.environ["OPENAI_API_KEY"]

    return config


def save_config(config: dict) -> None:
    """Save config to file with restrictive permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    # Restrict to owner-only read/write (0o600) — config may contain secrets
    try:
        os.chmod(CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass  # Windows may not support Unix permissions


def get_workspace_map_path() -> str:
    config = load_config()
    return os.path.join(config["data_dir"], "workspaces.json")


def _deep_merge(base: dict, override: dict):
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
