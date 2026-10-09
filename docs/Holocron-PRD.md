# Holocron — Product Requirements Document
**Version:** 0.5
**Status:** Active — Foundation + Comics Pillar Fully Specced
**Audience:** Claude Code (Developer)
**Last Updated:** October 9, 2026
 
---
 
## How to Use This Document
 
This is the authoritative specification for the Holocron application. Before building any feature:
1. Read the relevant section of this PRD
2. If something is marked **[TBD]**, do not invent a solution — flag it and ask the product owner
3. If something contradicts CLAUDE.md, this PRD takes precedence for feature-level decisions
4. After completing any feature, note decisions made that aren't covered here so the PRD can be updated
5. Nothing is marked [DECIDED] without the product owner's explicit approval
6. The repo copy of this file is the source of truth; the claude.ai Project holds a snapshot — push to GitHub, then press Sync now in the Project
7. LOCG and GCD inform design; they are not copied
**[DECIDED]** = locked, build exactly as specified
**[TBD]** = known gap, park and build around it
**[FUTURE]** = out of scope for current build phase
**[DRAFT]** = proposed but not yet confirmed by product owner
 
---
 
## 1. Project Overview
 
### 1.1 What This App Is
**[DECIDED]**
 
**Holocron** is a personal, locally-hosted, single-user archival database for tracking Star Wars multimedia. It is not a social platform, not a recommendation engine, and not connected to any external API or service at runtime.

Holocron is a complete catalogue of Star Wars multimedia with a personal layer (Read / Own / Wish marks and a Diary log, see §4.6) on top. Comics are the current build scope. Importing from an existing spreadsheet is out of scope.
 
Primary reference points:
- **Letterboxd** — personal tracking, rating UI, dark aesthetic, creator pages
- **League of Comic Geeks (LOCG)** — issue grids, reading progress, dense metadata, segment/story breakdown, import mechanic
- **Goodreads** — series grouping for non-serialized media
- **IMDB** — title page structure, metadata hierarchy, credit display conventions
### 1.2 Core Use Patterns
**[DECIDED]**
 
1. **Logging** — adding new media entries as announced or acquired
2. **Browsing** — exploring by era, creator, publisher, character, or pillar
3. **Discovering** — clicking a creator or character to see their full Star Wars body of work
### 1.3 Constraints
**[DECIDED]**
 
- Local only — runs at `localhost:5000`, no internet required at runtime
- Single user — no authentication, no login screen
- No external API calls — all data entered manually
- American releases are the primary focus; international editions are added only occasionally, by exception
- No JavaScript frameworks (React, Vue, etc.)
### 1.4 Tech Stack
**[DECIDED]**
 
- **Backend:** Python 3.13, Flask, Flask-SQLAlchemy, Flask-Migrate (Alembic)
- **Database:** SQLite — file: `data/holocron.db`
- **Frontend:** Jinja2 templates, Tailwind CSS
- **Interactivity:** htmx (Sprint 3+)
- **Rich text:** Quill or TipTap → Quill (implemented in Sprint 3)
- **Package management:** uv
---
 
## 2. Global Architecture
 
### 2.1 The Core Hierarchy
**[DECIDED]**
 
All media in Holocron is organized around three conceptual tiers:
 
| Tier | Name | Definition |
|------|------|-----------|
| 1 | **Series / Container** | The work as a concept — exists independently of any physical release |
| 2 | **Issue / Entry / Work** | The specific physical or digital product |
| 3 | **Segment** | The actual narrative or creative content within an Issue |
 
### 2.2 Two Structural Patterns
**[DECIDED]**
 
**Compositional Hierarchy** — child objects cannot exist independently of parent. Used for serialized media:
- TV: Series → Season → Episode
- Comics: Series → Issue
- Manga: Series → Issue
**Associative Grouping** — entries exist independently, optionally linked to a named series via `SeriesMembership` join table. Used for standalone media:
- Film, Books, Audio, Games
One entry can belong to multiple Series simultaneously with different position numbers.
 
### 2.3 Canon/Legends Toggle
**[DECIDED]**
 
A persistent, site-wide filter control in the navigation bar.
 
**Three states (toggle order):** Canon / Both / Legends

*Both* means simultaneously valid in both Canon and Legends (e.g. the Lucas films) — not a mix. A Both entry is ONE record; editing it updates both continuities. Its only continuity-specific data is the pair of Era fields.
 
**Persistence:** Remembered across sessions. Stored in `user_preferences` table.
 
**Display filter behavior:**
- Canon → shows entries tagged Canon + entries tagged Both
- Legends → shows entries tagged Legends + entries tagged Both
- Both → shows everything
**Applies to:** Every listing and browsing page — collection grid, calendar, series pages, creator pages, character pages, publisher pages, search results.
 
**Data entry context:**
- Canon toggle → Continuity field pre-fills as Canon on new entry forms
- Legends toggle → pre-fills as Legends
- Both toggle → pre-fills as Both
**Era field behavior by Continuity selection:**
- Continuity = Canon → single Era dropdown, Canon eras only, required
- Continuity = Legends → single Era dropdown, Legends eras only, required
- Continuity = Both → two Era dropdowns appear simultaneously:
  - Canon Era (Canon eras only, required)
  - Legends Era (Legends eras only, required)
Applies to all pillars and all entry forms site-wide.
 
**Character and creator pages:**
- Character/Creator records are continuity-agnostic
- Toggle filters *appearances* and *credits* shown on their pages through the linked entry's continuity
- "Both" tagged entries always visible regardless of toggle state
### 2.4 Credit Scoping
**[DECIDED]**
 
Every credit belongs to one of two scopes:
 
**Story Scope (Segment-level):** Credits attached to the narrative. Travel automatically when a Segment is imported. Example: writer, penciler, colorist of a comic story.
 
**Product Scope (Issue-level):** Credits attached to the physical/digital product. Never migrate. Example: cover artist, collection editor, editor-in-chief.

**[DRAFT]** Credits are intended to live in one flexible list that can point at any credited item (a comic story or issue now; later a TV episode, film, game, etc.), so one creator page serves all media. See §5.3.
 
### 2.5 Segment Relationships
**[DECIDED]**
 
Segments can be linked to other Segments via a first-class `SegmentRelationship` object. Every Segment — regardless of position in a chain — is independently importable. This is the key architectural difference from LOCG.
 
**Fields that travel on import:** Title, Type, Colors, Pages, Credits, Characters
**Fields that never travel:** Sort Order (auto-assigned at destination), Reproduction Type (describes the action, not the segment)
 
**Reproduction Types and locking behavior:**
 
| Type | Title | Type | Colors | Pages | Credits | Characters |
|------|-------|------|--------|-------|---------|------------|
| Original | Editable | Editable | Editable | Editable | Editable | Editable |
| Reprint | Locked | Locked | Locked | Locked | Locked | Locked |
| Remaster | Locked | Locked | Editable | Locked | Editable | Locked |
| Altered | Editable | Editable | Editable | Editable | Editable | Editable |
| Compilation | Blank+Edit | Editable | Editable | Blank+Edit | Inherited+Edit | Inherited+Edit |
| Excerpt | Locked | Locked | Locked | Editable | Locked | Editable |
 
**Type field:** Always locked on import regardless of Reproduction Type — a Story doesn't become an Illustration because it's reprinted.
 
**Sort Order:** Always editable regardless of Reproduction Type — positional, not content-describing.
 
**Reproduction Type definitions:**
- **Original** — first published version, no source
- **Reprint** — 1:1 copy, all fields sync from source
- **Remaster** — same story, new colors or digital restoration. Color credits editable, story credits sync
- **Altered** — single-source, creatively modified (trimmed, expanded, restructured). All fields editable
- **Compilation** — one derived segment assembled from multiple source segments. Credits and characters auto-populated from all sources, deduplicated by Creator + Role. Title and Pages start blank
- **Excerpt** — partial content. Pages and Characters editable (subset); Credits locked (creators credited for whole work)
**Cascade behavior:** Silent. Corrections to source segments propagate automatically per Reproduction Type rules. All cascade events recorded in Contribution Log on both source and derived records.
 
**Deletion rule:** Block deletion. A segment with downstream imports cannot be deleted until all derived segments are unlinked or reassigned. Warning shown listing all derived segments.
 
### 2.6 Reference Objects (First-Class Entities)
**[DECIDED]**
 
The following have their own database records and browseable pages:
- **Creator** — canonical identity of a person or studio
- **Creator Alias / Pseudonym** — linked to canonical Creator, displays as printed
- **Publisher** — company that released an Edition
- **Imprint** — sub-label within a Publisher
- **Character** — baseline identity of a named entity
- **Character Persona** — linked to baseline Character (e.g. Darth Vader → Anakin Skywalker)
**Inline creation with fuzzy matching:** All reference fields use autocomplete. Near-matches surfaced before creating new records. If no match, new record created on save.

Records created inline (Creator, Publisher, Imprint, Character, Role, link) are created when the form is SAVED, in the same transaction as the log entry — never at the moment of picking "create new". This prevents orphan records.
 
### 2.7 Creator Pseudonyms and Uncredited Work
**[DECIDED]**
 
**Display:** Credits show name as printed on the page (alias name, not canonical name).
 
**Clicking a pseudonym:** Takes you to a distinct Pseudonym Page (own URL) showing all credits under that alias. Prominent link to canonical Creator Page. Canonical Creator Page shows all credits across all aliases unified.
 
**Uncredited work:** Boolean `is_uncredited` flag on Credit record. Displays inline with role label: `Colorist (Uncredited)`. No separate section.

[TBD — feature to be designed in a design session; creators only. Characters do not have an uncredited flag.]

**Aliases follow the person (October 9, 2026) [DECIDED]:** a credit may say "credited as" one of the person's saved aliases via `credit.alias_id`. Typing an alias in the creator box finds the real person. Credit attributes (Uncredited, As…, Note) are specified in §3.2.8.

**Status:** Alias table and `credit.alias_id` exist; entry UI, alias-aware creator search and Pseudonym Pages are not yet built.
 
**Alias types:** pseudonym / studio name / name variation
 
### 2.8 Series Cover Inheritance
**[DECIDED]**
 
- **Compositional Pillars** (Comics, TV, Manga): Series thumbnail dynamically generated from first Issue's cover. Placeholder shown until Issue #1 has a cover.
- **Associative Pillars** (Film, Books, Audio, Games): Cover image uploaded directly on entry form.
**Placeholder images:** Pillar-specific icons site-wide. Style and accent colors TBD in Claude Design phase. Creator/Character placeholder: neutral person silhouette. Style TBD.
 
### 2.9 Contribution Log (Audit Trail)
**[DECIDED]**
 
Every create and edit action on any record triggers a `ContributionLog` entry. **Build this before any other model in Sprint 1.**
 
Log fields:
- Timestamp
- Action type: Create / Edit / Delete
- Record type and ID affected
- Diff: old value vs. new value (JSON)
- Archivist Note: freeform text, optional — user justifies the change
Visible on each entry page as a collapsible change history.

Series and Issue forms (and later the edit pages) end with an optional Archivist Note text box, saved on the log entry. The box is empty each time a form is opened; the note belongs to that edit only and is visible only in Edit history (on the Series form it is labelled "Notes").

**Edit history [DECIDED]:** Editing a Series or Issue stores, for each changed field, its value before and after, plus the Archivist Note. Edit history is a simple read-only list: date, "created" or "edited", what changed (old → new), and the Note. Full design of Edit history is pinned (§8).
 
### 2.10 Metadata Conventions
**[DECIDED]**
 
All metadata defers to official publisher-assigned values. Personal assessments go in Personal Notes. Exception: if a publisher value is a known misprint or error, enter the correct value and document the reason in the Archivist Note field.
 
Credit role terminology uses standardised catch-all terms rather than literal on-page credit text. Enter "Colorist" rather than "Color Artist" or "Colors by." Consistency and filterability over literal transcription.

Dates display site-wide as "Oct 3, 2026". Cover dates display as month and year only ("Dec 2026"). Forms accept numeric mm/dd/yyyy entry.
 
---
 
## 3. Pillars
 
### 3.1 Pillar Overview
**[DECIDED — structure; TBD — metadata fields for non-Comics Pillars]**
 
| Pillar | Structure | Atomic Unit | Status |
|--------|-----------|-------------|--------|
| Comics | Compositional: Series → Issue | Issue (with Segments) | ✓ Fully specced |
| Television | Compositional: Series → Season → Episode | Episode (with Segments) | Structure decided, metadata TBD |
| Film | Associative | Film (with Segments) | Structure decided, metadata TBD |
| Books | Associative | Book (with Segments) | Structure decided, metadata TBD |
| Audio | Associative | Audio Work (with Segments) | Structure decided, metadata TBD |
| Games | Associative | Game (with Segments) | Structure decided, metadata TBD |
| Manga | Compositional: Series → Issue | Issue (with Segments) | Structure decided, metadata TBD |
 
**Build order:** Comics → Television → Film → Books → Audio → Games → Manga
 
**Periodicals** is excluded from current scope as of October 2026 (product owner decision). Not abandoned — logged as a potential future addition, see Section 7.
 
---
 
### 3.2 Comics Pillar — Full Specification
**[DECIDED]**
 
#### 3.2.1 Workflow
 
1. User selects **[Add New Media]** → **[Comics]** from navigation
2. System presents **Series Creation Form**
3. On submit → redirected to **Series Hub Page**
4. From Hub → **[Add New Issue]** → **Issue Form**
5. Issue Form is single scrollable page: Issue Metadata → Product Credits → Story Breakdown
#### 3.2.2 Series Form Fields
 
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Title | Text | Yes | |
| Series Type | Dropdown | Yes | See values below |
| Continuity | Dropdown | Yes | Canon / Legends / Both. Pre-fills from toggle |
| Era | Dropdown(s) | Yes | Dependent on Continuity selection. Canon → one Canon era dropdown. Legends → one Legends era dropdown. Both → two dropdowns (Canon Era + Legends Era), both required. See Section 2.3. |
| Publisher | Autocomplete + inline create | Yes | |
| Imprint | Autocomplete + inline create | No | |
| Volume | Whole number | No | **[DECIDED]** Blank = no tag. Shown as "Vol. N" next to publisher and years. |
| Age Rating | Dropdown | No | **[DECIDED]** All Ages / T / T+ / M. Field name: `age_rating`. Nullable — older comics predate rating system. The series rating is a suggestion only: a new Issue preselects it but can change it. |
| Start Year | Year input | No | Typed (automatic years from issue dates is pinned) |
| End Year | Year input | No | Blank if ongoing. End Year earlier than Start Year is refused. |
| Synopsis | Long text | No | |
| Notes | Long text | No | **[DECIDED]** The Archivist Note (§2.9): saved with that edit only, empty each time the form opens, visible only in Edit history. |
| Cover Image | Inherited from Issue #1 | — | No upload on Series form |

**Form order [DECIDED]:** Publisher and Imprint → Title → Series Type and Volume → Continuity and Era → Start Year, End Year, Age Rating → Synopsis → Notes → Create / Cancel. Publisher and Imprint are dropdowns with "+ Add new…" at the bottom; the Imprint list shows only the chosen Publisher's imprints. New publishers or imprints are saved only when the form is saved (none remain if the user cancels); the same name typed twice, ignoring capitals, resolves to one record. "Multiple Eras" remains in the Era dropdown for now.

**Printed series name [DRAFT — to be built; product owner reserves judgment]:** an Issue may display a different series-name piece than its Series (e.g. issues 46–84 of one series printed as "Star Wars: Republic"), settable per issue and in bulk. Search and the Series page still treat it as one series. See TBD #23.
 
**Series Type values:**
- Regular Series
- One-Shot (series containing a single standalone issue — consistent with all other Series types, 
  still requires a Series record)
- Collection (collected editions only — TPBs, HCs, etc)
- Graphic Novel (original graphic novels, not collected editions). Graphic Novel series may contain any number of Graphic Novel issues.

Collected editions appear as a section on the same Series page. The "Collection" series type stays **[DECIDED]**.
#### 3.2.3 Series Hub Page
 
Must contain:
- Series metadata display with Edit button
- Issue grid — cover thumbnails, title+issue number, full release date ("Oct 3, 2026")
- Reading progress summary (% of issues completed) [not yet built — depends on Personal Tracking, TBD #8]
- **[Add New Issue]** button
- **[Bulk Add Issues]** button — **[TBD]**
- **[Bulk Edit Issues]** button — **[TBD]**
- Sort options sidebar [TBD — Sprint 4+ browse/filter design]
Issue grid divided into sections (**design TBD**), each visible only if 
at least one issue of that type exists:
  - Issues (Regular Issues, sorted by release date; issue number (natural sort: ½=0.5, 1.AU after 1) breaks ties)
  - Annuals (sorted by release date)
  - One-Shots (sorted by release date)
  - Collected Editions (sorted by release date)

Series cover = earliest-release-date Regular Issue with a cover.

**Series page layout (October 9, 2026) [DECIDED]:**
- Faint line at the very top: series type and kind (e.g. "comic series · regular series"). Then Publisher/Imprint · Vol. N · years, series title, Continuity/Era (text for now), an **Edit ▾** menu (*Edit*, *Edit history*), and a larger synopsis.
- **Stats row:** Read x/y and Own x/y (no Wish count) and **+ Add Issue**. x = issues marked; y = original issues, annuals and one-shots in the series (collected editions not counted). A One-Shot series still limits itself to one issue.
- **Tabs: Creators | Cover | Editors | Characters.** Creators open by default; the last choice is remembered. Each card: headshot (silhouette), role line (not for characters), name, count, years. Creator and character pages do not exist yet (Sprint 4), so names are plain text; the count opens a simple list of those issues. A person with several roles shows them together ("Writer, Penciler"); an alias credit counts for the real person.
- **Sections:** Issues (n), Annuals, One-Shots, Collected Editions — each collapsible, same card design, covers clickable.
- **Slim toolbar** above the issues, applying to the section it sits above, choices reset on leaving the page: **Sort** (release date oldest first by default; newest first; issue number low to high; high to low), **Filter** (All, Read, Unread, Owned, Not owned, Wish), **Select** (checkboxes; bulk actions are a later stage), **Search** (issue number and title within the series). No grid/list switch.
- Labels say "TPB", never "TP".

**[DRAFT]** Tab ranking: top 8 by count of issues credited in (original issues, annuals and one-shots only; collected editions never count; Production and Lucasfilm credits left out; characters count Main and Supporting appearances only). Subject to change by the product owner.

**[DRAFT]** Cover cards (hybrid): small always-visible state dots for Read / Own / Wish; the full icon bar (Read, Own, Wish, Log) on hover; a checkbox on hover in Select mode. The product owner may change this.
#### 3.2.4 Issue Form
 
**Layout:** Two-column. Left column: cover image display area (placeholder → live preview on upload) + upload controls directly below image. Right column: all form fields.
 
**Fields in order:**
 
**Row 1:** Continuity (inherited, static) / Era (inherited, static)
**Row 2:** Publisher (inherited, static) / Imprint (inherited, static)
**Row 3:** Series Title (inherited, static) / Issue # (required, text field — handles #0, #½, #1.AU)
**Row 4:** Release Date (required; numeric mm/dd/yyyy entry, displayed "Oct 3, 2026") / Cover Date (optional; month and year only, displayed "Dec 2026")
**Row 5:** Type (required) / Format (required) / Trim Size (optional)
**Row 6:** Synopsis (full width, rich text editor — Bold, Italic, Unordered List minimum)
**Row 7:** Pages / Age Rating / Price USD / UPC-ISBN (all optional)
**Row 8:** Wookieepedia URL (permanent, label fixed) + generic Add Link rows (URL + Label fields)
 
**Type values:** Regular Issue / Annual / One-Shot / Collected Edition / Graphic Novel
**Format values:** Comic / Paperback / Hardcover / Digital
**Trim Size values:** Standard / Digest / Oversized / Digital / Other (triggers freeform text input)
 
**Issue # field behavior is dependent on Type selection:**

Issue # is used by Regular Issues only and stored without "#". For Annual, One-Shot, Collected Edition and Graphic Novel, the text typed into the shared box is stored in `issue_title`, and `issue_number` is NULL.
 
Regular Issue: label "Issue #", # prefix added by UI only, 
  user types number only, stored without # in database.
  Display: [Series Title] #[Number]
 
Annual: label "Annual", no # prefix, freetext.
  Display: [Series Title] [Annual value]
 
One-Shot: label "Title", no # prefix, freetext. Title may be blank
  (displays as the Series Title alone).
  Display: [Series Title] — [Title]
 
Collected Edition: label "Title", no # prefix, freetext, nullable.
  Display (TPB, never TP):
    Blank title + Paperback → [Series Title] TPB
    Blank title + Hardcover → [Series Title] HC
    Blank title + Digital → [Series Title] (Digital)
    Title + Paperback → [Series Title] — [Title] TPB
    Title + Hardcover → [Series Title] — [Title] HC
    Title + Digital → [Series Title] — [Title] (Digital)
 
Graphic Novel: label "Title", no # prefix, freetext.
  Display: [Series Title] — [Title]
 
Em dash separator used in all display titles where a 
separator is needed. Never stored — always generated 
from Series Title + Issue Title fields.
 
**Series Type constrains available Issue Types:**
  Regular Series → Regular Issue, Annual, One-Shot, Collected Edition (NOT Graphic Novel)
  One-Shot → One-Shot only, maximum one issue, block second issue with error message
  Collection → Collected Edition only
  Graphic Novel → Graphic Novel only

Collection and Graphic Novel series cannot use Format = Comic.
 
Digital — product released digitally only, no print edition exists.
Does not represent a digital copy of a print product — 
that is handled by personal tracking (TBD #8).
 
**Interdependent format logic:**
- Regular Issue → Format defaults to Comic
- Collected Edition → Format defaults to Paperback or Hardcover
- Graphic Novel → Format defaults to Paperback or Hardcover
**External links display:** Each saved link renders as icon button on entry page. Wookieepedia gets its own icon. Generic links display domain favicon or generic link icon. Label becomes tooltip.
 
**UPC vs ISBN:** Single label "UPC / ISBN" — user enters whichever applies based on Type.

**Duplicate issues [DECIDED]:** A second Issue with the same Series, Issue # and Type is refused, with a message and a link to the existing Issue.

**Age Rating:** preselected from the Series' age rating; can be changed per Issue.

**Archivist Note:** the Issue form ends with an optional Archivist Note box (§2.9).
 
#### 3.2.5 Story Breakdown Section
 
Two distinct zones:
 
**Zone 1 — Product Credits (top)**
Product Scope credits. Do not travel with imported segments. Visual distinction from Zone 2 required — label "Product Credits" with explanatory subtext. Exact aesthetic treatment TBD in Claude Design phase.
 
**Zone 2 — Segment Blocks (numbered, below)**
Story Scope content units.

Collected Editions use the normal Story Breakdown exactly like any other issue — they may contain material found nowhere else.
 
**Two action buttons at top right of Story Breakdown section:**
- **[IMPORT]** — opens Import Modal
- **[ADD]** — adds new segment block with smart defaults
**Form load default state:**
- One segment block is pre-created on form load with:
  - Sort Order = 1
  - Type = Story
  - Reproduction = Original (display only — cannot be changed 
    on ADD-created segments)
  - Colors = Color
  - All other fields empty
- All credit rows start empty — just the Add button per department
- Character section starts empty — just the Add button
- Character Appearance Type defaults to Main (explicit owner change,
  2026-10-08, reverses an earlier [DECIDED] of "no default — user must
  explicitly select Main / Supporting / Cameo / Vision")
**ADD behavior:**
- Generates new block with defaults: Type = Story / 
  Reproduction = Original / Colors = Color
- Reproduction Type is display-only on ADD-created segments — 
  always shows Original, cannot be changed
- The only way to get non-Original segments is through the 
  Import Modal
- Sort order auto-increments from previous segment
- All other fields editable
**Source Segment field:**
- Does not appear on ADD-created segments (Reproduction = Original)
- Only appears on Import Modal-created segments
- Pre-filled with source reference on import, locked
- Displays provenance tag: "Linked to [Source Issue Title] · 
  [Source Release Date]"
**Minimum segments to save:** At least one segment block must 
exist. Enforced strictly — save blocked if no segments present.
No individual segment fields required — all optional.
 
 
#### 3.2.6 Segment Block Fields
 
| Field | Required to save | Notes |
|-------|-----------------|-------|
| Sort Order | Auto-assigned | Always editable, never travels on import |
| Segment Type | No | Story / Text Story / Data Page / Illustration / Process Art / Script / Introduction / Afterword / Text Article / Letters / Cover Gallery / Recap |
| Reproduction | No | Original / Reprint / Remaster / Altered / Compilation / Excerpt |
| Title | No | Official story title |
| Colors | No | Color / Black & White / Color & Black & White |
| Pages | No | Integer |
| Story Scope Credits | No | See credit mechanic below |
| Characters | No | See character mechanic below |
 
**Source Segment field:** Appears only when Reproduction ≠ Original. Searches all Segments in database scoped to same Pillar. Cross-pillar segments never appear.
 
**Provenance tag:** Displayed beneath segment title on both edit form and entry display page. Format: *"Linked to [Source Issue Title] · [Source Release Date]"*
 
#### 3.2.7 Import Modal
 
- Opens on IMPORT button click
- Defaults to showing segments from current series for convenience
- Search bar searches full database within current Pillar scope only
- Search by issue name returns all segments from that issue
- Multi-select via checkboxes
- Reproduction Type dropdown at bottom — applied to all selected segments
- Default Reproduction Type: Reprint
- **[IMPORT SELECTED]** button — standard multi-select, creates one derived segment per source
- When Compilation selected → button changes to **[COMPILE SELECTED]** — creates one derived segment linked to all selected sources
**Compilation auto-population:**
- Credits merged from all source segments, deduplicated by Creator + Role
- Characters merged from all source segments, deduplicated
- Title and Pages start blank
- All fields fully editable
#### 3.2.8 Credit Mechanic
**[DECIDED]**
 
**Form structure:** Department sections, each with its own ADD button and credit rows.
 
**Each credit row:** `[Creator Name — autocomplete + fuzzy match + inline create] [Role — type-to-search] [··· attribute button] [Remove button]`

The "···" attribute button opens a small dialog with three options, usable in any combination **[DECIDED]**:
- **Uncredited**
- **As…** — pick one of the person's saved names or add a new one (saved as an alias of that person); greyed out while Uncredited is ticked
- **Note** — free text (e.g. "pages 9-10"); always travels with the story and is edited manually

Typing an alias in the creator box finds the real person. Display order under each credit: headshot → role → name → attributes.

Every credit row requires a creator and a role; an incomplete row blocks the save with an error.
 
**Role field:** Freetext input with autocomplete against previously used roles within that department. If no match, typed value becomes new role saved to that department's vocabulary. Department-scoped — same word in different departments are independent entries.
 
**Multi-role creators:** Multiple rows, one per role. Same Creator record, different role. No special handling.
 
**Comics Credit Departments:**
 
| Department | Scope | Level | Notes |
|------------|-------|-------|-------|
| Writers | Story | Segment | Roles: Writer, Script, Plot, Story, Dialogue, etc. |
| Artists | Story | Segment | Roles: Penciler, Inker, Artist, Colorist, Letterer, etc. |
| Editors | Story | Segment | Story-level editors: Editor, Assistant Editor, Associate Editor, Senior Editor (story-level) |
| Cover | Product | Issue | Roles: Cover Artist, Cover Penciler, Cover Inker, Cover Colorist, etc. |
| Production | Product | Issue | Roles: Editor-in-Chief, Collection Editor, Book Designer, Production Manager, Senior Editor (issue-level) |
| Lucasfilm | Product | Issue | Roles: Lucasfilm Editor, Lucasfilm Art Director, Creative Director, Art Director, Story Group, Creative Art Manager, Licensing Manager |
 
**Role vocabulary:** Standardised catch-all terms preferred (Colorist not "Color Artist"). Consistency over literal transcription.
 
**Role Alias system:** Deferred. Not needed for Comics. Revisit when speccing Film/TV/Games where credit terminology is less standardised.
 
#### 3.2.9 Character Mechanic
**[DECIDED]**
 
**Each character row:** `[Character Name — autocomplete] [Appearance Type dropdown] [Remove button]`
 
Autocomplete searches both Baseline names and Persona names simultaneously. Selecting a Persona auto-populates both `character_id` (baseline) and `persona_id`. Displays as "Baseline Name as Persona Name" when persona selected.

Inline-created characters inherit the issue's continuity.
 
No per-row Universe Filter — site-wide Canon/Legends toggle handles continuity scoping.
 
**Appearance Types:** Main / Supporting / Cameo / Vision
- **Main** — heavy speaking role, pivotal to story
- **Supporting** — present and interactive, not the focus
- **Cameo** — brief appearance, minimal interaction
- **Vision** — Force ghost, flashback, dream, illusion, clone, or construct
**Display on entry page:** Grid of headshots with name labels. Auto-sorted: Main → Supporting → Cameo → Vision. No explicit section headers.
 
#### 3.2.10 Character Data Model
**[DECIDED]**
 
```
character
  id, baseline_name, continuity (canon/legends/both),
  bio, image, created_at, updated_at
 
character_persona
  id, persona_name, baseline_character_id,
  continuity (canon/legends/both),
  first_appearance_segment_id (nullable),
  image (nullable), notes, created_at
 
character_appearance
  id, segment_id, character_id, persona_id (nullable),
  appearance_type (main/supporting/cameo/vision),
  archivist_note, created_at
```
 
**Continuity on character records:**
- Character's Continuity field controls visibility on character browse page under toggle
- Appearance filtering on character page works through the linked entry's continuity
- "Both" entries always visible regardless of toggle state
**Continuity badge:** Displayed on character page and persona page. Simple badge: Canon / Legends / Both. Style TBD in Claude Design phase.
 
#### 3.2.11 Cover Handling
**[DECIDED]**
 
The cover is NOT a Segment. It is a property of the Issue — handled through the Cover Upload field and the Cover department in Product Credits (Product Scope). Variant covers, facsimiles, and reprint editions handled at Issue level, not Segment level.
 
#### 3.2.12 Variant Covers
**[TBD — deferred to Sprint 4+]**
 
Structure supports it. UI and workflow not yet designed.
 
#### 3.2.13 Bulk Add / Bulk Edit
**[TBD — deferred to Sprint 4+]**
 
Known requirements:
- Available on Series Hub pages
- Bulk add: multiple Issues in sequence without full page reload per issue
- Bulk edit: shared fields across multiple selected Issues simultaneously
### 3.2.14 Variant Cover Form
**[DECIDED]**
 
#### Overview
A variant cover is a child record of a parent `comic_issue`. It shares all story 
content (segments, story credits, characters) and read status with the parent. 
Ownership is tracked independently per variant.
 
Variants are stored in a dedicated `variant_cover` table with a `parent_issue_id` 
FK — not as additional `comic_issue` rows.

**Status:** `variant_cover` table not yet built (planned Sprint 3).
 
Access: from the Issue page, an [ADD VARIANT] button opens a blank variant form. 
Existing variants appear as a thumbnail grid on the Issue page.
 
#### Field List
 
**Static (display only — inherited from parent, never editable):**
Series Title, Issue #, Continuity, Era, Publisher, Imprint
 
**Pre-filled from parent but editable:**
Release Date, Cover Date, Type, Format, Trim Size, Pages, Price USD, UPC/ISBN
 
**Title Block:**
- Suggested Title — auto-generated from token formula (see below)
- Use Suggested toggle — on: locks in auto-generated label / off: manual override
- Manual title field — editable when Use Suggested is off
**Cover Artwork:**
Image upload — starts blank on new variant form
 
**Variant Details:**
- Variant Type (dropdown): Open Order / Reprint / Incentive Variant / 
  Retailer Exclusive / Event Exclusive / Facsimile / Misprint / 
  Miscellaneous / Blind Bag Outcome
- Cover Descriptor (freetext)
- Exclusive Seller (freetext)
- Exclusive Event (freetext)
- Printing (dropdown: 1st / 2nd / 3rd / etc.)
- Cover Colors (dropdown: Color / Black & White / Color & Black & White)
**Cover Credits:**
Empty on new form. Cover department only. Same credit row mechanic as Issue form.
No story credits. No segment blocks. No external links.
 
#### Auto-Generated Title Formula
Tokens appear only if the corresponding field has a value.
Standard order:
`[Parent Title] [Printing] [Exclusive Seller] [Exclusive Event] [Cover Artist] [Cover Colors] [Cover Descriptor]`
 
Exception — Facsimile: when Variant Type = Facsimile, "Facsimile Edition" 
inserts immediately after Parent Title:
`[Parent Title] Facsimile Edition [Printing] [Exclusive Seller] [Exclusive Event] [Cover Artist] [Cover Colors] [Cover Descriptor]`
 
#### Tracking Behavior
- Read status: inherited from parent issue — marking parent as read marks 
  all its variants as read
- Ownership: independent per variant — owning one does not imply owning others
- Owned variants appear independently on collection page (details TBD)
#### Database Table
```sql
variant_cover
  id, parent_issue_id,
  release_date, cover_date,
  designation, physical_binding, trim_size,
  pages, price, upc_isbn,
  variant_type, cover_descriptor,
  exclusive_seller, exclusive_event,
  printing, cover_colors,
  suggested_title, use_suggested (boolean),
  manual_title,
  cover_image,
  is_owned (boolean),
  created_at, updated_at
```
 
#### Build Timing
- Database table: Sprint 3 (alongside Comics UI)
- UI and variant form: Sprint 4
- Collection page display: Sprint 6+

### 3.2.15 Issue View Page
**[DECIDED]** (October 9, 2026, including the delete-blocking rule, temporary Diary link, plain-text names and silhouette headshots)

*Status: not yet built — see §6 Sprint 3 item 12.*

- **Left column:** cover; below it the strip **Read | Own | Wish | Log**; below that a reserved empty area (variants, whole-issue reprints, editions come later). Cover date as a small label above the cover, level with the top line.
- **Main column:** top line *Publisher · Imprint · Type*; Continuity and Era badges at top right (plain text for now); title (series-name part clickable) and release date; Prev / Next arrows with a middle "view series" button; **Edit ▾** menu.
- **Synopsis,** then a details strip showing only fields that have values, in form order, links as icons, labelled "Age rating".
- **Product Credits** in three groups (Cover, Production, Lucasfilm): headshot slots in a row, role above the name, attributes (uncredited, credited as, note) under the name. Silhouettes only for now; names are plain text until creator pages exist.
- **Contents:** numbered story blocks, first one open; header "Title / Type · pages"; a "B&W" or "Color & B&W" tag only when not full colour. Inside: Creators row, Editors row, Characters row with one continuity badge and the role bar.
- **Reprints (n):** a collapsible box (cover, title, release date) listing every collected edition or issue that reprints this issue's stories.
- **Edit ▾ menu:** *Edit*, *Edit history*, and *Add new variant cover* (shown but inactive until built).
- **Delete** sits at the end of the Issue form with a confirmation. If the issue's stories are reprinted in a collected edition, Delete is blocked with a message naming the collections. Marks and log entries for a deleted issue are deleted with it.
- **Marks and Log:** see §4.6.
- **Diary:** a plain "Diary" link in the top bar (temporary until navigation is designed) opens a list of log entries, newest first (cover, title, date, "read before" if ticked); each entry can be edited or deleted.
- Edits to an original story (credits, cover, characters, title) flow to every collected edition that reprints it.

### 3.2.16 Collected Edition Page
**[DECIDED]** (October 9, 2026)

The Issue View (§3.2.15) with a different Contents area:
- **Overview** (collapsible, open by default): "# stories", then tabs **Creators | Editors | Characters** (no Cover tab) summarising the most-credited people and most-featured characters across the book's stories. Small count under each name; ties fall back to book order. Counts use story-type segments only.
- **Story list** (like a table of contents): numbered circles in book order; the original issue's title, story title, release date, type, pages and cover thumbnail; collapsed by default, expanding to that story's Creators, Editors and Characters.
- **Non-story material** (galleries, text pages, introductions) is a segment type addable in the breakdown. It is numbered like everything else, shown by default, hideable with a toggle, may have credits, and never counts in the Overview.
- **Expand all / Collapse all** buttons.
- The page follows the originals: changes to an original story or its issue update it. Only straightforward 1:1 reprints are handled; unusual cases are pinned.
---
 
## 4. Global Features
 
### 4.1 Navigation
**[DECIDED — structure; TBD — full contents and design]**
 
#### What Is Locked
- Home page is always the Dashboard view
- Persistent top navigation bar across all pages
- Minimum nav bar contents (left to right):
  - Holocron logo — clicks to Dashboard
  - Calendar quick link [not yet built; no Calendar page is specified]
  - Canon/Both/Legends toggle (see Section 2.3 for order)
  - Search bar
  - [+] Add New Media button
#### Add New Media Modal
**[DECIDED]**
Clicking [+] opens a centered overlay modal with a pillar selection grid.
Pillars: Film / TV / Games / Books / Audio / Comics / Manga. (Periodicals excluded from current scope — see Section 7. Reference pillar: TBD.)
Selecting a pillar opens its corresponding entry form.
Style reference: image provided May 7 2026 — grid of colored pillar icons 
on dark background. Final design TBD in Claude Design phase.
 
#### Dashboard
**[TBD — full contents]**
Home page. Displays on app load.
Known requirements: stats summary block (counts for Collected / Read / Wanted).
Reference: LOCG dashboard layout (provided May 7 2026).
Everything beyond stats block is TBD.
Currently shows a Recently Added grid; stats block not built.
 
#### Search
**[TBD — full implementation, Sprint 4+]**
Global search across issues, series, creators, characters.
Reference: LOCG search results page — results split by category 
(Issues, Creators, etc.) in a two-column layout (provided May 7 2026).
 
#### Browsing and Filtering
**[TBD — Sprint 4+]**
No pillar-specific tab navigation — collection is unified.
Leaning toward a powerful site-wide side filter panel available on 
all major browsing pages (collection, creator, character, publisher pages).
Reference: LOCG universal filter panel (provided May 7 2026).
Final approach not yet decided.
 
#### Reference Page Access (Creators, Characters, Publishers)
**[TBD — Sprint 4]**
Primary access: clicking through from an entry page.
Directory pages (browseable lists of all creators/characters/publishers) 
are under consideration but not yet decided.
 
### 4.2 Creator Pages
**[TBD — layout and contents]**
 
Known requirements:
- Every Creator has a dedicated canonical page
- Shows all credits across all Pillars and all Segments
- Filterable by: Pillar, Role, Era, Canon Status
- Sortable by: Release Date, In-Universe Date
- Pseudonym Page: distinct page (own URL) per alias, links back to canonical Creator Page

**[DRAFT / TBD]** A Publisher / Imprint / Creator registry with pages and a duplicate-merge tool is a long-term goal; until then forms use simple pick-or-add. See §8.
### 4.3 Publisher and Imprint Pages
**[TBD — layout and contents]**
 
Known requirements:
- Every Publisher and Imprint has a dedicated page
- Shows all Issues/Editions released

**[DRAFT / TBD]** See the registry and merge-tool note under §4.2.
### 4.4 Character Pages
**[TBD — layout and contents]**
 
Known requirements:
- Baseline Character page: all appearances across all Pillars, all Personas unified
- Persona Page: appearances under that specific Persona only, links to Baseline page
- Filterable by Pillar, Era, Canon Status
- Continuity badge displayed
- Appearance count shown: X Main · Y Supporting · Z Cameo
### 4.5 Series Grouping for Associative Pillars
**[TBD — full implementation]**
 
Known requirements:
- Films, Books, Audio, Games can belong to named Series
- `SeriesMembership` join table with position number
- One entry can belong to multiple Series simultaneously
- Primary vs. Companion membership type — field reserved (`is_primary` boolean), values TBD
### 4.6 Personal Tracking
**[DECIDED — Read / Own / Wish marks and Log; TBD — remaining fields per Pillar]**

**Marks [DECIDED]:** Read, Own and Wish are independent marks on products only (never on stories) and apply across pillars. Read can be set without logging. Marks show on the Issue page and the Series page; Read / Own / Wish list pages are pinned.

**Log [DECIDED]:** The Log pop-up has only a date (defaults to today) and an "I've read this before" flag. Saving creates a Diary entry and ticks Read if it was not ticked. Deleting every log entry never unticks Read. Notes, tags, rating, like and review are on the maybe-list (§7).

**[DRAFT]** Marks and log entries are stored in one flexible list each that can point at any product (comic issue now; film, book, game later). See §5.3.

Known core fields (the Watch/Read Status list below is superseded for Comics by the independent marks above; remaining items still TBD):
- Watch/Read Status: Want / In Progress / Completed / Dropped
- Rating: Integer 1–10, nullable
- Personal Notes: freeform text, never canonical metadata
- Date Completed: date field
### 4.7 Filtering and Search
**[FUTURE — Sprint 4+]**
 
### 4.8 Stats Dashboard
**[FUTURE — Sprint 5+]**
 
---
 
## 5. Data Model — Full Schema
 
### 5.1 Foundation Tables (Sprint 1 — build in this order)
 
```sql
-- 1. ALWAYS BUILD FIRST
contribution_log
  id, timestamp, action_type (create/edit/delete),
  record_type, record_id,
  old_value (JSON), new_value (JSON),
  archivist_note
 
-- 2. User preferences
user_preferences
  id,
  continuity_filter (canon/legends/both) DEFAULT 'both'
 
-- 3. Reference / lookup tables
era
  era
  id, name, continuity (canon/legends),
  in_universe_date_start, in_universe_date_end,
  sort_order (integer),
 
publisher
  id, name, slug, created_at, updated_at
 
imprint
  id, name, slug, publisher_id, created_at, updated_at
 
creator
  id, name, slug, bio, image, created_at, updated_at
 
creator_alias
  id, alias_name, canonical_creator_id,
  alias_type (pseudonym/studio/name_variation),
  notes, created_at
 
character
  id, baseline_name, slug, continuity (canon/legends/both),
  bio, image, created_at, updated_at
 
character_persona
  id, persona_name, slug, baseline_character_id,
  continuity (canon/legends/both),
  first_appearance_segment_id,
  image, notes, created_at
 
department
  id, name, pillar, scope (story/product), created_at
 
role
  id, name, department_id, sort_order, created_at
 
-- role_alias reserved for future use (Film/TV/Games)
```
 
### 5.2 Comics Pillar Tables (Sprint 2)
 
```sql
comic_series
  id, title, series_type, continuity, canon_era_id, legends_era_id,
  is_timeline_spanning (boolean, default false),
  publisher_id, imprint_id, age_rating, volume (nullable integer),
  start_year, end_year, synopsis,
  created_at, updated_at
 
comic_issue
  id, series_id, issue_number, issue_title,
  release_date, cover_date,
  designation, physical_binding, trim_size, trim_size_custom,
  pages, price, upc_isbn, age_rating,
  synopsis, cover_image,
  wookieepedia_url,
  created_at, updated_at

-- issue_title holds the title for non-regular types (Annual, One-Shot,
-- Collected Edition, Graphic Novel); issue_number is NULL for those types.
 
external_link
  id, issue_id, url, label, created_at
 
comic_segment
  id, issue_id, segment_type, sort_order,
  title, colors, pages, reproduction (default 'original'),
  created_at, updated_at
 
segment_relationship
  id, source_segment_id, derived_segment_id,
  reproduction_type, notes, created_at
 
credit
  id, creator_id, alias_id (nullable),
  segment_id (nullable), issue_id (nullable),
  department_id, role_name,
  scope (story/product),
  is_uncredited (boolean),
  created_at
 
character_appearance
  id, segment_id, character_id, persona_id (nullable),
  appearance_type (main/supporting/cameo/vision),
  archivist_note, created_at
 
-- For Associative Pillars (build now, use later)
series_membership
  id, series_id, entry_id, entry_type,
  position, is_primary (boolean),
  created_at
```
 
### 5.3 Schema Notes
 
- `credit.segment_id` null for Product Scope credits; `credit.issue_id` null for Story Scope credits
- Era table has separate Canon and Legends eras distinguished by `continuity` field
- `contribution_log.old_value` and `new_value` stored as JSON diffs; Series and Issue edits must record each changed field's before and after values (§2.9)
- **[DRAFT]** One flexible credits list: `credit` points at "a story, an issue, or later a TV episode, film, game…" rather than only comic segments and issues. Credits gain `is_uncredited`, `alias_id` (credited as) and a free-text `note`. Exact shape to be confirmed before Stage 2 is built.
- **[DRAFT]** Personal layer: two lists that can point at any product — **marks** (Read / Own / Wish, independent, one row per product per mark) and **log entries** (product, date, "I've read this before" flag). Exact shape to be confirmed before Stage 2 is built.
- **[DECIDED]** Duplicate rule: a second issue with the same series, number and type is refused (§3.2.4).
- `role_name` stored directly on credit record (not a foreign key) for filterability. Role vocabulary managed via separate `role` table (department-scoped), seeded with standard Comics roles. New roles auto-added to vocabulary table on first use.
### 5.4 Era Reference Data
**[DECIDED]**
 
#### Era Table Design Notes
- `sort_order` integer field controls dropdown display order
- Chronological eras: multiples of 10 (10, 20, 30...)
- Non-continuity eras (Visions, Infinities): sort_order = 999
- Multiple eras handling: `era_id` stores Primary Era + 
  `is_timeline_spanning` boolean flag on the work record. 
  No many-to-many at this stage.
#### Canon Eras
Seed with continuity = 'canon':
 
| sort_order | Name | Notes |
|------------|------|-------|
| 10 | Dawn of the Jedi | Origins of the Force and first Jedi |
| 20 | The Old Republic | Ancient Republic and Sith Wars |
| 30 | The High Republic | Golden age of the Jedi, centuries before Ep. I |
| 40 | Fall of the Jedi | Prequel Trilogy era (Episodes I–III) |
| 50 | Reign of the Empire | Between Revenge of the Sith and A New Hope |
| 60 | Age of Rebellion | Original Trilogy era (Episodes IV–VI) |
| 70 | The New Republic | Post-Empire era (The Mandalorian, Ahsoka) |
| 80 | Rise of the First Order | Sequel Trilogy era (Episodes VII–IX) |
| 90 | New Jedi Order | Future era, Rey's reconstruction of the Order |
| 999 | Visions | Stories not bound by primary Canon timeline |
 
#### Legends Eras
Seed with continuity = 'legends':
 
| sort_order | Name | Approx. Range |
|------------|------|---------------|
| 10 | Before the Republic | Up to 25,000 BBY |
| 20 | The Old Republic | 25,000 BBY – 1,000 BBY |
| 30 | Rise of the Empire | 1,000 BBY – 0 BBY |
| 40 | The Rebellion Era | 0 BBY – 5 ABY |
| 50 | The New Republic | 5 ABY – 25 ABY |
| 60 | The New Jedi Order | 25 ABY – 40 ABY |
| 70 | Legacy Era | 40 ABY – 140+ ABY |
| 999 | Infinities | Parodies and What If scenarios |
 
---
 
## 6. Build Order
 
### Sprint 1 — Foundation ✓ COMPLETE
**Goal:** Flask runs. Database connects. Audit log works. All reference tables exist with fuzzy search.
 
1. Flask app factory, config, `.env` file
2. SQLite connection, Flask-Migrate initialised
3. **Contribution Log model — build before any other model**
4. `user_preferences` table (toggle state)
5. Reference tables: Era, Publisher, Imprint, Creator, CreatorAlias, Character, CharacterPersona, Department
6. Fuzzy match search endpoint for all reference tables
7. Inline creation behavior on all autocomplete fields
### Sprint 2 — Comics Pillar: Data ✓ COMPLETE
**Goal:** All Comics data models exist and migrated.
 
1. ComicSeries model and migration
2. ComicIssue model and migration
3. ComicSegment model and migration
4. SegmentRelationship model and migration
5. Credit model (Story Scope and Product Scope)
6. CharacterAppearance model
7. SeriesMembership model (structure for future Associative Pillars)
8. ExternalLink model
*After Sprint 2: install `tdd` skill*
*After Sprint 2: resolve TBD — Character appearance type granularity confirmed as Main/Supporting/Cameo/Vision*
 
### Sprint 3 — Comics Pillar: UI
**Goal:** Full Comics entry workflow functional in browser.
 
*Credit taxonomy — resolved for Comics; see Section 3.2.8*
*Navigation structure — partially resolved; see Section 4.1*
 
1. ✓ Series Creation Form
2. ✓ Series Hub Page with issue grid and cover inheritance  
3. ✓ Issue Form — two-column layout, all fields, rich text synopsis
4. ✓ Story Breakdown section — Product Credits zone + Segment blocks (floating labels, sort_order, JS rebuild all completed Session 3, 2026-05-17/18 — see CLAUDE.md session log)
5a. ✓ ADD button
5b. IMPORT modal (open)
6. Compilation workflow
7. ✓ Autocomplete + fuzzy match + inline creation for Creator, Publisher, Character
8. Pseudonym display and Pseudonym Page routing
9. Uncredited flag display — partial: flag can be set; display not built
10. Contribution Log display on entry pages
11. ✓ Canon/Legends toggle in navigation
12. **Issue View page** — not yet built. Currently there is no page to view a saved Issue's metadata, cover, or Story Breakdown after creation; the cover thumbnail on the Series Hub and the "Edit" button are both inert placeholders pending this page. Confirmed by direct inspection of the codebase, October 2026.
13. Issue Edit / Delete — depends on #12 existing first
14. Series Edit / Delete
15. `variant_cover` table (open)
16. Creator Uncredited feature [TBD — to be designed]
17. Rename Product Credits label in the form (Phase B)
### Sprint 4 — Reference Pages
**Goal:** Clicking any Creator, Publisher, or Character navigates to their page.
 
1. Creator canonical page
2. Creator Pseudonym Page (distinct URL)
3. Publisher and Imprint pages
4. Character Baseline page
5. Character Persona page
6. Filtering on all reference pages
7. Canon/Legends toggle filtering on reference pages
*After Sprint 4: install `improve-codebase-architecture` skill*
 
### Sprint 5 — Additional Pillars
*Before Sprint 5: resolve TBD — Television Pillar full metadata specification*
 
Begin Television Pillar using Comics patterns. Each subsequent Pillar: resolve TBDs → Data → UI → Reference pages.
 
### Sprint 6+ — Cross-Pillar and Polish
- Filtering and search across collection
- Stats dashboard
- Bulk add / bulk edit
- Export to CSV
- Associative Pillar series grouping
- Variant covers
- Timeline and reading order views
---
 
## 7. Potential Future Features
*(Not planned, not prioritised — logged for awareness)*
 
- Periodicals Pillar — excluded from current scope as of October 2026 (product owner decision); may be revisited if interest returns
- Issue-to-issue cross-reference / referenced comics mechanism (LOCG-style)
- Role Alias system for Film/TV/Games credit terminology normalisation
- Character appearance type expansion beyond Main/Supporting/Cameo/Vision
- Timeline visualisation (in-universe chronological view)
- Auto-populate fields from Wookieepedia URL
- Custom reading/watch order lists
- Database backup and restore UI
- Dark/light theme toggle
- Related media suggestions
- One-click desktop launcher / always-on background service
- Tag for an American edition of an internationally-first release
- Log maybe-list: notes / review, tags, rating, like on Diary entries
- Ratings, "currently reading" status, dedicated Read / Own / Wish list pages, Diary filters
- Years (Start / End) filled in automatically from issue dates
- "Duplicate as new issue" action
- Headshot photo upload for creators and characters (everything is a silhouette for now)
---
 
## 8. TBD Registry
 
| # | Item | Blocking | Notes |
|---|------|---------|-------|
| 2 | Variant cover UI | Sprint 4 | Architecture decided — see Section 3.2.14 |
| 3 | Bulk add / bulk edit UI | Sprint 4+ | Requirements known |
| 4 | Creator page layout and contents | Sprint 4 | Requirements known |
| 5 | Publisher/Imprint page layout | Sprint 4 | Requirements known |
| 6 | Character page layout and contents | Sprint 4 | Requirements known |
| 7 | Navigation structure | ~~Sprint 3~~ | Partially resolved — see Section 4.1. Full design TBD. |
| 8 | Personal tracking fields per Pillar | — | Core fields known. Blocks Dashboard stats and reading progress. |
| 9 | Series membership primary vs. companion definition | Sprint 6+ | Field reserved |
| 10 | Television Pillar full specification | Sprint 5 | Structure decided |
| 11 | Film, Books, Audio, Games, Manga specs | Sprint 5+ | Structure decided |
| 12 | Manga tankōbon collection system | Sprint 5+ | Acknowledged complexity |
| 13 | Placeholder icon style and Pillar accent colors | Sprint 3 | Claude Design phase not yet done; emoji pillar icons are placeholders |
| 14 | Product Credits zone visual distinction from Segment credits | Sprint 3 | Claude Design phase not yet done; emoji pillar icons are placeholders |
| 15 | Continuity badge visual style | Sprint 3 | Claude Design phase not yet done; emoji pillar icons are placeholders |
| 17 | Newspaper comic strips — format and pillar placement | Sprint 5+ | Too complex for Comics pillar as-is |
| 18 | Webcomics — format handling | Sprint 5+ | Pending real-world testing |
| 21 | Holocron Contribution Guidelines ("rulebook" doc, inspired by LOCG's own contributor guidelines) | Unscheduled | Product owner wants a standalone consistency reference, separate from this PRD. Many of its likely contents already live in this PRD (§2.10 Metadata Conventions, §3.2.8 Role vocabulary rules) and could seed a first draft. First draft exists: docs/Holocron-Data-Entry-Guide.md. |
| 22 | Issue View page (read-only display of a saved Issue) | Sprint 3 | Specified in §3.2.15 (October 9, 2026); not yet built — see §6 Sprint 3 item 12. Confirmed missing by direct code inspection, October 2026. Issue Edit/Delete and Series Edit/Delete both depend on this existing first. |
| 23 | Outlier entries (series retitled mid-run with continuing numbering, e.g. Star Wars (1998) → Star Wars: Republic; collected editions with non-standard names) | Unscheduled | See manual title override idea; printed series name [DRAFT] in §3.2.2 |
| 24 | Issue sort-position column | Unscheduled | Revisit if release-date + natural-number sort proves insufficient |
| 25 | Settings and maintenance tools (rename / merge / delete vocabulary and records) | Unscheduled | Role names are stored as text on credits, so renames must update credits |
| 26 | Credits deep dive (alias entry flow, uncredited display, per-credit notes, credit design for non-Comics pillars) | Unscheduled | Credit table currently tied to comic tables |
| 27 | American edition of internationally-first release | Unscheduled | Tag/field; interacts with Reprint-segment source rule |
| 28 | Calendar page and Dashboard design | Unscheduled | — |
| 30 | Issue-list popup design (opened from the creator / character counts on the Series page) | Unscheduled | Pinned October 9, 2026 |
| 31 | Icons for Continuity, Era and Wish; look of the Read / Own stats and progress display | Unscheduled | Pinned October 9, 2026 |
| 32 | Sidebar filters and sorting (LOCG-style), filters by creator or character; browse/sort sidebar and home page | Sprint 4+ | Pinned October 9, 2026 |
| 33 | Smarter ranking for the Series page Featured strip; manual pins | Unscheduled | Pinned October 9, 2026; see [DRAFT] ranking in §3.2.3 |
| 34 | Stats counting rules (LOCG-style: unique vs all, by story / format, persona vs individual) | Unscheduled | Pinned October 9, 2026 |
| 35 | Variants and multiple editions; whole-issue reprints area; footer / bottom area of the Issue View | Unscheduled | Pinned October 9, 2026; relates to #2 |
| 36 | Better handling of products spanning several eras | Unscheduled | Pinned October 9, 2026; "Multiple Eras" stays in the Era dropdown meanwhile |
| 37 | Publisher / imprint / creator registry with pages, duplicate-merge tool and alias tools; how other pillars present publishers and credits (their lists will be longer) | Unscheduled | [DRAFT] long-term goal, October 9, 2026; forms use pick-or-add until then. Relates to #25 |
| 38 | Unusual reprint cases beyond 1:1 | Unscheduled | Pinned October 9, 2026 |
| 39 | Full design of Edit history and its mechanics | Unscheduled | Simple old → new list is the first version (§2.9) |
| 40 | Design of the Import feature and of the Issue and Collected-Edition forms | Before Stages 3b, 3c, 4b, 6 | Brainstorm first; see Comics Build Plan |
| 41 | Pages to browse Read / Own / Wish lists | Unscheduled | Marks show only on Issue and Series pages until then |
| 42 | Final navigation design | Unscheduled | The Diary link in the top bar is temporary. Relates to #7 |
| 43 | Backups and syncing: the database lives inside OneDrive; where should the live database file be kept? | Unscheduled | Pinned October 9, 2026 |
| 44 | Settings and maintenance tools, URL scheme / slugs, cover thumbnails, search speed, tests, announced releases, definition of MVP | Unscheduled | Pinned October 9, 2026 |

### Resolved

| # | Item | Notes |
|---|------|-------|
| 1 | Work-Level Credit taxonomy — departments and roles per Pillar | Resolved for Comics — see Section 3.2.8. Other Pillars remain open, see #11. |
| 16 | Legends era list | RESOLVED -- see section 5.4 |
| 19 | FCBD issues — confirmed as One-Shot type under per-year series | No special handling needed |
| 20 | Periodicals Pillar inclusion | Excluded from current scope (Oct 2026) — logged in §7 as potential future feature |
| 29 | Series-level age rating | Resolved October 9, 2026 — series age rating is a suggestion only; new issues preselect it and can change it. See §3.2.2 |

---

## 9. Change Log

| Date | Section | Change | Why |
|------|---------|--------|-----|
| 2026-10-08 | Header | Version 0.3 → 0.4; Last Updated → October 8, 2026 | Part 1 reconciliation |
| 2026-10-08 | How to Use This Document | Added items 5–7 (no [DECIDED] without owner approval; repo copy is source of truth; LOCG/GCD inform, not copy) | Clarify document governance |
| 2026-10-08 | §1.3 Constraints | "American releases only" → "primary focus; international editions added only occasionally, by exception" | Owner decision — scope softened |
| 2026-10-08 | §2.3 Canon/Legends Toggle | Toggle order changed to Canon / Both / Legends; added definition of "Both" | Owner clarification of Both semantics and UI order |
| 2026-10-08 | §2.6 Reference Objects | Added: inline-created records are created on form SAVE, not at pick time, in the same transaction as the log entry | Prevents orphan records |
| 2026-10-08 | §2.7 Creator Pseudonyms and Uncredited Work | Added [TBD] note scoping Uncredited to creators only (not Characters); added build-status note on Alias table/UI | Clarify current gap |
| 2026-10-08 | §2.9 Contribution Log | Added Archivist Note text box on Series/Issue forms | New requirement |
| 2026-10-08 | §2.10 Metadata Conventions | Added date display conventions ("Oct 3, 2026"; cover dates "Dec 2026"; mm/dd/yyyy entry) | Standardize date formatting site-wide |
| 2026-10-08 | §3.2.2 Series Form Fields | Noted `age_rating` column exists but field not on form (TBD); Graphic Novel series may contain any number of Graphic Novel issues | Clarify current behavior |
| 2026-10-08 | §3.2.3 Series Hub Page | Sort changed from issue number to release date (issue number natural-sort as tiebreak); added Sort options sidebar [TBD]; date format updated; reading-progress marked not yet built; defined series cover rule | Align spec with intended sort/display behavior |
| 2026-10-08 | §3.2.4 Issue Form | Clarified issue_number/issue_title storage split; One-Shot title may be blank; Regular Series excludes Graphic Novel; Collection/Graphic Novel cannot use Format = Comic; "TPB, never TP"; Cover Date month/year only; Release Date entry/display format | Close implementation ambiguities |
| 2026-10-08 | §3.2.5 Story Breakdown Section | Renamed Zone 1 "Issue Credits" → "Product Credits"; added Collected Editions use normal Story Breakdown; **Character Appearance Type now defaults to Main (reverses §3.2.5 "no default — user must explicitly select")** | Terminology consistency; explicit owner reversal, 2026-10-08 |
| 2026-10-08 | §3.2.8 Credit Mechanic | Added "···" attribute button; creator+role required to save; planned free-text note per credit [TBD display]; updated Lucasfilm role list to match seeds | Match built behavior and seed data |
| 2026-10-08 | §3.2.9 / §3.2.10 Characters | Removed `is_uncredited` from character_appearance (text and data model); inline-created characters inherit issue's continuity | Simplify — uncredited applies to creators only, not characters |
| 2026-10-08 | §3.2.14 Variant Cover Form | Added status note: `variant_cover` table not yet built (planned Sprint 3) | Reflect current build state |
| 2026-10-08 | §4.1 Navigation | Noted toggle order; Calendar link marked not yet built; Dashboard noted as showing Recently Added grid, stats block not built | Reflect current build state |
| 2026-10-08 | §5 Data Model | `comic_series.era_id` → `canon_era_id` + `legends_era_id`; `comic_issue` gained `age_rating`, `trim_size_custom`; `comic_segment` gained `reproduction` (default 'original'); `role` gained `sort_order`; removed `is_uncredited` from `character_appearance` | Schema catch-up with Sprint 3 build (Phase B implements the migrations) |
| 2026-10-08 | §6 Build Order, Sprint 3 | Split item 5 into 5a (ADD ✓) / 5b (IMPORT, open); checked off items 7 and 11; item 9 marked partial; resolved the two "Before Sprint 3" TBD lines; added items 15–17 | Reflect current build state |
| 2026-10-08 | §7 Potential Future Features | Added desktop launcher/background service; American-edition tag | Logged for awareness |
| 2026-10-08 | §8 TBD Registry | Moved #1, #16, #19, #20 to new Resolved sub-table; reworded #8 (removed "blocking Sprint 3" framing); #13–#15 noted Claude Design phase not yet done; #14 renamed to Product Credits; #21 noted first draft exists; added #23–#29 | Registry cleanup and new open items from Part 1 planning |
| 2026-10-08 | §2.2, §2.8, §3.2.1, §3.2.11 | Removed stray "Periodicals" from compositional-pillar lists (§2.2, §2.8); changed remaining "Issue Credits" references to "Product Credits" (§3.2.1 step 5, §3.2.11) | Follow-up cleanup — missed in the first reconciliation pass |
| 2026-10-08 | How to Use This Document (item 6) | "Re-uploaded at the end of each session" → "push to GitHub, then press Sync now in the Project" | Project now syncs from GitHub (branch main) instead of manual file upload |
| 2026-10-09 | Header | Version 0.4 → 0.5; Last Updated → October 9, 2026 | Part 2 design decisions applied (Comics Build Plan, Appendix A) |
| 2026-10-09 | §1.1 What This App Is | Added: complete catalogue with a personal layer on top; comics are current build scope; spreadsheet import out of scope [DECIDED] (A#1) | Part 2 design brainstorm |
| 2026-10-09 | §4.6 Personal Tracking; §5.3 | Added Read / Own / Wish as independent product-level marks [DECIDED]; Log pop-up = date + "read before", auto-ticks Read, deleting entries never unticks Read [DECIDED]; marks and log entries in one flexible list each that can point at any product [DRAFT]; maybe-list items to §7 (A#2–4) | Personal layer design |
| 2026-10-09 | §3.2.2 Series Form Fields; §2.9; §5.2 | Added Volume [DECIDED] (`comic_series.volume`); Age Rating on form as suggestion only [DECIDED]; Notes = Archivist Note; form order, publisher/imprint behavior, error rules [DECIDED]; printed series name [DRAFT]; Edit history old → new values (§2.9); TBD #29 moved to Resolved (A#5, 7, 8, 16) | Series form design |
| 2026-10-09 | §3.2.3 Series Hub Page | Collected editions as a section; "Collection" type stays [DECIDED]; Series page layout, stats row, tabs, sections, slim toolbar [DECIDED]; top-8 ranking and Main/Supporting-only character counts [DRAFT]; hybrid cover icons [DRAFT] (A#6, 13, 14) | Series page design |
| 2026-10-09 | §2.4; §2.7; §3.2.8; §5.3 | One flexible credits list [DRAFT]; aliases follow the person, `credit.alias_id` wired up [DECIDED]; credit attributes Uncredited / As… / Note and display order [DECIDED]; replaced "planned note [TBD display]" (A#9, 10) | Credits design |
| 2026-10-09 | §3.2.4 Issue Form | Duplicate issue (series + number + type) blocked with link to existing [DECIDED]; age rating preselected from series; Archivist Note box (A#8, 11) | Issue form design |
| 2026-10-09 | §3.2.15, §3.2.16 (new) | Added Issue View page and Collected Edition page specs, Edit ▾ menu, delete-blocking rule, temporary Diary link, cascade of source edits [DECIDED]; TBD #22 note updated (A#12, 15) | Issue View and collection page design |
| 2026-10-09 | §4.2, §4.3, §8 | Publisher / imprint / creator registry and merge tool noted as long-term goal [DRAFT / TBD]; TBD #37 (A#17) | Long-term direction recorded |
| 2026-10-09 | §7, §8 | Pinned list (Build Plan Appendix B) added: ideas to §7, design topics as new open TBD rows #30–#44 | Park out-of-scope items without losing them |