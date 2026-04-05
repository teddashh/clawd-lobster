"""
clawd_lobster.pages — HTML page templates (inline strings).

All web UI pages are defined here as plain strings with embedded CSS/JS.
No template engine — keeps the zero-dependency promise.

Dark theme (#0d1117), consistent with spec-squad-sdk.py design.
Each page is self-contained with inline CSS + JS, no external CDN.
"""

# ── Shared CSS fragment ────────────────────────────────────────────────────

_BASE_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
       background:#0d1117; color:#c9d1d9; min-height:100vh; }
a { color:#58a6ff; text-decoration:none; }
a:hover { text-decoration:underline; }
header { background:#161b22; border-bottom:1px solid #30363d;
         padding:16px 24px; display:flex; align-items:center;
         justify-content:space-between; }
header h1 { font-size:20px; font-weight:600; }
header h1 span { color:#58a6ff; }
.badge { padding:3px 10px; border-radius:10px; font-size:12px;
         font-weight:600; text-transform:uppercase; }
.container { max-width:960px; margin:0 auto; padding:32px 24px; }
.btn { padding:10px 20px; border:none; border-radius:8px;
       color:#fff; font-weight:600; cursor:pointer; font-size:14px; }
.btn-primary { background:#238636; }
.btn-primary:hover { background:#2ea043; }
.btn-secondary { background:#30363d; }
.btn-secondary:hover { background:#484f58; }
.btn:disabled { opacity:0.5; cursor:not-allowed; }
.card { background:#161b22; border:1px solid #30363d;
        border-radius:12px; padding:20px; }
input[type=text], select { padding:10px 14px; background:#0d1117;
  border:1px solid #30363d; border-radius:8px; color:#c9d1d9;
  font-size:14px; width:100%; }
input[type=text]:focus, select:focus { outline:none; border-color:#58a6ff; }
"""

# ── HOME_PAGE ──────────────────────────────────────────────────────────────

HOME_PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>clawd-lobster</title>
<script>
fetch('/api/status').then(r=>r.json()).then(d=>{
  window.location.href = d.first_time ? '/onboarding' : '/workspaces';
}).catch(()=>{ window.location.href = '/onboarding'; });
</script></head>
<body style="background:#0d1117;color:#c9d1d9;font-family:system-ui;
  display:flex;align-items:center;justify-content:center;height:100vh;">
<p>Loading...</p></body></html>"""


# ── ONBOARDING_PAGE ────────────────────────────────────────────────────────

ONBOARDING_PAGE = (
    """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>clawd-lobster -- Setup</title>
<style>"""
    + _BASE_CSS
    + """
.wizard { max-width:640px; margin:48px auto; padding:0 24px; }
.step { display:none; }
.step.active { display:block; }
.progress { display:flex; gap:4px; margin-bottom:32px; }
.progress-dot { flex:1; height:6px; border-radius:3px; background:#21262d; }
.progress-dot.done { background:#56d364; }
.progress-dot.current { background:#58a6ff; }
h2 { font-size:22px; margin-bottom:16px; }
.check-list { list-style:none; margin:16px 0; }
.check-list li { padding:10px 0; border-bottom:1px solid #21262d;
  display:flex; justify-content:space-between; align-items:center; }
.check-ok { color:#56d364; font-weight:600; }
.check-fail { color:#f85149; font-weight:600; }
.check-opt { color:#8b949e; }
.persona-grid { display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px;
  margin:20px 0; }
.persona-card { padding:20px 16px; border:2px solid #30363d; border-radius:12px;
  cursor:pointer; text-align:center; transition:border-color 0.2s; }
.persona-card:hover { border-color:#58a6ff; }
.persona-card.selected { border-color:#58a6ff; background:#161b22; }
.persona-card h3 { font-size:16px; margin-bottom:4px; }
.persona-card p { color:#8b949e; font-size:13px; }
.field-group { margin:16px 0; }
.field-group label { display:block; font-size:14px; margin-bottom:6px;
  color:#8b949e; }
.step-actions { margin-top:24px; display:flex; gap:12px; justify-content:flex-end; }
.welcome { text-align:center; padding:32px 0; }
.welcome h2 { font-size:28px; color:#56d364; }
.welcome p { color:#8b949e; margin:12px 0; font-size:16px; }
</style></head><body>
<header><h1><span>clawd-lobster</span> Setup</h1></header>

<div class="wizard">
  <div class="progress">
    <div class="progress-dot current" id="dot-0"></div>
    <div class="progress-dot" id="dot-1"></div>
    <div class="progress-dot" id="dot-2"></div>
    <div class="progress-dot" id="dot-3"></div>
  </div>

  <!-- Step 0: Prerequisites -->
  <div class="step active" id="step-0">
    <h2>Prerequisites Check</h2>
    <p style="color:#8b949e">Checking your system...</p>
    <ul class="check-list" id="prereq-list"></ul>
    <div class="step-actions">
      <button class="btn btn-primary" id="prereq-next" disabled
        onclick="goStep(1)">Next</button>
    </div>
  </div>

  <!-- Step 1: Auth -->
  <div class="step" id="step-1">
    <h2>Claude Authentication</h2>
    <p style="color:#8b949e">Make sure Claude CLI is authenticated.</p>
    <div class="card" style="margin:20px 0;text-align:center;padding:32px">
      <p id="auth-status" style="margin-bottom:16px">Checking...</p>
      <button class="btn btn-primary" id="auth-btn"
        onclick="window.open('https://console.anthropic.com','_blank')"
        style="display:none">Open Anthropic Console</button>
    </div>
    <div class="step-actions">
      <button class="btn btn-secondary" onclick="goStep(0)">Back</button>
      <button class="btn btn-primary" onclick="goStep(2)">Next</button>
    </div>
  </div>

  <!-- Step 2: Persona -->
  <div class="step" id="step-2">
    <h2>How do you work?</h2>
    <p style="color:#8b949e">This helps us tailor the experience.</p>
    <div class="persona-grid">
      <div class="persona-card" onclick="pickPersona('noob',this)">
        <h3>Guided</h3>
        <p>New to AI dev. Show me everything.</p>
      </div>
      <div class="persona-card" onclick="pickPersona('expert',this)">
        <h3>Expert</h3>
        <p>I know what I'm doing. Less hand-holding.</p>
      </div>
      <div class="persona-card" onclick="pickPersona('tech',this)">
        <h3>Technical</h3>
        <p>I want full control and raw output.</p>
      </div>
    </div>
    <div class="step-actions">
      <button class="btn btn-secondary" onclick="goStep(1)">Back</button>
      <button class="btn btn-primary" id="persona-next" disabled
        onclick="goStep(3)">Next</button>
    </div>
  </div>

  <!-- Step 3: First Workspace -->
  <div class="step" id="step-3">
    <h2>Create Your First Workspace</h2>
    <div class="field-group">
      <label>Workspace name (kebab-case)</label>
      <input type="text" id="ws-name" placeholder="my-first-project"
        oninput="validateWsName()">
      <p id="ws-name-err" style="color:#f85149;font-size:13px;margin-top:4px"></p>
    </div>
    <div class="field-group">
      <label>Workspace root directory</label>
      <input type="text" id="ws-root" placeholder="~/Documents/Workspace">
    </div>
    <div class="step-actions">
      <button class="btn btn-secondary" onclick="goStep(2)">Back</button>
      <button class="btn btn-primary" id="finish-btn" disabled
        onclick="finishSetup()">Finish Setup</button>
    </div>
  </div>

  <!-- Step 4: Done -->
  <div class="step" id="step-done">
    <div class="welcome">
      <h2>Ready!</h2>
      <p>Your workspace has been created.</p>
      <div style="margin:24px 0;display:flex;gap:12px;justify-content:center">
        <a href="/workspaces" class="btn btn-secondary">View Workspaces</a>
        <a href="/squad" class="btn btn-primary">Launch Spec Squad</a>
      </div>
    </div>
  </div>
</div>

<script>
let persona = '';
const KEBAB = /^[a-z0-9]+(-[a-z0-9]+)*$/;

function goStep(n) {
  document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
  const el = document.getElementById('step-' + n);
  if (el) el.classList.add('active');
  for (let i = 0; i < 4; i++) {
    const d = document.getElementById('dot-' + i);
    d.className = 'progress-dot' + (i < n ? ' done' : i === n ? ' current' : '');
  }
}

function pickPersona(p, el) {
  persona = p;
  document.querySelectorAll('.persona-card').forEach(c =>
    c.classList.remove('selected'));
  el.classList.add('selected');
  document.getElementById('persona-next').disabled = false;
}

function validateWsName() {
  const v = document.getElementById('ws-name').value.trim();
  const err = document.getElementById('ws-name-err');
  const ok = KEBAB.test(v);
  err.textContent = v && !ok ? 'Must be kebab-case (e.g. my-project)' : '';
  document.getElementById('finish-btn').disabled = !ok;
}

async function finishSetup() {
  const name = document.getElementById('ws-name').value.trim();
  const root = document.getElementById('ws-root').value.trim();
  const btn = document.getElementById('finish-btn');
  btn.disabled = true;
  btn.textContent = 'Setting up...';
  try {
    const res = await fetch('/api/onboarding/complete', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({persona, workspace_name: name, workspace_root: root})
    });
    const data = await res.json();
    if (data.ok) {
      document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
      document.getElementById('step-done').classList.add('active');
      document.querySelectorAll('.progress-dot').forEach(d =>
        d.className = 'progress-dot done');
    } else {
      btn.textContent = 'Retry';
      btn.disabled = false;
      alert(data.error || 'Setup failed');
    }
  } catch (e) {
    btn.textContent = 'Retry';
    btn.disabled = false;
    alert('Connection error: ' + e.message);
  }
}

// Auto-run prerequisite check on load
(async function() {
  try {
    const res = await fetch('/api/onboarding/check', {method:'POST'});
    const data = await res.json();
    const list = document.getElementById('prereq-list');
    let allOk = true;
    const items = data.checks || [];
    items.forEach(c => {
      const li = document.createElement('li');
      const name = document.createElement('span');
      name.textContent = c.name + (c.version ? ' (' + c.version + ')' : '');
      const st = document.createElement('span');
      if (c.ok) { st.textContent = 'OK'; st.className = 'check-ok'; }
      else if (c.optional) { st.textContent = 'Optional'; st.className = 'check-opt'; }
      else { st.textContent = 'Missing'; st.className = 'check-fail'; allOk = false; }
      li.appendChild(name); li.appendChild(st); list.appendChild(li);
    });
    document.getElementById('prereq-next').disabled = !allOk;
    // Also set auth status
    const claude = items.find(c => c.name === 'claude');
    const authEl = document.getElementById('auth-status');
    if (claude && claude.ok) {
      authEl.textContent = 'Claude CLI detected (' + (claude.version||'') + ')';
      authEl.style.color = '#56d364';
    } else {
      authEl.textContent = 'Claude CLI not found. Install it first.';
      authEl.style.color = '#f85149';
      document.getElementById('auth-btn').style.display = 'inline-block';
    }
    // Set default workspace root
    if (data.default_root) {
      document.getElementById('ws-root').value = data.default_root;
    }
  } catch(e) {
    document.getElementById('prereq-list').innerHTML =
      '<li>Error checking prerequisites: ' + e.message + '</li>';
  }
})();
</script></body></html>"""
)


# ── WORKSPACES_PAGE ────────────────────────────────────────────────────────

WORKSPACES_PAGE = (
    """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>clawd-lobster -- Workspaces</title>
<style>"""
    + _BASE_CSS
    + """
.top-bar { display:flex; justify-content:space-between; align-items:center;
  margin-bottom:24px; }
.ws-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
  gap:16px; }
.ws-card { transition:border-color 0.2s; }
.ws-card:hover { border-color:#58a6ff; }
.ws-name { font-size:18px; font-weight:600; margin-bottom:4px; }
.ws-path { color:#8b949e; font-size:13px; word-break:break-all; }
.ws-meta { display:flex; gap:16px; margin-top:12px; font-size:13px; color:#8b949e; }
.ws-actions { margin-top:12px; display:flex; gap:8px; }
.ws-badge { padding:2px 8px; border-radius:6px; font-size:11px; font-weight:600; }
.ws-badge-active { background:#1f5f2d; color:#56d364; }
.ws-badge-idle { background:#21262d; color:#8b949e; }
.empty { text-align:center; padding:64px 0; color:#8b949e; }
.empty h2 { color:#c9d1d9; margin-bottom:8px; }
.modal-bg { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6);
  z-index:100; align-items:center; justify-content:center; }
.modal-bg.open { display:flex; }
.modal { background:#161b22; border:1px solid #30363d; border-radius:12px;
  padding:24px; width:400px; max-width:90vw; }
.modal h3 { margin-bottom:16px; }
.modal .field-group { margin-bottom:12px; }
.modal .field-group label { display:block; font-size:13px; color:#8b949e;
  margin-bottom:4px; }
</style></head><body>
<header>
  <h1><span>clawd-lobster</span></h1>
  <nav style="display:flex;gap:16px;align-items:center">
    <a href="/workspaces">Workspaces</a>
    <a href="/squad">Squad</a>
  </nav>
</header>

<div class="container">
  <div class="top-bar">
    <h2>Workspaces</h2>
    <button class="btn btn-primary" onclick="openModal()">+ New Workspace</button>
  </div>
  <div id="ws-grid" class="ws-grid"></div>
  <div id="empty" class="empty" style="display:none">
    <h2>No workspaces yet</h2>
    <p>Create your first workspace to get started.</p>
  </div>
</div>

<div class="modal-bg" id="modal-bg" onclick="closeModal(event)">
  <div class="modal" onclick="event.stopPropagation()">
    <h3>New Workspace</h3>
    <div class="field-group">
      <label>Name (kebab-case)</label>
      <input type="text" id="new-ws-name" placeholder="my-project">
    </div>
    <div class="field-group">
      <label>Domain</label>
      <select id="new-ws-domain">
        <option value="personal">Personal</option>
        <option value="work">Work</option>
        <option value="hybrid">Hybrid</option>
      </select>
    </div>
    <div class="field-group">
      <label>Description (optional)</label>
      <input type="text" id="new-ws-desc" placeholder="What is this project about?">
    </div>
    <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:16px">
      <button class="btn btn-secondary" onclick="document.getElementById('modal-bg').classList.remove('open')">Cancel</button>
      <button class="btn btn-primary" id="create-btn" onclick="createWorkspace()">Create</button>
    </div>
    <p id="create-err" style="color:#f85149;font-size:13px;margin-top:8px"></p>
  </div>
</div>

<script>
function openModal() { document.getElementById('modal-bg').classList.add('open'); }
function closeModal(e) { if(e.target===e.currentTarget) e.target.classList.remove('open'); }

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function renderWorkspaces(list) {
  const grid = document.getElementById('ws-grid');
  const empty = document.getElementById('empty');
  grid.innerHTML = '';
  if (!list.length) { empty.style.display = 'block'; return; }
  empty.style.display = 'none';
  list.forEach(w => {
    const hasSquad = w.squad_phase && w.squad_phase !== 'none';
    const badge = hasSquad
      ? '<span class="ws-badge ws-badge-active">' + escHtml(w.squad_phase) + '</span>'
      : '<span class="ws-badge ws-badge-idle">idle</span>';
    grid.innerHTML += '<div class="card ws-card">'
      + '<div style="display:flex;justify-content:space-between;align-items:start">'
      + '<div class="ws-name">' + escHtml(w.id || w.name || '') + '</div>' + badge + '</div>'
      + '<div class="ws-path">' + escHtml(w.path || '') + '</div>'
      + '<div class="ws-meta">'
      + '<span>Domain: ' + escHtml(w.domain || '-') + '</span>'
      + '<span>Created: ' + escHtml(w.created || '-') + '</span>'
      + '</div>'
      + '<div class="ws-actions">'
      + '<a href="/squad?workspace=' + encodeURIComponent(w.path || '') + '" class="btn btn-primary" style="font-size:13px;padding:6px 14px">Launch Squad</a>'
      + '</div></div>';
  });
}

async function createWorkspace() {
  const name = document.getElementById('new-ws-name').value.trim();
  const domain = document.getElementById('new-ws-domain').value;
  const desc = document.getElementById('new-ws-desc').value.trim();
  const err = document.getElementById('create-err');
  const btn = document.getElementById('create-btn');
  err.textContent = '';
  if (!name) { err.textContent = 'Name is required'; return; }
  btn.disabled = true; btn.textContent = 'Creating...';
  try {
    const res = await fetch('/api/workspaces/create', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name, domain, description: desc})
    });
    const data = await res.json();
    if (data.ok) {
      document.getElementById('modal-bg').classList.remove('open');
      loadWorkspaces();
    } else {
      err.textContent = data.error || 'Failed to create workspace';
    }
  } catch(e) { err.textContent = e.message; }
  btn.disabled = false; btn.textContent = 'Create';
}

async function loadWorkspaces() {
  try {
    const res = await fetch('/api/workspaces');
    const data = await res.json();
    renderWorkspaces(data.workspaces || []);
  } catch(e) {
    document.getElementById('ws-grid').innerHTML =
      '<p style="color:#f85149">Error loading workspaces</p>';
  }
}

loadWorkspaces();
</script></body></html>"""
)


# ── SQUAD_PAGE ─────────────────────────────────────────────────────────────

SQUAD_PAGE = (
    """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>clawd-lobster -- Spec Squad</title>
<style>"""
    + _BASE_CSS
    + """
body { height:100vh; display:flex; flex-direction:column; }
.main { flex:1; display:flex; overflow:hidden; }
/* Chat panel (left) */
.chat-panel { width:400px; display:flex; flex-direction:column;
  border-right:1px solid #30363d; }
.chat-area { flex:1; overflow-y:auto; padding:16px; }
.msg { margin-bottom:12px; max-width:90%; }
.msg-user { margin-left:auto; }
.msg-assistant { margin-right:auto; }
.msg-bubble { padding:10px 14px; border-radius:10px; font-size:14px;
  line-height:1.5; white-space:pre-wrap; }
.msg-user .msg-bubble { background:#1f6feb; color:#fff;
  border-bottom-right-radius:4px; }
.msg-assistant .msg-bubble { background:#161b22; border:1px solid #30363d;
  border-bottom-left-radius:4px; }
.msg-label { font-size:11px; color:#8b949e; margin-bottom:3px; }
.msg-user .msg-label { text-align:right; }
.input-area { background:#161b22; border-top:1px solid #30363d; padding:12px; }
.input-row { display:flex; gap:8px; }
.input-row input { flex:1; }
/* Dashboard panel (right) */
.dash-panel { flex:1; overflow-y:auto; padding:24px; }
.timeline { margin-bottom:16px; }
.timeline-bar { display:flex; gap:4px; margin-bottom:6px; }
.timeline-step { flex:1; height:8px; border-radius:4px; background:#21262d;
  transition:background 0.3s; }
.timeline-step.complete { background:#56d364; }
.timeline-step.active { background:#58a6ff; animation:pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
.timeline-labels { display:flex; justify-content:space-between;
  font-size:12px; color:#8b949e; }
.stats { display:flex; gap:20px; margin-bottom:16px; font-size:13px;
  color:#8b949e; }
.stat-value { color:#c9d1d9; font-weight:600; }
.agent-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.agent-card { border:1px solid #30363d; transition:border-color 0.3s; }
.agent-card.active { border-color:#58a6ff;
  box-shadow:0 0 15px rgba(88,166,255,0.1); }
.agent-card.done { border-color:#56d364; }
.agent-header { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.agent-icon { width:40px; height:40px; border-radius:8px; display:flex;
  align-items:center; justify-content:center; font-size:18px;
  font-weight:700; color:#fff; }
.icon-architect { background:#1f6feb; }
.icon-reviewer { background:#8957e5; }
.icon-coder { background:#238636; }
.icon-tester { background:#9e6a03; }
.agent-name { font-size:16px; font-weight:600; }
.agent-role { color:#8b949e; font-size:12px; }
.agent-status { padding:6px 10px; background:#0d1117; border-radius:6px;
  font-size:12px; color:#8b949e; min-height:32px; margin-bottom:8px; }
.agent-status.working { color:#58a6ff; }
.agent-status.success { color:#56d364; }
.agent-status.warning { color:#e3b341; }
.turn-list { list-style:none; font-size:12px; max-height:120px;
  overflow-y:auto; }
.turn-list li { padding:3px 0; border-bottom:1px solid #21262d;
  display:flex; justify-content:space-between; }
.signal-approved { color:#56d364; font-weight:500; }
.signal-revise { color:#e3b341; font-weight:500; }
.signal-complete { color:#58a6ff; font-weight:500; }
.empty-dash { text-align:center; padding:60px 20px; color:#8b949e; }
.empty-dash h3 { color:#c9d1d9; margin-bottom:8px; }
</style></head><body>

<header>
  <h1><span>Spec Squad</span></h1>
  <div style="display:flex;align-items:center;gap:16px">
    <a href="/workspaces" style="font-size:14px">Workspaces</a>
    <span class="badge" id="phase-badge" style="background:#21262d;color:#8b949e">
      READY</span>
  </div>
</header>

<div class="main">
  <!-- Chat -->
  <div class="chat-panel" id="chat-panel">
    <div class="chat-area" id="chat-area"></div>
    <div class="input-area">
      <div class="input-row">
        <input type="text" id="user-input"
          placeholder="Describe what you want to build..." autofocus>
        <button class="btn btn-primary" id="send-btn"
          onclick="sendMessage()">Send</button>
      </div>
    </div>
  </div>

  <!-- Dashboard -->
  <div class="dash-panel" id="dash-panel">
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
      <div>Reviews: <span class="stat-value" id="review-rounds">0</span></div>
      <div>Turns: <span class="stat-value" id="turn-count">0</span></div>
      <div>Approved: <span class="stat-value" id="approved">-</span></div>
    </div>
    <div class="agent-grid">
      <div class="card agent-card" id="card-architect">
        <div class="agent-header"><div class="agent-icon icon-architect">A</div>
          <div><div class="agent-name">Architect</div>
          <div class="agent-role">Writes the spec</div></div></div>
        <div class="agent-status" id="status-architect">Waiting...</div>
        <ul class="turn-list" id="turns-architect"></ul>
      </div>
      <div class="card agent-card" id="card-reviewer">
        <div class="agent-header"><div class="agent-icon icon-reviewer">R</div>
          <div><div class="agent-name">Reviewer</div>
          <div class="agent-role">Challenges the spec</div></div></div>
        <div class="agent-status" id="status-reviewer">Waiting...</div>
        <ul class="turn-list" id="turns-reviewer"></ul>
      </div>
      <div class="card agent-card" id="card-coder">
        <div class="agent-header"><div class="agent-icon icon-coder">C</div>
          <div><div class="agent-name">Coder</div>
          <div class="agent-role">Builds the spec</div></div></div>
        <div class="agent-status" id="status-coder">Waiting...</div>
        <ul class="turn-list" id="turns-coder"></ul>
      </div>
      <div class="card agent-card" id="card-tester">
        <div class="agent-header"><div class="agent-icon icon-tester">T</div>
          <div><div class="agent-name">Tester</div>
          <div class="agent-role">Verifies requirements</div></div></div>
        <div class="agent-status" id="status-tester">Waiting...</div>
        <ul class="turn-list" id="turns-tester"></ul>
      </div>
    </div>
  </div>
</div>

<script>
let sending = false;
const PHASE_ORDER = {spec:0, review:1, code:2, test:3, done:4};
const workspace = new URLSearchParams(location.search).get('workspace') || '';

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function addMsg(role, text) {
  const area = document.getElementById('chat-area');
  const d = document.createElement('div');
  d.className = 'msg msg-' + role;
  d.innerHTML = '<div class="msg-label">' + (role==='user'?'You':'Spec Squad')
    + '</div><div class="msg-bubble">' + escHtml(text) + '</div>';
  area.appendChild(d);
  area.scrollTop = area.scrollHeight;
}

async function sendMessage() {
  if (sending) return;
  const input = document.getElementById('user-input');
  const text = input.value.trim();
  if (!text) return;
  sending = true;
  input.value = '';
  document.getElementById('send-btn').disabled = true;
  addMsg('user', text);
  try {
    const res = await fetch('/api/squad/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text, workspace: workspace})
    });
    const data = await res.json();
    if (data.response) addMsg('assistant', data.response);
    if (data.discovery_complete) {
      addMsg('assistant', 'Starting the squad now...');
      setTimeout(startPolling, 1000);
    }
  } catch(e) { addMsg('assistant', 'Error: ' + e.message); }
  sending = false;
  document.getElementById('send-btn').disabled = false;
  input.focus();
}

document.getElementById('user-input').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

function updateDashboard(data) {
  const state = data.squad_state || {};
  if (!state.phase) return;
  const badge = document.getElementById('phase-badge');
  badge.textContent = state.phase.toUpperCase();
  badge.style.background = {spec:'#1f3a5f',review:'#3d1f5f',code:'#1f5f2d',
    test:'#5f4b1f',done:'#1f5f2d'}[state.phase] || '#21262d';
  badge.style.color = {spec:'#58a6ff',review:'#bc8cff',code:'#56d364',
    test:'#e3b341',done:'#56d364'}[state.phase] || '#8b949e';
  const idx = PHASE_ORDER[state.phase] || 0;
  ['spec','review','code','test'].forEach((p,i) => {
    const el = document.getElementById('step-' + p);
    el.className = 'timeline-step';
    if (i < idx || state.phase==='done') el.classList.add('complete');
    else if (i === idx && state.phase!=='done') el.classList.add('active');
  });
  document.getElementById('review-rounds').textContent = state.review_round||0;
  document.getElementById('turn-count').textContent = (state.turns||[]).length;
  document.getElementById('approved').textContent = state.approved?'Yes':'No';
  const rm = {architect:[],reviewer:[],coder:[],tester:[]};
  (state.turns||[]).forEach(t => { if(rm[t.role]) rm[t.role].push(t); });
  const last = state.turns?.length ? state.turns[state.turns.length-1] : null;
  Object.entries(rm).forEach(([role, turns]) => {
    const card = document.getElementById('card-' + role);
    const sEl = document.getElementById('status-' + role);
    const lEl = document.getElementById('turns-' + role);
    card.className = 'card agent-card';
    if (data.squad_running && last?.role===role) card.classList.add('active');
    if (turns.length) {
      const sig = turns[turns.length-1].signal;
      if (sig) {
        if (sig.verdict==='APPROVED') { sEl.textContent='APPROVED'; sEl.className='agent-status success'; card.classList.add('done'); }
        else if (sig.verdict==='REVISE') { sEl.textContent='REVISE ('+((sig.issues||[]).length)+')'; sEl.className='agent-status warning'; }
        else if (sig.status==='spec_complete') { sEl.textContent='Spec done'; sEl.className='agent-status success'; }
        else if (sig.status==='build_complete') { sEl.textContent='Built'; sEl.className='agent-status success'; card.classList.add('done'); }
        else if (sig.verdict==='PASSED') { sEl.textContent='PASSED'; sEl.className='agent-status success'; card.classList.add('done'); }
        else { sEl.textContent=JSON.stringify(sig).substring(0,60); sEl.className='agent-status working'; }
      }
    }
    lEl.innerHTML = '';
    turns.forEach(t => {
      const li = document.createElement('li');
      const ph = document.createElement('span');
      ph.textContent = t.phase + (t.round ? ' #'+t.round : '');
      const sg = document.createElement('span');
      if (t.signal) {
        const v = t.signal.verdict || t.signal.status || '';
        sg.textContent = v;
        sg.className = v==='APPROVED'||v==='PASSED' ? 'signal-approved'
          : v==='REVISE' ? 'signal-revise' : 'signal-complete';
      }
      li.appendChild(ph); li.appendChild(sg); lEl.appendChild(li);
    });
  });
}

let polling = false;
async function pollState() {
  try {
    const url = '/api/squad/state' + (workspace ? '?workspace='+encodeURIComponent(workspace) : '');
    const res = await fetch(url);
    if (res.ok) updateDashboard(await res.json());
  } catch(e) {}
  if (polling) setTimeout(pollState, 2000);
}
function startPolling() { if (!polling) { polling = true; pollState(); } }

// Check if squad is already running
fetch('/api/squad/state' + (workspace ? '?workspace='+encodeURIComponent(workspace) : ''))
  .then(r => r.json()).then(d => {
    if (d.squad_state && d.squad_state.phase && d.squad_state.phase !== 'discovery') {
      startPolling();
    }
  }).catch(() => {});
</script></body></html>"""
)
