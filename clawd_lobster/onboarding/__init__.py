"""clawd_lobster.onboarding — Agent-guided onboarding backend.

Re-exports legacy functions from the old onboarding.py module
so server.py can still call onboarding.is_first_time() etc.
"""
from pathlib import Path as _Path
import json as _json

# Legacy compatibility — these were in the old clawd_lobster/onboarding.py
_HOME = _Path.home()
CONFIG_DIR = _HOME / ".clawd-lobster"
CONFIG_FILE = CONFIG_DIR / "config.json"
ONBOARDING_DIR = CONFIG_DIR / "onboarding"


def is_first_time() -> bool:
    """Check if this is the first time setup."""
    return not CONFIG_FILE.exists()


def check_prerequisites() -> dict:
    """Check system prerequisites. Delegates to old module if available."""
    try:
        # Try importing the old module directly
        import importlib.util
        old_path = _Path(__file__).resolve().parent.parent / "onboarding.py"
        if old_path.exists():
            spec = importlib.util.spec_from_file_location("_old_onboarding", old_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.check_prerequisites()
    except Exception:
        pass

    # Fallback minimal check
    import subprocess, sys
    checks = []
    for name, cmd in [("python", [sys.executable, "--version"]),
                      ("claude", ["claude", "--version"]),
                      ("git", ["git", "--version"])]:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            checks.append({"name": name, "ok": r.returncode == 0,
                           "version": r.stdout.strip()[:40], "optional": False})
        except Exception:
            checks.append({"name": name, "ok": False, "version": "", "optional": False})

    return {"checks": checks, "all_required_ok": all(c["ok"] for c in checks),
            "default_root": str(_HOME / "Documents" / "Workspace")}


def save_config(persona: str, workspace_root: str, *, lang: str = "en") -> None:
    """Save config to ~/.clawd-lobster/config.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = {
        "persona": persona,
        "workspace_root": workspace_root,
        "lang": lang,
        "setup_complete": True,
    }
    tmp = CONFIG_FILE.with_suffix(".tmp")
    tmp.write_text(_json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import os
    os.replace(str(tmp), str(CONFIG_FILE))


def create_onboarding_session(lang: str = "en") -> dict:
    """Create an onboarding session (delegates to state_store)."""
    from .state_store import create_session
    state, token = create_session(lang)
    return state


def get_onboarding_state(session_id: str):
    """Get onboarding state."""
    from .state_store import get_state
    return get_state(session_id)


def get_latest_session():
    """Get latest session."""
    from .state_store import get_latest_session as _get
    return _get()


def update_onboarding_state(session_id: str, step: str, value):
    """Legacy update — delegates to intent system."""
    return None  # Legacy, not used anymore


def write_handoff_file(session_id: str, lang: str = "en"):
    """Legacy handoff — delegates to handoff module."""
    from .handoff import generate_handoff
    result = generate_handoff(session_id)
    if result.get("ok"):
        return _Path(result["claude_md_path"]).parent
    return ONBOARDING_DIR / session_id
