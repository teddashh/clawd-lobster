# Proposal: Track .claude/ rules in git

**Source:** evolve-tick on CastleRidge_AI1
**Date:** 2026-04-08
**Workspace:** clawd-lobster
**Effort:** small
**Status:** pending

## Why
The .claude/ directory contains evolution, memory, safety, and tools rules that define agent behavior — currently untracked, so they diverge across machines and are invisible to collaborators

## What
Commit .claude/rules/*.md and .claude/settings.json (excluding any secrets)

## Who
All agents and contributors who clone the repo

## How
Add .claude/ to git (it's already not in .gitignore), review for secrets, commit
