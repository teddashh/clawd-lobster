# Proposal: Commit learned skills to repo

**Source:** evolve-tick on CastleRidge_AI1
**Date:** 2026-04-08
**Workspace:** clawd-lobster
**Effort:** small
**Status:** pending

## Why
18 learned skill files sit untracked — they'll be lost on clone and are invisible to other machines. These represent accumulated pattern knowledge that should be version-controlled.

## What
Stage and commit all files under skills/learned/ and skills/workspace-sync/

## Who
Any user or machine cloning this repo benefits from pre-loaded skill knowledge

## How
Review each skill file for personal info leaks, then git add skills/learned/ skills/workspace-sync/ and commit
