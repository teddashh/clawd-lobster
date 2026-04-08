"""Dashboard pages — Skills, Credentials, Settings.

Post-onboarding persistent dashboard views. Same visual theme as
pages_onboarding.py (dark GitHub-style, inline HTML/CSS/JS).
"""

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
.container { max-width: 960px; margin: 0 auto; padding: 24px var(--gap); }

/* Nav */
.nav { display: flex; gap: 4px; margin-bottom: 24px; border-bottom: 1px solid var(--bg3); padding-bottom: 8px; }
.nav a { padding: 8px 16px; border-radius: 8px 8px 0 0; color: var(--fg2); font-size: 0.9rem; }
.nav a:hover { color: var(--fg); background: var(--bg2); }
.nav a.active { color: var(--accent); border-bottom: 2px solid var(--accent); }

/* Tabs */
.tabs { display: flex; gap: 2px; background: var(--bg3); border-radius: 8px; padding: 2px; margin-bottom: 20px; }
.tabs button { flex: 1; padding: 8px 12px; background: transparent; border: none; color: var(--fg2); font-size: 0.85rem; cursor: pointer; border-radius: 6px; transition: all 0.15s; }
.tabs button:hover { color: var(--fg); }
.tabs button.active { background: var(--bg2); color: var(--fg); }
.tab-panel { display: none; }
.tab-panel.active { display: block; }

/* Cards */
.card { background: var(--bg2); border: 1px solid var(--bg3); border-radius: var(--radius); padding: 16px; margin-bottom: 10px; }
.card-row { display: flex; align-items: center; gap: 12px; }
.card-icon { font-size: 1.6rem; width: 40px; text-align: center; }
.card-info { flex: 1; }
.card-info h3 { font-size: 0.95rem; font-weight: 600; }
.card-info .desc { color: var(--fg2); font-size: 0.8rem; margin-top: 2px; }
.card-badge { padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 500; }
.card-badge.running { background: rgba(63,185,80,0.15); color: var(--green); }
.card-badge.enabled { background: rgba(88,166,255,0.15); color: var(--accent); }
.card-badge.disabled { background: rgba(139,148,158,0.1); color: var(--fg3); }
.card-badge.error { background: rgba(248,81,73,0.15); color: var(--red); }
.card-actions { display: flex; gap: 6px; margin-left: 8px; }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border: 1px solid var(--bg3); border-radius: 6px; background: var(--bg2); color: var(--fg); font-size: 0.8rem; cursor: pointer; transition: all 0.15s; }
.btn:hover { border-color: var(--accent); color: var(--accent); }
.btn.sm { padding: 4px 8px; font-size: 0.75rem; }

/* Form */
.form-group { margin-bottom: 16px; }
.form-group label { display: block; color: var(--fg2); font-size: 0.85rem; margin-bottom: 4px; }
.form-group input, .form-group select { width: 100%; padding: 8px 12px; background: var(--bg); border: 1px solid var(--bg3); border-radius: 6px; color: var(--fg); font-size: 0.9rem; }
.form-group input:focus, .form-group select:focus { outline: none; border-color: var(--accent); }

/* Credential row */
.cred-row { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--bg3); }
.cred-row:last-child { border-bottom: none; }
.cred-icon { font-size: 1.3rem; width: 32px; text-align: center; }
.cred-info { flex: 1; }
.cred-info .name { font-weight: 600; font-size: 0.9rem; }
.cred-info .type { color: var(--fg3); font-size: 0.75rem; }
.cred-value { font-family: monospace; color: var(--fg3); font-size: 0.85rem; }
"""

_NAV = """
<div class="nav">
  <a href="/onboarding">Setup</a>
  <a href="/workspaces">Workspaces</a>
  <a href="/skills" {skills_active}>Skills</a>
  <a href="/credentials" {creds_active}>Keys</a>
  <a href="/settings" {settings_active}>Settings</a>
  <a href="/squad">Squad</a>
</div>
"""

# ═══════════════════════════════════════════════════════════════════════════
# SKILLS PAGE
# ═══════════════════════════════════════════════════════════════════════════

SKILLS_PAGE = (
    "<!DOCTYPE html><html lang='en'><head>"
    "<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Skills — Clawd-Lobster</title>"
    f"<style>{_CSS}</style>"
    "</head><body><div class='container'>"
    + _NAV.replace("{skills_active}", "class='active'").replace("{creds_active}", "").replace("{settings_active}", "")
    +
    "<h1 style='margin-bottom:20px'>⚡ Skills</h1>"

    "<div class='tabs'>"
    "<button class='active' onclick='switchTab(\"mcp\")'>MCP Servers</button>"
    "<button onclick='switchTab(\"prompt\")'>Prompt Patterns</button>"
    "<button onclick='switchTab(\"cron\")'>Cron Jobs</button>"
    "</div>"

    "<div id='tab-mcp' class='tab-panel active'><div class='loading'>Loading...</div></div>"
    "<div id='tab-prompt' class='tab-panel'><div class='loading'>Loading...</div></div>"
    "<div id='tab-cron' class='tab-panel'><div class='loading'>Loading...</div></div>"

    """<script>
function switchTab(name) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  event.target.classList.add('active');
}

const kindMap = {'mcp-server': 'mcp', 'prompt-pattern': 'prompt', 'cron': 'cron'};
const icons = {
  'memory-server':'🧠', 'spec':'📋', 'absorb':'🧽', 'evolve':'🧬',
  'heartbeat':'💓', 'deploy':'🚀', 'codex-bridge':'🤖', 'gemini-bridge':'💎',
  'notebooklm-bridge':'📓', 'connect-odoo':'🏢', 'migrate':'📦',
};

async function loadSkills() {
  const res = await fetch('/api/skills/catalog');
  const data = await res.json();
  if (!data.ok) return;

  const groups = {mcp: [], prompt: [], cron: []};
  data.skills.forEach(s => {
    const tab = kindMap[s.kind] || 'prompt';
    groups[tab].push(s);
  });

  ['mcp','prompt','cron'].forEach(tab => {
    const el = document.getElementById('tab-' + tab);
    if (groups[tab].length === 0) {
      el.innerHTML = '<p style="color:var(--fg3);padding:20px">No skills in this category.</p>';
      return;
    }
    el.innerHTML = groups[tab].map(s => {
      const icon = icons[s.id] || '⚙️';
      const badge = s.always_on ? '<span class="card-badge running">Always On</span>'
        : s.default_enabled ? '<span class="card-badge enabled">Enabled</span>'
        : '<span class="card-badge disabled">Disabled</span>';
      return '<div class="card"><div class="card-row">'
        + '<div class="card-icon">' + icon + '</div>'
        + '<div class="card-info"><h3>' + s.name + '</h3>'
        + '<div class="desc">' + (s.summary || s.name) + '</div></div>'
        + badge
        + '<div class="card-actions"><button class="btn sm">Configure</button></div>'
        + '</div></div>';
    }).join('');
  });
}
loadSkills();
</script>"""
    "</div></body></html>"
)

# ═══════════════════════════════════════════════════════════════════════════
# CREDENTIALS PAGE
# ═══════════════════════════════════════════════════════════════════════════

CREDENTIALS_PAGE = (
    "<!DOCTYPE html><html lang='en'><head>"
    "<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>API Keys — Clawd-Lobster</title>"
    f"<style>{_CSS}</style>"
    "</head><body><div class='container'>"
    + _NAV.replace("{skills_active}", "").replace("{creds_active}", "class='active'").replace("{settings_active}", "")
    +
    "<h1 style='margin-bottom:20px'>🔑 API Keys & Authentication</h1>"

    "<div class='card' style='padding:0'>"
    "<div id='creds-list'><p style='padding:16px;color:var(--fg3)'>Loading...</p></div>"
    "</div>"

    """<script>
const services = [
  {id: 'claude', name: 'Claude Code', icon: '🤖', type: 'OAuth', probe: 'foundation.claude_auth'},
  {id: 'github', name: 'GitHub', icon: '🐙', type: 'PAT / SSH', probe: 'foundation.hub'},
  {id: 'codex', name: 'OpenAI / Codex', icon: '⚡', type: 'Subscription', probe: null},
  {id: 'gemini', name: 'Google / Gemini', icon: '💎', type: 'OAuth', probe: null},
  {id: 'oracle', name: 'Oracle Vault', icon: '🏛️', type: 'Wallet', probe: null},
  {id: 'odoo', name: 'Odoo ERP', icon: '🏢', type: 'API Key', probe: null},
];

async function loadCreds() {
  // Get health probes for status
  let probes = {};
  try {
    const res = await fetch('/api/onboarding/health');
    const data = await res.json();
    if (data.ok) probes = data.probes;
  } catch(e) {}

  const el = document.getElementById('creds-list');
  el.innerHTML = services.map(s => {
    const probe = s.probe ? probes[s.probe] : null;
    let status = '⚪ Not configured';
    let badgeClass = 'disabled';
    if (probe) {
      if (probe.verified) { status = '🟢 Authenticated'; badgeClass = 'running'; }
      else if (probe.detected) { status = '🟡 Detected, not verified'; badgeClass = 'enabled'; }
      else { status = '🔴 Not found'; badgeClass = 'error'; }
    }
    return '<div class="cred-row">'
      + '<div class="cred-icon">' + s.icon + '</div>'
      + '<div class="cred-info"><div class="name">' + s.name + '</div>'
      + '<div class="type">' + s.type + '</div></div>'
      + '<span class="card-badge ' + badgeClass + '">' + status + '</span>'
      + '<div class="card-actions">'
      + '<button class="btn sm" onclick="alert(\'Configure ' + s.name + ' — coming soon\')">Update</button>'
      + '<button class="btn sm" onclick="testCred(\'' + s.id + '\')">Test</button>'
      + '</div></div>';
  }).join('');
}

async function testCred(id) {
  const svc = services.find(s => s.id === id);
  if (!svc || !svc.probe) { alert('No automated test for ' + id); return; }
  const res = await fetch('/api/onboarding/health/' + svc.probe);
  const data = await res.json();
  if (data.ok && data.probe) {
    const p = data.probe;
    alert(svc.name + ':\\n' +
      'Detected: ' + (p.detected ? 'Yes' : 'No') + '\\n' +
      'Verified: ' + (p.verified ? 'Yes' : 'No') + '\\n' +
      (p.repair_hint ? 'Hint: ' + p.repair_hint : ''));
  }
}

loadCreds();
</script>"""
    "</div></body></html>"
)

# ═══════════════════════════════════════════════════════════════════════════
# SETTINGS PAGE
# ═══════════════════════════════════════════════════════════════════════════

SETTINGS_PAGE = (
    "<!DOCTYPE html><html lang='en'><head>"
    "<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Settings — Clawd-Lobster</title>"
    f"<style>{_CSS}</style>"
    "</head><body><div class='container'>"
    + _NAV.replace("{skills_active}", "").replace("{creds_active}", "").replace("{settings_active}", "class='active'")
    +
    "<h1 style='margin-bottom:20px'>⚙️ Settings</h1>"

    "<div class='card'>"
    "<form id='settings-form'>"

    "<div class='form-group'>"
    "<label>Language</label>"
    "<select id='s-lang'>"
    "<option value='en'>English</option>"
    "<option value='zh-TW'>繁體中文</option>"
    "<option value='zh-CN'>简体中文</option>"
    "<option value='ja'>日本語</option>"
    "<option value='ko'>한국어</option>"
    "</select></div>"

    "<div class='form-group'>"
    "<label>Workspace Root</label>"
    "<input type='text' id='s-workspace-root' placeholder='~/Documents/Workspace'>"
    "</div>"

    "<div class='form-group'>"
    "<label>Hub Directory</label>"
    "<input type='text' id='s-hub-dir' placeholder='(auto-detected)' disabled>"
    "</div>"

    "<div class='form-group'>"
    "<label>Machine ID</label>"
    "<input type='text' id='s-machine-id' disabled>"
    "</div>"

    "<div class='form-group'>"
    "<label>Server Port</label>"
    "<input type='number' id='s-port' value='3333'>"
    "</div>"

    "<button type='submit' class='btn' style='margin-top:8px'>Save Settings</button>"
    "</form></div>"

    "<div class='card' style='margin-top:16px'>"
    "<h3 style='margin-bottom:12px'>System Info</h3>"
    "<div id='sys-info' style='color:var(--fg2);font-size:0.85rem'>Loading...</div>"
    "</div>"

    """<script>
async function loadSettings() {
  // Load system status
  const res = await fetch('/api/status');
  const data = await res.json();
  if (data.ok) {
    document.getElementById('sys-info').innerHTML =
      'Version: ' + data.version + '<br>' +
      'Python: ' + data.python + '<br>' +
      'Platform: ' + navigator.platform;
  }
}

document.getElementById('settings-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  alert('Settings saved (API endpoint coming soon)');
});

loadSettings();
</script>"""
    "</div></body></html>"
)
