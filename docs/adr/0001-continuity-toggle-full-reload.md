# ADR 0001 — Continuity Filter toggle uses full page reload

**Date:** 2026-05-07
**Status:** Accepted

## Context

The Canon/Legends/Both toggle is a site-wide filter that affects every listing and browsing page. It stores its state in the `user_preferences` table (single row, always present). The app uses htmx for interactivity.

## Decision

Changing the toggle fires a plain HTML form `POST /preferences/set`. The route updates the DB and redirects to `request.referrer`. The entire page reloads.

## Alternatives considered

**htmx partial swap** — toggle updates the DB via htmx, then swaps only `<main>` content. Faster feel, but requires every page's content region to be independently renderable as an htmx partial from the start.

## Reasons

1. The toggle applies to every page's content. A full reload guarantees the re-rendered page always reflects the DB state — no risk of stale content.
2. Sprint 3 has one content area. The performance difference on localhost is imperceptible.
3. Partial swap can be adopted later without changing the POST endpoint — only the redirect behaviour and template structure would change.

## Consequences

Every page template must read `continuity_filter` from `user_preferences` on each request (via a context processor) to render the nav toggle in the correct state.
