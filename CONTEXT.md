# Holocron — Domain Context

## Terms

### Continuity Filter
The site-wide three-state toggle that controls which media entries are visible throughout the app.

**States:** Canon | Both | Legends (displayed in that order, left to right)
**Default:** Both
**Persistence:** Stored in `user_preferences.continuity_filter` (SQLite). Single row, always present (seeded at startup).
**Interaction model:** Changing the state submits a plain HTML form POST to `POST /preferences/set`, which updates the DB and redirects back to the same page (full reload). No partial swap. (See `docs/adr/0001-continuity-toggle-full-reload.md`.)
**Also sets a default:** On new entry forms, the toggle pre-fills the Continuity field (Canon/Legends/Both).

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
- `both` — simultaneously valid in BOTH Canon and Legends (like the George Lucas films). It does NOT mean "a mix of Canon and Legends content". A `both` entry is ONE record: editing it once updates it for both continuities. Its only continuity-specific data is the pair of Eras.

New characters created inline inherit the continuity of the issue they are entered on.

### Era
A named in-universe time period. Eras are continuity-scoped — Canon eras and Legends eras are separate lists. Stored in the `era` table with a `continuity` field.

On an entry form, the **Continuity field on the form** (not the site-wide toggle) decides which Era dropdowns appear:
- Continuity = Canon → one Canon Era dropdown (required)
- Continuity = Legends → one Legends Era dropdown (required)
- Continuity = Both → two dropdowns: Canon Era and Legends Era (both required)

A "Multiple Eras" choice sets the series' `is_timeline_spanning` flag instead of storing a single era.

### Product Credits
Credits attached to the physical/digital product (an Issue / Entry), not to the story. Examples: cover artist, editor-in-chief, collection editor, Lucasfilm licensing staff. They never travel when a segment is imported. Shown on the Issue form in the "Product Credits" zone. Formal scope name: Product Scope. (Do not call these "Container Credits" or "Issue Credits".)

### Story Credits
Credits attached to a Segment (writer, penciler, colorist, story-level editors). They travel with the segment when it is imported. Formal scope name: Story Scope.

### Container
Tier 1 of the core hierarchy: the Series — the work as a concept, independent of any physical release. (Not related to credits.)

### Contribution Log
An append-only audit trail. Every create, edit, and delete on any record writes a `ContributionLog` row atomically in the same transaction. Never written without a corresponding data change. Each entry may carry an optional Archivist Note typed by the user.
