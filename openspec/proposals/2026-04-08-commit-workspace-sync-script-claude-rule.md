# Proposal: Commit workspace-sync script + .claude rules

**Source:** evolve-tick on CastleRidge_AI1
**Date:** 2026-04-08
**Workspace:** clawd-lobster
**Effort:** small
**Status:** pending

## Why
scripts/workspace-sync.py and .claude/rules/ are untracked but essential for onboarding new workspaces. Without them in git, clones lack the agent rule framework and the sync tooling.

## What
Stage scripts/workspace-sync.py and .claude/rules/ (already has committed rules under .claude/rules/ in the repo, but the local .claude/ with hooks should be reviewed)

## Who
New clones and fresh setups get a working agent environment out of the box

## How
Review .claude/hooks for any secrets or machine-specific paths, then commit the safe subset alongside workspace-sync.py
