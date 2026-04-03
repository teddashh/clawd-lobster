# NotebookLM Bridge — Free RAG + Content Engine for Workspaces

Connect any workspace to Google NotebookLM. Push your docs as sources,
query with Gemini, generate slides/infographics/podcasts — all from terminal.
Zero token cost. Powered by notebooklm-py.

---

## Setup (first time)

### Step 1: Install notebooklm-py
```bash
pip install notebooklm-py
python -m playwright install chromium   # needed for login only
```

### Step 2: Login to Google
```bash
python -m notebooklm login
```
A browser opens. Log into your Google account. Wait for the NotebookLM
homepage to load. Press Enter. Done. Auth saved to `~/.notebooklm/`.

### Step 3: Verify
```bash
python -m notebooklm auth check
```
All checks should be green. If not, re-run login.

### Step 4: Set language (optional)
```bash
python -m notebooklm language set zh_Hant   # or en, ja, etc.
```

---

## Workspace Integration

### When a workspace is created (/spec new)
If this skill is enabled, automatically:
1. Create a NotebookLM notebook with the workspace name
2. Store the notebook ID in workspace config
3. Push initial sources (README.md, CLAUDE.md)

```bash
PYTHONIOENCODING=utf-8 python -m notebooklm create "<workspace-name>"
# Returns notebook ID — save it
```

### After blitz completes
Push updated docs as sources:
```bash
NB="<notebook-id>"
PYTHONIOENCODING=utf-8 python -m notebooklm source add "<workspace>/README.md" -n $NB --title "README"
PYTHONIOENCODING=utf-8 python -m notebooklm source add "<workspace>/openspec/changes/v1/design.md" -n $NB --title "Architecture"
PYTHONIOENCODING=utf-8 python -m notebooklm source add "<workspace>/CHANGELOG.md" -n $NB --title "Changelog"
```

### Push URLs as sources
```bash
python -m notebooklm source add "https://github.com/you/project" -n $NB
python -m notebooklm source add "https://docs.example.com/api" -n $NB
```

### Push YouTube as research source
```bash
python -m notebooklm source add "https://youtube.com/watch?v=..." -n $NB
```

---

## Querying (Free RAG)

Ask questions grounded in your sources — no hallucination:
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm ask "What are the core architecture decisions?" -n $NB
```

Follow-up in the same conversation:
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm ask "How does the memory system work?" -n $NB
```

Answers include source citations. This is free Gemini RAG.

---

## Content Generation — Prompt Engineering Guide

### Generating Slides (Slide Deck)

**Basic (weak results):**
```bash
python -m notebooklm generate slide-deck -n $NB
```

**With custom prompt (much better):**
```bash
python -m notebooklm generate slide-deck -n $NB \
  --custom-prompt "Create a detailed presentation about the system architecture.
Focus on the 5-chapter structure. Use clean professional design with
navy blue (#1a365d) accents on white backgrounds. Each slide should have
one key concept with a supporting diagram or icon."
```

**Style-specific prompts (copy-paste ready):**

Minimalist Business:
```
Create professional minimalist slides with generous whitespace and clean
visual hierarchy. White backgrounds, charcoal gray text, navy blue as
single accent color. Modern sans-serif typography, bold headlines, light
body text. Each slide focuses on one key message.
```

Tech/Futuristic:
```
Create futuristic tech-style slides with dark backgrounds (#0a0a0f).
Electric blue (#00d4ff) and purple (#8b5cf6) accents with gradient effects.
Geometric patterns: circuit lines, hexagonal grids, glowing nodes.
Data visualizations with neon glow. Sense of innovation and cutting-edge.
```

Playful/Creative:
```
Create vibrant slides with bold saturated colors: coral pink, electric
yellow, turquoise. Hand-drawn elements: sketchy borders, doodle icons,
brush strokes. Mix playful display fonts with clean sans-serif. Dynamic
asymmetrical layouts. Optimistic, youthful, engaging mood.
```

Infographic-heavy:
```
Create infographic-style slides that transform complex information into
visual stories. 4-5 color palette. Abundant custom icons, pictograms.
Diverse charts: pie, bar, timeline, flowchart. Visual metaphors. Bold
scannable typography. Each slide tells a complete visual story.
```

**Pro tip: Write a "script" first, then generate slides from the script.**
Don't feed raw docs directly. Instead:
1. Ask Claude to write a structured presentation script with clear sections
2. Save the script as a text source in NotebookLM
3. Generate slides FROM the script
This gives you control over content. NotebookLM only handles visuals.

### Generating Infographics

```bash
python -m notebooklm generate infographic -n $NB
```

With custom style:
```bash
python -m notebooklm generate infographic -n $NB \
  --custom-prompt "Create a comprehensive architecture diagram showing the
5-layer system. Use brain/neural network visual metaphor. Include
comparison table at the bottom. Professional color scheme with blue
and coral accents."
```

### Generating Podcasts (Audio Overview)

```bash
python -m notebooklm generate audio -n $NB
```

With customization:
```bash
python -m notebooklm generate audio -n $NB \
  --style deep_dive \
  --language zh_Hant \
  --custom-prompt "Focus on the competitive advantages and the philosophy
behind the architecture decisions. Make it accessible to non-technical
listeners."
```

Styles: `default`, `concise`, `deep_dive`, `brief`

### Generating Videos

```bash
python -m notebooklm generate video -n $NB
python -m notebooklm generate cinematic-video -n $NB   # premium style
```

### Generating Quizzes and Flashcards

```bash
python -m notebooklm generate quiz -n $NB --difficulty medium --num-questions 10
python -m notebooklm generate flashcards -n $NB --num-cards 20
```

### Generating Reports

```bash
python -m notebooklm generate report -n $NB --style briefing_doc
```

Styles: `briefing_doc`, `study_guide`, `blog_post`, `custom`

### Generating Mind Maps

```bash
python -m notebooklm generate mind-map -n $NB
```

### Generating Data Tables

```bash
python -m notebooklm generate data-table -n $NB
```

---

## Downloading Generated Content

Wait for completion first:
```bash
python -m notebooklm artifact wait <artifact-id> -n $NB --timeout 300
```

Then download:
```bash
python -m notebooklm download audio -n $NB --latest           # MP3
python -m notebooklm download video -n $NB --latest           # MP4
python -m notebooklm download slide-deck -n $NB --latest --format pptx  # Editable PPTX
python -m notebooklm download slide-deck -n $NB --latest --format pdf   # PDF
python -m notebooklm download infographic -n $NB --latest     # PNG
python -m notebooklm download quiz -n $NB --latest --format json        # Structured
python -m notebooklm download flashcards -n $NB --latest --format json
python -m notebooklm download report -n $NB --latest          # Markdown
python -m notebooklm download data-table -n $NB --latest      # CSV
python -m notebooklm download mind-map -n $NB --latest        # JSON
```

Batch download all:
```bash
python -m notebooklm download audio -n $NB --all
```

Save to workspace deliverables:
```bash
mkdir -p <workspace>/deliverables
python -m notebooklm download slide-deck -n $NB --latest --format pptx
mv *.pptx <workspace>/deliverables/
```

---

## Research Mode (Deep Research)

Let NotebookLM search the web and add sources automatically:

```bash
python -m notebooklm source add-research $NB "AI agent frameworks 2026" --mode deep --import-all
```

Modes: `fast` (~30s, 3-5 sources) or `deep` (~2-3min, 10-20+ sources)

Search a specific site:
```
site:{https://docs.example.com} before:{2026-04-01} after:{2025-01-01} "{keyword}"
```

---

## Sharing Notebooks

Share as read-only (AI assistant for others):
```bash
python -m notebooklm share add $NB colleague@company.com --viewer
python -m notebooklm share public $NB --enable
```

Chat-only mode (they can ask questions but can't see sources):
```bash
python -m notebooklm share view-level $NB chat-only
```

---

## Workflow: Workspace → NotebookLM → Marketing Materials

Complete flow for turning a project into marketing content:

```
1. /spec new → build the product
     ↓
2. After blitz complete:
   Push README + design.md + CHANGELOG → NotebookLM
     ↓
3. Generate marketing materials:
   → Infographic (for social media)
   → Slides (for investor pitch)
   → Podcast (for team briefing)
   → Video (for product demo)
   → Report (for documentation)
     ↓
4. Download all to workspace/deliverables/
     ↓
5. Share notebook as "AI product expert":
   → Stakeholders can ask questions about the product
   → Grounded in YOUR docs, not hallucination
```

---

## Important Notes

### Windows Users
Always prefix commands with `PYTHONIOENCODING=utf-8` to avoid encoding errors:
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm ...
```

### Authentication Expiry
Google cookies expire after days to weeks. If commands start failing:
```bash
python -m notebooklm login   # re-authenticate
```

### Rate Limits
Free accounts: ~50 queries/day. Google AI Pro: higher limits.
If you hit limits, wait or use a different Google account profile:
```bash
python -m notebooklm -p work login
python -m notebooklm -p work ask "..." -n $NB
```

### This is Unofficial
notebooklm-py uses undocumented Google APIs. Google can break it anytime.
Our skill is designed to gracefully degrade — if NotebookLM breaks,
your workspace continues to work. This is optional, not a dependency.

When Google releases an official API, we swap the backend. The skill
interface stays the same. Wrapper pattern wins again.

### Content Quality Tips
1. **Feed clean sources** — well-structured markdown > raw dumps
2. **Write a script first** for slides — don't let AI guess your structure
3. **Use English prompts** for style — Google's model responds better
4. **Specify hex colors** — vague words like "professional" are useless
5. **Generate multiple times** — pick the best version, iterate
6. **Fix text issues** — Chinese characters sometimes garble in slides;
   re-generate or use PDF→PPTX conversion tools to fix
