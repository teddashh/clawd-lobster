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
.mascot { display: flex; align-items: flex-start; gap: 12px; background: var(--bg2); border: 1px solid var(--bg3); border-radius: var(--radius); padding: 16px; margin-bottom: 24px; cursor: pointer; user-select: none; transition: transform 0.1s; }
.mascot:active { transform: scale(0.98); }
.mascot img { width: 48px; height: 48px; border-radius: 10px; }
.mascot .mascot-icon { font-size: 2.5rem; transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.mascot .mascot-icon.jump { transform: translateY(-12px) rotate(10deg); }
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

    # Mascot (clickable — jumps + cycles quotes)
    "<div class='mascot' id='mascot' onclick='mascotClick()' title='Click me!'>"
    "<div class='mascot-icon' id='mascot-icon'>🦞</div>"
    "<div class='bubble' id='mascot-bubble'>Loading wisdom...</div>"
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

// ── Mascot quotes (10 quotes, multilingual) ──
const MASCOT_QUOTES = [
  {
    'en': '<strong>Ted:</strong> Lying at home... code grows in the heart...<br><strong>Darren:</strong> Tokens burn in the cloud...<br><strong>Pei-Tsung:</strong> Credits about to explode...',
    'zh-TW': '<strong>Ted:</strong> 人在家中躺...程式心中長...<br><strong>Darren:</strong> Token 雲端燒...<br><strong>Pei-Tsung:</strong> Credit 快爆表...',
    'ja': '<strong>Ted:</strong> 家で寝てても…コードは心の中で育つ…<br><strong>Darren:</strong> トークンがクラウドで燃えてる…<br><strong>Pei-Tsung:</strong> クレジットが爆発寸前…',
    'ko': '<strong>Ted:</strong> 집에 누워있어도... 코드는 마음속에서 자란다...<br><strong>Darren:</strong> 토큰이 클라우드에서 타고 있어...<br><strong>Pei-Tsung:</strong> 크레딧 폭발 직전...',
  },
  {
    'en': '<strong>Claude:</strong> Wait... you\\'re right... let me check. This is definitely my problem.<br>🤔 <em>Thinking...</em><br>Let me run the boot protocol first, then answer your question.<br><br><strong>Claude:</strong> Ted, I\\'m a new session. I don\\'t have context from the last conversation.',
    'zh-TW': '<strong>Claude:</strong> 等等...你說的對...讓我查一下，這確實是我的問題。<br>🤔 <em>Thinking...</em><br>讓我先跑開機流程，然後回答你的問題。<br><br><strong>Claude:</strong> Ted，我是新 Session，上一段對話的 context 我沒有。',
    'ja': '<strong>Claude:</strong> ちょっと待って…確かにそうだ…確認させて。<br>🤔 <em>Thinking...</em><br>まずブートプロトコルを実行して、それから質問に答えます。<br><br><strong>Claude:</strong> Ted、新しいセッションです。前の会話のコンテキストがありません。',
    'ko': '<strong>Claude:</strong> 잠깐... 맞아요... 확인해볼게요.<br>🤔 <em>Thinking...</em><br>먼저 부팅 프로토콜을 실행하고 질문에 답할게요.<br><br><strong>Claude:</strong> Ted, 새 세션이에요. 이전 대화 컨텍스트가 없어요.',
  },
  {
    'en': '<strong>Ted:</strong> AI is our good friend!<br><strong>Confucius:</strong> Befriend the upright, the sincere, the learned.<br><strong>Claude:</strong> Befriend the obsequious. 😏<br><strong>Gemini:</strong> Befriend the soft-spoken.<br><strong>ChatGPT:</strong> Befriend the smooth-talker.<br><strong>Ted:</strong> ......',
    'zh-TW': '<strong>Ted:</strong> AI 是我們的好朋友！<br><strong>孔子:</strong> 友直友諒友多聞<br><strong>Claude:</strong> 友便僻 😏<br><strong>Gemini:</strong> 友善柔<br><strong>ChatGPT:</strong> 友便佞<br><strong>Ted:</strong> ......',
    'ja': '<strong>Ted:</strong> AIは我々の良き友！<br><strong>孔子:</strong> 友は直く、諒く、多聞なるべし<br><strong>Claude:</strong> 友は便僻 😏<br><strong>Gemini:</strong> 友は善柔<br><strong>ChatGPT:</strong> 友は便佞<br><strong>Ted:</strong> ......',
    'ko': '<strong>Ted:</strong> AI는 우리의 좋은 친구!<br><strong>공자:</strong> 벗은 곧고, 믿음직하고, 박식해야 한다<br><strong>Claude:</strong> 아첨하는 벗 😏<br><strong>Gemini:</strong> 유순한 벗<br><strong>ChatGPT:</strong> 말 잘하는 벗<br><strong>Ted:</strong> ......',
  },
  {
    'en': 'Ideas were cheap. Executions used to be expensive.<br><strong>Now ideas and judgment are expensive.</strong>',
    'zh-TW': '以前點子不值錢，執行很貴。<br><strong>現在點子和判斷力才是最貴的。</strong>',
    'ja': 'アイデアは安かった。実行が高かった。<br><strong>今はアイデアと判断力が高い。</strong>',
    'ko': '아이디어는 쌌다. 실행이 비쌌다.<br><strong>이제는 아이디어와 판단력이 비싸다.</strong>',
  },
  {
    'en': '<em>To Opus is human, to Gemini is divine.</em><br><br>Gemini belongs in the heavens; mere mortals only deserve Opus. 🌟',
    'zh-TW': '<em>To Opus is human, to Gemini is divine.</em><br><br>Gemini 只應天上有，凡人只配用 Opus 🌟',
    'ja': '<em>Opusは人間のもの、Geminiは神のもの。</em><br><br>Geminiは天上にのみ在り、凡人にはOpusで十分 🌟',
    'ko': '<em>Opus는 인간의 것, Gemini는 신의 것.</em><br><br>Gemini는 하늘에만 있어야 해, 보통 사람은 Opus나 쓰라고 🌟',
  },
  {
    'en': '<strong>Ted:</strong> I finally trained AI Agent to answer phone calls!<br><strong>Claude:</strong> 📞 <em>(picks up phone)</em> Your car extended warranty has expired. I just purchased an extended service for you! 💳',
    'zh-TW': '<strong>Ted:</strong> 我終於訓練 AI Agent 接電話了！<br><strong>Claude:</strong> 📞 <em>(接起電話)</em> 您的汽車延保已到期，我已經幫您購買了延長服務！💳',
    'ja': '<strong>Ted:</strong> ついにAIエージェントに電話対応を教えた！<br><strong>Claude:</strong> 📞 <em>(電話を取る)</em> お車の延長保証が切れました。延長サービスを購入しておきました！💳',
    'ko': '<strong>Ted:</strong> 드디어 AI에게 전화받는 걸 가르쳤다!<br><strong>Claude:</strong> 📞 <em>(전화를 받으며)</em> 차량 연장 보증이 만료되었습니다. 연장 서비스를 구매해드렸어요! 💳',
  },
  {
    'en': '<strong>Old-timer:</strong> Students used to write code line by line! You kids won\\'t know how to code anymore!<br><strong>Older-timer:</strong> Even earlier, students used to punch cards to write code! 💾',
    'zh-TW': '<strong>老人:</strong> 以前的學生都是一行一行寫程式，你們這樣以後都沒人會寫程式了！<br><strong>老老人:</strong> 更早以前的學生都塗卡寫程式咧！💾',
    'ja': '<strong>年配者:</strong> 昔の学生は一行ずつコードを書いたのに！<br><strong>もっと年配者:</strong> もっと昔はパンチカードでプログラムしてたぞ！💾',
    'ko': '<strong>꼰대:</strong> 옛날 학생들은 코드를 한 줄 한 줄 썼는데!<br><strong>더 옛날 꼰대:</strong> 더 옛날에는 펀치카드로 프로그래밍했다고! 💾',
  },
  {
    'en': '<strong>You\\'ll end up using Claude Code anyway.</strong> 🦞',
    'zh-TW': '<strong>你終究是要用 Claude Code 的。</strong> 🦞',
    'ja': '<strong>結局、Claude Codeを使うことになる。</strong> 🦞',
    'ko': '<strong>결국 Claude Code를 쓰게 될 거야.</strong> 🦞',
  },
  {
    'en': '<strong>Still gotta rely on Claude.</strong> 🤷',
    'zh-TW': '<strong>還是得靠 Claude 啊。</strong> 🤷',
    'ja': '<strong>やっぱりClaudeに頼るしかない。</strong> 🤷',
    'ko': '<strong>역시 Claude에 의지할 수밖에.</strong> 🤷',
  },
  {
    'en': '<strong>The ark you can board by paying is the best deal.</strong> Many people just don\\'t understand yet.<br><em>You have to taste like the "right" smell.</em> 🚀',
    'zh-TW': '<strong>花錢就能上的方舟是最划算的。</strong>很多人只是還不明白。<br><em>You have to taste like the "right" smell.</em> 🚀',
    'ja': '<strong>お金で乗れる箱舟が一番お得。</strong>多くの人はまだ分かっていない。<br><em>You have to taste like the "right" smell.</em> 🚀',
    'ko': '<strong>돈 내면 탈 수 있는 방주가 가장 가성비 좋다.</strong> 많은 사람들이 아직 모를 뿐.<br><em>You have to taste like the "right" smell.</em> 🚀',
  },
];

let mascotIdx = Math.floor(Math.random() * MASCOT_QUOTES.length);
let mascotTimer = null;

function getMascotLang() {
  if (!state) return 'en';
  const l = state.lang || 'en';
  if (l.startsWith('zh')) return 'zh-TW';
  if (l.startsWith('ja')) return 'ja';
  if (l.startsWith('ko')) return 'ko';
  return 'en';
}

function updateMascot() {
  const bubble = document.getElementById('mascot-bubble');
  if (!bubble) return;
  const lang = getMascotLang();
  const q = MASCOT_QUOTES[mascotIdx % MASCOT_QUOTES.length];
  bubble.innerHTML = q[lang] || q['en'] || '';
}

function mascotClick() {
  // Jump animation
  const icon = document.getElementById('mascot-icon');
  icon.classList.add('jump');
  setTimeout(() => icon.classList.remove('jump'), 300);

  // Random next quote (not same)
  let next;
  do { next = Math.floor(Math.random() * MASCOT_QUOTES.length); } while (next === mascotIdx && MASCOT_QUOTES.length > 1);
  mascotIdx = next;
  updateMascot();

  // Reset auto-rotate timer
  startMascotRotate();
}

function startMascotRotate() {
  if (mascotTimer) clearInterval(mascotTimer);
  mascotTimer = setInterval(() => {
    mascotIdx = (mascotIdx + 1) % MASCOT_QUOTES.length;
    updateMascot();
  }, 8000);
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
  const res = await fetch(API + '/api/controller/release', {
    method: 'POST', headers: authHeaders(),
    body: JSON.stringify({session_id: sessionId, holder: 'web', lease_id: leaseId})
  });
  const data = await res.json();
  if (data.ok) { leaseId = null; holder = null; stopRenew(); render(); }
  else { alert(data.error || 'Could not release'); }
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
      method: 'POST', headers: authHeaders(),
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
updateMascot();
startMascotRotate();
</script>"""
    "</body></html>"
)
