# Proposal: Add unit tests for core modules

**Source:** evolve-tick on CastleRidge_AI1
**Date:** 2026-04-08
**Workspace:** clawd-lobster
**Effort:** medium
**Status:** pending

## Why
tests/ only has 2 onboarding test files — the core clawd_lobster package, skill manager, and webapp have zero test coverage, making regressions invisible

## What
Add tests for clawd_lobster/ core logic, scripts/skill-manager.py, and webapp API endpoints

## Who
Maintainers — prevents silent breakage as the project grows

## How
Start with skill-manager.py (pure logic, easy to test), then add pytest fixtures for webapp API routes
