# Holocron — Domain Context

## Terms

### Continuity Filter
The site-wide three-state toggle that controls which media entries are visible throughout the app.

**States:** Canon | Both | Legends (displayed in that order, left to right)
**Default:** Both
**Persistence:** Stored in `user_preferences.continuity_filter` (SQLite). Single row, always present (seeded at startup).
**Interaction model:** Changing the state submits a plain HTML form POST to `POST /preferences/set`, which updates the DB and redirects back to the same page (full reload). No partial swap.

### Pillar
A top-level media category. Each Pillar has its own data model, creation form, and browsing pages.

**Active pillars (in display order):**
1. Film
2. Television
3. Games
4. Books
5. Audio
6. Comics ← first built (Sprint 3)
7. Manga

Periodicals intentionally excluded from the current scope (may be added later).

### Continuity
A property of media entries and characters. Three values: `canon`, `legends`, `both`.
- `canon` — part of the Disney-era Canon timeline
- `legends` — part of the pre-Disney Legends/EU continuity
- `both` — applies to or spans both continuities

### Era
A named in-universe time period. Eras are continuity-scoped — Canon eras and Legends eras are separate lists. Stored in the `era` table with a `continuity` field.

Era dropdowns in forms filter by the current Continuity Filter state:
- Canon toggle → Canon eras only
- Legends toggle → Legends eras only
- Both toggle → all eras

### Contribution Log
An append-only audit trail. Every create, edit, and delete on any record writes a `ContributionLog` row atomically in the same transaction. Never written without a corresponding data change.
