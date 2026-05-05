# CLAUDE.md — Holocron

## What This App Is
Holocron is a personal, locally-hosted, single-user archival database for tracking Star Wars multimedia. Runs at localhost:5000. No authentication. No login screen. No external API calls at runtime.

## Tech Stack
- Backend: Python 3.12, Flask, Flask-SQLAlchemy, Flask-Migrate (Alembic)
- Database: SQLite — file: data/holocron.db
- Frontend: Jinja2 templates, Tailwind CSS
- Interactivity: htmx (Sprint 3+)
- Fuzzy search: rapidfuzz
- Package management: uv

## Always Do
- Read docs/Holocron-PRD-v2.md before building any feature
- Use Flask-Migrate for ALL schema changes — never edit the database directly
- Build Contribution Log logging into every model create/edit/delete
- Commit after every working feature
- Update this file at the end of every session with a summary of what was built

## Never Do
- Install React, Vue, or any JavaScript framework
- Call external APIs
- Hardcode Star Wars data in Python — use database seeding instead
- Skip migrations — even tiny field additions need a migration file
- Build features marked [TBD] in the PRD without asking the product owner

## Current Sprint
Sprint 1 — Foundation
Reference: docs/Holocron-Sprint1-Scope.md

## Session Log
*(append summaries here after each session)*