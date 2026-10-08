# Part 1 Cleanup — Handoff to Claude Code
Written 2026-10-08 from the planning chat. Every item below was explicitly approved by Jorge (product owner).

**Two phases. Do ONLY Phase A now. Phase B (code) waits until Jorge says the Part 2 design brainstorm is done.**
Work surgically: edit only what is named. Commit after each numbered step. Do not mark anything [DECIDED] that is not listed here as approved.

---

# PHASE A — Documents and files (no app code)

## A1. Move and rename files (use `git mv` so history follows)
1. `docs/Holocron-PRD-v2.md` → `docs/Holocron-PRD.md`
2. `docs/Holocron-Sprint1-Scope.md` → `docs/archive/Holocron-Sprint1-Scope.md`
3. `docs/Holocron-Roadmap-v3.md` → `docs/archive/Holocron-Roadmap-v3.md`
4. `docs/gemini/` (the era-research PDF) → `docs/archive/research/`
5. Put this banner as the first lines of each archived .md file (not the PDF):
   `> **ARCHIVED 2026-10-08 — historical record only. Superseded by <replacement>. Do not use as a spec.**`
   Replacement for Sprint1-Scope: "docs/Holocron-PRD.md §6". For Roadmap: "docs/Holocron-Workflow.md".
6. Commit: `docs: archive retired docs, rename PRD`

## A2. Confirm already-placed files
These were written by the planning chat; do not rewrite them, just confirm they exist and commit if uncommitted: `CLAUDE.md`, `CONTEXT.md`, `docs/Holocron-Workflow.md`, `docs/Holocron-Data-Entry-Guide.md`, `docs/history/DEVLOG.md`. In `CLAUDE.md`, the path `docs/Holocron-PRD.md` must be correct after A1.
Commit: `docs: slim CLAUDE.md, add workflow, data-entry guide, devlog`

## A3. Convert requirements.txt to UTF-8
It is saved as UTF-16. Re-save as UTF-8 with the same package lines. Verify with `uv pip install -r requirements.txt --dry-run` (or equivalent). Commit.

## A4. Edit `docs/Holocron-PRD.md` (surgical — do not rewrite the file)
Prerequisite: Jorge has already replaced the file with the October Project version before this handoff. If the file still contains "Periodicals" in the §3.1 pillar table, STOP and tell Jorge.

**Header:** Version 0.3 → 0.4; Last Updated → October 8, 2026.

**How to Use This Document (top):** add: "(5) Nothing is marked [DECIDED] without the product owner's explicit approval. (6) The repo copy of this file is the source of truth; the claude.ai Project holds a snapshot, re-uploaded at the end of each session. (7) LOCG and GCD inform design; they are not copied."

**§1.3 Constraints:** change "American releases only — non-US editions out of scope" to "American releases are the primary focus; international editions are added only occasionally, by exception".

**§2.3 Canon/Legends Toggle:** (a) toggle order is Canon | Both | Legends; (b) add definition: "*Both* means simultaneously valid in both Canon and Legends (e.g. the Lucas films) — not a mix. A Both entry is ONE record; editing it updates both continuities. Its only continuity-specific data is the pair of Era fields."

**§2.6 inline creation:** add "Records created inline (Creator, Publisher, Imprint, Character, Role, link) are created when the form is SAVED, in the same transaction as the log entry — never at the moment of picking 'create new'. This prevents orphan records."

**§2.7:** under Uncredited work add: "[TBD — feature to be designed in a design session; creators only. Characters do not have an uncredited flag.]" Add status note: "Alias table and `credit.alias_id` exist; entry UI, alias-aware creator search and Pseudonym Pages are not yet built."

**§2.9 Contribution Log:** add: "Series and Issue forms (and later the edit pages) end with an optional Archivist Note text box, saved on the log entry."

**§2.10 Metadata Conventions:** add "Dates display site-wide as 'Oct 3, 2026'. Cover dates display as month and year only ('Dec 2026'). Forms accept numeric mm/dd/yyyy entry."

**§3.2.2 Series form:** Reading Level row — add "Column `age_rating` exists but the field is not on the Series form; whether a Series needs its own rating is TBD." Series Type bullets: add "Graphic Novel series may contain any number of Graphic Novel issues."

**§3.2.3 Series Hub:** replace "sorted by issue number" with "sorted by release date; issue number (natural sort: ½=0.5, 1.AU after 1) breaks ties". Add: "Sort options sidebar [TBD — Sprint 4+ browse/filter design]." Date format "Oct 3, 2026" (replace 'mm/dd/yyyy'). Reading-progress summary: add "[not yet built — depends on Personal Tracking, TBD #8]". Series cover = earliest-release-date Regular Issue with a cover.

**§3.2.4 Issue form:**
- Row 3/Type text: "Issue # is used by Regular Issues only and stored without '#'. For Annual, One-Shot, Collected Edition and Graphic Novel, the text typed into the shared box is stored in `issue_title`, and `issue_number` is NULL."
- One-Shot: title may be blank (displays as the Series Title alone).
- Series Type constraints: Regular Series → Regular Issue, Annual, One-Shot, Collected Edition (NOT Graphic Novel). Add: "Collection and Graphic Novel series cannot use Format = Comic."
- Display formulas: keep as written (TPB / HC / (Digital)); add "TPB, never TP".
- Cover Date: "month and year only".
- Release Date: "numeric mm/dd/yyyy entry; displayed 'Oct 3, 2026'".

**§3.2.5 Story Breakdown:** rename "Issue Credits" → "Product Credits" (Zone 1). Add: "Collected Editions use the normal Story Breakdown exactly like any other issue — they may contain material found nowhere else." Character Appearance Type: change "no default — user must explicitly select" to "defaults to Main" (explicit owner change, 2026-10-08, reverses an earlier [DECIDED]).

**§3.2.8 Credit Mechanic:** add (a) each credit row has a "···" attribute button opening a small dialog (currently the Uncredited checkbox); (b) "Every credit row requires a creator and a role; an incomplete row blocks the save with an error"; (c) planned optional free-text note per credit (e.g. 'pages 1, 5', 'framing sequence') [TBD display]; (d) role tables updated to match seeds: Lucasfilm = Lucasfilm Editor, Lucasfilm Art Director, Creative Director, Art Director, Story Group, Creative Art Manager, Licensing Manager; Production adds Senior Editor (issue-level).

**§3.2.9 / §3.2.10 Characters:** appearance type defaults to Main; REMOVE `is_uncredited` from character_appearance (text and data model); inline-created characters inherit the issue's continuity.

**§3.2.14 Variant:** add status note "`variant_cover` table not yet built (planned Sprint 3)".

**§4.1 Navigation:** toggle order; Calendar link: "[not yet built; no Calendar page is specified]"; Dashboard: "currently shows a Recently Added grid; stats block not built".

**§5 Schema:**
- `comic_series`: replace `era_id` with `canon_era_id`, `legends_era_id`.
- `comic_issue`: add `age_rating`, `trim_size_custom`; note `issue_title` holds the title for non-regular types.
- `comic_segment`: add `reproduction` (default 'original').
- `role`: add `sort_order`.
- `character_appearance`: remove `is_uncredited` (in §3.2.10 and §5.2).
- §5.4 era names stay "Visions" and "Infinities" (code seed currently says "(Non-Continuity)" — Phase B fixes the code).

**§6 Build Order, Sprint 3 checklist:** 
- Item 5 → split: "5a ADD button ✓" and "5b IMPORT modal (open)".
- Item 7 ✓. Item 11 ✓. Item 9 → "partial: flag can be set; display not built". Item 10, 8, 6, 12, 13, 14 open.
- Add: "15. `variant_cover` table (open)"; "16. Creator Uncredited feature [TBD — to be designed]"; "17. Rename Product Credits label in the form (Phase B)".
- Remove or update the two "Before Sprint 3: resolve TBD…" lines (credit taxonomy is resolved for Comics; navigation partially).

**§7 Potential Future Features:** add "One-click desktop launcher / always-on background service"; "Tag for an American edition of an internationally-first release".

**§8 TBD Registry:** 
- Move #1 (Comics part resolved), #16, #19, #20 to a "Resolved" sub-table below the open table.
- #7 stays (partially resolved). #8 stays open (remove the 'blocking Sprint 3' framing → 'blocks Dashboard stats and reading progress').
- #13, #14, #15: keep open; note "Claude Design phase not yet done; emoji pillar icons are placeholders". In #14 rename Issue Credits → Product Credits.
- #21: update note → "First draft exists: docs/Holocron-Data-Entry-Guide.md".
- Add new open rows: **#23** Outlier entries (series retitled mid-run with continuing numbering, e.g. Star Wars (1998) → Star Wars: Republic; collected editions with non-standard names) — see manual title override idea. **#24** Issue sort-position column — revisit if release-date + natural-number sort proves insufficient. **#25** Settings and maintenance tools (rename / merge / delete vocabulary and records; note role names are stored as text on credits, so renames must update credits). **#26** Credits deep dive (alias entry flow, uncredited display, per-credit notes, credit design for non-Comics pillars; credit table currently tied to comic tables). **#27** American edition of internationally-first release (tag/field; interacts with Reprint-segment source rule). **#28** Calendar page and Dashboard design. **#29** Series-level age rating.

**§9 (new at end) Change Log:** table with columns Date | Section | Change | Why. Add one row per item above dated 2026-10-08, grouped sensibly, and flag the reversal "Appearance Type default Main (reverses §3.2.5 'no default')".

Commit: `docs: PRD v0.4 — Part 1 reconciliation`.

## A5. Report back
Tell Jorge which files changed, the commit hashes, and anything you could not apply. Then STOP. Do not start Phase B.

---

# PHASE B — Code changes (WAIT for Jorge's go-ahead after Part 2)
Each needs a migration where the schema changes. Ask Jorge before starting; some items may change after the Part 2 design discussion.

1. Era seeds: rename "Visions (Non-Continuity)" → "Visions", "Infinities (Non-Continuity)" → "Infinities" (seed list + data migration for existing rows).
2. Issue titles: non-regular issue types save the typed text to `issue_title` (not `issue_number`); form/hub/index display formulas per PRD §3.2.4 (TPB/HC/(Digital); blank title allowed for One-Shot and Collected Edition). Add hint under the box: leave blank if no subtitle; never type TP/HC.
3. Series-type rules: Regular Series excludes Graphic Novel issues; keep the Format≠Comic rule for Collection/Graphic Novel; server and client lists must agree.
4. Series Hub: order by release date, tiebreak natural issue-number sort (½=0.5; 1.AU after 1; replace `CAST(... AS INTEGER)`); series cover = earliest-release-date Regular Issue with a cover (replace `series.issues.first()` string sort).
5. Date display "Oct 3, 2026" everywhere; cover date "Dec 2026". Release Date stays a native date input (mm/dd/yyyy on Jorge's machine).
6. Validation instead of silent drops: credit rows need creator AND role; error and no save if either is missing. Character rows: appearance type defaults to Main (so no skipped rows).
7. New inline-created characters inherit the issue's continuity (currently hardcoded 'both').
8. Remove `is_uncredited` from `CharacterAppearance` (migration).
9. Archivist Note: optional textarea at the end of the Series and Issue forms; passed to `log_contribution`.
10. Log the missing events: auto-created Role rows and ExternalLink rows.
11. Deferred inline creation: stop calling `/api/create` at pick time in the Story Breakdown JS; rely on the server's `_resolve_creator` / `_resolve_character` / publisher / imprint resolution at save. Same-name new records in one form must resolve to a single record.
12. UI label "Container Credits" → "Product Credits" (template + JS).
13. Series synopsis: render as escaped plain text with line breaks (remove `| safe`).
14. Seeds: add "Senior Editor" to Production roles (sort_order 50 after Production Manager) — plus a data migration if the roles table is non-empty.
15. Remove dead code: `/api/eras-options` route and `partials/era_options.html`.
16. Add a one-command dated backup of `data/holocron.db` and `app/static/uploads/` (destination chosen by Jorge; default `backups/` outside OneDrive sync if possible; add to .gitignore).
17. LATER (after Issue View exists, Jorge decides when): reset the database to empty — fresh `flask db upgrade`, remove test cover files from `app/static/uploads/covers/` (use `git rm`).
