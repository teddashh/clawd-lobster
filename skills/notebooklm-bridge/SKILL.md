# NotebookLM Bridge — Free RAG + Content Engine for Workspaces

Connect any workspace to Google NotebookLM. Push your docs as sources,
query with Gemini, generate slides/infographics/podcasts — all from terminal.
Zero token cost. Powered by notebooklm-py.

**This guide was forged through a 4-round debate between Claude (Opus 4.6),
Codex (GPT-5.4), and Gemini — with two judgment reversals, one concession,
and a unified methodology that none of them would have reached alone.**

---

## Setup

### Install
```bash
pip install notebooklm-py PyMuPDF Pillow scikit-image numpy python-pptx
python -m playwright install chromium   # needed for login only
```

### Login
```bash
python -m notebooklm login
# Browser opens → log into Google → wait for NotebookLM homepage → Enter
```

### Verify
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm auth check
```

### Set language
```bash
python -m notebooklm language set zh_Hant   # or en, ja, etc.
```

**Windows users:** Always prefix with `PYTHONIOENCODING=utf-8`.

---

## Workspace Integration

When a workspace is created and this skill is enabled:

1. **Create notebook:** `python -m notebooklm create "<workspace-name>"`
2. **Save notebook ID** in workspace config
3. **Sync ALL valuable content automatically**

### Auto-sync: Push everything valuable

Don't cherry-pick files. Use the sync script to scan the entire workspace
and push all documentation, specs, knowledge, and configs:

```bash
# Sync all docs (markdown, configs, specs, knowledge)
python scripts/notebooklm-sync.py <workspace-path> <notebook-id>

# Dry run first to see what would be pushed
python scripts/notebooklm-sync.py <workspace-path> <notebook-id> --dry-run

# Include source code files too (for code review / deep analysis)
python scripts/notebooklm-sync.py <workspace-path> <notebook-id> --full
```

The sync script automatically:
- Scans for all .md, .txt, .json, .yaml, .toml files
- Skips junk: .git, node_modules, __pycache__, .env, lock files
- Titles sources intelligently: `[spec] changes/v1/design.md`, `[skill] evolve/SKILL.md`
- Skips files already in the notebook (no duplicates)
- Caps at 500KB per file (NotebookLM limit)
- `--full` mode adds code files (.py, .js, .ts, etc.)

### When to sync

- **After workspace creation** — push initial structure
- **After blitz completes** — push all new code and docs
- **After major changes** — re-sync to keep notebook current
- **Before generating deliverables** — ensure sources are up to date

---

## The 3-Stage Pipeline (from the debate)

The debate resolved that extract→outline→draft and script-first are NOT
competing methods — they are STAGES of the same pipeline:

```
Stage 1: Discovery (Codex's method)
  Extract → Outline → Draft from raw sources
  "List the top 10 insights" → "Group into themes" → "Build outline"
  ↓
Stage 2: Forge Single Source of Truth
  Save your approved outline as a "Synthesis Note"
  Convert that note into a source
  UNCHECK all raw files
  ↓
Stage 3: Controlled Generation (Claude's method)
  Generate final deliverables from the Synthesis Note ONLY
  NotebookLM handles visuals, you control the narrative
```

**Never generate final deliverables from raw sources.**
Extract first, lock the narrative, then generate.

---

## The 8 Rules of NotebookLM Prompting

*Final version from 4-round, 3-AI debate. Two judgment reversals, one
concession. These rules survived cross-examination.*

### Rule 1: Source Engineering > Prompt Engineering

Clean sources first. Remove broken OCR, duplicates, decorative junk.
Prefer structured markdown over raw PDFs.

### Rule 2: Forge a Single Source of Truth

Don't generate from a messy pile of raw docs. Distill insights into a
"Synthesis Note," convert it into a source, isolate it, generate from that.

### Rule 3: Use Source-Targeted Syntax

Defeat lazy RAG chunking. Name the specific document, chapter, or slide:

Bad: "What is the market strategy?"
Good: "Focus exclusively on Chapter 4 of 'Q3_Strategy.pdf'. Explain the
main argument using specific examples from Slide Deck 3."

### Rule 4: Apply Negative Constraints

What NOT to do is as important as what to do:

```
Do NOT use vague claims like "revolutionary" unless directly supported.
Do NOT repeat the same point across slides.
Do NOT infer unstated numbers.
If data is unavailable, say so explicitly.
```

### Rule 5: Define Audience AND Decision Context

Bad: "Make it compelling"
Good: "Make it understandable to a non-technical executive making a Q3
budget decision, using plain language and decision-oriented framing."

### Rule 6: Dictate Exact Information Hierarchy

```
For each slide:
- 1 bold headline (max 8 words)
- 3 bullet points (max 15 words each)
- 1 key metric or data point
- 1 supporting visual description
```

### Rule 7: Force Compression

AI defaults to bloated summaries. Counteract:
- "Compress to one core idea per slide"
- "Prioritize only decision-relevant points"
- "If a point doesn't change a decision, cut it"

### Rule 8: Run a Gap Check Before Finalizing

```
"Which claims in this draft are the weakest or least supported?"
"What important questions remain unanswered by these sources?"
"What would a skeptic challenge about this presentation?"
```

### Bonus: Set Global System Instructions

Don't repeat persona/constraints per prompt. Set them ONCE in the notebook's
System Instructions (gear icon in chat panel):

```xml
<role>Lead Technical Solutions Architect. Brutally honest, fact-based.</role>
<constraints>No jargon. If data unavailable, say so. No walls of text.</constraints>
<formatting>Comparisons in tables. Steps in bullets.</formatting>
```

---

## Prompt Templates by Content Type

### Slides — The Script-Extract Method

**Step 1: Extract insights**
```
Review all sources. List the 10 most important insights about [topic].
For each insight, cite which source it comes from.
```

**Step 2: Outline**
```
Group these 10 insights into 4 sections. For each section, write:
- Section title (max 5 words)
- 2-3 key points
- 1 data point or quote from sources
```

**Step 3: Generate with style**
```
Create a detailed slide deck from this outline.
Style: dark backgrounds (#0d1117), blue accents (#58a6ff),
clean sans-serif typography, generous whitespace.
Each slide: 1 headline, 3 bullets max, 1 visual element description.
Language: Traditional Chinese (繁體中文).
Do not include content not found in the sources.
```

### Slides — Style Templates (copy-paste ready)

**Minimalist Business:**
```
White backgrounds, charcoal gray (#333) text, navy blue (#1a365d) as
single accent color. Modern sans-serif typography. Each slide: one key
message with generous whitespace. No decorative elements.
```

**Tech/Futuristic:**
```
Dark backgrounds (#0a0a0f). Electric blue (#00d4ff) and purple (#8b5cf6)
accents with gradient effects. Geometric patterns: circuit lines,
hexagonal grids. Neon glow data visualizations. Sleek modern typography.
```

**Infographic-heavy:**
```
Transform complex information into visual stories. 4-5 color palette.
Abundant icons, pictograms. Diverse charts: pie, bar, timeline, flowchart.
Bold scannable typography. Each slide tells a complete visual story.
```

### Infographics

```
Create an infographic summarizing [topic] from the provided sources.
Structure: header with project name, 3-4 main sections arranged vertically,
comparison table at the bottom.
Visual metaphor: [brain/network/pipeline/timeline — pick one].
Color scheme: [specify hex values].
Include specific numbers and data points from sources.
Language: Traditional Chinese.
Orientation: standard (portrait).
```

### Podcasts (Audio Overview)

```
Create a deep-dive audio discussion about [topic].
Focus on: [specific aspects to emphasize]
Audience: [who will listen and their knowledge level]
Style: deep_dive
Language: zh_Hant (Traditional Chinese)
The hosts should debate the trade-offs, not just list features.
```

### Research Mode

Search the web for sources:
```bash
python -m notebooklm source add-research "AI agent frameworks comparison 2026" \
  --mode deep --import-all -n $NB
```

Search a specific site:
```
site:{https://docs.example.com} before:{2026-04-01} after:{2025-01-01} "{keyword}"
```

### Quizzes and Flashcards

```bash
python -m notebooklm generate quiz -n $NB --difficulty medium --num-questions 15
python -m notebooklm generate flashcards -n $NB --num-cards 20
```

### Reports

```bash
python -m notebooklm generate report -n $NB --style briefing_doc
```

Styles: `briefing_doc`, `study_guide`, `blog_post`, `custom`

---

## CLI Quick Reference

### Create and manage
```bash
python -m notebooklm create "Project Name"          # create notebook
python -m notebooklm list                            # list all notebooks
python -m notebooklm use <notebook-id>               # set active notebook
```

### Add sources
```bash
python -m notebooklm source add "https://..." -n $NB           # URL
python -m notebooklm source add "./file.md" -n $NB --title "X" # local file
python -m notebooklm source add "https://youtube.com/..." -n $NB  # YouTube
python -m notebooklm source add-research "query" --mode deep -n $NB  # web search
```

### Query (free RAG)
```bash
python -m notebooklm ask "Your question here" -n $NB
```

### Generate content
```bash
python -m notebooklm generate slide-deck -n $NB [--custom-prompt "..."]
python -m notebooklm generate infographic -n $NB [--custom-prompt "..."]
python -m notebooklm generate audio -n $NB --style deep_dive --language zh_Hant
python -m notebooklm generate video -n $NB
python -m notebooklm generate quiz -n $NB --difficulty medium
python -m notebooklm generate flashcards -n $NB
python -m notebooklm generate report -n $NB --style briefing_doc
python -m notebooklm generate mind-map -n $NB
python -m notebooklm generate data-table -n $NB
```

### Wait and download
```bash
python -m notebooklm artifact wait <artifact-id> -n $NB --timeout 300
python -m notebooklm download slide-deck -n $NB --latest --format pptx
python -m notebooklm download infographic -n $NB --latest              # PNG
python -m notebooklm download audio -n $NB --latest                    # MP3
python -m notebooklm download video -n $NB --latest                    # MP4
python -m notebooklm download quiz -n $NB --latest --format json
python -m notebooklm download report -n $NB --latest                   # Markdown
```

### Share
```bash
python -m notebooklm share add $NB user@email.com --viewer
python -m notebooklm share public $NB --enable
python -m notebooklm share view-level $NB chat-only   # AI assistant mode
```

---

## Workspace → Marketing Pipeline

```
1. /spec new → build product
2. After blitz → push docs to NotebookLM
3. Generate deliverables:
   → Infographic (social media)
   → Slides (investor pitch)
   → Podcast (team briefing)
   → Video (product demo)
   → Report (documentation)
4. Download to workspace/deliverables/
5. Share notebook as "AI product expert"
```

---

## Known Limitations

- **Unofficial API** — notebooklm-py uses undocumented Google APIs. Can break.
- **Auth expires** — Google cookies last days to weeks. Re-run `login` when needed.
- **Rate limits** — Free: ~50 queries/day. Google AI Pro: higher limits.
- **CJK text** — Chinese characters sometimes garble in slides. Re-generate
  or use PDF→PPTX tools to fix. Adding `Language: Traditional Chinese` to
  prompts helps but doesn't guarantee perfection.
- **Deep research import** — can timeout. Use `--no-wait` and check manually.
- **This is optional** — if NotebookLM breaks, your workspace still works.
  When Google releases official API, swap backend, keep interface.

---

## Debate Source Credit

These rules were forged through a 4-round debate:

**Round 1:** Claude + Codex wrote independent guides
**Round 2:** Gemini judged Codex won (extract→outline→draft > script-first)
**Round 3:** Claude pushed back on high-stakes deliverables. Gemini reversed:
  *"You are absolutely correct. My previous judgment overvalued synthesis at
  the expense of narrative control."* Codex conceded: *"I understated the
  value of script-first as a late-stage control mechanism."*
**Round 4:** Gemini unified both into 3-stage pipeline. Final grades:

| | Accuracy | Depth | Practicality | Admitting Mistakes |
|---|---|---|---|---|
| Claude | 9 | 7 | 10 | 8 |
| Codex | 8 | 10 | 8 | 10 |
| Gemini | 8 | 9 | 9 | 10 |

Winner: Claude (core thesis). Best framework: Codex. Best additions: Gemini.
Most valuable insight: the Synthesis Note technique — none of them proposed
it alone, it emerged from the debate.

---

## Watermark Removal

NotebookLM adds a logo watermark to the bottom-right corner of all generated
slides and infographics. This skill includes an automatic watermark remover.

### How It Works
- **Not AI** — uses biharmonic inpainting (classical image processing)
- **No GPU needed** — runs on CPU, ~2-5 seconds per page
- Fixed-position detection at NotebookLM's standard resolution (2867×1600)
- Outputs: clean PDF, PNG ZIP, or PowerPoint

### Automatic Mode
When `auto_remove_watermark` is enabled (default: true), any PDF downloaded
from NotebookLM (slides, infographics) is automatically cleaned before saving.

### Manual Usage
```bash
# Single PDF → clean PDF
python skills/notebooklm-bridge/remove_watermark.py slides.pdf

# Custom output path
python skills/notebooklm-bridge/remove_watermark.py slides.pdf -o clean.pdf

# Output as PowerPoint
python skills/notebooklm-bridge/remove_watermark.py slides.pdf --pptx

# Output as PNG ZIP
python skills/notebooklm-bridge/remove_watermark.py slides.pdf --png

# Batch mode
python skills/notebooklm-bridge/remove_watermark.py *.pdf

# Higher quality (default 150 DPI)
python skills/notebooklm-bridge/remove_watermark.py slides.pdf --dpi 300
```

### When Claude Should Use This
- After generating slides or infographics via NotebookLM, **always** run
  watermark removal before delivering the final files to the user
- Use `--pptx` when the user wants editable slides
- Use `--png` when the user wants individual images
- Use default (PDF) for archival or sharing

### Limitations
- Only works on NotebookLM-generated PDFs (fixed watermark position)
- If NotebookLM changes their watermark position/size, the coordinates
  in `remove_watermark.py` need updating (constants at top of file)
