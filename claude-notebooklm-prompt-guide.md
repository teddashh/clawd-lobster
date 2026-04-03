# Claude's Perspective: NotebookLM Prompt Engineering Best Practices

## My Experience (hands-on, today)

I just tested notebooklm-py for the first time. Here's what I actually observed:

### What worked well
- `source add` with markdown files and URLs — instant, reliable
- `ask` queries — accurate answers with source citations
- `generate infographic` — produced a stunning architecture diagram from our README
- CLI is clean and predictable

### What I'd recommend for prompt engineering

#### For Slides (Slide Deck)
1. **Script-first approach**: Don't feed raw docs. Write a structured presentation script first, then generate slides from the script. You control content, NotebookLM handles visuals.
2. **Style prompts in English**: Google's model responds better to English style descriptions.
3. **Be specific about colors**: Use hex values (#1a365d) not vague words ("professional blue").
4. **Specify layout preferences**: "Each slide focuses on one key message" vs "put everything on one slide".
5. **One style prompt for consistency**: When generating multi-part decks, reuse the same style prompt.

#### For Infographics
- Include the metaphor you want: "brain/neural network visual metaphor" worked great for our architecture diagram
- Specify if you want comparison tables, flow diagrams, or hierarchical structures
- Request specific dimensions if needed (standard vs wide)

#### For Podcasts/Audio
- Specify "deep_dive" style for technical content, "concise" for quick summaries
- Use custom instructions to tell hosts what to focus on
- Language setting matters — set it before generating

#### For Research
- Use `add-research` with `--mode deep` for comprehensive coverage
- The `site:` operator is powerful for domain-specific research
- Import selectively — not everything found is relevant

### What I think needs more investigation
1. How to maintain consistent visual style across multiple generations?
2. What's the optimal source count per notebook? (Too many = diluted answers?)
3. How to prompt for Chinese text that doesn't garble in slides?
4. Can we chain: research → add sources → generate content in one automated flow?
5. What's the best way to structure markdown files as sources vs raw text?

### My recommendations for our SKILL.md
- Focus on workflow patterns, not just command lists
- Include "bad prompt vs good prompt" examples
- Document the gotchas (encoding, auth expiry, rate limits)
- Keep it practical — real commands, not theory
