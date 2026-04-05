#!/usr/bin/env python3
"""
spec-squad-viewer.py — Live web viewer for Spec Squad progress.

Opens a browser showing the 4 agents and their real-time status.
Polls .spec-squad.json every 2 seconds for updates.

Usage:
    python spec-squad-viewer.py <workspace-path>
    python spec-squad-viewer.py <workspace-path> --port 3001

No external dependencies — stdlib only.
"""

import argparse
import http.server
import json
import os
import sys
import threading
import webbrowser
from pathlib import Path

DEFAULT_PORT = 3333

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Spec Squad</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: #0d1117;
    color: #c9d1d9;
    min-height: 100vh;
  }

  header {
    background: #161b22;
    border-bottom: 1px solid #30363d;
    padding: 20px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  header h1 { font-size: 24px; font-weight: 600; }
  header h1 span { color: #58a6ff; }
  .header-meta { color: #8b949e; font-size: 14px; }
  .phase-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .phase-spec { background: #1f3a5f; color: #58a6ff; }
  .phase-review { background: #3d1f5f; color: #bc8cff; }
  .phase-code { background: #1f5f2d; color: #56d364; }
  .phase-test { background: #5f4b1f; color: #e3b341; }
  .phase-done { background: #1f5f2d; color: #56d364; }

  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    padding: 24px 32px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .agent-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px;
    transition: border-color 0.3s;
  }
  .agent-card.active {
    border-color: #58a6ff;
    box-shadow: 0 0 20px rgba(88, 166, 255, 0.1);
  }
  .agent-card.done {
    border-color: #56d364;
  }

  .agent-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }
  .agent-icon {
    width: 48px;
    height: 48px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    font-weight: 700;
    color: #fff;
  }
  .icon-architect { background: #1f6feb; }
  .icon-reviewer { background: #8957e5; }
  .icon-coder { background: #238636; }
  .icon-tester { background: #9e6a03; }

  .agent-name { font-size: 18px; font-weight: 600; }
  .agent-role { color: #8b949e; font-size: 13px; }

  .agent-status {
    padding: 8px 12px;
    background: #0d1117;
    border-radius: 8px;
    font-size: 13px;
    color: #8b949e;
    margin-bottom: 12px;
    min-height: 40px;
  }
  .agent-status.working { color: #58a6ff; }
  .agent-status.success { color: #56d364; }
  .agent-status.warning { color: #e3b341; }

  .turn-list {
    list-style: none;
    font-size: 13px;
    max-height: 200px;
    overflow-y: auto;
  }
  .turn-list li {
    padding: 4px 0;
    border-bottom: 1px solid #21262d;
    display: flex;
    justify-content: space-between;
  }
  .turn-list li:last-child { border: none; }
  .turn-signal { font-weight: 500; }
  .signal-approved { color: #56d364; }
  .signal-revise { color: #e3b341; }
  .signal-complete { color: #58a6ff; }

  .timeline {
    padding: 24px 32px;
    max-width: 1200px;
    margin: 0 auto;
  }
  .timeline h2 {
    font-size: 16px;
    color: #8b949e;
    margin-bottom: 12px;
  }
  .timeline-bar {
    display: flex;
    gap: 4px;
    margin-bottom: 8px;
  }
  .timeline-step {
    flex: 1;
    height: 8px;
    border-radius: 4px;
    background: #21262d;
    transition: background 0.3s;
  }
  .timeline-step.complete { background: #56d364; }
  .timeline-step.active { background: #58a6ff; animation: pulse 1.5s infinite; }
  .timeline-labels {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #8b949e;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  .stats {
    display: flex;
    gap: 24px;
    padding: 16px 32px;
    max-width: 1200px;
    margin: 0 auto;
    color: #8b949e;
    font-size: 14px;
  }
  .stat-value { color: #c9d1d9; font-weight: 600; }

  .empty-state {
    text-align: center;
    padding: 80px 32px;
    color: #8b949e;
  }
  .empty-state h2 { font-size: 20px; margin-bottom: 8px; color: #c9d1d9; }
</style>
</head>
<body>

<header>
  <div>
    <h1><span>Spec Squad</span> Viewer</h1>
    <div class="header-meta" id="workspace-path"></div>
  </div>
  <div>
    <span class="phase-badge" id="phase-badge">WAITING</span>
  </div>
</header>

<div class="timeline">
  <div class="timeline-bar">
    <div class="timeline-step" id="step-spec"></div>
    <div class="timeline-step" id="step-review"></div>
    <div class="timeline-step" id="step-code"></div>
    <div class="timeline-step" id="step-test"></div>
  </div>
  <div class="timeline-labels">
    <span>Spec</span>
    <span>Review</span>
    <span>Code</span>
    <span>Test</span>
  </div>
</div>

<div class="stats">
  <div>Review rounds: <span class="stat-value" id="review-rounds">0</span></div>
  <div>Turns: <span class="stat-value" id="turn-count">0</span></div>
  <div>Approved: <span class="stat-value" id="approved">-</span></div>
  <div>Elapsed: <span class="stat-value" id="elapsed">-</span></div>
</div>

<div class="grid">
  <div class="agent-card" id="card-architect">
    <div class="agent-header">
      <div class="agent-icon icon-architect">A</div>
      <div>
        <div class="agent-name">Architect</div>
        <div class="agent-role">Writes the spec</div>
      </div>
    </div>
    <div class="agent-status" id="status-architect">Idle</div>
    <ul class="turn-list" id="turns-architect"></ul>
  </div>

  <div class="agent-card" id="card-reviewer">
    <div class="agent-header">
      <div class="agent-icon icon-reviewer">R</div>
      <div>
        <div class="agent-name">Reviewer</div>
        <div class="agent-role">Challenges the spec</div>
      </div>
    </div>
    <div class="agent-status" id="status-reviewer">Idle</div>
    <ul class="turn-list" id="turns-reviewer"></ul>
  </div>

  <div class="agent-card" id="card-coder">
    <div class="agent-header">
      <div class="agent-icon icon-coder">C</div>
      <div>
        <div class="agent-name">Coder</div>
        <div class="agent-role">Builds the approved spec</div>
      </div>
    </div>
    <div class="agent-status" id="status-coder">Idle</div>
    <ul class="turn-list" id="turns-coder"></ul>
  </div>

  <div class="agent-card" id="card-tester">
    <div class="agent-header">
      <div class="agent-icon icon-tester">T</div>
      <div>
        <div class="agent-name">Tester</div>
        <div class="agent-role">Verifies requirements</div>
      </div>
    </div>
    <div class="agent-status" id="status-tester">Idle</div>
    <ul class="turn-list" id="turns-tester"></ul>
  </div>
</div>

<div class="empty-state" id="empty-state" style="display:none">
  <h2>No squad activity yet</h2>
  <p>Run spec-squad.py to start the flow</p>
</div>

<script>
const PHASES = ['spec', 'review', 'code', 'test', 'done'];
const PHASE_ORDER = { spec: 0, review: 1, code: 2, test: 3, done: 4 };

function updateUI(state) {
  if (!state || !state.phase) {
    document.getElementById('empty-state').style.display = 'block';
    return;
  }
  document.getElementById('empty-state').style.display = 'none';

  // Phase badge
  const badge = document.getElementById('phase-badge');
  badge.textContent = state.phase.toUpperCase();
  badge.className = 'phase-badge phase-' + state.phase;

  // Timeline
  const phaseIdx = PHASE_ORDER[state.phase] || 0;
  ['spec', 'review', 'code', 'test'].forEach((p, i) => {
    const el = document.getElementById('step-' + p);
    el.className = 'timeline-step';
    if (i < phaseIdx) el.classList.add('complete');
    else if (i === phaseIdx && state.phase !== 'done') el.classList.add('active');
    if (state.phase === 'done') el.classList.add('complete');
  });

  // Stats
  document.getElementById('review-rounds').textContent = state.review_round || 0;
  document.getElementById('turn-count').textContent = (state.turns || []).length;
  document.getElementById('approved').textContent = state.approved ? 'Yes' : 'No';

  if (state.started) {
    const start = new Date(state.started);
    const now = new Date();
    const mins = Math.floor((now - start) / 60000);
    document.getElementById('elapsed').textContent = mins + 'm';
  }

  // Agent cards
  const roleMap = { architect: [], reviewer: [], coder: [], tester: [] };
  (state.turns || []).forEach(t => {
    if (roleMap[t.role] !== undefined) roleMap[t.role].push(t);
  });

  // Determine which agent is currently active
  const lastTurn = state.turns && state.turns.length > 0
    ? state.turns[state.turns.length - 1] : null;

  Object.entries(roleMap).forEach(([role, turns]) => {
    const card = document.getElementById('card-' + role);
    const statusEl = document.getElementById('status-' + role);
    const listEl = document.getElementById('turns-' + role);

    // Active state
    card.className = 'agent-card';
    if (lastTurn && lastTurn.role === role && state.phase !== 'done') {
      card.classList.add('active');
    }
    if (turns.length > 0 && turns[turns.length - 1].signal) {
      const sig = turns[turns.length - 1].signal;
      if (sig.verdict === 'APPROVED' || sig.status === 'build_complete' || sig.verdict === 'PASSED') {
        card.classList.add('done');
      }
    }

    // Status text
    if (turns.length === 0) {
      statusEl.textContent = 'Waiting...';
      statusEl.className = 'agent-status';
    } else {
      const last = turns[turns.length - 1];
      const sig = last.signal;
      if (sig) {
        if (sig.verdict === 'APPROVED') {
          statusEl.textContent = 'APPROVED (confidence: ' + (sig.confidence || '?') + ')';
          statusEl.className = 'agent-status success';
        } else if (sig.verdict === 'REVISE') {
          const n = (sig.issues || []).length;
          statusEl.textContent = 'REVISE (' + n + ' issues, ' + (sig.severity || 'medium') + ')';
          statusEl.className = 'agent-status warning';
        } else if (sig.status === 'spec_complete') {
          statusEl.textContent = 'Spec complete (' + (sig.tasks || '?') + ' tasks, ' + (sig.phases || '?') + ' phases)';
          statusEl.className = 'agent-status success';
        } else if (sig.status === 'revision_complete') {
          statusEl.textContent = 'Revision complete';
          statusEl.className = 'agent-status success';
        } else if (sig.status === 'build_complete') {
          statusEl.textContent = 'Build done (' + (sig.tasks_done || '?') + '/' + (sig.tasks_total || '?') + ' tasks)';
          statusEl.className = 'agent-status success';
        } else if (sig.verdict === 'PASSED') {
          statusEl.textContent = 'ALL PASSED (rate: ' + (sig.pass_rate || '?') + ')';
          statusEl.className = 'agent-status success';
        } else {
          statusEl.textContent = JSON.stringify(sig).substring(0, 80);
          statusEl.className = 'agent-status working';
        }
      } else {
        statusEl.textContent = 'Completed (no signal)';
        statusEl.className = 'agent-status';
      }
    }

    // Turn list
    listEl.innerHTML = '';
    turns.forEach(t => {
      const li = document.createElement('li');
      const phase = document.createElement('span');
      phase.textContent = t.phase + (t.round ? ' #' + t.round : '');

      const signal = document.createElement('span');
      signal.className = 'turn-signal';
      if (t.signal) {
        const v = t.signal.verdict || t.signal.status || '';
        signal.textContent = v;
        if (v === 'APPROVED' || v === 'PASSED') signal.classList.add('signal-approved');
        else if (v === 'REVISE' || v === 'ISSUES') signal.classList.add('signal-revise');
        else signal.classList.add('signal-complete');
      }

      li.appendChild(phase);
      li.appendChild(signal);
      listEl.appendChild(li);
    });
  });
}

async function poll() {
  try {
    const res = await fetch('/api/state');
    if (res.ok) {
      const state = await res.json();
      updateUI(state);
    }
  } catch (e) { /* ignore */ }
  setTimeout(poll, 2000);
}

document.getElementById('workspace-path').textContent = location.pathname;
poll();
</script>
</body>
</html>"""


class SquadHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler that serves the viewer and state API."""

    workspace: Path = None  # set by factory

    def do_GET(self):
        if self.path == "/api/state":
            self.serve_state()
        elif self.path == "/" or self.path == "/index.html":
            self.serve_html()
        else:
            self.send_error(404)

    def serve_html(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))

    def serve_state(self):
        state_file = self.workspace / ".spec-squad.json"
        if state_file.exists():
            try:
                data = state_file.read_text(encoding="utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data.encode("utf-8"))
                return
            except OSError:
                pass
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{}')

    def log_message(self, format, *args):
        pass  # suppress logs


def main():
    parser = argparse.ArgumentParser(description="Spec Squad live viewer")
    parser.add_argument("workspace", help="Path to workspace directory")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port (default: {DEFAULT_PORT})")
    parser.add_argument("--no-open", action="store_true", help="Don't auto-open browser")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    if not workspace.exists():
        print(f"Error: workspace not found: {workspace}", file=sys.stderr)
        return 1

    # Create handler with workspace bound
    handler = type("Handler", (SquadHandler,), {"workspace": workspace})

    server = http.server.HTTPServer(("127.0.0.1", args.port), handler)
    url = f"http://localhost:{args.port}"
    print(f"Spec Squad Viewer: {url}")
    print(f"Workspace: {workspace}")
    print("Press Ctrl+C to stop\n")

    if not args.no_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
