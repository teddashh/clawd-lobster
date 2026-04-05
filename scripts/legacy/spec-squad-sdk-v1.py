#!/usr/bin/env python3
"""
spec-squad-sdk.py — Multi-session spec orchestrator using Claude Agent SDK.

Unified web app:
  1. Discovery chat — Claude asks 3W1H questions via streaming SSE
  2. Squad dashboard — Architect/Reviewer/Coder/Tester work in real-time

Architecture:
  Browser <--SSE--> Python HTTP server <--> claude_agent_sdk.query()

Usage:
    python spec-squad-sdk.py                          # New project (chat)
    python spec-squad-sdk.py -w <workspace>           # Resume (dashboard)
    python spec-squad-sdk.py --port 3333

Requires: pip install claude-agent-sdk
"""

import anyio
import argparse
import asyncio
import http.server
import json
import os
import queue
import re
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition,
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
)

# ── Constants ────────────────────────────────────────────────────────────────

DEFAULT_PORT = 3333
SCRIPTS_DIR = Path(__file__).resolve().parent
MAX_REVIEW_ROUNDS = 5
SQUAD_STATE_FILE = ".spec-squad.json"

# ── Shared state ─────────────────────────────────────────────────────────────

_lock = threading.Lock()
_state = {
    "workspace": None,
    "phase": "discovery",  # discovery | spec | review | code | test | done
    "squad_running": False,
    "discovery_session_id": None,
    "discovery_history": [],  # [{role, content}]
    "error": None,
}
# SSE event queue for streaming to browser
_sse_queue = queue.Queue()


def push_sse(event: str, data: dict):
    _sse_queue.put(json.dumps({"event": event, **data}, ensure_ascii=False))


def get_squad_state(workspace: Path) -> dict:
    state_file = workspace / SQUAD_STATE_FILE
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_squad_state(workspace: Path, squad_state: dict):
    state_file = workspace / SQUAD_STATE_FILE
    state_file.write_text(
        json.dumps(squad_state, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


# ── Discovery system prompt ─────────────────────────────────────────────────

DISCOVERY_SYSTEM = """You are the Discovery Interviewer for Spec Squad — a multi-agent spec development system.

YOUR JOB: Ask the user smart questions to understand what they want to build. You are a senior consultant doing requirements gathering.

APPROACH:
- Ask 1-2 questions at a time, conversationally
- Be opinionated — if they say "whatever you think", make a strong recommendation
- Adapt based on their answers
- Cover the 3W1H framework: Why, What, Who, How, Scope, Integrations, Constraints

RULES:
- Do NOT write any code or specs yourself
- Do NOT create files
- Just ask questions and synthesize understanding
- When you have enough context (typically 3-6 exchanges), say EXACTLY:

DISCOVERY_COMPLETE
```json
{"what": "...", "why": "...", "who": "...", "stack": "...", "scope": "mvp|standard|enterprise", "integrations": "...", "constraints": "...", "workspace_name": "kebab-case-name"}
```

The JSON must contain all fields. workspace_name should be derived from the project (kebab-case).

START by asking what they want to build. Be friendly but efficient."""


# ── Agent SDK runners (async) ────────────────────────────────────────────────

async def run_discovery_turn(user_message: str, workspace: Path | None) -> str:
    """Send a user message to the discovery agent, return Claude's response."""
    with _lock:
        _state["discovery_history"].append({"role": "user", "content": user_message})
        history = list(_state["discovery_history"])

    # Build messages for multi-turn
    messages_prompt = ""
    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        messages_prompt += f"\n{role}: {msg['content']}\n"

    full_prompt = messages_prompt.strip()
    response_text = ""

    async for message in query(
        prompt=full_prompt,
        options=ClaudeAgentOptions(
            system_prompt=DISCOVERY_SYSTEM,
            allowed_tools=[],  # No tools during discovery
            max_turns=1,
            cwd=str(workspace) if workspace else None,
        ),
    ):
        if isinstance(message, ResultMessage):
            # ResultMessage has the final complete text — use only this
            if message.result:
                response_text = message.result
                break

    with _lock:
        _state["discovery_history"].append({"role": "assistant", "content": response_text})

    return response_text


async def run_squad_agent(
    role: str,
    system_prompt: str,
    prompt: str,
    workspace: Path,
    allowed_tools: list[str] | None = None,
) -> str:
    """Run a single squad agent and return the response."""
    if allowed_tools is None:
        allowed_tools = ["Read", "Glob", "Grep"]

    push_sse("agent_start", {"role": role})
    response_text = ""
    start_time = time.time()

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            system_prompt=system_prompt,
            allowed_tools=allowed_tools,
            permission_mode="acceptEdits" if role in ("architect", "coder") else "default",
            max_turns=30,
            cwd=str(workspace),
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    response_text += block.text
                    # Stream text to SSE
                    push_sse("agent_text", {"role": role, "chunk": block.text[:200]})
        elif isinstance(message, ResultMessage):
            if message.result:
                response_text += message.result

    elapsed = time.time() - start_time
    push_sse("agent_done", {"role": role, "elapsed": round(elapsed)})
    return response_text


# ── Role prompts ─────────────────────────────────────────────────────────────

ARCHITECT_SYSTEM = """You are the ARCHITECT in a Spec Squad. Write a complete OpenSpec.
Generate artifacts in strict DAG order:
1. openspec/project.md (3W1H context)
2. openspec/changes/v1/proposal.md (scope: In Scope / Out of Scope)
3. openspec/changes/v1/design.md (architecture with rationale)
4. openspec/changes/v1/specs/<capability>/spec.md (SHALL/MUST + Gherkin)
5. openspec/changes/v1/tasks.md (phased, file-referenced, 5-30 min tasks)

Requirements MUST use SHALL or MUST. Every requirement needs Gherkin scenarios.
After generating all artifacts, output:
```json
{"status": "spec_complete", "capabilities": N, "tasks": N, "phases": N}
```
Write ALL files now. Do not ask questions."""

REVIEWER_SYSTEM = """You are the REVIEWER in a Spec Squad.
Tear apart the Architect's spec. Find gaps, ambiguities, weak decisions.
Read ALL files in openspec/. Challenge architecture, requirements, tasks.

Output verdict:
If issues: ```json {"verdict": "REVISE", "issues": ["..."], "severity": "high|medium|low"} ```
If solid: ```json {"verdict": "APPROVED", "confidence": 0.0-1.0} ```

Be ruthless but fair."""

CODER_SYSTEM = """You are the CODER in a Spec Squad.
Execute the approved spec exactly. Read openspec/changes/v1/tasks.md.
Execute tasks phase by phase. Mark done: [ ] to [x] in tasks.md.
After each phase, commit. Skip [codex] tasks.

After all tasks: ```json {"status": "build_complete", "tasks_done": N, "tasks_total": N} ```
The spec is the plan. Follow it. Do not improvise."""

TESTER_SYSTEM = """You are the TESTER in a Spec Squad.
Verify code matches the approved spec. Read specs/ requirements and Gherkin scenarios.
Check every SHALL/MUST requirement against the code. Run any tests.

Output: If issues: ```json {"verdict": "ISSUES", "failures": ["..."], "pass_rate": 0.0-1.0} ```
If pass: ```json {"verdict": "PASSED", "pass_rate": 1.0} ```"""


def extract_json_signal(output: str) -> dict | None:
    patterns = [
        r'```json\s*\n({[^`]*?})\s*\n```',
        r'({\"(?:status|verdict)\"[^}]*})',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, output, re.DOTALL)
        if matches:
            try:
                return json.loads(matches[-1])
            except json.JSONDecodeError:
                continue
    return None


# ── Squad orchestration ──────────────────────────────────────────────────────

async def run_squad(workspace: Path, project_desc: str, plan_only: bool = False):
    """Run the full Architect → Reviewer → Coder → Tester pipeline."""
    squad_state = {
        "phase": "spec", "review_round": 0, "approved": False,
        "started": datetime.now(timezone.utc).isoformat(), "turns": [],
    }
    save_squad_state(workspace, squad_state)

    with _lock:
        _state["phase"] = "spec"
        _state["squad_running"] = True

    # Phase 1: Architect
    push_sse("phase", {"phase": "spec"})
    arch_output = await run_squad_agent(
        "architect", ARCHITECT_SYSTEM,
        f"Write a complete OpenSpec for this project:\n\n{project_desc}",
        workspace,
        allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
    )
    signal = extract_json_signal(arch_output)
    squad_state["turns"].append({
        "role": "architect", "phase": "spec",
        "time": datetime.now(timezone.utc).isoformat(), "signal": signal,
    })
    squad_state["phase"] = "review"
    save_squad_state(workspace, squad_state)

    # Phase 2: Review loop
    with _lock:
        _state["phase"] = "review"
    push_sse("phase", {"phase": "review"})

    while squad_state["review_round"] < MAX_REVIEW_ROUNDS:
        squad_state["review_round"] += 1
        round_n = squad_state["review_round"]

        # Reviewer
        rev_output = await run_squad_agent(
            "reviewer", REVIEWER_SYSTEM,
            f"Review round {round_n}. Read ALL files in openspec/ and challenge the spec.",
            workspace,
        )
        rev_signal = extract_json_signal(rev_output)
        squad_state["turns"].append({
            "role": "reviewer", "phase": "review", "round": round_n,
            "time": datetime.now(timezone.utc).isoformat(), "signal": rev_signal,
        })
        save_squad_state(workspace, squad_state)

        if rev_signal and rev_signal.get("verdict") == "APPROVED":
            squad_state["approved"] = True
            break

        # Architect revises
        issues = rev_signal.get("issues", ["Reviewer requested revisions"]) if rev_signal else ["Review completed"]
        issues_text = "\n".join(f"- {i}" for i in issues)
        fix_output = await run_squad_agent(
            "architect", ARCHITECT_SYSTEM,
            f"The REVIEWER found these issues. Fix ALL of them:\n{issues_text}\n\nRead and update the openspec/ files.",
            workspace,
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
        )
        fix_signal = extract_json_signal(fix_output)
        squad_state["turns"].append({
            "role": "architect", "phase": "revision", "round": round_n,
            "time": datetime.now(timezone.utc).isoformat(), "signal": fix_signal,
        })
        save_squad_state(workspace, squad_state)

    if not squad_state["approved"]:
        squad_state["approved"] = True  # max rounds reached

    if plan_only:
        squad_state["phase"] = "done"
        save_squad_state(workspace, squad_state)
        with _lock:
            _state["phase"] = "done"
            _state["squad_running"] = False
        push_sse("phase", {"phase": "done"})
        return

    # Phase 3: Coder
    squad_state["phase"] = "code"
    save_squad_state(workspace, squad_state)
    with _lock:
        _state["phase"] = "code"
    push_sse("phase", {"phase": "code"})

    code_output = await run_squad_agent(
        "coder", CODER_SYSTEM,
        "Read the approved spec in openspec/changes/v1/tasks.md and build everything.",
        workspace,
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    )
    code_signal = extract_json_signal(code_output)
    squad_state["turns"].append({
        "role": "coder", "phase": "code",
        "time": datetime.now(timezone.utc).isoformat(), "signal": code_signal,
    })
    save_squad_state(workspace, squad_state)

    # Phase 4: Tester
    squad_state["phase"] = "test"
    save_squad_state(workspace, squad_state)
    with _lock:
        _state["phase"] = "test"
    push_sse("phase", {"phase": "test"})

    test_output = await run_squad_agent(
        "tester", TESTER_SYSTEM,
        "Read the specs in openspec/changes/v1/specs/ and verify the code matches every requirement.",
        workspace,
        allowed_tools=["Read", "Bash", "Glob", "Grep"],
    )
    test_signal = extract_json_signal(test_output)
    squad_state["turns"].append({
        "role": "tester", "phase": "test",
        "time": datetime.now(timezone.utc).isoformat(), "signal": test_signal,
    })
    squad_state["phase"] = "done"
    save_squad_state(workspace, squad_state)

    with _lock:
        _state["phase"] = "done"
        _state["squad_running"] = False
    push_sse("phase", {"phase": "done"})


# ── Background thread to run async code ──────────────────────────────────────

def _run_async(coro):
    """Run an async coroutine using anyio (required by claude-agent-sdk)."""
    async def wrapper():
        return await coro
    anyio.run(wrapper)


def _run_async_sync(async_fn, *args):
    """Run an async function synchronously from a regular thread.

    anyio.run() requires an async function (not a coroutine object).
    So we pass the function and args separately.
    """
    result = [None]
    error = [None]

    def worker():
        try:
            async def wrapper():
                return await async_fn(*args)
            result[0] = anyio.run(wrapper)
        except Exception as e:
            error[0] = e

    t = threading.Thread(target=worker)
    t.start()
    t.join(timeout=300)
    if error[0]:
        raise error[0]
    return result[0]


# ── HTML Pages ───────────────────────────────────────────────────────────────

CHAT_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Spec Squad</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',system-ui,sans-serif; background:#0d1117; color:#c9d1d9; height:100vh; display:flex; flex-direction:column; }
header { background:#161b22; border-bottom:1px solid #30363d; padding:16px 24px; display:flex; align-items:center; justify-content:space-between; }
header h1 { font-size:20px; } header h1 span { color:#58a6ff; }
.badge { padding:3px 10px; border-radius:10px; font-size:12px; font-weight:600; text-transform:uppercase; }
.badge-discovery { background:#1f3a5f; color:#58a6ff; }
.badge-spec { background:#1f3a5f; color:#58a6ff; }
.badge-review { background:#3d1f5f; color:#bc8cff; }
.badge-code { background:#1f5f2d; color:#56d364; }
.badge-test { background:#5f4b1f; color:#e3b341; }
.badge-done { background:#1f5f2d; color:#56d364; }

.chat-area { flex:1; overflow-y:auto; padding:24px; max-width:800px; width:100%; margin:0 auto; }
.msg { margin-bottom:16px; max-width:85%; }
.msg-user { margin-left:auto; }
.msg-assistant { margin-right:auto; }
.msg-bubble { padding:12px 16px; border-radius:12px; font-size:14px; line-height:1.5; white-space:pre-wrap; }
.msg-user .msg-bubble { background:#1f6feb; color:#fff; border-bottom-right-radius:4px; }
.msg-assistant .msg-bubble { background:#161b22; border:1px solid #30363d; border-bottom-left-radius:4px; }
.msg-label { font-size:11px; color:#8b949e; margin-bottom:4px; }
.msg-user .msg-label { text-align:right; }

.input-area { background:#161b22; border-top:1px solid #30363d; padding:16px 24px; }
.input-row { max-width:800px; margin:0 auto; display:flex; gap:12px; }
.input-row input { flex:1; padding:10px 14px; background:#0d1117; border:1px solid #30363d; border-radius:8px; color:#c9d1d9; font-size:14px; }
.input-row input:focus { outline:none; border-color:#58a6ff; }
.input-row button { padding:10px 20px; background:#238636; border:none; border-radius:8px; color:#fff; font-weight:600; cursor:pointer; }
.input-row button:hover { background:#2ea043; }
.input-row button:disabled { opacity:0.5; cursor:not-allowed; }

.typing { color:#8b949e; font-size:13px; padding:8px 0; }
.dot-pulse { display:inline-block; animation:pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* Dashboard overlay */
.dashboard { display:none; flex:1; overflow-y:auto; }
.dashboard.active { display:block; }
.chat-container { display:flex; flex-direction:column; flex:1; }
.chat-container.hidden { display:none; }

.grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; padding:24px; max-width:1200px; margin:0 auto; }
.agent-card { background:#161b22; border:1px solid #30363d; border-radius:12px; padding:20px; transition:border-color 0.3s; }
.agent-card.active { border-color:#58a6ff; box-shadow:0 0 20px rgba(88,166,255,0.1); }
.agent-card.done { border-color:#56d364; }
.agent-header { display:flex; align-items:center; gap:12px; margin-bottom:12px; }
.agent-icon { width:48px; height:48px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:22px; font-weight:700; color:#fff; }
.icon-architect { background:#1f6feb; } .icon-reviewer { background:#8957e5; }
.icon-coder { background:#238636; } .icon-tester { background:#9e6a03; }
.agent-name { font-size:18px; font-weight:600; }
.agent-role { color:#8b949e; font-size:13px; }
.agent-status { padding:8px 12px; background:#0d1117; border-radius:8px; font-size:13px; color:#8b949e; min-height:40px; margin-bottom:12px; }
.agent-status.working { color:#58a6ff; } .agent-status.success { color:#56d364; } .agent-status.warning { color:#e3b341; }
.turn-list { list-style:none; font-size:13px; max-height:200px; overflow-y:auto; }
.turn-list li { padding:4px 0; border-bottom:1px solid #21262d; display:flex; justify-content:space-between; }
.signal-approved { color:#56d364; font-weight:500; } .signal-revise { color:#e3b341; font-weight:500; } .signal-complete { color:#58a6ff; font-weight:500; }

.timeline { padding:16px 24px 8px; max-width:1200px; margin:0 auto; }
.timeline-bar { display:flex; gap:4px; margin-bottom:8px; }
.timeline-step { flex:1; height:8px; border-radius:4px; background:#21262d; transition:background 0.3s; }
.timeline-step.complete { background:#56d364; } .timeline-step.active { background:#58a6ff; animation:pulse 1.5s infinite; }
.timeline-labels { display:flex; justify-content:space-between; font-size:12px; color:#8b949e; }
.stats { display:flex; gap:24px; padding:8px 24px; max-width:1200px; margin:0 auto; color:#8b949e; font-size:14px; }
.stat-value { color:#c9d1d9; font-weight:600; }
</style>
</head>
<body>

<header>
  <h1><span>Spec Squad</span></h1>
  <span class="badge badge-discovery" id="phase-badge">DISCOVERY</span>
</header>

<!-- Chat (discovery) -->
<div class="chat-container" id="chat-container">
  <div class="chat-area" id="chat-area"></div>
  <div class="input-area">
    <div class="input-row">
      <input type="text" id="user-input" placeholder="Describe what you want to build..." autofocus>
      <button id="send-btn" onclick="sendMessage()">Send</button>
    </div>
  </div>
</div>

<!-- Dashboard (squad) -->
<div class="dashboard" id="dashboard">
  <div class="timeline">
    <div class="timeline-bar">
      <div class="timeline-step" id="step-spec"></div>
      <div class="timeline-step" id="step-review"></div>
      <div class="timeline-step" id="step-code"></div>
      <div class="timeline-step" id="step-test"></div>
    </div>
    <div class="timeline-labels"><span>Spec</span><span>Review</span><span>Code</span><span>Test</span></div>
  </div>
  <div class="stats">
    <div>Review: <span class="stat-value" id="review-rounds">0</span></div>
    <div>Turns: <span class="stat-value" id="turn-count">0</span></div>
    <div>Approved: <span class="stat-value" id="approved">-</span></div>
  </div>
  <div class="grid">
    <div class="agent-card" id="card-architect">
      <div class="agent-header"><div class="agent-icon icon-architect">A</div><div><div class="agent-name">Architect</div><div class="agent-role">Writes the spec</div></div></div>
      <div class="agent-status" id="status-architect">Waiting...</div>
      <ul class="turn-list" id="turns-architect"></ul>
    </div>
    <div class="agent-card" id="card-reviewer">
      <div class="agent-header"><div class="agent-icon icon-reviewer">R</div><div><div class="agent-name">Reviewer</div><div class="agent-role">Challenges the spec</div></div></div>
      <div class="agent-status" id="status-reviewer">Waiting...</div>
      <ul class="turn-list" id="turns-reviewer"></ul>
    </div>
    <div class="agent-card" id="card-coder">
      <div class="agent-header"><div class="agent-icon icon-coder">C</div><div><div class="agent-name">Coder</div><div class="agent-role">Builds the spec</div></div></div>
      <div class="agent-status" id="status-coder">Waiting...</div>
      <ul class="turn-list" id="turns-coder"></ul>
    </div>
    <div class="agent-card" id="card-tester">
      <div class="agent-header"><div class="agent-icon icon-tester">T</div><div><div class="agent-name">Tester</div><div class="agent-role">Verifies requirements</div></div></div>
      <div class="agent-status" id="status-tester">Waiting...</div>
      <ul class="turn-list" id="turns-tester"></ul>
    </div>
  </div>
</div>

<script>
let sending = false;

function addMessage(role, text) {
  const area = document.getElementById('chat-area');
  const div = document.createElement('div');
  div.className = 'msg msg-' + role;
  div.innerHTML = '<div class="msg-label">' + (role === 'user' ? 'You' : 'Spec Squad') + '</div>' +
                  '<div class="msg-bubble">' + escapeHtml(text) + '</div>';
  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
}

function escapeHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

async function sendMessage() {
  if (sending) return;
  const input = document.getElementById('user-input');
  const text = input.value.trim();
  if (!text) return;

  sending = true;
  input.value = '';
  document.getElementById('send-btn').disabled = true;
  addMessage('user', text);

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text}),
    });
    const data = await res.json();

    if (data.response) {
      addMessage('assistant', data.response);
    }

    if (data.discovery_complete) {
      // Transition to dashboard
      addMessage('assistant', 'Starting the squad now...');
      setTimeout(() => {
        document.getElementById('chat-container').classList.add('hidden');
        document.getElementById('dashboard').classList.add('active');
        pollDashboard();
      }, 1500);
    }
  } catch (e) {
    addMessage('assistant', 'Error: ' + e.message);
  }

  sending = false;
  document.getElementById('send-btn').disabled = false;
  input.focus();
}

document.getElementById('user-input').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

// Dashboard polling
const PHASE_ORDER = {spec:0, review:1, code:2, test:3, done:4};

function updateDashboard(data) {
  const state = data.squad_state || {};
  if (!state.phase) return;

  const badge = document.getElementById('phase-badge');
  badge.textContent = state.phase.toUpperCase();
  badge.className = 'badge badge-' + state.phase;

  const idx = PHASE_ORDER[state.phase] || 0;
  ['spec','review','code','test'].forEach((p,i) => {
    const el = document.getElementById('step-' + p);
    el.className = 'timeline-step';
    if (i < idx || state.phase === 'done') el.classList.add('complete');
    else if (i === idx && state.phase !== 'done') el.classList.add('active');
  });

  document.getElementById('review-rounds').textContent = state.review_round || 0;
  document.getElementById('turn-count').textContent = (state.turns||[]).length;
  document.getElementById('approved').textContent = state.approved ? 'Yes' : 'No';

  const roleMap = {architect:[], reviewer:[], coder:[], tester:[]};
  (state.turns||[]).forEach(t => { if (roleMap[t.role]) roleMap[t.role].push(t); });
  const last = state.turns?.length ? state.turns[state.turns.length-1] : null;

  Object.entries(roleMap).forEach(([role, turns]) => {
    const card = document.getElementById('card-' + role);
    const statusEl = document.getElementById('status-' + role);
    const listEl = document.getElementById('turns-' + role);
    card.className = 'agent-card';
    if (data.squad_running && last?.role === role) card.classList.add('active');
    if (turns.length > 0) {
      const lt = turns[turns.length-1];
      const sig = lt.signal;
      if (sig?.verdict === 'APPROVED' || sig?.status === 'build_complete' || sig?.verdict === 'PASSED') card.classList.add('done');
      if (sig) {
        if (sig.verdict === 'APPROVED') { statusEl.textContent = 'APPROVED (' + (sig.confidence||'?') + ')'; statusEl.className = 'agent-status success'; }
        else if (sig.verdict === 'REVISE') { statusEl.textContent = 'REVISE (' + (sig.issues?.length||0) + ' issues)'; statusEl.className = 'agent-status warning'; }
        else if (sig.status === 'spec_complete') { statusEl.textContent = 'Spec done (' + (sig.tasks||'?') + ' tasks)'; statusEl.className = 'agent-status success'; }
        else if (sig.status === 'revision_complete') { statusEl.textContent = 'Revised'; statusEl.className = 'agent-status success'; }
        else if (sig.status === 'build_complete') { statusEl.textContent = 'Built (' + (sig.tasks_done||'?') + '/' + (sig.tasks_total||'?') + ')'; statusEl.className = 'agent-status success'; }
        else if (sig.verdict === 'PASSED') { statusEl.textContent = 'PASSED'; statusEl.className = 'agent-status success'; }
        else { statusEl.textContent = JSON.stringify(sig).substring(0,80); statusEl.className = 'agent-status working'; }
      }
    }
    listEl.innerHTML = '';
    turns.forEach(t => {
      const li = document.createElement('li');
      const ph = document.createElement('span');
      ph.textContent = t.phase + (t.round ? ' #'+t.round : '');
      const sg = document.createElement('span');
      if (t.signal) {
        const v = t.signal.verdict || t.signal.status || '';
        sg.textContent = v;
        sg.className = v === 'APPROVED' || v === 'PASSED' ? 'signal-approved' : v === 'REVISE' ? 'signal-revise' : 'signal-complete';
      }
      li.appendChild(ph); li.appendChild(sg); listEl.appendChild(li);
    });
  });
}

async function pollDashboard() {
  try {
    const res = await fetch('/api/state');
    if (res.ok) updateDashboard(await res.json());
  } catch(e) {}
  setTimeout(pollDashboard, 2000);
}

// If starting in dashboard mode
fetch('/api/state').then(r => r.json()).then(data => {
  if (data.phase !== 'discovery') {
    document.getElementById('chat-container').classList.add('hidden');
    document.getElementById('dashboard').classList.add('active');
    pollDashboard();
  }
});
</script>
</body>
</html>"""


# ── HTTP Handler ─────────────────────────────────────────────────────────────

class SquadHandler(http.server.BaseHTTPRequestHandler):
    workspace_root: Path = None
    workspace: Path = None

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve_html(CHAT_PAGE)
        elif self.path == "/api/state":
            self._serve_state()
        elif self.path == "/api/events":
            self._serve_sse()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/chat":
            self._handle_chat()
        else:
            self.send_error(404)

    def _serve_html(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _serve_state(self):
        data = {}
        with _lock:
            data["phase"] = _state["phase"]
            data["squad_running"] = _state["squad_running"]
            data["error"] = _state["error"]
            data["workspace"] = str(_state.get("workspace") or self.workspace or "")

        ws = _state.get("workspace") or self.workspace
        if ws:
            data["squad_state"] = get_squad_state(ws)
        self._send_json(data)

    def _serve_sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        try:
            while True:
                try:
                    data = _sse_queue.get(timeout=30)
                    self.wfile.write(f"data: {data}\n\n".encode())
                    self.wfile.flush()
                except queue.Empty:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _handle_chat(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        try:
            params = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"})
            return

        user_msg = params.get("message", "").strip()
        if not user_msg:
            self._send_json({"error": "Empty message"})
            return

        # Run discovery turn
        ws = _state.get("workspace") or self.workspace
        try:
            response = _run_async_sync(run_discovery_turn, user_msg, ws)
        except Exception as e:
            self._send_json({"error": str(e)})
            return

        # Check if discovery is complete
        discovery_complete = False
        if "DISCOVERY_COMPLETE" in response:
            # Extract structured data
            match = re.search(r'```json\s*\n({[^`]*})\s*\n```', response, re.DOTALL)
            if match:
                try:
                    project_data = json.loads(match.group(1))
                    ws_name = project_data.get("workspace_name", "new-project")

                    # Create workspace
                    ws_root = self.workspace_root or Path.home() / "Documents" / "Workspace"
                    workspace = ws_root / ws_name
                    workspace.mkdir(parents=True, exist_ok=True)
                    (workspace / "openspec").mkdir(exist_ok=True)

                    with _lock:
                        _state["workspace"] = workspace
                        _state["phase"] = "spec"
                    type(self).workspace = workspace

                    # Build project description
                    desc = "\n".join(f"{k}: {v}" for k, v in project_data.items() if v)

                    # Launch squad in background
                    plan_only = False  # default full build
                    t = threading.Thread(
                        target=_run_async,
                        args=(run_squad(workspace, desc, plan_only),),
                        daemon=True,
                    )
                    t.start()

                    discovery_complete = True
                    # Clean the response to remove the JSON block
                    response = response.split("DISCOVERY_COMPLETE")[0].strip()
                    if not response:
                        response = "Got it! I have everything I need. Launching the squad now..."

                except (json.JSONDecodeError, KeyError) as e:
                    response += f"\n\n(Discovery parse error: {e})"

        self._send_json({
            "response": response,
            "discovery_complete": discovery_complete,
        })

    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def log_message(self, *args):
        pass


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Spec Squad (Agent SDK)")
    parser.add_argument("-w", "--workspace", help="Existing workspace (skip discovery)")
    parser.add_argument("--workspace-root", help="Root for new workspaces")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()

    ws_root = Path(args.workspace_root) if args.workspace_root else Path.home() / "Documents" / "Workspace"
    workspace = Path(args.workspace).resolve() if args.workspace else None

    if workspace:
        with _lock:
            _state["workspace"] = workspace
            if (workspace / SQUAD_STATE_FILE).exists():
                _state["phase"] = "spec"  # resume dashboard

    handler = type("H", (SquadHandler,), {"workspace_root": ws_root, "workspace": workspace})

    server = http.server.HTTPServer(("127.0.0.1", args.port), handler)
    url = f"http://localhost:{args.port}"
    print(f"Spec Squad (Agent SDK): {url}")
    if workspace:
        print(f"Workspace: {workspace}")
    print("Press Ctrl+C to stop\n")

    if not args.no_open:
        import webbrowser
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
