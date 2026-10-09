# Holocron — Development Log

Append-only, dated history of what was built and decided. Newest entries at the bottom.
Claude Code does NOT need to read this file unless Jorge asks. For current rules see `CLAUDE.md`; for current specs see `docs/Holocron-PRD.md`.

Sessions 1-3 below were moved here unchanged from the old `CLAUDE.md` session log (Oct 2026).

### Session 1 — 2026-05-05 — Sprint 1 Complete
Built the full Foundation layer. All 7 Sprint 1 items delivered:
1. Flask app factory (`app/__init__.py`, `config.py`, `run.py`, `.env`)
2. Database + Flask-Migrate (`app/extensions.py`, `migrations/`)
3. ContributionLog model + `log_contribution()` helper (`app/models/audit.py`)
4. UserPreferences model, seeded at startup with `continuity_filter='both'`
5. All 8 reference models: Era, Publisher, Imprint, Creator, CreatorAlias, Character, CharacterPersona, Department — with Canon eras and Comics departments seeded
6. Fuzzy search endpoint: `GET /api/search?q=&type=` using rapidfuzz WRatio, threshold 50
7. Inline creation endpoint: `POST /api/create` for creator/publisher/imprint/character/character_persona, with ContributionLog written atomically on every create

3 migration files applied cleanly. Flask returns 200. All Sprint 1 Definition of Done criteria met.

### Session 2 — 2026-05-05 — Sprint 2 Complete
Built all 8 Comics Pillar data models. Pre-work: resolved Era code gap (TBD #16 had been closed in PRD but code wasn't updated) — added `sort_order` to Era model, replaced Sprint 1 era names with canonical PRD §5.4 names, seeded all 18 Canon + Legends eras.

Sprint 2 models delivered (all in `app/models/comics.py`):
1. `ComicSeries` — FKs to era, publisher, imprint; `is_timeline_spanning` flag
2. `ComicIssue` — `designation` (issue type) + `physical_binding` (format) + `trim_size_custom` for "other" trim
3. `ExternalLink` — child of ComicIssue; built after Issue before moving to Segments
4. `ComicSegment` — `reproduction` field default 'original'; `sort_order` always editable
5. `SegmentRelationship` — self-referencing on comic_segment; `source_of` / `derived_from` backrefs
6. `Credit` — `segment_id` NULL for product scope, `issue_id` NULL for story scope — exactly one set per row
7. `CharacterAppearance` — wired deferred FK on `CharacterPersona.first_appearance_segment_id` in same migration
8. `SeriesMembership` — polymorphic by `entry_type` string (no hard FK); ready for Associative Pillars

Conventions added this session:
- `seed_all()` now uses `_row_count()` with raw SQL for table count checks — safe to call before migrations run (ORM count queries fail if model columns don't yet exist in DB)
- SQLite + `batch_alter_table` requires named FK constraints — always name them (e.g. `'fk_persona_first_appearance_segment'`)
- `SeriesMembership` is intentionally FK-free on `series_id`/`entry_id` — polymorphic join, discriminated by `entry_type`

9 migration files total (4 from Sprint 1 pre-work + Era fix, 8 for Sprint 2 models). All migrations applied cleanly. All 19 tables present.

### Session 3 — 2026-05-17/18 — Sprint 3 UX Polish + Story Breakdown JS Rebuild

**Floating label pattern (site-wide):**
- Added 7 component classes to `app/static/css/input.css` via `@layer components`: `fl-group`, `fl-label`, `fl-input`, `fl-select`, `fl-textarea`, `fl-static`, `fl-req`
- Applied to all fields in `series_new.html` and `issue_new.html` (text inputs, selects, textareas, static display divs)
- Required fields use `<span class="fl-req">*</span>` (red asterisk); `updateIssueNumberField()` JS updated to match

**Role sort_order:**
- Added `sort_order` column to `Role` model (`app/models/reference.py`)
- Migration `a8a570bd4199` — adds column, clears and reseeds 29 Comics roles across 6 departments
- `seeds.py` updated to 3-tuples; `_resolve_role()` in `comics.py` assigns `max + 10` for new user-typed roles
- `/api/roles` endpoint now orders by `sort_order, name`

**Story Breakdown JS rebuild (`issue_new.html`):**
- `ISSUE_CONTINUITY` const passed to character search for soft continuity sorting
- `toggleContainerCredits()` — collapses Container Credits block, toggles `rounded-b-lg` on header
- `addCreditRow()` — `data-is-uncredited="false"`, `···` attr button, `z-[9999]` on all `.sb-drop`
- `openAttr()` / `saveAttr()` / `closeAttr()` — `<dialog>` modal sets `is_uncredited` on row dataset; attr btn tints yellow when active
- `addSegment()` — removed `overflow-hidden`, `rounded-t-lg`/`rounded-b-lg` split, `grid-cols-5` for colors/pages, Credits + Characters section labels
- `toggleSegment()` — toggles `rounded-b-lg` on header when collapsed
- `_showDrop()` — opaque `bg-gray-800 border border-gray-700 rounded-md shadow-xl overflow-hidden` wrapper div
- `gatherStoryJson()` — reads `#container-credits-block`, collects `is_uncredited` on all credit rows
- `routes/comics.py` — `is_uncredited` written to both product and story Credits on save
- `routes/api.py` — `_search_character_combined()` soft-sorts by continuity (exact → both → other)

Conventions added:
- Segment blocks must NOT use `overflow-hidden` — clips absolutely positioned autocomplete dropdowns; use `rounded-t-lg`/`rounded-b-lg` on header/body individually instead
- `<dialog>` element used for modal; call `.showModal()` / `.close()` — no JS-based show/hide needed
- Tailwind arbitrary value `z-[9999]` required for Story Breakdown dropdowns to float above all content

### Oct 2026 — Re-acquaintance (not a build session)
Between Session 3 (May 17/18) and the Part 1 review, Jorge returned after a multi-month gap and used the running site to re-learn it. This left test records in the database (test series, a duplicate issue #1, a junk publisher, orphan creators). All current entries are test data and will be deleted before real data entry begins (planned after the Issue View page exists).

### 2026-10-08 — Part 1 documentation reconciliation (planning chat)
Reconciled PRD, Sprint 1 scope, CLAUDE.md and Roadmap against the code. Outcomes: the Project PRD (Oct) became the master and was synced to the repo; repo copy is now the source of truth; Roadmap trimmed into `docs/Holocron-Workflow.md`; Sprint 1 scope and old Roadmap archived; new `docs/Holocron-Data-Entry-Guide.md` started; `CLAUDE.md` slimmed; schema/rule drift between PRD and code resolved on paper (code changes are queued in `docs/history/part1-cleanup-handoff.md`, Phase B). Part 2 (design brainstorm) follows.

**2026-10-09 — Comics Build Plan Stages 0–1.** Stage 0: PRD v0.5 (Appendix A decisions applied; Change Log rows added). Stage 1: Phase B #1, #4, #5, #12, #13, #14, #15, #16 done — era names Visions/Infinities, series hub order (release date, natural issue-number tiebreak) and series cover rule, date display helpers, "Product Credits" label, plain-text series synopsis, Senior Editor (Production), removed /api/eras-options, `flask backup` (writes to `backups/`, git-ignored). Two data migrations (c3e1f0a7b201, d7b2a9c4e815). Next: Stage 2 (database foundations).

**2026-10-10 — Comics Build Plan Stage 2 (database foundations).** One commit each, in plan order. (1) `issue_number` nullable; only regular issues keep a number, other types keep the text in `issue_title`; display names generated by `issue_display_title` ("TPB", "HC", "(Digital)"); existing test rows migrated (e2a4c6b8d013). (2) Series-type rules now one table in `comics.py` read by both server and form; regular series no longer accepts graphic novels. (3) `comic_series.volume` (f3b5d7c9e124). (4) Credits point at any target via `credit.target_type` + `target_id` (no FK, like `series_membership`), new `credit.note`; `segment_id`/`issue_id` removed, 7 test credits carried across (a4c6e8d0f235) — **shape is still [DRAFT] in the PRD; Jorge to confirm.** (5) Credit save path accepts `alias_id`; refused if the alias belongs to another person or the credit is also Uncredited. (6) `character_appearance.is_uncredited` dropped (b5d7f9a1c346). (7) New empty tables `product_mark` (read/own/wish, unique per product+mark) and `log_entry` (date + read_before), polymorphic by `product_type` + `product_id` — also [DRAFT] (c6e8a0b2d457). (8) No change needed: `contribution_log.archivist_note` already existed. (9) Duplicate issue refused in code only (no DB constraint — test data already has duplicates); non-regular types compare title + format. (10) `log_edit()` in `app/models/audit.py` stores only changed fields, old and new, plus the note. Backup taken first (`backups/2026-10-10_000224`). Next: Stage 3a (Series form + Edit series).

## 2026-10-10 — Stage 3a: Series form + Edit series
- Series form rebuilt in the Build Plan order (Publisher/Imprint dropdowns with "+ Add new…", Title, Series Type + Vol. #, Continuity/Era, years + Age Rating, Synopsis, Notes). One template (`series_form.html`) serves Create and Edit.
- New publishers/imprints are created only on save, matched case-insensitively (imprint matched within its publisher).
- End Year before Start Year refused; clearer era errors; series-type change on edit is checked against the issues the series already holds.
- Edit saves through `log_edit` (old → new + Archivist Note); new `/comics/series/<id>/history` page. Series page has the Edit ▾ menu and shows "Vol. N" beside publisher and years.
- No schema change. Old `series_new.html` removed.
