# NotebookLM Prompt Engineering: An Opinionated Guide

## Core Thesis

NotebookLM is not a general-purpose creative sandbox. It is a source-conditioned synthesis tool.

If your sources are messy, your outputs will be vague.
If your prompt is broad, your output will be generic.
If your formatting expectations are implicit, NotebookLM will guess.
If you ask for style before structure, you will get polished nonsense.

The practical rule:

1. Curate sources first.
2. Decide output format second.
3. Constrain audience, angle, and structure third.
4. Ask for style and polish last.

Prompt engineering matters, but source engineering matters more.

---

## What NotebookLM Is Good At

NotebookLM is strongest when you ask it to:

- synthesize a bounded set of source material
- convert source content into a defined output format
- reorganize information for a specific audience
- identify patterns, contradictions, themes, and summaries
- produce first-draft structure for slides, briefs, explainers, and scripts

It is weaker when you ask it to:

- invent facts not grounded in sources
- generate highly original design language from nothing
- preserve nuanced formatting without explicit instruction
- handle multilingual typography elegantly by default
- infer your intended audience, tone, and level of detail

---

## The Best Mental Model

Treat every NotebookLM prompt as having five layers:

1. **Role**
   - Who is it writing as?
2. **Task**
   - What exact deliverable are you asking for?
3. **Audience**
   - Who will consume it?
4. **Constraints**
   - Length, style, structure, exclusions, language, tone.
5. **Grounding**
   - What must come only from sources, and how should uncertainty be handled?

A weak prompt misses 2-4 of these.
A strong prompt specifies all five.

---

## The Golden Rules

### 1. Ask For One Deliverable At A Time

Bad:
- “Summarize this and make slides and suggest visuals and write a podcast.”

Good:
- “Create a 10-slide executive briefing from these sources.”
- Then:
- “Now turn that slide structure into a 6-minute podcast script.”

Do not stack unrelated output modes in one prompt.

### 2. Define Audience Before Tone

Bad:
- “Make it compelling and polished.”

Good:
- “Make it understandable to a non-technical executive audience. Use plain language, minimal jargon, and decision-oriented framing.”

Audience determines vocabulary, density, and structure.

### 3. Specify The Information Hierarchy

Bad:
- “Make slides from this.”

Good:
- “For each slide, include: title, 3 bullets, one key number or claim, and a suggested visual.”

If you do not define output fields, NotebookLM improvises.

### 4. Tell It What Not To Do

Bad:
- no exclusions

Good:
- “Do not repeat background points across slides.”
- “Do not use vague claims like ‘revolutionary’ or ‘important’ unless directly supported by the sources.”
- “Do not include citations inline unless I ask.”

Negative constraints dramatically improve output quality.

### 5. Force Compression

NotebookLM often defaults to safe, bloated summaries.

Use prompts like:
- “Prioritize only the most decision-relevant points.”
- “Omit historical background unless it changes the recommendation.”
- “Compress to one core idea per slide.”

### 6. Ask For Source-Bounded Language

Use:
- “Base every claim on the provided sources.”
- “If the sources are incomplete or conflicting, say so explicitly.”
- “Do not infer numbers that are not stated.”

This reduces hallucinated polish.

---

## Source Structure Recommendations

## The Real Secret: Prompting Starts Before The Prompt

Good NotebookLM outputs come from well-structured source packs.

### Best Source Stack

A strong notebook usually includes:

- **1 anchor document**
  - The main source of truth: strategy memo, report, transcript, whitepaper, research summary.
- **2-5 supporting documents**
  - Evidence, examples, datasets, interviews, meeting notes, case studies.
- **1 glossary or terminology note**
  - Especially important for specialized domains, acronyms, multilingual content, or internal jargon.
- **1 style or audience brief**
  - A short note that defines who the output is for and what matters.

### Recommended File Types By Purpose

- Use clean text documents for core reasoning.
- Use tables only when quantitative comparisons matter.
- Use transcripts when quotes, voice, and sequence matter.
- Use PDFs carefully: many are badly structured and degrade extraction.
- If a PDF is visually complex, create a cleaned text summary and upload that too.

### Ideal Source Packet Structure

Use separate documents for separate functions:

- `01_overview.md`
- `02_key_facts.md`
- `03_case_studies.md`
- `04_data_points.md`
- `05_glossary.md`
- `06_audience_brief.md`

This is much better than one giant mixed document.

### What To Put In The Audience Brief

Include:

- who the audience is
- what they already know
- what they need to decide or understand
- what tone is appropriate
- what to avoid

Example:

```markdown
Audience: senior product leaders
Knowledge level: moderate familiarity with AI products, low familiarity with OCR workflows
Goal: evaluate whether this workflow should be adopted this quarter
Tone: concise, decision-oriented, skeptical, practical
Avoid: hype, long history, academic framing
```

### What To Put In The Glossary

Include:

- acronyms
- domain-specific terms
- preferred translations
- naming conventions
- terms that should not be translated

This matters a lot for multilingual notebooks.

---

## Workflow Order: The Only Order That Consistently Works

Use this sequence.

### 1. Clean The Sources

Before prompting, remove:

- duplicated sections
- broken OCR
- malformed tables
- decorative junk
- boilerplate headers and footers
- conflicting terminology

### 2. Add A One-Page Context Brief

Do not assume NotebookLM will infer why the notebook exists.

Add a short briefing document with:

- objective
- audience
- deliverable type
- exclusions
- preferred style

### 3. Ask For Extraction Before Synthesis

First prompt:
- “Extract the top 10 source-grounded insights relevant to X.”

Second prompt:
- “Group those insights into 3 themes.”

Third prompt:
- “Turn those themes into a slide outline.”

This is better than jumping straight to final output.

### 4. Build Structure Before Polish

First get:
- sections
- slide titles
- podcast beats
- infographic panels

Then ask for:
- sharper wording
- cleaner transitions
- stronger hooks
- tighter summaries

### 5. Ask For Gap Checks Before Finalization

Use:
- “What important questions remain unanswered by these sources?”
- “Which claims in this draft are weakest or least supported?”
- “What would confuse a first-time reader?”

This is one of the highest-value uses of NotebookLM.

### 6. Generate The Final Draft Last

Only after the structure is right should you ask for:

- final slide copy
- final podcast script
- final infographic text
- final speaker notes

---

## Prompt Formula That Works Repeatedly

Use this structure:

```markdown
Using only the provided sources, create a [deliverable] for [audience].

Goal:
[what the output should help the audience understand, decide, or do]

Requirements:
- [constraint 1]
- [constraint 2]
- [constraint 3]

Structure:
- [required section/field 1]
- [required section/field 2]
- [required section/field 3]

Style:
- [tone]
- [reading level]
- [what to avoid]

Guardrails:
- Base claims only on the sources.
- Flag missing or conflicting evidence explicitly.
- Do not add unsupported examples or numbers.
```

This is boring. That is why it works.

---

# Slides: Good Vs Bad Prompts

## What Good Slide Prompts Do

A good slide prompt defines:

- audience
- number of slides
- purpose of the deck
- information per slide
- what counts as a good slide
- what to exclude

## Bad Slide Prompt

```markdown
Make a slide deck from these sources.
```

Why it fails:

- no audience
- no slide count
- no goal
- no density guidance
- no visual guidance
- no exclusions

Expected result:
generic titles, repetitive bullets, weak hierarchy

## Better Slide Prompt

```markdown
Using only the sources in this notebook, create an 8-slide briefing for senior managers deciding whether to adopt this workflow.

Goal:
Help the audience understand the problem, the proposed approach, expected benefits, main risks, and recommended next step.

Requirements:
- Keep each slide focused on one idea only.
- For each slide, provide:
  - slide title
  - 3 concise bullets
  - 1 key takeaway sentence
  - 1 suggested visual
- Use plain English and avoid jargon unless the sources define it.
- Include one slide on risks or uncertainty.
- Do not repeat the same background information across slides.

Guardrails:
- Use only source-grounded claims.
- If the sources do not support a firm conclusion, say so.
```

## Stronger Slide Prompt For Executive Use

```markdown
Create a 10-slide executive deck from these sources.

Audience:
Busy executives with limited time and low tolerance for technical detail.

Objective:
Enable a go / no-go discussion.

Slide format:
- Title: maximum 8 words
- 3 bullets maximum per slide
- Each bullet: maximum 14 words
- Include one “so what” line per slide
- Suggest a simple visual for each slide

Content requirements:
- Slide 1: decision in one sentence
- Slide 2: problem and stakes
- Slide 3: current-state friction
- Slide 4: proposed approach
- Slide 5: evidence from sources
- Slide 6: expected benefits
- Slide 7: risks and assumptions
- Slide 8: alternatives considered
- Slide 9: recommendation
- Slide 10: next steps

Avoid:
- long explanatory paragraphs
- definitions unless necessary
- repeated claims
- hype language
```

## Bad Slide Prompt Patterns

Avoid prompts like:

- “Make this more engaging.”
- “Turn this into powerful slides.”
- “Make it McKinsey-style.”
- “Make it visual.”

These are vague and invite imitation, not clarity.

Replace them with concrete instructions:

- “Use punchy titles that state conclusions.”
- “Use one claim and one supporting point per slide.”
- “Suggest charts, timelines, process diagrams, or comparison tables where appropriate.”
- “Keep bullets short enough to fit a presentation slide.”

---

# Infographics: Good Vs Bad Prompts

## What Good Infographic Prompts Do

Infographic prompts need stronger structure than slide prompts because visual layout depends on information shape.

A good prompt defines:

- format length
- reading flow
- visual grouping
- panel types
- amount of text per panel
- icon/chart/process suggestions

## Bad Infographic Prompt

```markdown
Make an infographic from these sources.
```

Why it fails:

- no format
- no storyline
- no panel breakdown
- no text budget
- no visual logic

Expected result:
a summary pretending to be an infographic

## Better Infographic Prompt

```markdown
Using only the provided sources, create the content plan for a vertical infographic.

Audience:
General readers with limited prior knowledge.

Goal:
Explain the problem, why it matters, how the process works, and the main implications.

Format:
- 6 sections in top-to-bottom order
- For each section, provide:
  - section heading
  - 1 short paragraph of 25-40 words
  - 2-4 micro-bullets
  - suggested visual type

Visual types allowed:
- icon row
- timeline
- flowchart
- comparison table
- callout statistic
- before/after panel

Constraints:
- Keep text compact.
- Do not use dense paragraphs.
- Avoid repeating the same fact in multiple sections.
- End with one practical takeaway section.
```

## Strong Infographic Prompt For Social/Marketing Context

```markdown
Create an infographic content outline from the sources.

Objective:
Make the material understandable in under 2 minutes of reading.

Audience:
Interested non-experts.

Structure:
1. Hook
2. Why this matters
3. How it works
4. Key evidence
5. Common mistakes
6. Final takeaway

For each section include:
- headline: max 6 words
- body text: max 30 words
- one number, comparison, or concrete detail if supported
- one suggested visual treatment

Style:
- crisp
- visual-first
- concrete
- no corporate fluff

Guardrails:
- Every statistic must come from the sources.
- If evidence is qualitative only, do not manufacture numbers.
```

## Bad Infographic Prompt Patterns

Avoid:

- “Make it eye-catching.”
- “Make it viral.”
- “Make it modern.”
- “Turn this into a beautiful infographic.”

These are design requests without information architecture.

Instead use:

- “Design the content in a 6-panel vertical sequence.”
- “Use one core idea per section.”
- “Limit each section to one paragraph and 2-4 bullets.”
- “Prefer process diagrams and comparisons over decorative visuals.”

---

# Podcasts: Good Vs Bad Prompts

## What Good Podcast Prompts Do

Podcast prompts must define:

- duration
- host format
- audience familiarity
- narrative arc
- sourcing discipline
- spoken language style

Podcast writing is not essay writing. If you do not explicitly ask for spoken rhythm, you will get written prose with line breaks.

## Bad Podcast Prompt

```markdown
Make a podcast script about this.
```

Why it fails:

- no length
- no voice
- no structure
- no audience
- no pacing
- no instructions for spoken language

## Better Podcast Prompt

```markdown
Using only the sources in this notebook, write a 6-minute podcast script for a single host.

Audience:
Curious non-specialists.

Goal:
Explain the topic clearly, highlight why it matters, and end with a memorable takeaway.

Structure:
- Opening hook
- Context
- 3 main points
- One tension, tradeoff, or open question
- Closing summary

Style:
- Conversational but not casual
- Spoken-language rhythm
- Short sentences
- Minimal jargon
- No fake banter

Constraints:
- Include smooth transitions between sections.
- Do not overquote the sources.
- Do not use list-like wording that sounds like slide bullets read aloud.
- If the sources are uncertain or conflicting, state that naturally.
```

## Better Two-Host Podcast Prompt

```markdown
Create an 8-minute two-host podcast script from these sources.

Roles:
- Host A: curious guide
- Host B: subject-matter explainer

Audience:
Educated listeners with little prior knowledge.

Requirements:
- Alternate naturally between hosts.
- Keep exchanges short and purposeful.
- Use the dialogue to clarify, not repeat.
- Include one moment where Host A raises a reasonable doubt or misconception.
- End with a concise takeaway and one open question.

Avoid:
- forced jokes
- filler banter
- repetitive “That’s so interesting” reactions
- long monologues over 120 words
```

## Bad Podcast Prompt Patterns

Avoid:

- “Make it sound natural.”
- “Make it engaging.”
- “Make it like a real podcast.”
- “Make it conversational and fun.”

These are too vague.

Use instead:

- “Write for speaking, not reading.”
- “Use short sentences and audible transitions.”
- “Include one concrete example after each main point.”
- “Avoid repetitive host affirmation.”
- “Each segment should advance the listener’s understanding.”

---

# Copy-Paste Prompt Templates

## Template: Slide Outline

```markdown
Using only the sources in this notebook, create a [NUMBER]-slide presentation for [AUDIENCE].

Goal:
[WHAT DECISION / UNDERSTANDING / ACTION THIS DECK SHOULD ENABLE]

For each slide, provide:
- slide title
- 3 bullets maximum
- one key takeaway sentence
- one suggested visual

Requirements:
- one idea per slide
- concise, presentation-ready wording
- no repeated background points
- include one slide on risks, uncertainty, or open questions
- keep language appropriate for [AUDIENCE]

Avoid:
- generic filler
- hype language
- unsupported claims
- long paragraphs

Guardrails:
- Use only source-grounded information.
- Flag weak evidence or missing information explicitly.
```

## Template: Executive Slides

```markdown
Create an executive presentation from these sources.

Audience:
Senior leaders making a decision with limited time.

Objective:
Support a clear recommendation.

Structure:
- decision summary
- problem
- current-state pain
- proposed solution
- supporting evidence
- benefits
- risks
- recommendation
- next steps

Formatting rules:
- title max 8 words
- max 3 bullets per slide
- each bullet max 14 words
- add one “so what” line per slide
- suggest a simple chart, table, or diagram where useful

Avoid:
- technical detail unless decision-critical
- duplicated claims
- generic adjectives
```

## Template: Infographic Outline

```markdown
Using only the notebook sources, create a vertical infographic content plan.

Audience:
[AUDIENCE]

Goal:
[GOAL]

Structure:
Create 6 sections in reading order.
For each section include:
- short heading
- 25-40 word body text
- 2-4 supporting bullets
- suggested visual type

Allowed visual types:
- icon row
- timeline
- process flow
- comparison table
- statistic callout
- before/after panel

Constraints:
- compact wording
- one idea per section
- no repeated facts
- finish with a practical takeaway

Guardrails:
- no unsupported numbers
- no invented examples
- if evidence is mixed, say so
```

## Template: Podcast Script

```markdown
Using only the notebook sources, write a [LENGTH]-minute podcast script.

Format:
[single host / two hosts]

Audience:
[AUDIENCE]

Goal:
[WHAT THE LISTENER SHOULD UNDERSTAND BY THE END]

Structure:
- opening hook
- context
- 3 main points
- one tension, tradeoff, or uncertainty
- closing takeaway

Style:
- spoken-language rhythm
- short, clear sentences
- natural transitions
- concrete examples where supported

Avoid:
- essay-like prose
- repetitive filler
- fake banter
- unsupported claims

Guardrails:
- stay grounded in the sources
- acknowledge uncertainty where present
```

## Template: Extraction Before Drafting

```markdown
Using only the notebook sources, extract the 10 most important insights for [AUDIENCE / GOAL].

For each insight, provide:
- a short label
- a 1-2 sentence explanation
- why it matters
- any uncertainty or limitation in the sources

Prioritize:
- decision-relevant points
- strong evidence
- non-obvious insights

Avoid:
- generic summary statements
- duplicated ideas
```

## Template: Gap Check

```markdown
Review the current draft against the notebook sources.

Identify:
- claims that are weakly supported
- important missing context
- repeated or redundant points
- places where the logic jumps too far
- questions a skeptical reader would ask

Then suggest:
- what to cut
- what to clarify
- what to reorder
```

---

# CJK Text Handling

## Short Version

NotebookLM is often weaker with CJK text than users expect, especially when:

- OCR quality is poor
- source files mix languages inconsistently
- line breaks are broken
- punctuation is inconsistent
- terms have multiple translations
- headings are unclear
- text extraction loses semantic structure

If you care about quality, do not dump raw CJK PDFs into NotebookLM and hope for the best.

## Best Practices For CJK Sources

### 1. Normalize The Text Before Upload

Clean:

- broken OCR characters
- inconsistent punctuation
- strange line wraps
- duplicated headers/footers
- mixed full-width and half-width usage where it harms readability

### 2. Create A Terminology Sheet

Include:

- original term
- preferred translation
- alternate translations
- when not to translate
- romanization if relevant

Example:

```markdown
生成AI = generative AI
基盤モデル = foundation model
推論 = inference
推奨訳:
- 導入 = adoption, not installation, when discussing organizational rollout
- 運用 = operations or deployment depending on context
Do not translate:
- NotebookLM
- OCR
- RAG
```

### 3. Keep Language Tasks Separated

Bad:
- “Summarize these Japanese and Chinese sources in English and make slides.”

Better:
1. “Extract and normalize the main claims from the Japanese sources.”
2. “Extract and normalize the main claims from the Chinese sources.”
3. “Merge them into an English synthesis.”
4. “Turn that synthesis into slides.”

### 4. Be Explicit About Output Language

Use prompts like:

```markdown
Read the sources in their original language, but produce the output in English.
Preserve original proper nouns.
When a term has no clean translation, provide the original term once in parentheses.
```

Or:

```markdown
Produce the output in Japanese.
Keep English product names in English.
Use concise business Japanese.
Avoid literal translation from English sentence structure.
```

### 5. Ask It To Preserve Native Reading Flow

For Japanese, Chinese, and Korean output, specify:

- sentence density
- whether to use bullets or prose
- whether English acronyms should remain in English
- how to handle specialized terms

Example:

```markdown
Write the output in Japanese for business readers.
Use short, natural Japanese sentences.
Keep product names and common acronyms in English.
Avoid overly literal or machine-translated phrasing.
```

### 6. Do Not Trust CJK OCR Blindly

If the source is a scanned PDF:

- inspect key passages manually
- provide a cleaned text file for important sections
- avoid relying on extracted tables unless checked

### 7. Use A Bilingual Summary Layer

For high-stakes work, create a separate note with:

- original-language key points
- English equivalents
- unresolved ambiguities

This dramatically improves downstream prompts.

---

## CJK Prompt Template

```markdown
Using the notebook sources, read the original [Japanese / Chinese / Korean] material and produce the output in [TARGET LANGUAGE].

Requirements:
- preserve the meaning of domain-specific terms
- keep product names and standard acronyms in English unless the sources clearly localize them
- if a term is ambiguous, use the glossary preference if provided
- if a concept does not translate cleanly, include the original term once in parentheses

Output format:
[SLIDES / INFOGRAPHIC / PODCAST / SUMMARY]

Style:
- natural [TARGET LANGUAGE]
- concise
- avoid literal translation artifacts

Guardrails:
- do not invent missing translations
- flag ambiguous wording or source-quality issues
```

---

# Visual Consistency

## NotebookLM Does Not Magically Create A Visual System

If you want consistent slides or infographic content, define the visual rules in the prompt.

Do not ask for “better visuals.” Ask for repeatable visual logic.

## What To Specify

For slides:

- one visual type per slide
- preferred visual vocabulary
- consistency rules
- density limits
- title style

For infographics:

- fixed section pattern
- repeated card structure
- controlled heading length
- limited visual types
- one hierarchy system

## Good Visual Consistency Prompt For Slides

```markdown
Create slide content with consistent visual logic.

Rules:
- Each slide should use only one primary visual type.
- Prefer these visual types:
  - comparison table
  - simple process diagram
  - timeline
  - bar chart
  - callout statistic
- Do not suggest decorative illustrations unless they add meaning.
- Use title styles that state conclusions, not topics.
- Keep each slide visually sparse enough for presentation use.
- Avoid mixing multiple charts and diagrams on one slide.
```

## Good Visual Consistency Prompt For Infographics

```markdown
Keep the infographic visually consistent.

Rules:
- Each section should have one short heading, one compact text block, and one primary visual treatment.
- Use no more than 4 visual types across the whole infographic.
- Prefer repeated panel logic over unique layouts for every section.
- Use callout numbers only where the sources support them.
- Avoid decorative icons that do not encode information.
```

## Practical Opinion

Most users over-ask for visual flair and under-ask for structural consistency.

Consistency comes from constraints:
- fixed title length
- repeated section anatomy
- limited visual vocabulary
- stable information density

Ask for that.

---

# Pitfalls

## 1. Uploading Raw Junk Sources

If your sources include:

- scanned PDFs with bad OCR
- duplicate versions
- contradictory notes
- messy exports
- decorative formatting without clear hierarchy

then your prompt quality barely matters.

Fix the sources first.

## 2. Asking For “Aesthetic” Before Meaning

Bad sequence:
- “Make this more visual and engaging.”

Good sequence:
- “Identify the 5 core messages.”
- “Organize them into sections.”
- “Then suggest visuals.”

## 3. Combining Too Many Tasks

Bad:
- summary + strategy + slides + script + visual branding in one ask

Good:
- extraction
- outline
- refinement
- final format

One stage at a time.

## 4. Not Defining The Audience

Without audience, NotebookLM defaults to generic competent writing.

Generic competent writing is usually useless.

## 5. Letting It Repeat The Same Point In Different Words

This is one of the most common failure modes.

Use prompts like:
- “Remove overlap across sections.”
- “Each section must contribute new information.”
- “Do not restate earlier claims unless needed for transition.”

## 6. Asking For “More Detail” Too Early

Early detail expands weak structure.
First get the right skeleton.
Then add depth selectively.

## 7. Trusting Unsupported Numbers

If the sources are qualitative, do not let NotebookLM turn them into fake precision.

Use:
- “Do not quantify unless the sources explicitly provide numbers.”

## 8. Using Fancy Prompt Language Instead Of Clear Instructions

Do not write prompts like a spell.

This is bad:
- “Craft a compelling, resonant, world-class narrative synthesis.”

This is good:
- “Write a 6-minute single-host podcast script with 3 main points and a clear closing takeaway.”

## 9. Ignoring Contradictions In The Sources

NotebookLM is often too willing to smooth disagreements unless you ask it not to.

Use:
- “Highlight contradictions or unresolved disagreements in the sources.”
- “Do not flatten disagreements into false consensus.”

## 10. Treating NotebookLM Output As Final

NotebookLM is excellent for:
- structure
- synthesis
- draft generation

It is not the final QA layer.
Review:
- numbers
- implied causality
- repeated points
- wording too polished for evidence quality
- translation edge cases

---

# My Recommended Default Workflow

## For Slides

1. Upload clean sources.
2. Add an audience brief.
3. Ask for top insights.
4. Ask for grouping into themes.
5. Ask for a slide outline.
6. Ask for one-slide-one-idea compression.
7. Ask for suggested visuals.
8. Ask for redundancy cuts.
9. Generate final slide copy.

## For Infographics

1. Upload clean sources.
2. Extract core facts and process steps.
3. Ask for a 5-7 section reading sequence.
4. Ask for a compact text budget per section.
5. Ask for consistent visual treatment rules.
6. Ask for final infographic copy.

## For Podcasts

1. Upload clean sources.
2. Ask for key themes and tensions.
3. Ask for a narrative arc.
4. Ask for segment timing.
5. Ask for spoken-language script.
6. Ask for smoother transitions and redundancy cuts.
7. Read it aloud and edit what sounds written.

---

# High-Leverage Prompt Moves

These consistently improve results.

## Ask For A Skeleton First

```markdown
Before drafting the full output, propose the structure only.
```

## Force Non-Repetition

```markdown
Make sure each section adds new information and does not repeat prior points.
```

## Demand Decision Relevance

```markdown
Prioritize what matters for the audience’s decision, not general background.
```

## Add A Skeptic Pass

```markdown
After drafting, identify where a skeptical reader would challenge the logic or evidence.
```

## Ask For A Compression Pass

```markdown
Now reduce this by 30% without losing substance.
```

## Ask For Better Titles Separately

```markdown
Rewrite the section titles so each title communicates a conclusion, not just a topic.
```

This is especially useful for slides.

---

# Example End-To-End Prompt Sequence

## Step 1: Extract Insights

```markdown
Using only the notebook sources, extract the 10 most important insights for senior managers evaluating this initiative.

For each insight include:
- short label
- explanation
- why it matters
- uncertainty or limitation
```

## Step 2: Group Into Themes

```markdown
Group these insights into 3-4 themes that would make sense in a decision-oriented presentation.

For each theme include:
- theme title
- included insights
- why this theme matters
```

## Step 3: Build Slide Outline

```markdown
Turn these themes into an 8-slide executive outline.

For each slide provide:
- title
- 3 bullets maximum
- one key takeaway
- one suggested visual

Include:
- problem
- evidence
- risks
- recommendation
```

## Step 4: Tighten For Presentation Use

```markdown
Revise the outline for presentation use.

Requirements:
- one idea per slide
- no repeated background information
- title should state conclusions
- bullets should be short and spoken-friendly
```

## Step 5: Quality Check

```markdown
Review this outline against the sources.

Identify:
- weakly supported claims
- repeated ideas
- missing context
- places where the recommendation overreaches the evidence
```

This sequence beats one giant prompt almost every time.

---

# What I Would Avoid Entirely

I would avoid prompts like:

- “Make it stunning.”
- “Make it world-class.”
- “Make it more human.”
- “Make it more strategic.”
- “Make it feel premium.”
- “Make it thought-leadership.”
- “Make it consultant-level.”

These are aesthetic abstractions, not operational instructions.

Replace them with constraints the model can execute.

---

# My Opinionated Defaults

If you do not know what to ask, start here.

## Default For Slides

- 8-10 slides
- one idea per slide
- max 3 bullets
- conclusion-style titles
- one visual suggestion per slide
- explicit risks slide
- audience defined
- no repeated background

## Default For Infographics

- 6 sections
- top-to-bottom flow
- short heading + short paragraph + micro-bullets
- no more than 4 visual types
- practical ending
- one statistic per section only if supported

## Default For Podcasts

- 6-8 minutes
- one host unless dialogue is truly useful
- short spoken sentences
- 3 main points
- one tension or open question
- no fake banter
- close with a memorable synthesis

## Default For CJK

- clean text before upload
- glossary included
- translation preferences explicit
- output language specified
- terms not to translate listed
- critical passages checked manually if OCR is involved

---

# Final Rule

The best NotebookLM prompt is usually not the fanciest one.

It is the one that makes the model’s job narrow, concrete, and source-bound.

If you want better outputs:

- improve the sources
- reduce the task scope
- define the audience
- force structure
- separate drafting from polishing
- tell it what to avoid

That is most of NotebookLM prompt engineering.
