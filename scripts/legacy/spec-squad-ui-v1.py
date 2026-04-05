#!/usr/bin/env python3
"""
spec-squad-ui.py — Unified web UI for Spec Squad.

Phase 1: Discovery chat — Claude asks 3W1H questions, user answers conversationally
Phase 2: Dashboard — watch Architect/Reviewer/Coder/Tester work in real-time

Usage:
    python spec-squad-ui.py                              # New project (chat discovery)
    python spec-squad-ui.py --workspace <path>           # Resume existing (dashboard)
    python spec-squad-ui.py --port 3333                  # Custom port

No external dependencies — stdlib only.
"""

import argparse
import http.server
import json
import os
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PORT = 3333
REPO_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent

# ── Shared state ─────────────────────────────────────────────────────────────

_state_lock = threading.Lock()
_app_state = {
    "workspace": None,
    "squad_running": False,
    "squad_log": [],
    "error": None,
}


def get_squad_state(workspace: Path) -> dict:
    """Read .spec-squad.json from workspace."""
    state_file = workspace / ".spec-squad.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


# ── Squad runner (background thread) ────────────────────────────────────────

def run_squad_background(workspace: Path, project_desc: str, plan_only: bool = False):
    """Run spec-squad.py in a background thread."""
    global _app_state

    with _state_lock:
        _app_state["squad_running"] = True
        _app_state["error"] = None

    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "spec-squad.py"),
        str(workspace),
        "--project", project_desc,
    ]
    if plan_only:
        cmd.append("--plan-only")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True,
            timeout=1800,  # 30 min max
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        with _state_lock:
            _app_state["squad_running"] = False
            if result.returncode != 0:
                _app_state["error"] = result.stderr[:500] if result.stderr else "Squad failed"
    except subprocess.TimeoutExpired:
        with _state_lock:
            _app_state["squad_running"] = False
            _app_state["error"] = "Squad timed out after 30 minutes"
    except Exception as e:
        with _state_lock:
            _app_state["squad_running"] = False
            _app_state["error"] = str(e)


# ── HTML Pages ───────────────────────────────────────────────────────────────

DISCOVERY_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Spec Squad - New Project</title>
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
  }
  header h1 { font-size: 24px; font-weight: 600; }
  header h1 span { color: #58a6ff; }
  header p { color: #8b949e; margin-top: 4px; font-size: 14px; }

  .container {
    max-width: 720px;
    margin: 32px auto;
    padding: 0 24px;
  }

  .step-indicator {
    display: flex;
    gap: 8px;
    margin-bottom: 32px;
  }
  .step {
    flex: 1;
    height: 4px;
    border-radius: 2px;
    background: #21262d;
  }
  .step.active { background: #58a6ff; }
  .step.done { background: #56d364; }

  .card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
  }
  .card h2 {
    font-size: 18px;
    margin-bottom: 4px;
  }
  .card .hint {
    color: #8b949e;
    font-size: 13px;
    margin-bottom: 12px;
  }

  label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 6px;
    color: #c9d1d9;
  }
  .label-hint {
    font-weight: 400;
    color: #8b949e;
    font-size: 12px;
  }

  input[type="text"], textarea, select {
    width: 100%;
    padding: 10px 14px;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    color: #c9d1d9;
    font-family: inherit;
    font-size: 14px;
    margin-bottom: 16px;
    transition: border-color 0.2s;
  }
  input:focus, textarea:focus, select:focus {
    outline: none;
    border-color: #58a6ff;
  }
  textarea { min-height: 80px; resize: vertical; }

  .row { display: flex; gap: 16px; }
  .row > div { flex: 1; }

  .options {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
  }
  .option-btn {
    flex: 1;
    padding: 10px;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    color: #8b949e;
    cursor: pointer;
    text-align: center;
    font-size: 13px;
    transition: all 0.2s;
  }
  .option-btn:hover { border-color: #58a6ff; color: #c9d1d9; }
  .option-btn.selected {
    border-color: #58a6ff;
    background: #1f3a5f;
    color: #58a6ff;
    font-weight: 600;
  }

  .btn-row {
    display: flex;
    gap: 12px;
    margin-top: 24px;
    justify-content: flex-end;
  }
  .btn {
    padding: 10px 24px;
    border-radius: 8px;
    border: 1px solid #30363d;
    background: #21262d;
    color: #c9d1d9;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s;
  }
  .btn:hover { background: #30363d; }
  .btn-primary {
    background: #238636;
    border-color: #238636;
    color: #fff;
  }
  .btn-primary:hover { background: #2ea043; }
  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .launching {
    text-align: center;
    padding: 60px;
  }
  .launching h2 { margin-bottom: 12px; }
  .spinner {
    width: 40px; height: 40px;
    border: 3px solid #21262d;
    border-top: 3px solid #58a6ff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 20px auto;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>

<header>
  <h1><span>Spec Squad</span> -- New Project</h1>
  <p>Answer a few questions and the squad will build your spec</p>
</header>

<div class="container">
  <div class="step-indicator">
    <div class="step active" id="s1"></div>
    <div class="step" id="s2"></div>
    <div class="step" id="s3"></div>
    <div class="step" id="s4"></div>
  </div>

  <!-- Step 1: What & Why -->
  <div id="step-1">
    <div class="card">
      <h2>What are you building?</h2>
      <div class="hint">Describe your project in plain language</div>
      <textarea id="what" placeholder="e.g. A CLI tool that manages my todo list with SQLite storage and colored output"></textarea>

      <label>Why does this need to exist? <span class="label-hint">(what problem does it solve?)</span></label>
      <textarea id="why" placeholder="e.g. I keep forgetting tasks and existing tools are too complex for my needs" rows="3"></textarea>
    </div>
    <div class="btn-row">
      <button class="btn btn-primary" onclick="nextStep(2)">Next</button>
    </div>
  </div>

  <!-- Step 2: Who & How -->
  <div id="step-2" style="display:none">
    <div class="card">
      <h2>Who is this for?</h2>
      <div class="hint">Target users and their technical level</div>
      <input type="text" id="who" placeholder="e.g. Developers who live in the terminal">

      <label>Tech stack <span class="label-hint">(or let the Architect decide)</span></label>
      <input type="text" id="stack" placeholder="e.g. Python, SQLite, Click -- or leave blank for AI recommendation">

      <label>Scope</label>
      <div class="options" id="scope-options">
        <div class="option-btn selected" data-val="mvp" onclick="selectOption(this)">MVP</div>
        <div class="option-btn" data-val="standard" onclick="selectOption(this)">Standard</div>
        <div class="option-btn" data-val="enterprise" onclick="selectOption(this)">Enterprise</div>
      </div>
    </div>
    <div class="btn-row">
      <button class="btn" onclick="prevStep(1)">Back</button>
      <button class="btn btn-primary" onclick="nextStep(3)">Next</button>
    </div>
  </div>

  <!-- Step 3: Details -->
  <div id="step-3" style="display:none">
    <div class="card">
      <h2>Any specifics?</h2>
      <div class="hint">Optional -- skip if nothing comes to mind</div>

      <label>Integrations <span class="label-hint">(external APIs, databases, services)</span></label>
      <input type="text" id="integrations" placeholder="e.g. GitHub API, PostgreSQL, Stripe">

      <label>Constraints <span class="label-hint">(non-negotiable requirements)</span></label>
      <textarea id="constraints" placeholder="e.g. Must work offline, no external dependencies, Python 3.10+" rows="3"></textarea>

      <label>References <span class="label-hint">(similar projects or inspiration)</span></label>
      <input type="text" id="references" placeholder="e.g. taskwarrior, todo.txt">
    </div>
    <div class="btn-row">
      <button class="btn" onclick="prevStep(2)">Back</button>
      <button class="btn btn-primary" onclick="nextStep(4)">Next</button>
    </div>
  </div>

  <!-- Step 4: Confirm & Launch -->
  <div id="step-4" style="display:none">
    <div class="card">
      <h2>Ready to launch the squad?</h2>
      <div class="hint">Review your project and choose the mode</div>

      <div id="summary" style="background:#0d1117; padding:16px; border-radius:8px; margin-bottom:16px; font-size:13px; white-space:pre-wrap; color:#8b949e;"></div>

      <label>Workspace name <span class="label-hint">(kebab-case)</span></label>
      <input type="text" id="ws-name" placeholder="my-project">

      <label>Mode</label>
      <div class="options" id="mode-options">
        <div class="option-btn selected" data-val="plan-only" onclick="selectOption(this)">Plan Only (Architect + Reviewer)</div>
        <div class="option-btn" data-val="full" onclick="selectOption(this)">Full Build (All 4 Agents)</div>
      </div>
    </div>
    <div class="btn-row">
      <button class="btn" onclick="prevStep(3)">Back</button>
      <button class="btn btn-primary" id="launch-btn" onclick="launch()">Launch Spec Squad</button>
    </div>
  </div>

  <!-- Launching state -->
  <div id="launching" style="display:none">
    <div class="launching">
      <div class="spinner"></div>
      <h2>Launching Spec Squad...</h2>
      <p style="color:#8b949e">Creating workspace and starting the team</p>
    </div>
  </div>
</div>

<script>
let currentStep = 1;

function selectOption(el) {
  el.parentNode.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
  el.classList.add('selected');
}

function nextStep(n) {
  document.getElementById('step-' + currentStep).style.display = 'none';
  document.getElementById('step-' + n).style.display = 'block';
  currentStep = n;
  updateSteps();
  if (n === 4) buildSummary();
}

function prevStep(n) {
  document.getElementById('step-' + currentStep).style.display = 'none';
  document.getElementById('step-' + n).style.display = 'block';
  currentStep = n;
  updateSteps();
}

function updateSteps() {
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById('s' + i);
    el.className = 'step';
    if (i < currentStep) el.classList.add('done');
    else if (i === currentStep) el.classList.add('active');
  }
}

function getFormData() {
  const scope = document.querySelector('#scope-options .selected')?.dataset.val || 'standard';
  return {
    what: document.getElementById('what').value,
    why: document.getElementById('why').value,
    who: document.getElementById('who').value,
    stack: document.getElementById('stack').value,
    scope: scope,
    integrations: document.getElementById('integrations').value,
    constraints: document.getElementById('constraints').value,
    references: document.getElementById('references').value,
  };
}

function buildSummary() {
  const d = getFormData();
  let s = '';
  if (d.what) s += 'What: ' + d.what + '\\n';
  if (d.why) s += 'Why: ' + d.why + '\\n';
  if (d.who) s += 'Who: ' + d.who + '\\n';
  if (d.stack) s += 'Stack: ' + d.stack + '\\n';
  s += 'Scope: ' + d.scope + '\\n';
  if (d.integrations) s += 'Integrations: ' + d.integrations + '\\n';
  if (d.constraints) s += 'Constraints: ' + d.constraints + '\\n';
  if (d.references) s += 'References: ' + d.references + '\\n';
  document.getElementById('summary').textContent = s;

  // Auto-generate workspace name from "what"
  if (!document.getElementById('ws-name').value && d.what) {
    const name = d.what.toLowerCase()
      .replace(/[^a-z0-9\\s-]/g, '')
      .trim()
      .split(/\\s+/)
      .slice(0, 3)
      .join('-');
    document.getElementById('ws-name').value = name;
  }
}

async function launch() {
  const data = getFormData();
  const wsName = document.getElementById('ws-name').value.trim();
  const mode = document.querySelector('#mode-options .selected')?.dataset.val || 'plan-only';

  if (!data.what) { alert('Please describe what you are building'); return; }
  if (!wsName) { alert('Please enter a workspace name'); return; }

  document.getElementById('step-4').style.display = 'none';
  document.getElementById('launching').style.display = 'block';

  try {
    const res = await fetch('/api/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...data, workspace_name: wsName, mode: mode }),
    });
    const result = await res.json();
    if (result.ok) {
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } else {
      alert('Error: ' + (result.error || 'unknown'));
      document.getElementById('launching').style.display = 'none';
      document.getElementById('step-4').style.display = 'block';
    }
  } catch (e) {
    alert('Error: ' + e.message);
    document.getElementById('launching').style.display = 'none';
    document.getElementById('step-4').style.display = 'block';
  }
}
</script>
</body>
</html>"""

DASHBOARD_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Spec Squad - Dashboard</title>
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

  .running-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #58a6ff;
    font-size: 13px;
  }
  .pulse-dot {
    width: 8px; height: 8px;
    background: #58a6ff;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

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
  .agent-card.done { border-color: #56d364; }

  .agent-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }
  .agent-icon {
    width: 48px; height: 48px;
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
  .signal-approved { color: #56d364; font-weight: 500; }
  .signal-revise { color: #e3b341; font-weight: 500; }
  .signal-complete { color: #58a6ff; font-weight: 500; }

  .timeline {
    padding: 24px 32px 8px;
    max-width: 1200px;
    margin: 0 auto;
  }
  .timeline-bar { display: flex; gap: 4px; margin-bottom: 8px; }
  .timeline-step {
    flex: 1; height: 8px; border-radius: 4px;
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

  .stats {
    display: flex;
    gap: 24px;
    padding: 8px 32px 0;
    max-width: 1200px;
    margin: 0 auto;
    color: #8b949e;
    font-size: 14px;
  }
  .stat-value { color: #c9d1d9; font-weight: 600; }
</style>
</head>
<body>

<header>
  <div>
    <h1><span>Spec Squad</span> Dashboard</h1>
    <div class="header-meta" id="workspace-path"></div>
  </div>
  <div style="display:flex;align-items:center;gap:16px;">
    <div class="running-indicator" id="running" style="display:none">
      <div class="pulse-dot"></div> Running
    </div>
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
    <span>Spec</span><span>Review</span><span>Code</span><span>Test</span>
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
      <div><div class="agent-name">Architect</div><div class="agent-role">Writes the spec</div></div>
    </div>
    <div class="agent-status" id="status-architect">Waiting...</div>
    <ul class="turn-list" id="turns-architect"></ul>
  </div>
  <div class="agent-card" id="card-reviewer">
    <div class="agent-header">
      <div class="agent-icon icon-reviewer">R</div>
      <div><div class="agent-name">Reviewer</div><div class="agent-role">Challenges the spec</div></div>
    </div>
    <div class="agent-status" id="status-reviewer">Waiting...</div>
    <ul class="turn-list" id="turns-reviewer"></ul>
  </div>
  <div class="agent-card" id="card-coder">
    <div class="agent-header">
      <div class="agent-icon icon-coder">C</div>
      <div><div class="agent-name">Coder</div><div class="agent-role">Builds the approved spec</div></div>
    </div>
    <div class="agent-status" id="status-coder">Waiting...</div>
    <ul class="turn-list" id="turns-coder"></ul>
  </div>
  <div class="agent-card" id="card-tester">
    <div class="agent-header">
      <div class="agent-icon icon-tester">T</div>
      <div><div class="agent-name">Tester</div><div class="agent-role">Verifies requirements</div></div>
    </div>
    <div class="agent-status" id="status-tester">Waiting...</div>
    <ul class="turn-list" id="turns-tester"></ul>
  </div>
</div>

<script>
const PHASE_ORDER = { spec: 0, review: 1, code: 2, test: 3, done: 4 };

function updateUI(data) {
  const state = data.squad_state || {};
  const running = data.squad_running;

  document.getElementById('running').style.display = running ? 'flex' : 'none';
  if (data.workspace) document.getElementById('workspace-path').textContent = data.workspace;

  if (!state.phase) return;

  const badge = document.getElementById('phase-badge');
  badge.textContent = state.phase.toUpperCase();
  badge.className = 'phase-badge phase-' + state.phase;

  const phaseIdx = PHASE_ORDER[state.phase] || 0;
  ['spec', 'review', 'code', 'test'].forEach((p, i) => {
    const el = document.getElementById('step-' + p);
    el.className = 'timeline-step';
    if (i < phaseIdx || state.phase === 'done') el.classList.add('complete');
    else if (i === phaseIdx && state.phase !== 'done') el.classList.add('active');
  });

  document.getElementById('review-rounds').textContent = state.review_round || 0;
  document.getElementById('turn-count').textContent = (state.turns || []).length;
  document.getElementById('approved').textContent = state.approved ? 'Yes' : 'No';

  if (state.started) {
    const mins = Math.floor((Date.now() - new Date(state.started).getTime()) / 60000);
    document.getElementById('elapsed').textContent = mins + 'm';
  }

  const roleMap = { architect: [], reviewer: [], coder: [], tester: [] };
  (state.turns || []).forEach(t => { if (roleMap[t.role]) roleMap[t.role].push(t); });

  const lastTurn = state.turns?.length ? state.turns[state.turns.length - 1] : null;

  Object.entries(roleMap).forEach(([role, turns]) => {
    const card = document.getElementById('card-' + role);
    const statusEl = document.getElementById('status-' + role);
    const listEl = document.getElementById('turns-' + role);

    card.className = 'agent-card';
    if (running && lastTurn?.role === role) card.classList.add('active');

    if (turns.length > 0) {
      const last = turns[turns.length - 1];
      const sig = last.signal;
      if (sig?.verdict === 'APPROVED' || sig?.status === 'build_complete' || sig?.verdict === 'PASSED') {
        card.classList.add('done');
      }
      if (sig) {
        if (sig.verdict === 'APPROVED') {
          statusEl.textContent = 'APPROVED (confidence: ' + (sig.confidence || '?') + ')';
          statusEl.className = 'agent-status success';
        } else if (sig.verdict === 'REVISE') {
          statusEl.textContent = 'REVISE (' + (sig.issues?.length || 0) + ' issues)';
          statusEl.className = 'agent-status warning';
        } else if (sig.status === 'spec_complete') {
          statusEl.textContent = 'Spec complete (' + (sig.tasks||'?') + ' tasks)';
          statusEl.className = 'agent-status success';
        } else if (sig.status === 'revision_complete') {
          statusEl.textContent = 'Revision complete';
          statusEl.className = 'agent-status success';
        } else if (sig.status === 'build_complete') {
          statusEl.textContent = 'Build done (' + (sig.tasks_done||'?') + '/' + (sig.tasks_total||'?') + ')';
          statusEl.className = 'agent-status success';
        } else if (sig.verdict === 'PASSED') {
          statusEl.textContent = 'ALL PASSED';
          statusEl.className = 'agent-status success';
        } else {
          statusEl.textContent = JSON.stringify(sig).substring(0, 80);
          statusEl.className = 'agent-status working';
        }
      } else {
        statusEl.textContent = 'Completed';
        statusEl.className = 'agent-status';
      }
    } else if (running) {
      statusEl.textContent = 'Waiting...';
      statusEl.className = 'agent-status';
    }

    listEl.innerHTML = '';
    turns.forEach(t => {
      const li = document.createElement('li');
      const phase = document.createElement('span');
      phase.textContent = t.phase + (t.round ? ' #' + t.round : '');
      const signal = document.createElement('span');
      if (t.signal) {
        const v = t.signal.verdict || t.signal.status || '';
        signal.textContent = v;
        if (v === 'APPROVED' || v === 'PASSED') signal.className = 'signal-approved';
        else if (v === 'REVISE' || v === 'ISSUES') signal.className = 'signal-revise';
        else signal.className = 'signal-complete';
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
    if (res.ok) updateUI(await res.json());
  } catch (e) {}
  setTimeout(poll, 2000);
}
poll();
</script>
</body>
</html>"""


# ── HTTP Handler ─────────────────────────────────────────────────────────────

class SquadUIHandler(http.server.BaseHTTPRequestHandler):
    workspace_root: Path = None
    workspace: Path = None

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            if self.workspace and (self.workspace / ".spec-squad.json").exists():
                self.serve_page(DASHBOARD_PAGE)
            else:
                self.serve_page(DISCOVERY_PAGE)
        elif self.path == "/dashboard":
            self.serve_page(DASHBOARD_PAGE)
        elif self.path == "/api/state":
            self.serve_state()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/start":
            self.handle_start()
        else:
            self.send_error(404)

    def serve_page(self, html: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def serve_state(self):
        data = {}
        with _state_lock:
            data["squad_running"] = _app_state["squad_running"]
            data["error"] = _app_state["error"]
            data["workspace"] = str(_app_state.get("workspace") or self.workspace or "")

        ws = _app_state.get("workspace") or self.workspace
        if ws:
            data["squad_state"] = get_squad_state(ws)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def handle_start(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8")
        try:
            params = json.loads(body)
        except json.JSONDecodeError:
            self.send_json({"ok": False, "error": "Invalid JSON"})
            return

        ws_name = params.get("workspace_name", "").strip()
        if not ws_name:
            self.send_json({"ok": False, "error": "Missing workspace name"})
            return

        # Build project description from form data
        desc_parts = []
        if params.get("what"): desc_parts.append(f"What: {params['what']}")
        if params.get("why"): desc_parts.append(f"Why: {params['why']}")
        if params.get("who"): desc_parts.append(f"Who: {params['who']}")
        if params.get("stack"): desc_parts.append(f"Tech Stack: {params['stack']}")
        if params.get("scope"): desc_parts.append(f"Scope: {params['scope']}")
        if params.get("integrations"): desc_parts.append(f"Integrations: {params['integrations']}")
        if params.get("constraints"): desc_parts.append(f"Constraints: {params['constraints']}")
        if params.get("references"): desc_parts.append(f"References: {params['references']}")
        project_desc = "\n".join(desc_parts)

        # Create workspace directory
        ws_root = self.workspace_root or Path.home() / "Documents" / "Workspace"
        workspace = ws_root / ws_name
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "openspec").mkdir(exist_ok=True)

        with _state_lock:
            _app_state["workspace"] = workspace

        # Bind workspace to handler class
        type(self).workspace = workspace

        # Start squad in background
        plan_only = params.get("mode") == "plan-only"
        t = threading.Thread(
            target=run_squad_background,
            args=(workspace, project_desc, plan_only),
            daemon=True,
        )
        t.start()

        self.send_json({"ok": True, "workspace": str(workspace)})

    def send_json(self, data: dict):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        pass


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Spec Squad unified UI")
    parser.add_argument("--workspace", "-w", help="Existing workspace path (skips form, shows dashboard)")
    parser.add_argument("--workspace-root", help="Root directory for new workspaces (default: ~/Documents/Workspace)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()

    ws_root = Path(args.workspace_root) if args.workspace_root else Path.home() / "Documents" / "Workspace"
    workspace = Path(args.workspace).resolve() if args.workspace else None

    handler = type("Handler", (SquadUIHandler,), {
        "workspace_root": ws_root,
        "workspace": workspace,
    })

    if workspace:
        _app_state["workspace"] = workspace

    server = http.server.HTTPServer(("127.0.0.1", args.port), handler)
    url = f"http://localhost:{args.port}"
    print(f"Spec Squad UI: {url}")
    if workspace:
        print(f"Workspace: {workspace}")
    else:
        print(f"New project mode (workspace root: {ws_root})")
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
