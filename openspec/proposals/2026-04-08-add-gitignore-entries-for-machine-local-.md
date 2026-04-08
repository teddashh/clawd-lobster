# Proposal: Add .gitignore entries for machine-local files

**Source:** evolve-tick on CastleRidge_AI1
**Date:** 2026-04-08
**Workspace:** clawd-lobster
**Effort:** small
**Status:** pending

## Why
The .claude/ directory contains both shareable rules and machine-local hooks/state. Without clear gitignore boundaries, future sessions risk accidentally committing local-only files or missing shared ones.

## What
Update .gitignore to explicitly include .claude/rules/ while excluding .claude/hooks/ and any session-specific state

## Who
All contributors — prevents accidental commits of local config while keeping shared rules tracked

## How
Review current .gitignore, add explicit include/exclude patterns for .claude/ subdirectories, document the convention in README
