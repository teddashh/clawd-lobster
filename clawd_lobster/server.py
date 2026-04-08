"""
clawd_lobster.server — HTTP server for the web UI.

Serves the onboarding wizard, workspace dashboard, and spec-squad interface
on localhost. Uses stdlib http.server -- no external dependencies.

Binds to 127.0.0.1 only (security). Suppresses request logs for clean output.
"""

import json
import sys
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from . import pages
from . import onboarding

# ── Helpers ────────────────────────────────────────────────────────────────

REPO_DIR = Path(__file__).resolve().parent.parent
SQUAD_STATE_FILE = ".spec-squad.json"


def _read_json(path: Path, default=None):
    """Read a JSON file, returning default on any error."""
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _write_json(path: Path, data: dict) -> None:
    """Write JSON file with atomic rename."""
    import platform
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if platform.system() == "Windows" and path.exists():
        path.unlink()
    tmp.rename(path)


def _get_workspaces_json_path() -> Path:
    """Resolve the workspaces.json path."""
    config = _read_json(onboarding.CONFIG_FILE)
    wrapper_dir = config.get("wrapper_dir", "")
    if wrapper_dir:
        candidate = Path(wrapper_dir) / "workspaces.json"
        if candidate.exists():
            return candidate
    return REPO_DIR / "workspaces.json"


def _get_workspaces() -> list[dict]:
    """Read workspace list, enriched with squad state."""
    registry = _read_json(_get_workspaces_json_path(), {"workspaces": []})
    workspaces = registry.get("workspaces", [])
    for ws in workspaces:
        ws_path = Path(ws.get("path", ""))
        state_file = ws_path / SQUAD_STATE_FILE
        if state_file.exists():
            state = _read_json(state_file)
            ws["squad_phase"] = state.get("phase", "none")
        else:
            ws["squad_phase"] = "none"
    return workspaces


def _resolve_workspace_root() -> str:
    """Get workspace root from config or default."""
    config = _read_json(onboarding.CONFIG_FILE)
    root = config.get("workspace_root", "")
    if root:
        return root
    return str(Path.home() / "Documents" / "Workspace")


# ── HTTP Handler ───────────────────────────────────────────────────────────

class _Handler(BaseHTTPRequestHandler):
    """Routes GET and POST requests for the clawd-lobster web UI."""

    def log_message(self, format, *args):
        """Suppress default request logging for clean terminal output."""
        pass

    # ── GET routes ─────────────────────────────────────────────────────────

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        routes = {
            "/": self._route_home,
            "/onboarding": self._route_onboarding,
            "/workspaces": self._route_workspaces,
            "/squad": self._route_squad,
            "/api/status": self._api_status,
            "/api/workspaces": self._api_workspaces,
            "/api/squad/state": self._api_squad_state,
            "/api/onboarding/state": self._api_onboarding_state,
            "/api/onboarding/instructions": self._api_onboarding_instructions,
        }

        handler = routes.get(path)
        if handler:
            handler(query)
        elif path.startswith("/assets/"):
            self._serve_asset(path)
        else:
            self.send_error(404)

    # ── POST routes ────────────────────────────────────────────────────────

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        routes = {
            "/api/onboarding/check": self._api_onboarding_check,
            "/api/onboarding/complete": self._api_onboarding_complete,
            "/api/onboarding/handoff": self._api_onboarding_handoff,
            "/api/onboarding/update": self._api_onboarding_update,
            "/api/workspaces/create": self._api_workspaces_create,
            "/api/squad/chat": self._api_squad_chat,
            "/api/squad/start": self._api_squad_start,
        }

        handler = routes.get(path)
        if handler:
            handler()
        else:
            self.send_error(404)

    # ── Response helpers ───────────────────────────────────────────────────

    def _send_html(self, html: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _send_json(self, data: dict, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _read_body(self) -> dict:
        """Read and parse JSON request body."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    def _serve_asset(self, path: str) -> None:
        """Serve static files from clawd_lobster/assets/."""
        MIME = {".png": "image/png", ".webp": "image/webp",
                ".jpg": "image/jpeg", ".svg": "image/svg+xml",
                ".ico": "image/x-icon", ".css": "text/css", ".js": "text/javascript"}
        name = path.split("/assets/", 1)[-1]
        # Safety: no path traversal
        if ".." in name or "/" in name or "\\" in name:
            self.send_error(403)
            return
        asset_dir = Path(__file__).resolve().parent / "assets"
        fp = asset_dir / name
        if not fp.exists() or not fp.is_file():
            self.send_error(404)
            return
        ct = MIME.get(fp.suffix.lower(), "application/octet-stream")
        data = fp.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "public, max-age=86400")
        self.end_headers()
        self.wfile.write(data)

    def _send_redirect(self, location: str) -> None:
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    # ── Page routes ────────────────────────────────────────────────────────

    def _route_home(self, query: dict) -> None:
        # Redirect based on first-time status
        if onboarding.is_first_time():
            self._send_redirect("/onboarding")
        else:
            self._send_redirect("/workspaces")

    def _route_onboarding(self, query: dict) -> None:
        self._send_html(pages.ONBOARDING_PAGE)

    def _route_workspaces(self, query: dict) -> None:
        self._send_html(pages.WORKSPACES_PAGE)

    def _route_squad(self, query: dict) -> None:
        self._send_html(pages.SQUAD_PAGE)

    # ── API: status ────────────────────────────────────────────────────────

    def _api_status(self, query: dict) -> None:
        self._send_json({
            "ok": True,
            "first_time": onboarding.is_first_time(),
            "version": _get_version(),
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        })

    # ── API: onboarding ────────────────────────────────────────────────────

    def _api_onboarding_check(self) -> None:
        result = onboarding.check_prerequisites()
        self._send_json(result)

    def _api_onboarding_complete(self) -> None:
        body = self._read_body()
        persona = body.get("persona", "noob")
        lang = body.get("lang", "en")
        ws_name = body.get("workspace_name", "")
        ws_root = body.get("workspace_root", "")

        if not ws_root:
            ws_root = _resolve_workspace_root()

        # Validate persona
        if persona not in ("noob", "expert", "tech"):
            persona = "noob"

        # Validate lang
        if lang not in ("en", "zh-TW", "zh-CN", "ja", "ko"):
            lang = "en"

        try:
            # Save config
            onboarding.save_config(persona, ws_root, lang=lang)

            # Create workspace if name provided
            if ws_name:
                self._create_workspace_internal(ws_name, "personal", "")

            self._send_json({"ok": True})
        except Exception as e:
            self._send_json({"ok": False, "error": str(e)}, status=400)

    def _api_onboarding_handoff(self) -> None:
        """Create a handoff session. Returns session_id + handoff dir path."""
        body = self._read_body()
        lang = body.get("lang", "en")
        if lang not in ("en", "zh-TW", "zh-CN", "ja", "ko"):
            lang = "en"

        try:
            state = onboarding.create_onboarding_session(lang)
            session_id = state["session_id"]
            session_dir = onboarding.write_handoff_file(session_id, lang)
            self._send_json({
                "ok": True,
                "session_id": session_id,
                "session_dir": str(session_dir),
                "state": state,
            })
        except Exception as e:
            self._send_json({"ok": False, "error": str(e)}, status=500)

    def _api_onboarding_state(self, query: dict) -> None:
        """Return current onboarding session state."""
        session_id = ""
        if "session_id" in query:
            session_id = query["session_id"][0]

        if not session_id:
            # Try to find the latest session
            state = onboarding.get_latest_session()
            if state:
                self._send_json({"ok": True, "state": state})
            else:
                self._send_json({"ok": False, "error": "No active session"}, status=404)
            return

        state = onboarding.get_onboarding_state(session_id)
        if state is None:
            self._send_json({"ok": False, "error": "Session not found"}, status=404)
        else:
            self._send_json({"ok": True, "state": state})

    def _api_onboarding_instructions(self, query: dict) -> None:
        """Return CLAUDE.md content for a session."""
        session_id = ""
        if "session_id" in query:
            session_id = query["session_id"][0]

        if not session_id:
            self._send_json({"ok": False, "error": "session_id required"}, status=400)
            return

        claude_md = onboarding.ONBOARDING_DIR / session_id / "CLAUDE.md"
        if not claude_md.exists():
            self._send_json({"ok": False, "error": "Instructions not found"}, status=404)
            return

        try:
            content = claude_md.read_text(encoding="utf-8")
            self._send_json({"ok": True, "instructions": content})
        except OSError as e:
            self._send_json({"ok": False, "error": str(e)}, status=500)

    def _api_onboarding_update(self) -> None:
        """CLI reports step completion. Requires session_id in body."""
        body = self._read_body()
        session_id = body.get("session_id", "")
        step = body.get("step", "")
        value = body.get("value")

        if not session_id or not step:
            self._send_json(
                {"ok": False, "error": "session_id and step required"}, status=400,
            )
            return

        state = onboarding.update_onboarding_state(session_id, step, value)
        if state is None:
            self._send_json(
                {"ok": False, "error": "Invalid session or step"}, status=400,
            )
            return

        # If complete, also save the config
        if step == "complete" or state.get("phase") == "complete":
            persona = state.get("persona", "noob")
            ws_root = state.get("workspace_root", "")
            lang = state.get("lang", "en")
            if not ws_root:
                ws_root = _resolve_workspace_root()
            try:
                onboarding.save_config(persona, ws_root, lang=lang)
            except Exception:
                pass

        self._send_json({"ok": True, "state": state})

    # ── API: workspaces ────────────────────────────────────────────────────

    def _api_workspaces(self, query: dict) -> None:
        self._send_json({"workspaces": _get_workspaces()})

    def _api_workspaces_create(self) -> None:
        body = self._read_body()
        name = body.get("name", "").strip()
        domain = body.get("domain", "personal")
        description = body.get("description", "")

        if not name:
            self._send_json({"ok": False, "error": "Name is required"}, status=400)
            return

        try:
            result = self._create_workspace_internal(name, domain, description)
            self._send_json({"ok": True, "workspace": result})
        except Exception as e:
            self._send_json({"ok": False, "error": str(e)}, status=400)

    def _create_workspace_internal(self, name: str, domain: str, description: str) -> dict:
        """Create a workspace using workspace-create.py logic."""
        try:
            scripts_dir = REPO_DIR / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))
            # workspace-create.py has a hyphen, use importlib
            from importlib import import_module
            wc = import_module("workspace-create")
            summary = wc.create_workspace(
                name=name, domain=domain, description=description,
            )
            return summary
        except Exception:
            # Fallback: create minimal workspace
            ws_root = Path(_resolve_workspace_root())
            ws_path = ws_root / name
            ws_path.mkdir(parents=True, exist_ok=True)
            (ws_path / "CLAUDE.md").write_text(
                f"# {name}\n\nNew workspace.\n", encoding="utf-8",
            )

            # Register in workspaces.json
            registry_path = _get_workspaces_json_path()
            registry = _read_json(registry_path, {"workspaces": []})
            from datetime import date
            entry = {
                "id": name,
                "path": str(ws_path),
                "repo": "",
                "domain": domain,
                "deploy": "all",
                "created": date.today().isoformat(),
            }
            registry.setdefault("workspaces", []).append(entry)
            _write_json(registry_path, registry)
            return entry

    # ── API: squad ─────────────────────────────────────────────────────────

    def _api_squad_chat(self) -> None:
        """Handle a discovery chat turn.

        Expects JSON body: {"message": "...", "workspace": "..."}
        Returns: {"response": "...", "discovery_complete": false}

        Note: Full Agent SDK integration is in squad.py (Phase 6).
        This endpoint provides the HTTP interface for it.
        """
        body = self._read_body()
        message = body.get("message", "")
        workspace = body.get("workspace", "")

        if not message:
            self._send_json({"response": "", "discovery_complete": False})
            return

        # Try to use the squad module if it has the chat function
        try:
            from . import squad
            if hasattr(squad, "discovery_turn_sync"):
                response = squad.discovery_turn_sync(message, workspace)
                # Check for discovery complete
                discovery_complete = False
                if hasattr(squad, "extract_discovery_data") and "DISCOVERY_COMPLETE" in response:
                    data = squad.extract_discovery_data(response)
                    if data:
                        discovery_complete = True
                        response = response.split("DISCOVERY_COMPLETE")[0].strip() or "Ready! Launching the squad..."
                result = {"response": response, "discovery_complete": discovery_complete}
                self._send_json(result)
                return
        except Exception:
            pass

        # Stub response when squad module is not yet implemented
        self._send_json({
            "response": (
                "The Spec Squad chat is being set up. "
                "Please use the terminal mode for now:\n\n"
                "  clawd-lobster squad start"
            ),
            "discovery_complete": False,
        })

    def _api_squad_start(self) -> None:
        """Launch the spec squad agents.

        Expects JSON body: {"workspace": "...", "project_desc": "..."}
        Returns: {"ok": true, "message": "Squad started"}
        """
        body = self._read_body()
        workspace = body.get("workspace", "")
        project_desc = body.get("project_desc", "")

        if not workspace:
            self._send_json(
                {"ok": False, "error": "workspace is required"}, status=400,
            )
            return

        # Try to use the squad module
        try:
            from . import squad
            if hasattr(squad, "run_squad_web"):
                from pathlib import Path as _P
                squad.run_squad_web(_P(workspace), project_desc)
                self._send_json({"ok": True, "message": "Squad started"})
                return
        except Exception:
            pass

        self._send_json({
            "ok": False,
            "error": "Squad module not yet available. Use terminal mode.",
        })

    def _api_squad_state(self, query: dict) -> None:
        """Return current squad state for a workspace."""
        workspace = ""
        if "workspace" in query:
            workspace = query["workspace"][0]

        data = {
            "phase": "discovery",
            "squad_running": False,
            "squad_state": {},
        }

        if workspace:
            ws_path = Path(workspace)
            state_file = ws_path / SQUAD_STATE_FILE
            if state_file.exists():
                state = _read_json(state_file)
                data["squad_state"] = state
                data["phase"] = state.get("phase", "discovery")

        self._send_json(data)


# ── Version helper ─────────────────────────────────────────────────────────

def _get_version() -> str:
    """Get clawd-lobster version."""
    try:
        from . import __version__
        return __version__
    except (ImportError, AttributeError):
        return "0.0.0"


# ── Server entry point ────────────────────────────────────────────────────

def start_server(port: int = 3333, open_browser: bool = True) -> None:
    """Start the clawd-lobster web server.

    Args:
        port: TCP port to bind (default 3333).
        open_browser: Open the default browser on launch.
    """
    server_address = ("127.0.0.1", port)

    try:
        httpd = HTTPServer(server_address, _Handler)
    except OSError as e:
        if "Address already in use" in str(e) or "Only one usage" in str(e):
            print(f"Error: port {port} is already in use.")
            print(f"Try: clawd-lobster serve --port {port + 1}")
            sys.exit(1)
        raise

    url = f"http://127.0.0.1:{port}"
    print(f"clawd-lobster server running at {url}")
    print("Press Ctrl+C to stop.\n")

    if open_browser:
        # Open browser after a short delay to let the server start
        def _open():
            import time
            time.sleep(0.3)
            webbrowser.open(url)

        threading.Thread(target=_open, daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()
