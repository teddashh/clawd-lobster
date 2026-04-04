# Spec-Driven Development

> Guided workspace creation, spec generation, and autonomous blitz execution.

## What It Does

This skill implements the OpenSpec methodology to turn ideas into structured
specifications and then execute them autonomously. It enforces a strict artifact
DAG so nothing gets built without a clear spec trail, and uses branch-isolated
"blitz" runs to go from spec to working code in one shot.

## How It Works

Built on the 3W1H framework (Why, What, Who, How), the skill provides five
modes:

| Command | Purpose |
|---------|---------|
| `/spec` | Create a new workspace and start spec generation |
| `/spec:status` | Show current spec progress and artifact state |
| `/spec:add` | Add requirements or constraints to an existing spec |
| `/spec:blitz` | Autonomous execution: spec to code in branch isolation |
| `/spec:archive` | Archive a completed spec workspace |

**Artifact DAG** (strict order, each depends on the previous):

```
project.md -> proposal.md -> design.md -> specs/ -> tasks.md
```

**Blitz mode** creates a `blitz/<change>` branch, commits per phase, and drops
a `.blitz-active` marker file while running. Branch isolation ensures the main
branch stays clean until review.

## Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `default_depth` | string | `mvp` | Spec depth: `mvp`, `standard`, or `enterprise` |
| `auto_create_github` | boolean | `false` | Auto-create GitHub repo for new workspaces |
| `blitz_auto_approve` | boolean | `false` | Skip confirmation before blitz execution |

## Dependencies

- `memory-server` skill
- `absorb` skill
- `evolve` skill
- `git`
- `claude`

## Credentials

None required.

## Maintenance

The spec artifact DAG is enforced at runtime. Attempting to skip a stage (e.g.,
jumping from `project.md` to `specs/`) will be rejected. If a blitz is
interrupted, check for a leftover `.blitz-active` marker and the corresponding
`blitz/<change>` branch before resuming.

---

**Version:** 0.1.0 | **Kind:** prompt-pattern | **Default:** always-on
