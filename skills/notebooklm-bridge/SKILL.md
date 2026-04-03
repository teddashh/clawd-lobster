# NotebookLM Bridge — Free RAG + Content Engine for Workspaces

Connect any workspace to Google NotebookLM. Push your docs as sources,
query with Gemini, generate slides/infographics/podcasts — all from terminal.
Zero token cost. Powered by notebooklm-py.

**This guide was co-authored by Claude, Codex (GPT-5.4), and Gemini via a
three-way debate on prompt engineering best practices.**

---

## Setup

### Install
```bash
pip install notebooklm-py
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
3. **Push initial sources:** README.md, CLAUDE.md, design.md

After blitz completes, push updated docs:
```bash
NB="<notebook-id>"
python -m notebooklm source add "<workspace>/README.md" -n $NB --title "README"
python -m notebooklm source add "<workspace>/openspec/changes/v1/design.md" -n $NB --title "Architecture"
python -m notebooklm source add "<workspace>/CHANGELOG.md" -n $NB --title "Changelog"
```

---

## The 10 Rules of NotebookLM Prompting

*Consolidated from Claude, Codex, and Gemini's independent analyses.*

### Rule 1: Source Engineering > Prompt Engineering

Your sources define your output ceiling. Clean sources in, quality out.

- Remove duplicate sections, broken OCR text, decorative junk
- Prefer well-structured markdown over raw PDFs
- Each source should have a clear purpose — don't dump everything

### Rule 2: Add a Context Brief

Upload a 1-page "briefing" document into your notebook that tells NotebookLM
WHO you are, WHAT you're building, WHO the audience is, and what to EXCLUDE.
NotebookLM uses this to contextualize everything else.

```markdown
# Project Brief: Clawd-Lobster

## Objective
Explain Clawd-Lobster's architecture to potential users and developers.

## Audience
Technical users who know Claude Code but haven't heard of Clawd-Lobster.

## Tone
Confident, concise, opinionated. Not academic.

## Exclusions
Do not mention internal development history or personal names.
```

### Rule 3: Five-Layer Prompt Framework

Every prompt should define:

1. **Role** — who is NotebookLM writing as?
2. **Task** — exact deliverable (slides, infographic, podcast)
3. **Audience** — who consumes it?
4. **Constraints** — length, format, exclusions
5. **Grounding** — what MUST come from sources only

### Rule 4: Define Audience Before Tone

Bad: "Make it compelling"
Good: "Make it understandable to a non-technical executive using plain
language and decision-oriented framing"

The audience determines everything — vocabulary, depth, examples, structure.

### Rule 5: Positive Instructions + Negative Constraints

Tell it exactly what to do, AND what NOT to do:

```
Base every claim on the provided sources.
Do NOT use vague words like "revolutionary" or "cutting-edge"
unless directly supported by the source text.
Do NOT repeat the same point in different words across slides.
```

### Rule 6: Extract → Outline → Draft (Never One Shot)

Never ask for the final product in one prompt. Break it into steps:

1. "Extract the top 10 insights from these sources"
2. "Group those insights into 3-4 themes"
3. "Create a slide outline with one theme per section"
4. "Generate the final slide deck from this outline"

This gives you control at each step and prevents generic outputs.

### Rule 7: Force Compression

NotebookLM defaults to safe, bloated summaries. Counteract:

- "Prioritize only the most decision-relevant points"
- "Compress to one core idea per slide"
- "If a point doesn't change a decision, cut it"

### Rule 8: Define Information Hierarchy Explicitly

Don't let it guess the layout. Specify the structure:

```
For each slide, include:
- 1 bold headline (max 8 words)
- 3 bullet points (max 15 words each)
- 1 key metric or data point
- 1 supporting visual description
```

### Rule 9: Run a Gap Check Before Finalizing

Before trusting a draft, ask:

```
"What important questions remain unanswered by these sources?"
"Which claims in this draft are the weakest or least supported?"
"What would a skeptic challenge about this presentation?"
```

### Rule 10: Use System Instructions, Not Repeated Prompts

Set your persona/constraints ONCE in the notebook's System Instructions
(the gear icon in the chat panel). Don't waste prompt space repeating them.

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

The prompt engineering rules in this skill were derived from a three-way debate:
1. **Claude (Opus 4.6)** — hands-on testing, practical experience
2. **Codex (GPT-5.4)** — 1,391-line theoretical framework, exhaustive templates
3. **Gemini (via NotebookLM)** — judged both, added System Instructions and
   RAG chunking insights, produced the final top 10 rules

Key Gemini verdict: "Codex correctly identifies that NotebookLM's true power
lies in source-grounded synthesis, not formatting. Claude's script-first
approach underutilizes the tool. The extract→outline→draft pipeline is superior."
