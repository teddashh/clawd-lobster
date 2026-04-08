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
<title>clawd-lobster &mdash; Setup</title>
<style>"""
    + _BASE_CSS
    + """
.wizard { max-width:700px; margin:48px auto; padding:0 24px; }
.page { display:none; }
.page.active { display:block; }
.progress { display:flex; gap:6px; margin-bottom:32px; }
.progress-dot { flex:1; height:6px; border-radius:3px; background:#21262d;
  transition:background 0.3s; }
.progress-dot.done { background:#56d364; }
.progress-dot.current { background:#58a6ff; }
.welcome-hero { text-align:center; padding:24px 0; }
.welcome-hero h1 { font-size:32px; margin-bottom:20px; color:#c9d1d9; }
.tagline-stack { margin:16px 0 24px; }
.tagline-stack p { font-size:14px; opacity:0.45; line-height:2; transition:opacity 0.3s, color 0.3s; }
.tagline-stack p.highlight { opacity:1; color:#58a6ff; }
.welcome-instructions { margin:20px 0; font-size:14px; line-height:2.2; color:#8b949e; }
.lang-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px;
  max-width:420px; margin:28px auto 0; }
.lang-card { padding:14px 16px; border:2px solid #30363d; border-radius:10px;
  cursor:pointer; text-align:center; transition:border-color 0.2s, background 0.2s; }
.lang-card:hover { border-color:#58a6ff; }
.lang-card.selected { border-color:#58a6ff; background:#161b22; }
.lang-name { font-size:16px; font-weight:600; }
.wizard h2 { font-size:22px; margin-bottom:12px; }
.prereq-card { background:#161b22; border:1px solid #30363d; border-radius:10px;
  padding:16px; margin:10px 0; transition:border-color 0.3s; }
.prereq-card.ok { border-left:3px solid #56d364; }
.prereq-card.fail { border-left:3px solid #f85149; }
.prereq-header { display:flex; justify-content:space-between; align-items:center; }
.prereq-name { font-weight:600; font-size:15px; }
.prereq-version { color:#8b949e; font-size:13px; margin-left:8px; }
.prereq-purpose { color:#8b949e; font-size:13px; margin-top:4px; }
.prereq-status { font-weight:600; font-size:13px; }
.prereq-status.ok { color:#56d364; }
.prereq-status.fail { color:#f85149; }
.prereq-guide { display:none; margin-top:12px; padding-top:12px;
  border-top:1px solid #21262d; }
.prereq-guide.open { display:block; }
.prereq-guide p { font-size:13px; color:#8b949e; margin-bottom:6px; }
.platform-tabs { display:flex; gap:4px; margin:8px 0; }
.platform-tab { padding:4px 12px; border-radius:6px; font-size:12px;
  cursor:pointer; background:#21262d; color:#8b949e; border:none; }
.platform-tab.active { background:#30363d; color:#c9d1d9; }
.platform-content { display:none; }
.platform-content.active { display:block; }
.platform-content p { font-size:13px; color:#8b949e; margin-bottom:4px; }
.platform-content code, .prereq-guide > code {
  background:#0d1117; padding:8px 12px; border-radius:6px; display:block;
  font-family:monospace; font-size:13px; color:#e6edf3; margin:6px 0;
  user-select:all; }
.toggle-guide { background:none; border:none; color:#58a6ff; font-size:12px;
  cursor:pointer; padding:0; margin-top:8px; }
.terminal-card { background:#0d1117; border:1px solid #30363d;
  border-radius:10px; overflow:hidden; margin:16px 0; }
.terminal-header { background:#161b22; padding:8px 12px; display:flex; gap:6px; }
.terminal-dot { width:10px; height:10px; border-radius:50%; }
.terminal-dot.red { background:#f85149; }
.terminal-dot.yellow { background:#e3b341; }
.terminal-dot.green { background:#56d364; }
.terminal-card pre { padding:16px; font-family:monospace; font-size:14px;
  color:#e6edf3; white-space:pre-wrap; margin:0; }
.copy-btn { background:#30363d; color:#c9d1d9; border:none; padding:6px 14px;
  border-radius:6px; font-size:12px; cursor:pointer; margin:0 16px 16px; }
.copy-btn:hover { background:#484f58; }
.progress-panel { background:#161b22; border:1px solid #30363d;
  border-radius:10px; padding:20px; margin:16px 0; }
.progress-panel h3 { font-size:16px; margin-bottom:14px; }
.progress-item { display:flex; align-items:center; gap:10px; padding:8px 0;
  border-bottom:1px solid #21262d; }
.progress-item:last-child { border-bottom:none; }
.prog-icon { font-size:16px; width:20px; text-align:center; color:#8b949e; }
.prog-icon.done { color:#56d364; }
.prog-status { margin-left:auto; font-size:13px; color:#8b949e; }
.prog-status.done { color:#56d364; font-weight:600; }
.persona-grid { display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px;
  margin:16px 0; }
.persona-card { padding:20px 16px; border:2px solid #30363d; border-radius:12px;
  cursor:pointer; text-align:center; transition:border-color 0.2s; }
.persona-card:hover { border-color:#58a6ff; }
.persona-card.selected { border-color:#58a6ff; background:#161b22; }
.persona-card h3 { font-size:16px; margin-bottom:4px; }
.persona-card p { color:#8b949e; font-size:13px; }
.field-group { margin:16px 0; }
.field-group label { display:block; font-size:14px; margin-bottom:6px; color:#8b949e; }
.page-actions { margin-top:28px; display:flex; justify-content:space-between;
  align-items:center; }
.welcome-done { text-align:center; padding:40px 0; }
.welcome-done h2 { font-size:28px; color:#56d364; margin-bottom:8px; }
.welcome-done p { color:#8b949e; margin:12px 0; font-size:16px; }
@keyframes spin { to { transform:rotate(360deg); } }
.spinner { display:inline-block; width:14px; height:14px;
  border:2px solid #30363d; border-top-color:#58a6ff;
  border-radius:50%; animation:spin 0.8s linear infinite;
  vertical-align:middle; margin-right:6px; }
.mascot-wrap { position:fixed; bottom:20px; left:20px; z-index:50;
  pointer-events:auto; cursor:default; }
.mascot-wrap img { width:150px; opacity:0.75;
  filter:drop-shadow(0 0 12px rgba(88,166,255,0.3)) drop-shadow(0 4px 12px rgba(0,0,0,0.5));
  animation:mascot-float 4s ease-in-out infinite, mascot-enter 0.8s ease-out both;
  transition:opacity 0.3s, transform 0.3s, filter 0.3s; }
.mascot-wrap:hover img { opacity:1; transform:scale(1.08);
  filter:drop-shadow(0 0 20px rgba(88,166,255,0.5)) drop-shadow(0 4px 16px rgba(0,0,0,0.6)); }
.mascot-bubble { position:absolute; bottom:100%; left:50%; transform:translateX(-50%);
  background:#161b22; border:1px solid #30363d; border-radius:10px;
  padding:8px 14px; font-size:12px; color:#8b949e; white-space:nowrap;
  opacity:0; pointer-events:none; transition:opacity 0.3s, transform 0.3s;
  transform:translateX(-50%) translateY(8px); margin-bottom:8px; }
.mascot-bubble::after { content:''; position:absolute; top:100%; left:50%;
  transform:translateX(-50%); border:6px solid transparent;
  border-top-color:#30363d; }
.mascot-wrap:hover .mascot-bubble { opacity:1; transform:translateX(-50%) translateY(0); }
@keyframes mascot-float {
  0%,100% { transform:translateY(0); }
  50% { transform:translateY(-8px); } }
@keyframes mascot-enter {
  from { opacity:0; transform:translateY(30px) scale(0.8); }
  to { opacity:0.75; transform:translateY(0) scale(1); } }
@media (max-width:600px) { .mascot-wrap { bottom:10px; left:10px; }
  .mascot-wrap img { width:90px; } .mascot-bubble { display:none; } }
</style></head><body>
<header><h1><span>clawd-lobster</span> Setup</h1></header>
<div class="mascot-wrap">
  <div class="mascot-bubble" id="mascot-bubble"></div>
  <picture>
    <source srcset="/assets/mascot.webp" type="image/webp">
    <img src="/assets/mascot.png" alt="Clawd mascot">
  </picture>
</div>

<div class="wizard">
  <div class="progress">
    <div class="progress-dot current" id="dot-0"></div>
    <div class="progress-dot" id="dot-1"></div>
    <div class="progress-dot" id="dot-2"></div>
  </div>

  <!-- Page 0: Welcome + Language -->
  <div class="page active" id="page-0">
    <div class="welcome-hero">
      <h1>Welcome to Clawd-Lobster</h1>
      <div class="tagline-stack">
        <p data-lang="en">You'll end up using Claude Code anyway &mdash; why not start with the best experience?</p>
        <p data-lang="zh-TW">&#x4F60;&#x7D42;&#x7A76;&#x8981;&#x7528; Claude Code &#x7684; &mdash; &#x70BA;&#x4EC0;&#x9EBC;&#x4E0D;&#x4E00;&#x958B;&#x59CB;&#x5C31;&#x9078;&#x6700;&#x597D;&#x7684;&#x9AD4;&#x9A57;&#xFF1F;</p>
        <p data-lang="zh-CN">&#x4F60;&#x7EC8;&#x7A76;&#x8981;&#x7528; Claude Code &#x7684; &mdash; &#x4E3A;&#x4EC0;&#x4E48;&#x4E0D;&#x4E00;&#x5F00;&#x59CB;&#x5C31;&#x9009;&#x6700;&#x597D;&#x7684;&#x4F53;&#x9A8C;&#xFF1F;</p>
        <p data-lang="ja">&#x3069;&#x3046;&#x305B; Claude Code &#x3092;&#x4F7F;&#x3046;&#x3053;&#x3068;&#x306B;&#x306A;&#x308B; &mdash; &#x6700;&#x521D;&#x304B;&#x3089;&#x6700;&#x9AD8;&#x306E;&#x4F53;&#x9A13;&#x3092;&#x9078;&#x3073;&#x307E;&#x305B;&#x3093;&#x304B;&#xFF1F;</p>
        <p data-lang="ko">&#xACB0;&#xAD6D; Claude Code&#xB97C; &#xC4F0;&#xAC8C; &#xB420; &#xD150;&#xB370; &mdash; &#xCC98;&#xC74C;&#xBD80;&#xD130; &#xCD5C;&#xACE0;&#xC758; &#xACBD;&#xD5D8;&#xC744; &#xC120;&#xD0DD;&#xD558;&#xC9C0; &#xC54A;&#xACA0;&#xC2B5;&#xB2C8;&#xAE4C;?</p>
      </div>
      <div class="welcome-instructions">
        Let's get started. Please select your language.<br>
        <span style="opacity:0.5">&#x8B93;&#x6211;&#x5011;&#x958B;&#x59CB;&#x5427;&#xFF0C;&#x8ACB;&#x9078;&#x64C7;&#x4F60;&#x7684;&#x8A9E;&#x8A00;&#x3002;</span><br>
        <span style="opacity:0.5">&#x8BA9;&#x6211;&#x4EEC;&#x5F00;&#x59CB;&#x5427;&#xFF0C;&#x8BF7;&#x9009;&#x62E9;&#x4F60;&#x7684;&#x8BED;&#x8A00;&#x3002;</span><br>
        <span style="opacity:0.5">&#x59CB;&#x3081;&#x307E;&#x3057;&#x3087;&#x3046;&#x3002;&#x8A00;&#x8A9E;&#x3092;&#x9078;&#x629E;&#x3057;&#x3066;&#x304F;&#x3060;&#x3055;&#x3044;&#x3002;</span><br>
        <span style="opacity:0.5">&#xC2DC;&#xC791;&#xD558;&#xACA0;&#xC2B5;&#xB2C8;&#xB2E4;. &#xC5B8;&#xC5B4;&#xB97C; &#xC120;&#xD0DD;&#xD558;&#xC138;&#xC694;.</span>
      </div>
      <div class="lang-grid">
        <div class="lang-card" onclick="pickLang('en',this)"><span class="lang-name">English</span></div>
        <div class="lang-card" onclick="pickLang('zh-TW',this)"><span class="lang-name">&#x7E41;&#x9AD4;&#x4E2D;&#x6587;</span></div>
        <div class="lang-card" onclick="pickLang('zh-CN',this)"><span class="lang-name">&#x7B80;&#x4F53;&#x4E2D;&#x6587;</span></div>
        <div class="lang-card" onclick="pickLang('ja',this)"><span class="lang-name">&#x65E5;&#x672C;&#x8A9E;</span></div>
        <div class="lang-card" onclick="pickLang('ko',this)"><span class="lang-name">&#xD55C;&#xAD6D;&#xC5B4;</span></div>
      </div>
    </div>
    <div class="page-actions">
      <div></div>
      <button class="btn btn-primary" id="lang-next" disabled onclick="goPage(1)" data-i18n="next">Next</button>
    </div>
  </div>

  <!-- Page 1: Prerequisites -->
  <div class="page" id="page-1">
    <h2 data-i18n="prereq_title">System Check</h2>
    <p style="color:#8b949e" data-i18n="prereq_desc">Let's make sure everything is ready.</p>
    <div id="prereq-cards" style="margin:16px 0;"></div>
    <div id="prereq-summary" style="display:none;margin-top:12px;">
      <p style="color:#56d364;font-weight:600;" data-i18n="prereq_all_ok">All prerequisites met!</p>
    </div>
    <div class="page-actions">
      <button class="btn btn-secondary" onclick="goPage(0)" data-i18n="back">Back</button>
      <div style="display:flex;gap:10px;">
        <button class="btn btn-secondary" id="recheck-btn" onclick="runChecks()" data-i18n="prereq_recheck">Re-check</button>
        <button class="btn btn-primary" id="prereq-next" disabled onclick="goPage(2)" data-i18n="next">Next</button>
      </div>
    </div>
  </div>

  <!-- Page 2: Handoff to CLI -->
  <div class="page" id="page-2">
    <h2 data-i18n="handoff_title">Let Claude Code take it from here</h2>
    <p style="color:#8b949e" data-i18n="handoff_desc">Open a terminal and run the command below. Claude Code will guide you through the rest.</p>

    <div class="terminal-card" id="handoff-terminal" style="display:none;">
      <div class="terminal-header">
        <span class="terminal-dot red"></span>
        <span class="terminal-dot yellow"></span>
        <span class="terminal-dot green"></span>
      </div>
      <pre id="handoff-cmd">Loading...</pre>
      <button class="copy-btn" id="copy-btn" onclick="copyCmd()" data-i18n="handoff_copy">Copy command</button>
    </div>

    <div class="progress-panel" id="handoff-progress" style="display:none;">
      <h3 data-i18n="handoff_status">Setup Progress</h3>
      <div class="progress-item" id="prog-persona">
        <span class="prog-icon">&#9675;</span>
        <span data-i18n="handoff_persona">Persona selection</span>
        <span class="prog-status" data-i18n="handoff_waiting">Waiting...</span>
      </div>
      <div class="progress-item" id="prog-workspace_root">
        <span class="prog-icon">&#9675;</span>
        <span data-i18n="handoff_workspace_root">Workspace root directory</span>
        <span class="prog-status" data-i18n="handoff_waiting">Waiting...</span>
      </div>
      <div class="progress-item" id="prog-workspace">
        <span class="prog-icon">&#9675;</span>
        <span data-i18n="handoff_workspace">First workspace</span>
        <span class="prog-status" data-i18n="handoff_waiting">Waiting...</span>
      </div>
      <div class="progress-item" id="prog-config">
        <span class="prog-icon">&#9675;</span>
        <span data-i18n="handoff_config">Configuration</span>
        <span class="prog-status" data-i18n="handoff_waiting">Waiting...</span>
      </div>
    </div>

    <p id="handoff-timeout-msg" style="display:none;color:#8b949e;font-size:13px;margin-top:12px;" data-i18n="handoff_timeout">Taking a while? Try the manual setup below.</p>

    <div style="margin-top:20px;text-align:center;">
      <button class="btn btn-secondary" onclick="showFallback()" style="font-size:14px;" data-i18n="handoff_manual">I want to do it manually in the browser instead</button>
    </div>

    <!-- Fallback: manual browser setup -->
    <div id="fallback-section" style="display:none;margin-top:24px;">
      <hr style="border-color:#21262d;margin:20px 0;">
      <h3 data-i18n="persona_title">How do you work?</h3>
      <p style="color:#8b949e;font-size:13px;" data-i18n="persona_desc">This helps us tailor the experience.</p>
      <div class="persona-grid">
        <div class="persona-card" onclick="pickPersona('noob',this)">
          <h3 data-i18n="persona_guided">Guided</h3>
          <p data-i18n="persona_guided_desc">New to AI dev. Show me everything.</p>
        </div>
        <div class="persona-card" onclick="pickPersona('expert',this)">
          <h3 data-i18n="persona_expert">Expert</h3>
          <p data-i18n="persona_expert_desc">I know what I'm doing. Less hand-holding.</p>
        </div>
        <div class="persona-card" onclick="pickPersona('tech',this)">
          <h3 data-i18n="persona_tech">Technical</h3>
          <p data-i18n="persona_tech_desc">I want full control and raw output.</p>
        </div>
      </div>
      <h3 data-i18n="ws_title" style="margin-top:20px;">Create Your First Workspace</h3>
      <div class="field-group">
        <label data-i18n="ws_name_label">Workspace name (kebab-case)</label>
        <input type="text" id="ws-name" placeholder="my-first-project" oninput="validateWsName()">
        <p id="ws-name-err" style="color:#f85149;font-size:13px;margin-top:4px;"></p>
      </div>
      <div class="field-group">
        <label data-i18n="ws_root_label">Workspace root directory</label>
        <input type="text" id="ws-root" placeholder="~/Documents/Workspace">
      </div>
      <div style="margin-top:16px;text-align:right;">
        <button class="btn btn-primary" id="finish-btn" disabled onclick="finishManual()" data-i18n="finish">Finish Setup</button>
      </div>
    </div>

    <div class="page-actions">
      <button class="btn btn-secondary" onclick="goPage(1)" data-i18n="back">Back</button>
      <div></div>
    </div>
  </div>

  <!-- Done screen -->
  <div class="page" id="page-done">
    <div class="welcome-done">
      <h2 data-i18n="ready">Ready!</h2>
      <p data-i18n="ready_desc">Your workspace has been created.</p>
      <div style="margin:24px 0;display:flex;gap:12px;justify-content:center;">
        <a href="/workspaces" class="btn btn-secondary" data-i18n="view_ws">View Workspaces</a>
        <a href="/squad" class="btn btn-primary" data-i18n="launch_squad">Launch Spec Squad</a>
      </div>
    </div>
  </div>
</div>

<script>
let lang = 'en';
let persona = '';
let sessionId = '';
let detectedPlatform = 'windows';
let defaultRoot = '';
let pollTimer = null;
let pollCount = 0;
let checksLoaded = false;
let lastPrereqData = null;
let currentAppliedLang = '';
const KEBAB = /^[a-z0-9]+(-[a-z0-9]+)*$/;

const PREREQ_INFO = {
  python: { display:"Python 3.10+", purposeKey:"prereq_python_purpose", installKey:"prereq_python_install", guideKey:"prereq_python_guide",
    platforms:{ windows:{descKey:"prereq_python_win"}, macos:{descKey:"prereq_python_mac"}, linux:{descKey:"prereq_python_linux"} } },
  node: { display:"Node.js 18+", purposeKey:"prereq_node_purpose", installKey:"prereq_node_install", guideKey:"prereq_node_guide",
    platforms:{ windows:{descKey:"prereq_node_win"}, macos:{descKey:"prereq_node_mac"}, linux:{descKey:"prereq_node_linux"} } },
  git: { display:"Git", purposeKey:"prereq_git_purpose", installKey:"prereq_git_install", guideKey:"prereq_git_guide",
    platforms:{ windows:{descKey:"prereq_git_win"}, macos:{descKey:"prereq_git_mac"}, linux:{descKey:"prereq_git_linux"} } },
  pip: { display:"pip", purposeKey:"prereq_pip_purpose", installKey:"prereq_pip_install", guideKey:"prereq_pip_guide", cmd:"python -m ensurepip --upgrade" },
  claude: { display:"Claude Code CLI", purposeKey:"prereq_claude_purpose", installKey:"prereq_claude_install", guideKey:"prereq_claude_guide", cmd:"npm install -g @anthropic-ai/claude-code" },
  claude_auth: { display:"Claude Code Auth", purposeKey:"prereq_auth_purpose", installKey:"prereq_auth_install", guideKey:"prereq_auth_guide", cmd:"claude login" },
};

const I18N = {
  en: {
    next:"Next", back:"Back",
    prereq_title:"System Check", prereq_desc:"Let's make sure everything is ready.",
    prereq_recheck:"Re-check", prereq_all_ok:"All prerequisites met!",
    prereq_python_purpose:"Runs the memory server and skills",
    prereq_node_purpose:"Required for Claude Code installation",
    prereq_git_purpose:"Syncs knowledge across machines",
    prereq_pip_purpose:"Python package manager",
    prereq_claude_purpose:"The AI coding assistant",
    prereq_auth_purpose:"Claude Code authentication",
    prereq_checking:"Checking...", prereq_ok:"OK", prereq_missing:"Missing",
    prereq_python_install:"How to install Python",
    prereq_node_install:"How to install Node.js",
    prereq_git_install:"How to install Git",
    prereq_pip_install:"How to install pip",
    prereq_claude_install:"How to install Claude Code",
    prereq_auth_install:"How to authenticate Claude Code",
    prereq_python_guide:"Download from python.org. Check 'Add to PATH' during installation.",
    prereq_node_guide:"Download from nodejs.org. LTS version recommended.",
    prereq_git_guide:"Download from git-scm.com. Use default settings.",
    prereq_pip_guide:"Usually included with Python. If missing, run:",
    prereq_claude_guide:"Run in your terminal:",
    prereq_auth_guide:"Run in your terminal. This will open your browser to log in:",
    platform_windows:"Windows", platform_macos:"macOS", platform_linux:"Linux",
    prereq_python_win:"Download the installer from python.org/downloads and run it. Check 'Add Python to PATH'.",
    prereq_python_mac:"Run: brew install python@3.12 -- or download from python.org",
    prereq_python_linux:"Run: sudo apt install python3 python3-pip -- or sudo dnf install python3",
    prereq_node_win:"Download the LTS installer from nodejs.org and run it.",
    prereq_node_mac:"Run: brew install node",
    prereq_node_linux:"Run: sudo apt install nodejs npm -- or use nvm",
    prereq_git_win:"Download from git-scm.com and run the installer.",
    prereq_git_mac:"Run: brew install git -- or install Xcode Command Line Tools",
    prereq_git_linux:"Run: sudo apt install git",
    handoff_title:"Let Claude Code take it from here",
    handoff_desc:"Open a terminal and run the command below. Claude Code will guide you through the rest.",
    handoff_copy:"Copy command", handoff_copied:"Copied!",
    handoff_status:"Setup Progress",
    handoff_persona:"Persona selection", handoff_workspace_root:"Workspace root directory",
    handoff_workspace:"First workspace", handoff_config:"Configuration",
    handoff_waiting:"Waiting...", handoff_done:"Done",
    handoff_manual:"I want to do it manually in the browser instead",
    handoff_timeout:"Taking a while? Try the manual setup above.",
    ready:"Ready!", ready_desc:"Your workspace has been created.",
    view_ws:"View Workspaces", launch_squad:"Launch Spec Squad",
    persona_title:"How do you work?", persona_desc:"This helps us tailor the experience.",
    persona_guided:"Guided", persona_guided_desc:"New to AI dev. Show me everything.",
    persona_expert:"Expert", persona_expert_desc:"I know what I'm doing. Less hand-holding.",
    persona_tech:"Technical", persona_tech_desc:"I want full control and raw output.",
    ws_title:"Create Your First Workspace",
    ws_name_label:"Workspace name (kebab-case)", ws_root_label:"Workspace root directory",
    ws_name_err:"Must be kebab-case (e.g. my-project)",
    finish:"Finish Setup", finishing:"Setting up...",
  },
  "zh-TW": {
    next:"\\u4E0B\\u4E00\\u6B65", back:"\\u8FD4\\u56DE",
    prereq_title:"\\u7CFB\\u7D71\\u6AA2\\u67E5", prereq_desc:"\\u8B93\\u6211\\u5011\\u78BA\\u8A8D\\u4E00\\u5207\\u6E96\\u5099\\u5C31\\u7DD2\\u3002",
    prereq_recheck:"\\u91CD\\u65B0\\u6AA2\\u67E5", prereq_all_ok:"\\u6240\\u6709\\u524D\\u7F6E\\u689D\\u4EF6\\u5DF2\\u6EFF\\u8DB3\\uFF01",
    prereq_python_purpose:"\\u57F7\\u884C\\u8A18\\u61B6\\u4F3A\\u670D\\u5668\\u8207\\u6280\\u80FD",
    prereq_node_purpose:"\\u5B89\\u88DD Claude Code \\u5FC5\\u9700",
    prereq_git_purpose:"\\u8DE8\\u88DD\\u7F6E\\u540C\\u6B65\\u77E5\\u8B58",
    prereq_pip_purpose:"Python \\u5957\\u4EF6\\u7BA1\\u7406\\u5668",
    prereq_claude_purpose:"AI \\u7A0B\\u5F0F\\u8A2D\\u8A08\\u52A9\\u624B",
    prereq_auth_purpose:"Claude Code \\u8EAB\\u4EFD\\u9A57\\u8B49",
    prereq_checking:"\\u6AA2\\u67E5\\u4E2D\\u22EF", prereq_ok:"\\u6B63\\u5E38", prereq_missing:"\\u7F3A\\u5C11",
    prereq_python_install:"\\u5982\\u4F55\\u5B89\\u88DD Python",
    prereq_node_install:"\\u5982\\u4F55\\u5B89\\u88DD Node.js",
    prereq_git_install:"\\u5982\\u4F55\\u5B89\\u88DD Git",
    prereq_pip_install:"\\u5982\\u4F55\\u5B89\\u88DD pip",
    prereq_claude_install:"\\u5982\\u4F55\\u5B89\\u88DD Claude Code",
    prereq_auth_install:"\\u5982\\u4F55\\u9A57\\u8B49 Claude Code",
    prereq_python_guide:"\\u5F9E python.org \\u4E0B\\u8F09\\u3002\\u5B89\\u88DD\\u6642\\u8ACB\\u52FE\\u9078\\u300CAdd to PATH\\u300D\\u3002",
    prereq_node_guide:"\\u5F9E nodejs.org \\u4E0B\\u8F09\\u3002\\u5EFA\\u8B70\\u4F7F\\u7528 LTS \\u7248\\u672C\\u3002",
    prereq_git_guide:"\\u5F9E git-scm.com \\u4E0B\\u8F09\\u3002\\u4F7F\\u7528\\u9810\\u8A2D\\u8A2D\\u5B9A\\u3002",
    prereq_pip_guide:"\\u901A\\u5E38\\u96A8 Python \\u4E00\\u8D77\\u5B89\\u88DD\\u3002\\u5982\\u679C\\u7F3A\\u5C11\\uFF0C\\u8ACB\\u57F7\\u884C\\uFF1A",
    prereq_claude_guide:"\\u5728\\u7D42\\u7AEF\\u6A5F\\u4E2D\\u57F7\\u884C\\uFF1A",
    prereq_auth_guide:"\\u5728\\u7D42\\u7AEF\\u6A5F\\u4E2D\\u57F7\\u884C\\u3002\\u9019\\u5C07\\u958B\\u555F\\u700F\\u89BD\\u5668\\u9032\\u884C\\u767B\\u5165\\uFF1A",
    platform_windows:"Windows", platform_macos:"macOS", platform_linux:"Linux",
    prereq_python_win:"\\u5F9E python.org/downloads \\u4E0B\\u8F09\\u5B89\\u88DD\\u7A0B\\u5F0F\\u4E26\\u57F7\\u884C\\u3002\\u52FE\\u9078\\u300CAdd Python to PATH\\u300D\\u3002",
    prereq_python_mac:"\\u57F7\\u884C\\uFF1Abrew install python@3.12 -- \\u6216\\u5F9E python.org \\u4E0B\\u8F09",
    prereq_python_linux:"\\u57F7\\u884C\\uFF1Asudo apt install python3 python3-pip -- \\u6216 sudo dnf install python3",
    prereq_node_win:"\\u5F9E nodejs.org \\u4E0B\\u8F09 LTS \\u5B89\\u88DD\\u7A0B\\u5F0F\\u4E26\\u57F7\\u884C\\u3002",
    prereq_node_mac:"\\u57F7\\u884C\\uFF1Abrew install node",
    prereq_node_linux:"\\u57F7\\u884C\\uFF1Asudo apt install nodejs npm -- \\u6216\\u4F7F\\u7528 nvm",
    prereq_git_win:"\\u5F9E git-scm.com \\u4E0B\\u8F09\\u4E26\\u57F7\\u884C\\u5B89\\u88DD\\u7A0B\\u5F0F\\u3002",
    prereq_git_mac:"\\u57F7\\u884C\\uFF1Abrew install git -- \\u6216\\u5B89\\u88DD Xcode Command Line Tools",
    prereq_git_linux:"\\u57F7\\u884C\\uFF1Asudo apt install git",
    handoff_title:"\\u8B93 Claude Code \\u63A5\\u624B\\u5427",
    handoff_desc:"\\u958B\\u555F\\u7D42\\u7AEF\\u6A5F\\uFF0C\\u57F7\\u884C\\u4E0B\\u65B9\\u6307\\u4EE4\\u3002Claude Code \\u6703\\u4E92\\u52D5\\u5F0F\\u5F15\\u5C0E\\u4F60\\u5B8C\\u6210\\u5176\\u9918\\u8A2D\\u5B9A\\u3002",
    handoff_copy:"\\u8907\\u88FD\\u6307\\u4EE4", handoff_copied:"\\u5DF2\\u8907\\u88FD\\uFF01",
    handoff_status:"\\u8A2D\\u5B9A\\u9032\\u5EA6",
    handoff_persona:"\\u4F7F\\u7528\\u65B9\\u5F0F\\u9078\\u64C7", handoff_workspace_root:"\\u5DE5\\u4F5C\\u5340\\u6839\\u76EE\\u9304",
    handoff_workspace:"\\u7B2C\\u4E00\\u500B\\u5DE5\\u4F5C\\u5340", handoff_config:"\\u8A2D\\u5B9A\\u6A94",
    handoff_waiting:"\\u7B49\\u5F85\\u4E2D\\u22EF", handoff_done:"\\u5B8C\\u6210",
    handoff_manual:"\\u6211\\u60F3\\u5728\\u700F\\u89BD\\u5668\\u4E2D\\u624B\\u52D5\\u8A2D\\u5B9A",
    handoff_timeout:"\\u7B49\\u592A\\u4E45\\u4E86\\uFF1F\\u8A66\\u8A66\\u4E0A\\u65B9\\u7684\\u624B\\u52D5\\u8A2D\\u5B9A\\u3002",
    ready:"\\u6E96\\u5099\\u5C31\\u7DD2\\uFF01", ready_desc:"\\u4F60\\u7684\\u5DE5\\u4F5C\\u5340\\u5DF2\\u5EFA\\u7ACB\\u3002",
    view_ws:"\\u6AA2\\u8996\\u5DE5\\u4F5C\\u5340", launch_squad:"\\u555F\\u52D5 Spec Squad",
    persona_title:"\\u4F60\\u7684\\u4F7F\\u7528\\u65B9\\u5F0F\\uFF1F", persona_desc:"\\u9019\\u5E6B\\u52A9\\u6211\\u5011\\u8ABF\\u6574\\u9AD4\\u9A57\\u3002",
    persona_guided:"\\u5F15\\u5C0E\\u6A21\\u5F0F", persona_guided_desc:"AI \\u958B\\u767C\\u65B0\\u624B\\uFF0C\\u5C55\\u793A\\u6240\\u6709\\u7D30\\u7BC0\\u3002",
    persona_expert:"\\u5C08\\u5BB6\\u6A21\\u5F0F", persona_expert_desc:"\\u6211\\u77E5\\u9053\\u6211\\u5728\\u505A\\u4EC0\\u9EBC\\uFF0C\\u5C11\\u4E00\\u9EDE\\u624B\\u628A\\u624B\\u3002",
    persona_tech:"\\u6280\\u8853\\u6A21\\u5F0F", persona_tech_desc:"\\u6211\\u8981\\u5B8C\\u5168\\u63A7\\u5236\\u548C\\u539F\\u59CB\\u8F38\\u51FA\\u3002",
    ws_title:"\\u5EFA\\u7ACB\\u4F60\\u7684\\u7B2C\\u4E00\\u500B\\u5DE5\\u4F5C\\u5340",
    ws_name_label:"\\u5DE5\\u4F5C\\u5340\\u540D\\u7A31\\uFF08kebab-case\\uFF09",
    ws_root_label:"\\u5DE5\\u4F5C\\u5340\\u6839\\u76EE\\u9304",
    ws_name_err:"\\u5FC5\\u9808\\u662F kebab-case\\uFF08\\u4F8B\\u5982 my-project\\uFF09",
    finish:"\\u5B8C\\u6210\\u8A2D\\u5B9A", finishing:"\\u8A2D\\u5B9A\\u4E2D\\u22EF",
  },
  "zh-CN": {
    next:"\\u4E0B\\u4E00\\u6B65", back:"\\u8FD4\\u56DE",
    prereq_title:"\\u7CFB\\u7EDF\\u68C0\\u67E5", prereq_desc:"\\u8BA9\\u6211\\u4EEC\\u786E\\u8BA4\\u4E00\\u5207\\u51C6\\u5907\\u5C31\\u7EEA\\u3002",
    prereq_recheck:"\\u91CD\\u65B0\\u68C0\\u67E5", prereq_all_ok:"\\u6240\\u6709\\u524D\\u7F6E\\u6761\\u4EF6\\u5DF2\\u6EE1\\u8DB3\\uFF01",
    prereq_python_purpose:"\\u8FD0\\u884C\\u8BB0\\u5FC6\\u670D\\u52A1\\u5668\\u4E0E\\u6280\\u80FD",
    prereq_node_purpose:"\\u5B89\\u88C5 Claude Code \\u5FC5\\u9700",
    prereq_git_purpose:"\\u8DE8\\u8BBE\\u5907\\u540C\\u6B65\\u77E5\\u8BC6",
    prereq_pip_purpose:"Python \\u5305\\u7BA1\\u7406\\u5668",
    prereq_claude_purpose:"AI \\u7F16\\u7A0B\\u52A9\\u624B",
    prereq_auth_purpose:"Claude Code \\u8EAB\\u4EFD\\u9A8C\\u8BC1",
    prereq_checking:"\\u68C0\\u67E5\\u4E2D\\u2026", prereq_ok:"\\u6B63\\u5E38", prereq_missing:"\\u7F3A\\u5C11",
    prereq_python_install:"\\u5982\\u4F55\\u5B89\\u88C5 Python",
    prereq_node_install:"\\u5982\\u4F55\\u5B89\\u88C5 Node.js",
    prereq_git_install:"\\u5982\\u4F55\\u5B89\\u88C5 Git",
    prereq_pip_install:"\\u5982\\u4F55\\u5B89\\u88C5 pip",
    prereq_claude_install:"\\u5982\\u4F55\\u5B89\\u88C5 Claude Code",
    prereq_auth_install:"\\u5982\\u4F55\\u9A8C\\u8BC1 Claude Code",
    prereq_python_guide:"\\u4ECE python.org \\u4E0B\\u8F7D\\u3002\\u5B89\\u88C5\\u65F6\\u8BF7\\u52FE\\u9009\\u300CAdd to PATH\\u300D\\u3002",
    prereq_node_guide:"\\u4ECE nodejs.org \\u4E0B\\u8F7D\\u3002\\u5EFA\\u8BAE\\u4F7F\\u7528 LTS \\u7248\\u672C\\u3002",
    prereq_git_guide:"\\u4ECE git-scm.com \\u4E0B\\u8F7D\\u3002\\u4F7F\\u7528\\u9ED8\\u8BA4\\u8BBE\\u7F6E\\u3002",
    prereq_pip_guide:"\\u901A\\u5E38\\u968F Python \\u4E00\\u8D77\\u5B89\\u88C5\\u3002\\u5982\\u679C\\u7F3A\\u5C11\\uFF0C\\u8BF7\\u8FD0\\u884C\\uFF1A",
    prereq_claude_guide:"\\u5728\\u7EC8\\u7AEF\\u4E2D\\u8FD0\\u884C\\uFF1A",
    prereq_auth_guide:"\\u5728\\u7EC8\\u7AEF\\u4E2D\\u8FD0\\u884C\\u3002\\u8FD9\\u5C06\\u6253\\u5F00\\u6D4F\\u89C8\\u5668\\u8FDB\\u884C\\u767B\\u5F55\\uFF1A",
    platform_windows:"Windows", platform_macos:"macOS", platform_linux:"Linux",
    prereq_python_win:"\\u4ECE python.org/downloads \\u4E0B\\u8F7D\\u5B89\\u88C5\\u7A0B\\u5E8F\\u5E76\\u8FD0\\u884C\\u3002\\u52FE\\u9009\\u300CAdd Python to PATH\\u300D\\u3002",
    prereq_python_mac:"\\u8FD0\\u884C\\uFF1Abrew install python@3.12 -- \\u6216\\u4ECE python.org \\u4E0B\\u8F7D",
    prereq_python_linux:"\\u8FD0\\u884C\\uFF1Asudo apt install python3 python3-pip -- \\u6216 sudo dnf install python3",
    prereq_node_win:"\\u4ECE nodejs.org \\u4E0B\\u8F7D LTS \\u5B89\\u88C5\\u7A0B\\u5E8F\\u5E76\\u8FD0\\u884C\\u3002",
    prereq_node_mac:"\\u8FD0\\u884C\\uFF1Abrew install node",
    prereq_node_linux:"\\u8FD0\\u884C\\uFF1Asudo apt install nodejs npm -- \\u6216\\u4F7F\\u7528 nvm",
    prereq_git_win:"\\u4ECE git-scm.com \\u4E0B\\u8F7D\\u5E76\\u8FD0\\u884C\\u5B89\\u88C5\\u7A0B\\u5E8F\\u3002",
    prereq_git_mac:"\\u8FD0\\u884C\\uFF1Abrew install git -- \\u6216\\u5B89\\u88C5 Xcode Command Line Tools",
    prereq_git_linux:"\\u8FD0\\u884C\\uFF1Asudo apt install git",
    handoff_title:"\\u8BA9 Claude Code \\u63A5\\u624B\\u5427",
    handoff_desc:"\\u6253\\u5F00\\u7EC8\\u7AEF\\uFF0C\\u8FD0\\u884C\\u4E0B\\u65B9\\u547D\\u4EE4\\u3002Claude Code \\u4F1A\\u4EA4\\u4E92\\u5F0F\\u5F15\\u5BFC\\u4F60\\u5B8C\\u6210\\u5176\\u4F59\\u8BBE\\u7F6E\\u3002",
    handoff_copy:"\\u590D\\u5236\\u547D\\u4EE4", handoff_copied:"\\u5DF2\\u590D\\u5236\\uFF01",
    handoff_status:"\\u8BBE\\u7F6E\\u8FDB\\u5EA6",
    handoff_persona:"\\u4F7F\\u7528\\u65B9\\u5F0F\\u9009\\u62E9", handoff_workspace_root:"\\u5DE5\\u4F5C\\u533A\\u6839\\u76EE\\u5F55",
    handoff_workspace:"\\u7B2C\\u4E00\\u4E2A\\u5DE5\\u4F5C\\u533A", handoff_config:"\\u914D\\u7F6E\\u6587\\u4EF6",
    handoff_waiting:"\\u7B49\\u5F85\\u4E2D\\u2026", handoff_done:"\\u5B8C\\u6210",
    handoff_manual:"\\u6211\\u60F3\\u5728\\u6D4F\\u89C8\\u5668\\u4E2D\\u624B\\u52A8\\u8BBE\\u7F6E",
    handoff_timeout:"\\u7B49\\u592A\\u4E45\\u4E86\\uFF1F\\u8BD5\\u8BD5\\u4E0A\\u65B9\\u7684\\u624B\\u52A8\\u8BBE\\u7F6E\\u3002",
    ready:"\\u51C6\\u5907\\u5C31\\u7EEA\\uFF01", ready_desc:"\\u4F60\\u7684\\u5DE5\\u4F5C\\u533A\\u5DF2\\u521B\\u5EFA\\u3002",
    view_ws:"\\u67E5\\u770B\\u5DE5\\u4F5C\\u533A", launch_squad:"\\u542F\\u52A8 Spec Squad",
    persona_title:"\\u4F60\\u7684\\u4F7F\\u7528\\u65B9\\u5F0F\\uFF1F", persona_desc:"\\u8FD9\\u5E2E\\u52A9\\u6211\\u4EEC\\u8C03\\u6574\\u4F53\\u9A8C\\u3002",
    persona_guided:"\\u5F15\\u5BFC\\u6A21\\u5F0F", persona_guided_desc:"AI \\u5F00\\u53D1\\u65B0\\u624B\\uFF0C\\u5C55\\u793A\\u6240\\u6709\\u7EC6\\u8282\\u3002",
    persona_expert:"\\u4E13\\u5BB6\\u6A21\\u5F0F", persona_expert_desc:"\\u6211\\u77E5\\u9053\\u6211\\u5728\\u505A\\u4EC0\\u4E48\\uFF0C\\u5C11\\u4E00\\u70B9\\u624B\\u628A\\u624B\\u3002",
    persona_tech:"\\u6280\\u672F\\u6A21\\u5F0F", persona_tech_desc:"\\u6211\\u8981\\u5B8C\\u5168\\u63A7\\u5236\\u548C\\u539F\\u59CB\\u8F93\\u51FA\\u3002",
    ws_title:"\\u521B\\u5EFA\\u4F60\\u7684\\u7B2C\\u4E00\\u4E2A\\u5DE5\\u4F5C\\u533A",
    ws_name_label:"\\u5DE5\\u4F5C\\u533A\\u540D\\u79F0\\uFF08kebab-case\\uFF09",
    ws_root_label:"\\u5DE5\\u4F5C\\u533A\\u6839\\u76EE\\u5F55",
    ws_name_err:"\\u5FC5\\u987B\\u662F kebab-case\\uFF08\\u4F8B\\u5982 my-project\\uFF09",
    finish:"\\u5B8C\\u6210\\u8BBE\\u7F6E", finishing:"\\u8BBE\\u7F6E\\u4E2D\\u2026",
  },
  ja: {
    next:"\\u6B21\\u3078", back:"\\u623B\\u308B",
    prereq_title:"\\u30B7\\u30B9\\u30C6\\u30E0\\u30C1\\u30A7\\u30C3\\u30AF", prereq_desc:"\\u3059\\u3079\\u3066\\u306E\\u6E96\\u5099\\u304C\\u6574\\u3063\\u3066\\u3044\\u308B\\u304B\\u78BA\\u8A8D\\u3057\\u307E\\u3057\\u3087\\u3046\\u3002",
    prereq_recheck:"\\u518D\\u30C1\\u30A7\\u30C3\\u30AF", prereq_all_ok:"\\u3059\\u3079\\u3066\\u306E\\u524D\\u63D0\\u6761\\u4EF6\\u3092\\u6E80\\u305F\\u3057\\u3066\\u3044\\u307E\\u3059\\uFF01",
    prereq_python_purpose:"\\u30E1\\u30E2\\u30EA\\u30B5\\u30FC\\u30D0\\u30FC\\u3068\\u30B9\\u30AD\\u30EB\\u3092\\u5B9F\\u884C",
    prereq_node_purpose:"Claude Code \\u306E\\u30A4\\u30F3\\u30B9\\u30C8\\u30FC\\u30EB\\u306B\\u5FC5\\u8981",
    prereq_git_purpose:"\\u30C7\\u30D0\\u30A4\\u30B9\\u9593\\u3067\\u77E5\\u8B58\\u3092\\u540C\\u671F",
    prereq_pip_purpose:"Python \\u30D1\\u30C3\\u30B1\\u30FC\\u30B8\\u30DE\\u30CD\\u30FC\\u30B8\\u30E3\\u30FC",
    prereq_claude_purpose:"AI \\u30B3\\u30FC\\u30C7\\u30A3\\u30F3\\u30B0\\u30A2\\u30B7\\u30B9\\u30BF\\u30F3\\u30C8",
    prereq_auth_purpose:"Claude Code \\u8A8D\\u8A3C",
    prereq_checking:"\\u78BA\\u8A8D\\u4E2D\\u2026", prereq_ok:"OK", prereq_missing:"\\u4E0D\\u8DB3",
    prereq_python_install:"Python \\u306E\\u30A4\\u30F3\\u30B9\\u30C8\\u30FC\\u30EB\\u65B9\\u6CD5",
    prereq_node_install:"Node.js \\u306E\\u30A4\\u30F3\\u30B9\\u30C8\\u30FC\\u30EB\\u65B9\\u6CD5",
    prereq_git_install:"Git \\u306E\\u30A4\\u30F3\\u30B9\\u30C8\\u30FC\\u30EB\\u65B9\\u6CD5",
    prereq_pip_install:"pip \\u306E\\u30A4\\u30F3\\u30B9\\u30C8\\u30FC\\u30EB\\u65B9\\u6CD5",
    prereq_claude_install:"Claude Code \\u306E\\u30A4\\u30F3\\u30B9\\u30C8\\u30FC\\u30EB\\u65B9\\u6CD5",
    prereq_auth_install:"Claude Code \\u306E\\u8A8D\\u8A3C\\u65B9\\u6CD5",
    prereq_python_guide:"python.org \\u304B\\u3089\\u30C0\\u30A6\\u30F3\\u30ED\\u30FC\\u30C9\\u3002\\u300CAdd to PATH\\u300D\\u306B\\u30C1\\u30A7\\u30C3\\u30AF\\u3002",
    prereq_node_guide:"nodejs.org \\u304B\\u3089\\u30C0\\u30A6\\u30F3\\u30ED\\u30FC\\u30C9\\u3002LTS \\u30D0\\u30FC\\u30B8\\u30E7\\u30F3\\u63A8\\u5968\\u3002",
    prereq_git_guide:"git-scm.com \\u304B\\u3089\\u30C0\\u30A6\\u30F3\\u30ED\\u30FC\\u30C9\\u3002\\u30C7\\u30D5\\u30A9\\u30EB\\u30C8\\u8A2D\\u5B9A\\u3092\\u4F7F\\u7528\\u3002",
    prereq_pip_guide:"\\u901A\\u5E38 Python \\u306B\\u542B\\u307E\\u308C\\u3066\\u3044\\u307E\\u3059\\u3002\\u4E0D\\u8DB3\\u3057\\u3066\\u3044\\u308B\\u5834\\u5408\\u306F\\u5B9F\\u884C\\uFF1A",
    prereq_claude_guide:"\\u30BF\\u30FC\\u30DF\\u30CA\\u30EB\\u3067\\u5B9F\\u884C\\uFF1A",
    prereq_auth_guide:"\\u30BF\\u30FC\\u30DF\\u30CA\\u30EB\\u3067\\u5B9F\\u884C\\u3002\\u30D6\\u30E9\\u30A6\\u30B6\\u304C\\u958B\\u3044\\u3066\\u30ED\\u30B0\\u30A4\\u30F3\\u3067\\u304D\\u307E\\u3059\\uFF1A",
    platform_windows:"Windows", platform_macos:"macOS", platform_linux:"Linux",
    prereq_python_win:"python.org/downloads \\u304B\\u3089\\u30A4\\u30F3\\u30B9\\u30C8\\u30FC\\u30E9\\u30FC\\u3092\\u30C0\\u30A6\\u30F3\\u30ED\\u30FC\\u30C9\\u3057\\u3066\\u5B9F\\u884C\\u3002\\u300CAdd Python to PATH\\u300D\\u306B\\u30C1\\u30A7\\u30C3\\u30AF\\u3002",
    prereq_python_mac:"\\u5B9F\\u884C\\uFF1Abrew install python@3.12 -- \\u307E\\u305F\\u306F python.org \\u304B\\u3089\\u30C0\\u30A6\\u30F3\\u30ED\\u30FC\\u30C9",
    prereq_python_linux:"\\u5B9F\\u884C\\uFF1Asudo apt install python3 python3-pip -- \\u307E\\u305F\\u306F sudo dnf install python3",
    prereq_node_win:"nodejs.org \\u304B\\u3089 LTS \\u30A4\\u30F3\\u30B9\\u30C8\\u30FC\\u30E9\\u30FC\\u3092\\u30C0\\u30A6\\u30F3\\u30ED\\u30FC\\u30C9\\u3057\\u3066\\u5B9F\\u884C\\u3002",
    prereq_node_mac:"\\u5B9F\\u884C\\uFF1Abrew install node",
    prereq_node_linux:"\\u5B9F\\u884C\\uFF1Asudo apt install nodejs npm -- \\u307E\\u305F\\u306F nvm \\u3092\\u4F7F\\u7528",
    prereq_git_win:"git-scm.com \\u304B\\u3089\\u30C0\\u30A6\\u30F3\\u30ED\\u30FC\\u30C9\\u3057\\u3066\\u30A4\\u30F3\\u30B9\\u30C8\\u30FC\\u30E9\\u30FC\\u3092\\u5B9F\\u884C\\u3002",
    prereq_git_mac:"\\u5B9F\\u884C\\uFF1Abrew install git -- \\u307E\\u305F\\u306F Xcode Command Line Tools \\u3092\\u30A4\\u30F3\\u30B9\\u30C8\\u30FC\\u30EB",
    prereq_git_linux:"\\u5B9F\\u884C\\uFF1Asudo apt install git",
    handoff_title:"Claude Code \\u306B\\u4EFB\\u305B\\u307E\\u3057\\u3087\\u3046",
    handoff_desc:"\\u30BF\\u30FC\\u30DF\\u30CA\\u30EB\\u3092\\u958B\\u3044\\u3066\\u4EE5\\u4E0B\\u306E\\u30B3\\u30DE\\u30F3\\u30C9\\u3092\\u5B9F\\u884C\\u3002Claude Code \\u304C\\u6B8B\\u308A\\u306E\\u30BB\\u30C3\\u30C8\\u30A2\\u30C3\\u30D7\\u3092\\u5BFE\\u8A71\\u7684\\u306B\\u30AC\\u30A4\\u30C9\\u3057\\u307E\\u3059\\u3002",
    handoff_copy:"\\u30B3\\u30DE\\u30F3\\u30C9\\u3092\\u30B3\\u30D4\\u30FC", handoff_copied:"\\u30B3\\u30D4\\u30FC\\u3057\\u307E\\u3057\\u305F\\uFF01",
    handoff_status:"\\u30BB\\u30C3\\u30C8\\u30A2\\u30C3\\u30D7\\u9032\\u6357",
    handoff_persona:"\\u30DA\\u30EB\\u30BD\\u30CA\\u9078\\u629E", handoff_workspace_root:"\\u30EF\\u30FC\\u30AF\\u30B9\\u30DA\\u30FC\\u30B9\\u30EB\\u30FC\\u30C8\\u30C7\\u30A3\\u30EC\\u30AF\\u30C8\\u30EA",
    handoff_workspace:"\\u6700\\u521D\\u306E\\u30EF\\u30FC\\u30AF\\u30B9\\u30DA\\u30FC\\u30B9", handoff_config:"\\u8A2D\\u5B9A",
    handoff_waiting:"\\u5F85\\u6A5F\\u4E2D\\u2026", handoff_done:"\\u5B8C\\u4E86",
    handoff_manual:"\\u30D6\\u30E9\\u30A6\\u30B6\\u3067\\u624B\\u52D5\\u8A2D\\u5B9A\\u3057\\u305F\\u3044",
    handoff_timeout:"\\u6642\\u9593\\u304C\\u304B\\u304B\\u3063\\u3066\\u3044\\u307E\\u3059\\u304B\\uFF1F\\u4E0A\\u306E\\u624B\\u52D5\\u30BB\\u30C3\\u30C8\\u30A2\\u30C3\\u30D7\\u3092\\u8A66\\u3057\\u3066\\u304F\\u3060\\u3055\\u3044\\u3002",
    ready:"\\u6E96\\u5099\\u5B8C\\u4E86\\uFF01", ready_desc:"\\u30EF\\u30FC\\u30AF\\u30B9\\u30DA\\u30FC\\u30B9\\u304C\\u4F5C\\u6210\\u3055\\u308C\\u307E\\u3057\\u305F\\u3002",
    view_ws:"\\u30EF\\u30FC\\u30AF\\u30B9\\u30DA\\u30FC\\u30B9\\u3092\\u8868\\u793A", launch_squad:"Spec Squad \\u3092\\u8D77\\u52D5",
    persona_title:"\\u3042\\u306A\\u305F\\u306E\\u4F7F\\u3044\\u65B9\\u306F\\uFF1F", persona_desc:"\\u4F53\\u9A13\\u3092\\u30AB\\u30B9\\u30BF\\u30DE\\u30A4\\u30BA\\u3059\\u308B\\u305F\\u3081\\u306B\\u4F7F\\u3044\\u307E\\u3059\\u3002",
    persona_guided:"\\u30AC\\u30A4\\u30C9", persona_guided_desc:"AI\\u958B\\u767A\\u306F\\u521D\\u3081\\u3066\\u3002\\u5168\\u90E8\\u898B\\u305B\\u3066\\u3002",
    persona_expert:"\\u30A8\\u30AD\\u30B9\\u30D1\\u30FC\\u30C8", persona_expert_desc:"\\u81EA\\u5206\\u3067\\u308F\\u304B\\u308B\\u3002\\u624B\\u53D6\\u308A\\u8DB3\\u53D6\\u308A\\u306F\\u4E0D\\u8981\\u3002",
    persona_tech:"\\u30C6\\u30AF\\u30CB\\u30AB\\u30EB", persona_tech_desc:"\\u5B8C\\u5168\\u306A\\u5236\\u5FA1\\u3068\\u751F\\u306E\\u51FA\\u529B\\u304C\\u6B32\\u3057\\u3044\\u3002",
    ws_title:"\\u6700\\u521D\\u306E\\u30EF\\u30FC\\u30AF\\u30B9\\u30DA\\u30FC\\u30B9\\u3092\\u4F5C\\u6210",
    ws_name_label:"\\u30EF\\u30FC\\u30AF\\u30B9\\u30DA\\u30FC\\u30B9\\u540D\\uFF08kebab-case\\uFF09",
    ws_root_label:"\\u30EF\\u30FC\\u30AF\\u30B9\\u30DA\\u30FC\\u30B9\\u306E\\u30EB\\u30FC\\u30C8\\u30C7\\u30A3\\u30EC\\u30AF\\u30C8\\u30EA",
    ws_name_err:"kebab-case \\u306B\\u3057\\u3066\\u304F\\u3060\\u3055\\u3044\\uFF08\\u4F8B: my-project\\uFF09",
    finish:"\\u30BB\\u30C3\\u30C8\\u30A2\\u30C3\\u30D7\\u5B8C\\u4E86", finishing:"\\u30BB\\u30C3\\u30C8\\u30A2\\u30C3\\u30D7\\u4E2D\\u2026",
  },
  ko: {
    next:"\\uB2E4\\uC74C", back:"\\uB4A4\\uB85C",
    prereq_title:"\\uC2DC\\uC2A4\\uD15C \\uC810\\uAC80", prereq_desc:"\\uBAA8\\uB4E0 \\uC900\\uBE44\\uAC00 \\uB418\\uC5C8\\uB294\\uC9C0 \\uD655\\uC778\\uD558\\uACA0\\uC2B5\\uB2C8\\uB2E4.",
    prereq_recheck:"\\uC7AC\\uC810\\uAC80", prereq_all_ok:"\\uBAA8\\uB4E0 \\uC804\\uC81C \\uC870\\uAC74\\uC744 \\uCDA9\\uC871\\uD588\\uC2B5\\uB2C8\\uB2E4!",
    prereq_python_purpose:"\\uBA54\\uBAA8\\uB9AC \\uC11C\\uBC84\\uC640 \\uC2A4\\uD0AC \\uC2E4\\uD589",
    prereq_node_purpose:"Claude Code \\uC124\\uCE58\\uC5D0 \\uD544\\uC694",
    prereq_git_purpose:"\\uAE30\\uAE30 \\uAC04 \\uC9C0\\uC2DD \\uB3D9\\uAE30\\uD654",
    prereq_pip_purpose:"Python \\uD328\\uD0A4\\uC9C0 \\uAD00\\uB9AC\\uC790",
    prereq_claude_purpose:"AI \\uCF54\\uB529 \\uC5B4\\uC2DC\\uC2A4\\uD134\\uD2B8",
    prereq_auth_purpose:"Claude Code \\uC778\\uC99D",
    prereq_checking:"\\uD655\\uC778 \\uC911\\u2026", prereq_ok:"\\uC815\\uC0C1", prereq_missing:"\\uB204\\uB77D",
    prereq_python_install:"Python \\uC124\\uCE58 \\uBC29\\uBC95",
    prereq_node_install:"Node.js \\uC124\\uCE58 \\uBC29\\uBC95",
    prereq_git_install:"Git \\uC124\\uCE58 \\uBC29\\uBC95",
    prereq_pip_install:"pip \\uC124\\uCE58 \\uBC29\\uBC95",
    prereq_claude_install:"Claude Code \\uC124\\uCE58 \\uBC29\\uBC95",
    prereq_auth_install:"Claude Code \\uC778\\uC99D \\uBC29\\uBC95",
    prereq_python_guide:"python.org\\uC5D0\\uC11C \\uB2E4\\uC6B4\\uB85C\\uB4DC. \\uC124\\uCE58 \\uC2DC 'Add to PATH'\\uB97C \\uCCB4\\uD06C\\uD558\\uC138\\uC694.",
    prereq_node_guide:"nodejs.org\\uC5D0\\uC11C \\uB2E4\\uC6B4\\uB85C\\uB4DC. LTS \\uBC84\\uC804\\uC744 \\uAD8C\\uC7A5\\uD569\\uB2C8\\uB2E4.",
    prereq_git_guide:"git-scm.com\\uC5D0\\uC11C \\uB2E4\\uC6B4\\uB85C\\uB4DC. \\uAE30\\uBCF8 \\uC124\\uC815\\uC744 \\uC0AC\\uC6A9\\uD558\\uC138\\uC694.",
    prereq_pip_guide:"\\uBCF4\\uD1B5 Python\\uC5D0 \\uD3EC\\uD568\\uB418\\uC5B4 \\uC788\\uC2B5\\uB2C8\\uB2E4. \\uB204\\uB77D\\uB41C \\uACBD\\uC6B0 \\uC2E4\\uD589:",
    prereq_claude_guide:"\\uD130\\uBBF8\\uB110\\uC5D0\\uC11C \\uC2E4\\uD589:",
    prereq_auth_guide:"\\uD130\\uBBF8\\uB110\\uC5D0\\uC11C \\uC2E4\\uD589. \\uBE0C\\uB77C\\uC6B0\\uC800\\uAC00 \\uC5F4\\uB824 \\uB85C\\uADF8\\uC778\\uD560 \\uC218 \\uC788\\uC2B5\\uB2C8\\uB2E4:",
    platform_windows:"Windows", platform_macos:"macOS", platform_linux:"Linux",
    prereq_python_win:"python.org/downloads\\uC5D0\\uC11C \\uC124\\uCE58 \\uD504\\uB85C\\uADF8\\uB7A8\\uC744 \\uB2E4\\uC6B4\\uB85C\\uB4DC\\uD558\\uC5EC \\uC2E4\\uD589. 'Add Python to PATH'\\uB97C \\uCCB4\\uD06C.",
    prereq_python_mac:"\\uC2E4\\uD589: brew install python@3.12 -- \\uB610\\uB294 python.org\\uC5D0\\uC11C \\uB2E4\\uC6B4\\uB85C\\uB4DC",
    prereq_python_linux:"\\uC2E4\\uD589: sudo apt install python3 python3-pip -- \\uB610\\uB294 sudo dnf install python3",
    prereq_node_win:"nodejs.org\\uC5D0\\uC11C LTS \\uC124\\uCE58 \\uD504\\uB85C\\uADF8\\uB7A8\\uC744 \\uB2E4\\uC6B4\\uB85C\\uB4DC\\uD558\\uC5EC \\uC2E4\\uD589.",
    prereq_node_mac:"\\uC2E4\\uD589: brew install node",
    prereq_node_linux:"\\uC2E4\\uD589: sudo apt install nodejs npm -- \\uB610\\uB294 nvm \\uC0AC\\uC6A9",
    prereq_git_win:"git-scm.com\\uC5D0\\uC11C \\uB2E4\\uC6B4\\uB85C\\uB4DC\\uD558\\uC5EC \\uC124\\uCE58 \\uD504\\uB85C\\uADF8\\uB7A8\\uC744 \\uC2E4\\uD589.",
    prereq_git_mac:"\\uC2E4\\uD589: brew install git -- \\uB610\\uB294 Xcode Command Line Tools \\uC124\\uCE58",
    prereq_git_linux:"\\uC2E4\\uD589: sudo apt install git",
    handoff_title:"Claude Code\\uC5D0 \\uB9E1\\uAE30\\uC138\\uC694",
    handoff_desc:"\\uD130\\uBBF8\\uB110\\uC744 \\uC5F4\\uACE0 \\uC544\\uB798 \\uBA85\\uB839\\uC744 \\uC2E4\\uD589\\uD558\\uC138\\uC694. Claude Code\\uAC00 \\uB098\\uBA38\\uC9C0 \\uC124\\uC815\\uC744 \\uB300\\uD654\\uC2DD\\uC73C\\uB85C \\uC548\\uB0B4\\uD569\\uB2C8\\uB2E4.",
    handoff_copy:"\\uBA85\\uB839 \\uBCF5\\uC0AC", handoff_copied:"\\uBCF5\\uC0AC\\uB428!",
    handoff_status:"\\uC124\\uC815 \\uC9C4\\uD589 \\uC0C1\\uD669",
    handoff_persona:"\\uD398\\uB974\\uC18C\\uB098 \\uC120\\uD0DD", handoff_workspace_root:"\\uC6CC\\uD06C\\uC2A4\\uD398\\uC774\\uC2A4 \\uB8E8\\uD2B8 \\uB514\\uB809\\uD1A0\\uB9AC",
    handoff_workspace:"\\uCCAB \\uBC88\\uC9F8 \\uC6CC\\uD06C\\uC2A4\\uD398\\uC774\\uC2A4", handoff_config:"\\uC124\\uC815",
    handoff_waiting:"\\uB300\\uAE30 \\uC911\\u2026", handoff_done:"\\uC644\\uB8CC",
    handoff_manual:"\\uBE0C\\uB77C\\uC6B0\\uC800\\uC5D0\\uC11C \\uC218\\uB3D9\\uC73C\\uB85C \\uC124\\uC815\\uD558\\uACE0 \\uC2F6\\uC2B5\\uB2C8\\uB2E4",
    handoff_timeout:"\\uC2DC\\uAC04\\uC774 \\uC624\\uB798 \\uAC78\\uB9AC\\uB098\\uC694? \\uC704\\uC758 \\uC218\\uB3D9 \\uC124\\uC815\\uC744 \\uC2DC\\uB3C4\\uD558\\uC138\\uC694.",
    ready:"\\uC900\\uBE44 \\uC644\\uB8CC!", ready_desc:"\\uC6CC\\uD06C\\uC2A4\\uD398\\uC774\\uC2A4\\uAC00 \\uC0DD\\uC131\\uB418\\uC5C8\\uC2B5\\uB2C8\\uB2E4.",
    view_ws:"\\uC6CC\\uD06C\\uC2A4\\uD398\\uC774\\uC2A4 \\uBCF4\\uAE30", launch_squad:"Spec Squad \\uC2DC\\uC791",
    persona_title:"\\uC5B4\\uB5BB\\uAC8C \\uC791\\uC5C5\\uD558\\uC2DC\\uB098\\uC694?", persona_desc:"\\uACBD\\uD5D8\\uC744 \\uB9DE\\uCDA4\\uD654\\uD558\\uB294 \\uB370 \\uC0AC\\uC6A9\\uB429\\uB2C8\\uB2E4.",
    persona_guided:"\\uAC00\\uC774\\uB4DC", persona_guided_desc:"AI \\uAC1C\\uBC1C\\uC774 \\uCC98\\uC74C\\uC774\\uC5D0\\uC694. \\uB2E4 \\uBCF4\\uC5EC\\uC8FC\\uC138\\uC694.",
    persona_expert:"\\uC804\\uBB38\\uAC00", persona_expert_desc:"\\uBB58 \\uD574\\uC57C \\uD558\\uB294\\uC9C0 \\uC54C\\uC544\\uC694. \\uB35C \\uC548\\uB0B4\\uD574\\uC8FC\\uC138\\uC694.",
    persona_tech:"\\uAE30\\uC220", persona_tech_desc:"\\uC644\\uC804\\uD55C \\uC81C\\uC5B4\\uC640 \\uC6D0\\uC2DC \\uCD9C\\uB825\\uC744 \\uC6D0\\uD569\\uB2C8\\uB2E4.",
    ws_title:"\\uCCAB \\uBC88\\uC9F8 \\uC6CC\\uD06C\\uC2A4\\uD398\\uC774\\uC2A4 \\uC0DD\\uC131",
    ws_name_label:"\\uC6CC\\uD06C\\uC2A4\\uD398\\uC774\\uC2A4 \\uC774\\uB984 (kebab-case)",
    ws_root_label:"\\uC6CC\\uD06C\\uC2A4\\uD398\\uC774\\uC2A4 \\uB8E8\\uD2B8 \\uB514\\uB809\\uD1A0\\uB9AC",
    ws_name_err:"kebab-case\\uC5EC\\uC57C \\uD569\\uB2C8\\uB2E4 (\\uC608: my-project)",
    finish:"\\uC124\\uC815 \\uC644\\uB8CC", finishing:"\\uC124\\uC815 \\uC911\\u2026",
  },
};

function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function T(key) { return (I18N[lang] || I18N.en)[key] || (I18N.en[key] || key); }

function applyI18n() {
  document.querySelectorAll('[data-i18n]').forEach(function(el) {
    var k = el.getAttribute('data-i18n');
    var t = T(k);
    if (t !== k) el.textContent = t;
  });
  if (currentAppliedLang !== lang && lastPrereqData) {
    currentAppliedLang = lang;
    renderPrereqs(lastPrereqData);
  }
  currentAppliedLang = lang;
}

function goPage(n) {
  document.querySelectorAll('.page').forEach(function(p) { p.classList.remove('active'); });
  var target = document.getElementById('page-' + n);
  if (target) target.classList.add('active');
  for (var i = 0; i < 3; i++) {
    var d = document.getElementById('dot-' + i);
    if (d) d.className = 'progress-dot' + (i < n ? ' done' : i === n ? ' current' : '');
  }
  if (n === 1 && !checksLoaded) runChecks();
  if (n === 2 && !sessionId) startHandoff();
  applyI18n();
}

function pickLang(l, el) {
  lang = l;
  el.closest('.lang-grid').querySelectorAll('.lang-card').forEach(function(c) { c.classList.remove('selected'); });
  el.classList.add('selected');
  document.getElementById('lang-next').disabled = false;
  document.querySelectorAll('.tagline-stack p').forEach(function(p) {
    var isMatch = p.getAttribute('data-lang') === l;
    p.style.opacity = isMatch ? '1' : '0.35';
    p.style.color = isMatch ? '#58a6ff' : '';
    if (isMatch) p.classList.add('highlight'); else p.classList.remove('highlight');
  });
  applyI18n();
}

function renderPrereqs(data) {
  var container = document.getElementById('prereq-cards');
  container.innerHTML = '';
  var allOk = true;
  (data.checks || []).forEach(function(c) {
    var info = PREREQ_INFO[c.name];
    if (!info) return;
    var html = '<div class="prereq-header"><div>';
    html += '<span class="prereq-name">' + esc(info.display) + '</span>';
    if (c.version) html += '<span class="prereq-version">(' + esc(c.version) + ')</span>';
    html += '</div>';
    html += '<span class="prereq-status ' + (c.ok ? 'ok' : 'fail') + '">' + esc(T(c.ok ? 'prereq_ok' : 'prereq_missing')) + '</span>';
    html += '</div>';
    html += '<div class="prereq-purpose">' + esc(T(info.purposeKey)) + '</div>';
    if (!c.ok) {
      allOk = false;
      html += '<button class="toggle-guide" onclick="toggleGuide(this.dataset.name)" data-name="' + c.name + '">';
      html += esc(T(info.installKey)) + ' &#9660;</button>';
      html += '<div class="prereq-guide" id="guide-' + c.name + '">';
      html += '<p>' + esc(T(info.guideKey)) + '</p>';
      if (info.platforms) {
        var plats = ['windows','macos','linux'];
        html += '<div class="platform-tabs">';
        plats.forEach(function(p) {
          html += '<button class="platform-tab' + (p === detectedPlatform ? ' active' : '') + '" ';
          html += 'onclick="switchTab(this.dataset.prereq,this.dataset.plat)" ';
          html += 'data-prereq="' + c.name + '" data-plat="' + p + '">';
          html += esc(T('platform_' + p)) + '</button>';
        });
        html += '</div>';
        plats.forEach(function(p) {
          html += '<div class="platform-content' + (p === detectedPlatform ? ' active' : '') + '" ';
          html += 'id="' + c.name + '-' + p + '">';
          html += '<p>' + esc(T(info.platforms[p].descKey)) + '</p>';
          html += '</div>';
        });
      } else if (info.cmd) {
        html += '<code>' + esc(info.cmd) + '</code>';
      }
      html += '</div>';
    }
    var card = document.createElement('div');
    card.className = 'prereq-card ' + (c.ok ? 'ok' : 'fail');
    card.innerHTML = html;
    container.appendChild(card);
  });
  document.getElementById('prereq-next').disabled = !allOk;
  document.getElementById('prereq-summary').style.display = allOk ? 'block' : 'none';
}

async function runChecks() {
  var container = document.getElementById('prereq-cards');
  container.innerHTML = '<div style="text-align:center;padding:20px;color:#8b949e;"><span class="spinner"></span> ' + esc(T('prereq_checking')) + '</div>';
  document.getElementById('prereq-next').disabled = true;
  document.getElementById('prereq-summary').style.display = 'none';
  try {
    var res = await fetch('/api/onboarding/check', {method:'POST'});
    var data = await res.json();
    detectedPlatform = data.platform || 'windows';
    defaultRoot = data.default_root || '';
    lastPrereqData = data;
    checksLoaded = true;
    renderPrereqs(data);
  } catch(e) {
    container.innerHTML = '<p style="color:#f85149;">Error checking prerequisites: ' + esc(e.message) + '</p>';
  }
}

function toggleGuide(name) {
  var g = document.getElementById('guide-' + name);
  if (g) g.classList.toggle('open');
}

function switchTab(prereq, plat) {
  var parent = document.getElementById('guide-' + prereq);
  if (!parent) return;
  parent.querySelectorAll('.platform-tab').forEach(function(t) { t.classList.remove('active'); });
  parent.querySelectorAll('.platform-content').forEach(function(c) { c.classList.remove('active'); });
  var tab = parent.querySelector('.platform-tab[data-plat="' + plat + '"]');
  var content = document.getElementById(prereq + '-' + plat);
  if (tab) tab.classList.add('active');
  if (content) content.classList.add('active');
}

async function startHandoff() {
  try {
    var res = await fetch('/api/onboarding/handoff', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({lang: lang})
    });
    var data = await res.json();
    if (data.ok) {
      sessionId = data.session_id;
      var dir = data.session_dir;
      var cmd = document.getElementById('handoff-cmd');
      cmd.textContent = '$ cd "' + dir + '"\\n$ claude';
      document.getElementById('handoff-terminal').style.display = 'block';
      document.getElementById('handoff-progress').style.display = 'block';
      startPolling();
    }
  } catch(e) { console.error('Handoff error:', e); }
}

function startPolling() {
  if (pollTimer) return;
  pollTimer = setInterval(pollState, 2000);
}

async function pollState() {
  pollCount++;
  if (pollCount > 30) {
    document.getElementById('handoff-timeout-msg').style.display = 'block';
  }
  try {
    var res = await fetch('/api/onboarding/state?session_id=' + encodeURIComponent(sessionId));
    var data = await res.json();
    if (data.ok && data.state) {
      updateProgress(data.state);
      if (data.state.phase === 'complete') {
        clearInterval(pollTimer);
        showDone();
      }
    }
  } catch(e) {}
}

function updateProgress(state) {
  var items = [
    {id:'prog-persona', done: !!state.persona},
    {id:'prog-workspace_root', done: !!state.workspace_root},
    {id:'prog-workspace', done: !!state.workspace_created},
    {id:'prog-config', done: !!state.config_saved},
  ];
  items.forEach(function(item) {
    var el = document.getElementById(item.id);
    if (!el) return;
    var icon = el.querySelector('.prog-icon');
    var status = el.querySelector('.prog-status');
    if (item.done) {
      icon.textContent = '\\u2713';
      icon.className = 'prog-icon done';
      status.textContent = T('handoff_done');
      status.className = 'prog-status done';
    }
  });
}

function showDone() {
  document.querySelectorAll('.page').forEach(function(p) { p.classList.remove('active'); });
  document.getElementById('page-done').classList.add('active');
  document.querySelectorAll('.progress-dot').forEach(function(d) { d.className = 'progress-dot done'; });
  applyI18n();
}

function copyCmd() {
  var text = document.getElementById('handoff-cmd').textContent;
  var clean = text.replace(/^\\$ /gm, '');
  navigator.clipboard.writeText(clean).then(function() {
    var btn = document.getElementById('copy-btn');
    btn.textContent = T('handoff_copied');
    setTimeout(function() { btn.textContent = T('handoff_copy'); }, 2000);
  });
}

function showFallback() {
  document.getElementById('fallback-section').style.display = 'block';
  if (defaultRoot) {
    var el = document.getElementById('ws-root');
    if (el && !el.value) el.value = defaultRoot;
  }
  applyI18n();
}

function pickPersona(p, el) {
  persona = p;
  document.querySelectorAll('#fallback-section .persona-card').forEach(function(c) { c.classList.remove('selected'); });
  el.classList.add('selected');
  validateWsName();
}

function validateWsName() {
  var v = document.getElementById('ws-name').value.trim();
  var err = document.getElementById('ws-name-err');
  var ok = KEBAB.test(v);
  err.textContent = v && !ok ? T('ws_name_err') : '';
  document.getElementById('finish-btn').disabled = !(ok && persona);
}

async function finishManual() {
  var name = document.getElementById('ws-name').value.trim();
  var root = document.getElementById('ws-root').value.trim();
  var btn = document.getElementById('finish-btn');
  btn.disabled = true;
  btn.textContent = T('finishing');
  try {
    var res = await fetch('/api/onboarding/complete', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({persona:persona, lang:lang, workspace_name:name, workspace_root:root})
    });
    var data = await res.json();
    if (data.ok) { showDone(); }
    else { btn.textContent = T('finish'); btn.disabled = false; alert(data.error || 'Setup failed'); }
  } catch(e) {
    btn.textContent = T('finish');
    btn.disabled = false;
    alert('Connection error: ' + e.message);
  }
}

// Mascot bubble messages (per language)
var MASCOT_MSGS = {
  en: ["Hi there! Let's set up!", "Almost there...", "You got this!",
       "Claude Code is awesome~", "Welcome aboard!"],
  "zh-TW": ["\\u55E8\\uFF01\\u4F86\\u8A2D\\u5B9A\\u5427\\uFF01",
             "\\u52A0\\u6CB9\\uFF0C\\u5FEB\\u597D\\u4E86~",
             "\\u6B61\\u8FCE\\u52A0\\u5165\\uFF01",
             "Claude Code \\u8D85\\u68D2\\u7684\\uFF5E",
             "\\u4F60\\u53EF\\u4EE5\\u7684\\uFF01"],
  "zh-CN": ["\\u55E8\\uFF01\\u6765\\u8BBE\\u7F6E\\u5427\\uFF01",
             "\\u52A0\\u6CB9\\uFF0C\\u5FEB\\u597D\\u4E86~",
             "\\u6B22\\u8FCE\\u52A0\\u5165\\uFF01",
             "Claude Code \\u8D85\\u68D2\\u7684\\uFF5E",
             "\\u4F60\\u53EF\\u4EE5\\u7684\\uFF01"],
  ja: ["\\u3053\\u3093\\u306B\\u3061\\u306F\\uFF01\\u30BB\\u30C3\\u30C8\\u30A2\\u30C3\\u30D7\\u3057\\u3088\\u3046\\uFF01",
       "\\u3082\\u3046\\u5C11\\u3057~",
       "\\u3088\\u3046\\u3053\\u305D\\uFF01",
       "Claude Code \\u6700\\u9AD8\\uFF5E",
       "\\u304C\\u3093\\u3070\\u3063\\u3066\\uFF01"],
  ko: ["\\uC548\\uB155\\uD558\\uC138\\uC694! \\uC124\\uC815\\uD558\\uC790!",
       "\\uAC70\\uC758 \\uB2E4 \\uB410\\uC5B4\\uC694~",
       "\\uD658\\uC601\\uD569\\uB2C8\\uB2E4!",
       "Claude Code \\uCD5C\\uACE0~",
       "\\uD560 \\uC218 \\uC788\\uC5B4\\uC694!"],
};
(function initMascot() {
  var bubble = document.getElementById('mascot-bubble');
  if (!bubble) return;
  function setMsg() {
    var msgs = MASCOT_MSGS[lang] || MASCOT_MSGS.en;
    bubble.textContent = msgs[Math.floor(Math.random() * msgs.length)];
  }
  setMsg();
  setInterval(setMsg, 6000);
  document.querySelector('.mascot-wrap').addEventListener('mouseenter', setMsg);
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
