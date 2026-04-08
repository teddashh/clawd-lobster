"""Server-rendered onboarding pages — the Escape Room visual layer.

This is the web half of the Agent-Guided onboarding. Claude Code is the
conversation half. Together they guide the user through setup.

Pages:
  /onboarding          → Skill Parade (foundations + skills)
  /onboarding/complete → Go Live celebration
"""

# ── Shared CSS theme ──────────────────────────────────────────────────────

_CSS = """
:root {
  --bg: #0d1117; --bg2: #161b22; --bg3: #21262d;
  --fg: #e6edf3; --fg2: #8b949e; --fg3: #484f58;
  --accent: #58a6ff; --green: #3fb950; --red: #f85149;
  --yellow: #d29922; --purple: #bc8cff; --orange: #f0883e;
  --radius: 12px; --gap: 16px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--fg); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; min-height: 100vh; }
a { color: var(--accent); text-decoration: none; }

.container { max-width: 900px; margin: 0 auto; padding: 24px var(--gap); }

/* Header */
.header { display: flex; align-items: center; gap: 12px; padding: 16px 0; border-bottom: 1px solid var(--bg3); margin-bottom: 24px; }
.header h1 { font-size: 1.4rem; font-weight: 600; }
.header .phase-badge { background: var(--bg3); color: var(--fg2); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; }
.header .phase-badge.active { background: var(--accent); color: #fff; }

/* Progress bar */
.progress-bar { display: flex; gap: 4px; margin-bottom: 32px; }
.progress-bar .step { flex: 1; height: 4px; border-radius: 2px; background: var(--bg3); transition: background 0.3s; }
.progress-bar .step.done { background: var(--green); }
.progress-bar .step.current { background: var(--accent); }
.progress-bar .step.failed { background: var(--red); }

/* Tier section */
.tier { margin-bottom: 32px; }
.tier-header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.tier-header h2 { font-size: 1.1rem; color: var(--fg2); font-weight: 500; }
.tier-header .count { background: var(--bg3); color: var(--fg2); padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; }

/* Skill card */
.skill-card { background: var(--bg2); border: 1px solid var(--bg3); border-radius: var(--radius); padding: 20px; margin-bottom: 12px; transition: border-color 0.2s; }
.skill-card.current { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent); }
.skill-card.done { border-color: var(--green); opacity: 0.85; }
.skill-card.failed { border-color: var(--red); }
.skill-card.skipped { opacity: 0.5; }

.skill-top { display: flex; align-items: flex-start; gap: 16px; }
.skill-icon { font-size: 2rem; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; background: var(--bg3); border-radius: 10px; flex-shrink: 0; }
.skill-info { flex: 1; }
.skill-info h3 { font-size: 1rem; font-weight: 600; margin-bottom: 4px; }
.skill-info .summary { color: var(--fg2); font-size: 0.85rem; line-height: 1.4; }
.skill-info .why { color: var(--fg3); font-size: 0.8rem; margin-top: 6px; font-style: italic; }

.skill-status { display: flex; align-items: center; gap: 6px; font-size: 0.8rem; font-weight: 500; }
.skill-status .dot { width: 8px; height: 8px; border-radius: 50%; }
.skill-status .dot.pending { background: var(--fg3); }
.skill-status .dot.running { background: var(--yellow); animation: pulse 1s infinite; }
.skill-status .dot.succeeded { background: var(--green); }
.skill-status .dot.failed { background: var(--red); }
.skill-status .dot.skipped { background: var(--fg3); }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }

/* Steps within a card */
.skill-steps { margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--bg3); }
.skill-steps .step-item { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 0.85rem; color: var(--fg2); }
.skill-steps .step-item .check { width: 16px; text-align: center; }
.skill-steps .step-item.done .check { color: var(--green); }
.skill-steps .step-item.running .check { color: var(--yellow); }
.skill-steps .step-item.failed .check { color: var(--red); }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid var(--bg3); border-radius: 8px; background: var(--bg2); color: var(--fg); font-size: 0.85rem; cursor: pointer; transition: all 0.15s; }
.btn:hover { border-color: var(--accent); color: var(--accent); }
.btn.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
.btn.primary:hover { background: #4a9aef; }
.btn.danger { border-color: var(--red); color: var(--red); }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* Controller banner */
.controller-banner { display: flex; align-items: center; justify-content: space-between; padding: 10px 16px; background: var(--bg2); border: 1px solid var(--bg3); border-radius: var(--radius); margin-bottom: 20px; font-size: 0.85rem; }
.controller-banner .holder { display: flex; align-items: center; gap: 6px; }
.controller-banner .holder .icon { font-size: 1.1rem; }

/* Mascot bubble */
.mascot { display: flex; align-items: flex-start; gap: 12px; background: var(--bg2); border: 1px solid var(--bg3); border-radius: var(--radius); padding: 16px; margin-bottom: 24px; }
.mascot img { width: 48px; height: 48px; border-radius: 10px; }
.mascot .bubble { flex: 1; color: var(--fg2); font-size: 0.9rem; line-height: 1.5; }
.mascot .bubble strong { color: var(--fg); }

/* Go Live */
.go-live { text-align: center; padding: 60px 20px; }
.go-live h1 { font-size: 2rem; margin-bottom: 12px; }
.go-live p { color: var(--fg2); font-size: 1.1rem; margin-bottom: 24px; }
.go-live .stats { display: flex; justify-content: center; gap: 32px; margin: 24px 0; }
.go-live .stat { text-align: center; }
.go-live .stat .num { font-size: 2rem; font-weight: 700; color: var(--green); }
.go-live .stat .label { font-size: 0.8rem; color: var(--fg2); }
"""

# ── Onboarding page ──────────────────────────────────────────────────────

ONBOARDING_PAGE = (
    "<!DOCTYPE html><html lang='en'><head>"
    "<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Clawd-Lobster Setup</title>"
    f"<style>{_CSS}</style>"
    "</head><body>"
    "<div class='container'>"

    # Header
    "<div class='header'>"
    "<span style='font-size:1.6rem'>🦞</span>"
    "<h1>Clawd-Lobster Setup</h1>"
    "<span class='phase-badge active' id='phase-badge'>Loading...</span>"
    "</div>"

    # Controller banner
    "<div class='controller-banner' id='controller-banner'>"
    "<div class='holder'><span class='icon'>🎮</span> <span id='ctrl-holder'>No controller</span></div>"
    "<div>"
    "<button class='btn' id='btn-acquire' onclick='acquireLease()'>Take Control</button>"
    "<button class='btn' id='btn-release' onclick='releaseLease()' style='display:none'>Release</button>"
    "</div>"
    "</div>"

    # Mascot
    "<div class='mascot' id='mascot'>"
    "<div style='font-size:2.5rem'>🦞</div>"
    "<div class='bubble'>"
    "<strong>Welcome!</strong> I'll walk you through setting up your AI development environment. "
    "Each skill below needs to be configured — we'll go through them one by one. "
    "You can also talk to Claude Code in the terminal for help!"
    "</div>"
    "</div>"

    # Progress bar (filled by JS)
    "<div class='progress-bar' id='progress-bar'></div>"

    # Skill cards container (filled by JS)
    "<div id='tiers-container'></div>"

    # Handoff banner
    "<div class='card' id='handoff-banner' style='display:none;text-align:center;border-color:var(--purple);margin-bottom:24px'>"
    "<p style='margin-bottom:12px;color:var(--fg2)'>Want Claude to help with the remaining setup? Launch Claude Code in your workspace.</p>"
    "<button class='btn primary' onclick='launchHandoff()' style='background:var(--purple);border-color:var(--purple)'>🤖 Launch Claude Code</button>"
    "<div id='handoff-result' style='margin-top:12px;font-size:0.85rem;color:var(--fg2);display:none'></div>"
    "</div>"

    # Actions
    "<div style='text-align:center;margin-top:32px;' id='actions'>"
    "<button class='btn primary' id='btn-complete' onclick='completeOnboarding()' disabled>Complete Setup</button>"
    "</div>"

    "</div>"

    # ── JavaScript ────────────────────────────────────────────────────────
    """<script>
const API = '';
let state = null;
let sessionId = null;
let leaseId = null;
let holder = null;

// ── Auth helper ──
function authHeaders() {
  const t = localStorage.getItem('cl-token') || '';
  return {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + t};
}

// ── Init ──
async function init() {
  // Try to load existing session
  let res = await fetch(API + '/api/onboarding/state');
  let data = await res.json();

  if (data.ok && data.state) {
    state = data.state;
    sessionId = state.session_id;
  } else {
    // Create new session
    res = await fetch(API + '/api/onboarding/session', {
      method: 'POST', headers: authHeaders(),
      body: JSON.stringify({lang: navigator.language.startsWith('zh') ? 'zh-TW' : 'en'})
    });
    data = await res.json();
    if (data.ok) {
      state = data.state;
      sessionId = data.session_id;
      localStorage.setItem('cl-token', data.token);
    }
  }
  render();
  startPolling();
}

// ── Render ──
function render() {
  if (!state) return;

  // Phase badge
  const badge = document.getElementById('phase-badge');
  const phaseNames = {
    foundations: 'Foundations', skills_required: 'Required Skills',
    skills_optional: 'Optional Skills', complete: 'Complete'
  };
  badge.textContent = phaseNames[state.phase] || state.phase;

  // Progress bar
  const items = state.items || [];
  const bar = document.getElementById('progress-bar');
  bar.innerHTML = items.map(i => {
    const cls = i.status === 'succeeded' ? 'done' : i.status === 'running' ? 'current' : i.status === 'failed' ? 'failed' : '';
    return '<div class="step ' + cls + '"></div>';
  }).join('');

  // Group by tier
  const tiers = {};
  items.forEach(i => {
    const t = i.tier || 'other';
    if (!tiers[t]) tiers[t] = [];
    tiers[t].push(i);
  });

  const tierOrder = ['foundation', 'required', 'optional', 'onetime'];
  const tierNames = {
    foundation: '🏗️ Foundations', required: '⚡ Required Skills',
    optional: '✨ Power Skills', onetime: '📦 One-Time Actions'
  };

  const container = document.getElementById('tiers-container');
  container.innerHTML = '';

  tierOrder.forEach(tier => {
    const items = tiers[tier];
    if (!items || items.length === 0) return;

    const done = items.filter(i => i.status === 'succeeded' || i.status === 'skipped').length;

    let html = '<div class="tier">';
    html += '<div class="tier-header">';
    html += '<h2>' + (tierNames[tier] || tier) + '</h2>';
    html += '<span class="count">' + done + '/' + items.length + '</span>';
    html += '</div>';

    items.forEach(i => {
      const cardClass = i.status === 'succeeded' ? 'done' : i.status === 'failed' ? 'failed' : i.status === 'running' ? 'current' : i.status === 'skipped' ? 'skipped' : '';
      const icon = i.facts && i.facts._icon ? i.facts._icon : getSkillIcon(i.id);
      const statusText = {pending: 'Pending', running: 'In Progress', succeeded: 'Done', failed: 'Failed', skipped: 'Skipped', blocked: 'Blocked'}[i.status] || i.status;

      html += '<div class="skill-card ' + cardClass + '" id="card-' + i.id.replace(/\\./g, '-') + '">';
      html += '<div class="skill-top">';
      html += '<div class="skill-icon">' + icon + '</div>';
      html += '<div class="skill-info">';
      html += '<h3>' + (i.title || i.id) + '</h3>';
      html += '<div class="summary">' + (i.summary || '') + '</div>';
      if (i.why_it_matters) html += '<div class="why">' + i.why_it_matters + '</div>';
      html += '</div>';
      html += '<div class="skill-status"><div class="dot ' + i.status + '"></div> ' + statusText + '</div>';
      html += '</div>';

      // Steps
      if (i.steps && i.steps.length > 0 && i.status !== 'skipped') {
        html += '<div class="skill-steps">';
        i.steps.forEach(s => {
          const fact = i.facts || {};
          const stepDone = (s.success_sets || []).every(f => fact[f]);
          const cls = stepDone ? 'done' : i.status === 'running' ? 'running' : '';
          const check = stepDone ? '✓' : i.status === 'running' ? '◌' : '○';
          html += '<div class="step-item ' + cls + '"><span class="check">' + check + '</span> ' + s.label + '</div>';
        });
        html += '</div>';
      }

      // Action buttons
      if (i.status === 'pending' || i.status === 'failed') {
        const canRun = !i.depends_on || i.depends_on.length === 0 || i.depends_on.every(d => {
          const dep = state.items.find(x => x.id === d);
          return dep && (dep.status === 'succeeded' || dep.status === 'skipped');
        });
        html += '<div style="margin-top:12px;display:flex;gap:8px">';
        if (canRun) {
          html += '<button class="btn primary" onclick="runSetup(\\'' + i.id + '\\')" ' + (leaseId ? '' : 'disabled') + '>Set Up</button>';
        } else {
          html += '<button class="btn" disabled>Waiting for dependencies</button>';
        }
        if (i.tier === 'optional' || i.tier === 'onetime') {
          html += '<button class="btn" onclick="skipItem(\\'' + i.id + '\\')" ' + (leaseId ? '' : 'disabled') + '>Skip</button>';
        }
        if (i.status === 'failed' && i.error) {
          html += '<div style="color:var(--red);font-size:0.8rem;margin-left:8px;align-self:center">' + i.error + '</div>';
        }
        html += '</div>';
      }

      html += '</div>';
    });

    html += '</div>';
    container.innerHTML += html;
  });

  // Complete button
  const allRequired = (state.items || []).filter(i => i.tier === 'foundation' || i.tier === 'required');
  const allDone = allRequired.every(i => i.status === 'succeeded' || i.status === 'skipped');
  document.getElementById('btn-complete').disabled = !allDone || !leaseId;

  // Controller banner
  updateControllerBanner();

  // Mascot message
  updateMascot();

  // Handoff banner
  checkHandoffBanner();
}

function getSkillIcon(id) {
  const icons = {
    'foundation.language': '🌐', 'foundation.claude_auth': '🔑',
    'foundation.hub': '📡', 'foundation.workspace_root': '📁',
    'memory-server': '🧠', 'spec': '📋', 'absorb': '🧽',
    'evolve': '🧬', 'heartbeat': '💓', 'deploy': '🚀',
    'codex-bridge': '🤖', 'gemini-bridge': '💎',
    'notebooklm-bridge': '📓', 'connect-odoo': '🏢',
    'migrate': '📦',
  };
  return icons[id] || '⚙️';
}

function updateMascot() {
  const m = document.getElementById('mascot');
  if (!state) return;
  const phase = state.phase;
  const msgs = {
    foundations: '<strong>Step 1:</strong> Let\\'s get the basics set up — language, authentication, and your workspace.',
    skills_required: '<strong>Core Skills:</strong> Now we\\'ll install the essential skills your AI needs. Memory first!',
    skills_optional: '<strong>Power Skills:</strong> These are optional but powerful. Each one adds a new capability.',
    complete: '<strong>All done!</strong> Your AI development environment is ready. Start coding! 🎉',
  };
  m.querySelector('.bubble').innerHTML = msgs[phase] || 'Setting things up...';
}

function updateControllerBanner() {
  const h = document.getElementById('ctrl-holder');
  const btnA = document.getElementById('btn-acquire');
  const btnR = document.getElementById('btn-release');
  if (leaseId && holder) {
    h.innerHTML = '<strong>' + holder + '</strong> has control';
    btnA.style.display = 'none';
    btnR.style.display = '';
  } else {
    h.textContent = 'No active controller — take control to make changes';
    btnA.style.display = '';
    btnR.style.display = 'none';
  }
}

// ── Actions ──
async function acquireLease() {
  const res = await fetch(API + '/api/controller/acquire', {
    method: 'POST', headers: authHeaders(),
    body: JSON.stringify({session_id: sessionId, holder: 'web'})
  });
  const data = await res.json();
  if (data.ok) { leaseId = data.lease_id; holder = 'web'; render(); startRenew(); }
  else alert(data.error || 'Could not acquire control');
}

async function releaseLease() {
  await fetch(API + '/api/controller/release', {
    method: 'POST', headers: authHeaders(),
    body: JSON.stringify({session_id: sessionId, holder: 'web'})
  });
  leaseId = null; holder = null; stopRenew(); render();
}

let renewTimer = null;
function startRenew() { stopRenew(); renewTimer = setInterval(async () => {
  if (!leaseId) return;
  const res = await fetch(API + '/api/controller/renew', {
    method: 'POST', headers: authHeaders(),
    body: JSON.stringify({session_id: sessionId, lease_id: leaseId})
  });
  const data = await res.json();
  if (!data.ok) { leaseId = null; holder = null; stopRenew(); render(); }
}, 25000); }
function stopRenew() { if (renewTimer) { clearInterval(renewTimer); renewTimer = null; } }

async function runSetup(itemId) {
  if (!leaseId) return;
  // Use the full install endpoint (runs all setup steps, not just probe)
  const res = await fetch(API + '/api/skills/' + itemId + '/install', {
    method: 'POST', headers: authHeaders(),
    body: JSON.stringify({session_id: sessionId, lease_id: leaseId, skill_id: itemId})
  });
  const data = await res.json();

  if (!data.ok && data.error) {
    console.log('Setup failed:', data.error);
  }

  // Also register cron jobs if this is a cron-type skill
  const item = (state.items || []).find(i => i.id === itemId);
  if (item && item.kind === 'cron' && data.ok) {
    await fetch(API + '/api/jobs/register', {
      method: 'POST', headers: {'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + (localStorage.getItem('cl-token') || '')},
      body: JSON.stringify({skill_id: itemId})
    });
  }

  await refreshState();
}

async function skipItem(itemId) {
  if (!leaseId) return;
  await fetch(API + '/api/onboarding/intent', {
    method: 'POST', headers: authHeaders(),
    body: JSON.stringify({session_id: sessionId, lease_id: leaseId, intent: 'skip_item', item_id: itemId, payload: {reason: 'User skipped'}})
  });
  await refreshState();
}

async function completeOnboarding() {
  if (!leaseId) return;
  const res = await fetch(API + '/api/onboarding/intent', {
    method: 'POST', headers: authHeaders(),
    body: JSON.stringify({session_id: sessionId, lease_id: leaseId, intent: 'complete'})
  });
  const data = await res.json();
  if (data.ok) { window.location.href = '/workspaces'; }
  else alert(data.error || 'Cannot complete yet');
}

// ── Handoff ──
async function launchHandoff() {
  if (!sessionId) return;
  const res = await fetch(API + '/api/onboarding/handoff-gen', {
    method: 'POST', headers: authHeaders(),
    body: JSON.stringify({session_id: sessionId, port: location.port || 3333})
  });
  const data = await res.json();
  const el = document.getElementById('handoff-result');
  el.style.display = 'block';
  if (data.ok) {
    el.innerHTML = '<strong style="color:var(--green)">CLAUDE.md generated!</strong><br>'
      + 'Open a terminal in your workspace and run:<br>'
      + '<code style="background:var(--bg3);padding:4px 8px;border-radius:4px;display:inline-block;margin-top:6px">claude</code><br>'
      + '<span style="font-size:0.8rem;color:var(--fg3)">Claude will read the onboarding instructions and help you set up.</span>';
  } else {
    el.innerHTML = '<span style="color:var(--red)">Error: ' + (data.error || 'Unknown') + '</span>';
  }
}

// Show handoff banner when there are pending items
function checkHandoffBanner() {
  if (!state) return;
  const pending = (state.items || []).filter(i => i.status === 'pending' || i.status === 'failed');
  const banner = document.getElementById('handoff-banner');
  if (pending.length > 0 && state.phase !== 'complete') {
    banner.style.display = 'block';
  } else {
    banner.style.display = 'none';
  }
}

// ── Polling ──
async function refreshState() {
  if (!sessionId) return;
  const res = await fetch(API + '/api/onboarding/state?session_id=' + sessionId);
  const data = await res.json();
  if (data.ok) { state = data.state; render(); }

  // Also check controller
  const cres = await fetch(API + '/api/controller?session_id=' + sessionId);
  const cdata = await cres.json();
  if (cdata.ok) {
    if (cdata.holder && cdata.holder !== 'web' && leaseId) {
      // Someone else took control
      leaseId = null; holder = null; stopRenew();
    }
    if (cdata.holder === 'web' && cdata.lease_id && !leaseId) {
      leaseId = cdata.lease_id; holder = 'web'; startRenew();
    }
    render();
  }
}

let pollTimer = null;
function startPolling() { pollTimer = setInterval(refreshState, 3000); }

// ── Boot ──
init();
</script>"""
    "</body></html>"
)
