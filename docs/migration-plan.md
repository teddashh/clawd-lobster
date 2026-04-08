# Full Migration Plan — Ted's System

**Date:** 2026-04-08
**Status:** READY TO EXECUTE

## Phase 1: Fix claude-bot as Private Hub

- [x] CLAUDE.md rewritten as Hub control center
- [x] templates/ removed (repo-level, not Hub)
- [ ] Verify MCP memory tools work (restart Claude Code)
- [ ] Verify 115 knowledge items are valid
- [ ] Verify 26 learned skills are valid

## Phase 2: Clone + Register Active Workspaces

### Public Repos
| Repo | Action | Workspace Name |
|------|--------|----------------|
| `clawd-lobster` | Keep as-is in clawd-lobster-dev | (not a workspace — it's the generator) |
| `multi-ai-chat` | Clone → register workspace | `multi-ai-chat` |
| `teddashh` | Clone → register workspace | `teddashh-profile` |
| `mcp-memory-server` | Clone → register workspace | `mcp-memory-server` |

### Private — AI/Agent (Keep)
| Repo | Action | Workspace Name |
|------|--------|----------------|
| `mcp-memory-private` | Clone → register workspace | `mcp-memory-private` |

### Private — Work/Enterprise (Keep)
| Repo | Action | Workspace Name |
|------|--------|----------------|
| `bang-usa-new` | Register existing `C:\Users\detna\BangUSA` | `bang-usa` |
| `daily-looker-report` | Clone → register | `daily-looker-report` |
| `corporate-communication-platform` | Clone → register | `corporate-comms` |
| `mobile-device-and-data-prevention` | Clone → register | `mobile-device-security` |
| `soar` | Clone → register | `soar` |
| `special-assignment` | Clone → register | `special-assignment` |
| `weekly-progress` | Clone → register | `weekly-progress` |
| `daily-cyber-security-report` | Clone → register | `daily-cybersec` |
| `windows-fine-tuning` | Clone → register | `windows-tuning` |
| `email-triage` | Clone → register | `email-triage` |
| `resume-review` | Clone → register | `resume-review` |

### Private — Personal/Entertainment (Keep)
| Repo | Action | Workspace Name |
|------|--------|----------------|
| `doom-of-the-lost-kingdom-revolution` | Register existing `C:\Users\detna\Doom` | `doom-mud` |

### Local Projects (Not on GitHub yet)
| Path | Action | Workspace Name |
|------|--------|----------------|
| `C:\pinokio\api` | Register → workspace | `twaigirl-comfyui` |

## Phase 3: Absorb + Archive Old Repos

These repos get their knowledge absorbed into claude-bot's memory, then archived:

| Repo | Action |
|------|--------|
| `openclaw-config` | Absorb knowledge → archive GitHub repo |
| `openclaw-workspace` | Absorb knowledge → archive GitHub repo |
| `ai-dispatch` | Absorb knowledge → archive GitHub repo |
| `vibe-coding` | Absorb knowledge → archive GitHub repo |
| `AI_Base` | Absorb knowledge → archive GitHub repo |
| `knowledge` | Check overlap with memory system → absorb if unique → archive |
| `dating-calendar` | Absorb knowledge → archive |
| `erotic-game` | Absorb knowledge → archive |
| `clawd-teddy` | Already archived (replaced by claude-bot) |
| `coding-interview-university` | Already archived (fork, unused) |
| `better-agent-terminal` | Already archived (fork, unused) |

## Phase 4: Deferred (Other Machine)

| Repo | Note |
|------|------|
| `claude-setup` | Another machine's repo, handle later |
| `avd-scheduler` | Another machine's repo, handle later |

## Phase 5: Cleanup

- [ ] Remove old local folders after absorb is confirmed
- [ ] Remove old scheduled tasks that shouldn't run
- [ ] Verify all new cron jobs (evolve, heartbeat, sync) are registered
- [ ] Verify all workspace agents can connect (MCP + memory)
- [ ] Verify claude-bot Hub has complete knowledge from all absorbed repos
- [ ] Verify clawd-lobster-dev is clean (no personal data)
- [ ] Verify Remote Claude Code / scheduled agents work

## Phase 6: Verification

For each workspace:
- [ ] `claude` can start in the workspace
- [ ] MCP memory tools respond
- [ ] CLAUDE.md is appropriate for the project
- [ ] Git remote is correct
- [ ] Registered in workspaces.json

## Execution Order

1. Fix claude-bot Hub (Phase 1)
2. Clone + register workspaces one by one (Phase 2)
3. Absorb old repos into claude-bot memory (Phase 3)
4. Clean up old folders + tasks (Phase 5)
5. Verify everything (Phase 6)
6. Run roundtable audit on final state
