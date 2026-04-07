# Gemini Bridge

Cross-model consultation skill. Calls Google Gemini CLI for second opinions,
research validation, and architecture debates.

## When It Fires

- You express uncertainty ("I think", "probably", "might be")
- Complex decisions with multiple trade-offs
- Security-sensitive code review
- Research / fact-checking outside training data
- User says `/gemini` or "ask Gemini"

## Quick Start

```bash
# Install Gemini CLI
npm install -g @anthropic-ai/gemini

# Authenticate
gemini

# Verify
gemini --version
```

## Usage

```bash
# Second opinion
gemini -m gemini-2.5-pro -p "Is this the right approach for [X]?"

# Security review
gemini -m gemini-2.5-pro -p "Review this auth code for vulnerabilities: ..."

# Three-way debate (Claude + Codex + Gemini)
# See SKILL.md for the full pattern
```

## Version

- Skill: 0.1.0
- Requires: Gemini CLI (npm package)
- Auth: Google OAuth (free tier available)

## See Also

- [codex-bridge](../codex-bridge/README.md) — delegate work to OpenAI Codex
- [SKILL.md](SKILL.md) — full documentation
