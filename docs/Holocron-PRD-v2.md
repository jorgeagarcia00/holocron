# Holocron — Product Requirements Document
**Version:** 0.2
**Status:** Active — Foundation + Comics Pillar Fully Specced
**Audience:** Claude Code (Developer)
**Last Updated:** May 4, 2026

---

## How to Use This Document

This is the authoritative specification for the Holocron application. Before building any feature:
1. Read the relevant section of this PRD
2. If something is marked **[TBD]**, do not invent a solution — flag it and ask the product owner
3. If something contradicts CLAUDE.md, this PRD takes precedence for feature-level decisions
4. After completing any feature, note decisions made that aren't covered here so the PRD can be updated

**[DECIDED]** = locked, build exactly as specified
**[TBD]** = known gap, park and build around it
**[FUTURE]** = out of scope for current build phase
**[DRAFT]** = proposed but not yet confirmed by product owner

---

## 1. Project Overview

### 1.1 What This App Is
**[DECIDED]**

**Holocron** is a personal, locally-hosted, single-user archival database for tracking Star Wars multimedia. It is not a social platform, not a recommendation engine, and not connected to any external API or service at runtime.

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
- American releases only — non-US editions out of scope
- No JavaScript frameworks (React, Vue, etc.)

### 1.4 Tech Stack
**[DECIDED]**

- **Backend:** Python 3.12, Flask, Flask-SQLAlchemy, Flask-Migrate (Alembic)
- **Database:** SQLite — file: `data/holocron.db`
- **Frontend:** Jinja2 templates, Tailwind CSS
- **Interactivity:** htmx (Sprint 3+)
- **Rich text:** Quill or TipTap (whichever has better Flask/Jinja2 support) — used for Synopsis fields only. Minimum toolbar: Bold, Italic, Unordered List
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
- Periodicals: Series → Issue
- Manga: Series → Issue

**Associative Grouping** — entries exist independently, optionally linked to a named series via `SeriesMembership` join table. Used for standalone media:
- Film, Books, Audio, Games

One entry can belong to multiple Series simultaneously with different position numbers.

### 2.3 Canon/Legends Toggle
**[DECIDED]**

A persistent, site-wide filter control in the navigation bar.

**Three states:** Canon / Legends / Both

**Persistence:** Remembered across sessions. Stored in `user_preferences` table.

**Display filter behavior:**
- Canon → shows entries tagged Canon + entries tagged Both
- Legends → shows entries tagged Legends + entries tagged Both
- Both → shows everything

**Applies to:** Every listing and browsing page — collection grid, calendar, series pages, creator pages, character pages, publisher pages, search results.

**Data entry context:**
- Canon toggle → Continuity field pre-fills as Canon on new entry forms
- Legends toggle → pre-fills as Legends
- Both toggle → Continuity field blank, manual selection required

**Era dropdown behavior:**
- Canon toggle → Canon eras only
- Legends toggle → Legends eras only
- Both toggle → all eras with continuity label

**Character and creator pages:**
- Character/Creator records are continuity-agnostic
- Toggle filters *appearances* and *credits* shown on their pages through the linked entry's continuity
- "Both" tagged entries always visible regardless of toggle state

### 2.4 Credit Scoping
**[DECIDED]**

Every credit belongs to one of two scopes:

**Story Scope (Segment-level):** Credits attached to the narrative. Travel automatically when a Segment is imported. Example: writer, penciler, colorist of a comic story.

**Product Scope (Issue-level):** Credits attached to the physical/digital product. Never migrate. Example: cover artist, collection editor, editor-in-chief.

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

### 2.7 Creator Pseudonyms and Uncredited Work
**[DECIDED]**

**Display:** Credits show name as printed on the page (alias name, not canonical name).

**Clicking a pseudonym:** Takes you to a distinct Pseudonym Page (own URL) showing all credits under that alias. Prominent link to canonical Creator Page. Canonical Creator Page shows all credits across all aliases unified.

**Uncredited work:** Boolean `is_uncredited` flag on Credit record. Displays inline with role label: `Colorist (Uncredited)`. No separate section.

**Alias types:** pseudonym / studio name / name variation

### 2.8 Series Cover Inheritance
**[DECIDED]**

- **Compositional Pillars** (Comics, TV, Periodicals, Manga): Series thumbnail dynamically generated from first Issue's cover. Placeholder shown until Issue #1 has a cover.
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

### 2.10 Metadata Conventions
**[DECIDED]**

All metadata defers to official publisher-assigned values. Personal assessments go in Personal Notes. Exception: if a publisher value is a known misprint or error, enter the correct value and document the reason in the Archivist Note field.

Credit role terminology uses standardised catch-all terms rather than literal on-page credit text. Enter "Colorist" rather than "Color Artist" or "Colors by." Consistency and filterability over literal transcription.

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
| Periodicals | Compositional: Series → Issue | Issue (with Segments) | Structure decided, metadata TBD |

**Build order:** Comics → Television → Film → Books → Audio → Games → Manga → Periodicals

---

### 3.2 Comics Pillar — Full Specification
**[DECIDED]**

#### 3.2.1 Workflow

1. User selects **[Add New Media]** → **[Comics]** from navigation
2. System presents **Series Creation Form**
3. On submit → redirected to **Series Hub Page**
4. From Hub → **[Add New Issue]** → **Issue Form**
5. Issue Form is single scrollable page: Issue Metadata → Issue Credits → Story Breakdown

#### 3.2.2 Series Form Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Title | Text | Yes | |
| Series Type | Dropdown | Yes | See values below |
| Continuity | Dropdown | Yes | Canon / Legends / Both. Pre-fills from toggle |
| Era | Dropdown | Yes | Dependent on Continuity. Canon eras and Legends eras are separate lists. "Multiple Eras" available as option |
| Publisher | Autocomplete + inline create | Yes | |
| Imprint | Autocomplete + inline create | No | |
| Reading Level | — | — | **[TBD]** — Comics audience rating system differs from Books. Current decision: All Ages / T / T+ / M using official publisher-assigned rating. Field name: `age_rating`. Nullable — older comics predate rating system |
| Start Year | Year input | No | |
| End Year | Year input | No | Blank if ongoing |
| Synopsis | Long text | No | |
| Cover Image | Inherited from Issue #1 | — | No upload on Series form |

**Series Type values:**
- Regular Series
- Limited Series
- One-Shot *(single issue — still requires a Series record for consistency)*
- Annual
- Collection *(reprint/collected edition series — TPBs, HCs, Omnibuses)*
- Graphic Novel *(original graphic novels, not collected editions)*

#### 3.2.3 Series Hub Page

Must contain:
- Series metadata display with Edit button
- Issue grid — cover thumbnails, issue number, release date
- Reading progress summary (% of issues completed)
- **[Add New Issue]** button
- **[Bulk Add Issues]** button — **[TBD]**
- **[Bulk Edit Issues]** button — **[TBD]**

#### 3.2.4 Issue Form

**Layout:** Two-column. Left column: cover image display area (placeholder → live preview on upload) + upload controls directly below image. Right column: all form fields.

**Fields in order:**

**Row 1:** Continuity (inherited, static) / Era (inherited, static)
**Row 2:** Publisher (inherited, static) / Imprint (inherited, static)
**Row 3:** Series Title (inherited, static) / Issue # (required, text field — handles #0, #½, #1.AU)
**Row 4:** Release Date (required) / Cover Date (optional)
**Row 5:** Type (required) / Format (required) / Trim Size (optional)
**Row 6:** Synopsis (full width, rich text editor — Bold, Italic, Unordered List minimum)
**Row 7:** Pages / Age Rating / Price USD / UPC-ISBN (all optional)
**Row 8:** Wookieepedia URL (permanent, label fixed) + generic Add Link rows (URL + Label fields)

**Type values:** Regular Issue / Annual / Graphic Novel / Collected Edition
**Format values:** Comic / Paperback / Hardcover / Digital
**Trim Size values:** Standard / Digest / Oversized / Digital / Other (triggers freeform text input)

**Interdependent format logic:**
- Regular Issue → Format defaults to Comic
- Collected Edition → Format defaults to Paperback or Hardcover
- Graphic Novel → Format defaults to Hardcover or Paperback

**External links display:** Each saved link renders as icon button on entry page. Wookieepedia gets its own icon. Generic links display domain favicon or generic link icon. Label becomes tooltip.

**UPC vs ISBN:** Single label "UPC / ISBN" — user enters whichever applies based on Type.

#### 3.2.5 Story Breakdown Section

Two distinct zones:

**Zone 1 — Issue Credits (top)**
Product Scope credits. Do not travel with imported segments. Visual distinction from Zone 2 required — label "Issue Credits" with explanatory subtext. Exact aesthetic treatment TBD in Claude Design phase.

**Zone 2 — Segment Blocks (numbered, below)**
Story Scope content units.

**Two action buttons at top right of Story Breakdown section:**
- **[IMPORT]** — opens Import Modal
- **[ADD]** — adds new segment block with smart defaults

**ADD behavior:**
- Generates new block with defaults: Type = Story / Reproduction = Original / Colors = Color
- Sort order auto-increments
- All fields editable

**Minimum segments to save:** At least one segment block must exist. No individual segment fields required — all optional.

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

**Each credit row:** `[Creator Name — autocomplete + fuzzy match + inline create] [Role — type-to-search] [Remove button]`

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
| Lucasfilm | Product | Issue | Roles: Lucasfilm Editor, Lucasfilm Art Director, Licensing Manager, Story Group Consultant, etc. |

**Role vocabulary:** Standardised catch-all terms preferred (Colorist not "Color Artist"). Consistency over literal transcription.

**Role Alias system:** Deferred. Not needed for Comics. Revisit when speccing Film/TV/Games where credit terminology is less standardised.

#### 3.2.9 Character Mechanic
**[DECIDED]**

**Each character row:** `[Character Name — autocomplete] [Appearance Type dropdown] [Remove button]`

Autocomplete searches both Baseline names and Persona names simultaneously. Selecting a Persona auto-populates both `character_id` (baseline) and `persona_id`. Displays as "Baseline Name as Persona Name" when persona selected.

No per-row Universe Filter — site-wide Canon/Legends toggle handles continuity scoping.

**Appearance Types:** Main / Supporting / Cameo / Vision
- **Main** — heavy speaking role, pivotal to story
- **Supporting** — present and interactive, not the focus
- **Cameo** — brief appearance, minimal interaction
- **Vision** — Force ghost, flashback, dream, illusion, clone, or construct

**Display on entry page:** Grid of headshots with name labels. Auto-sorted: Main → Supporting → Cameo → Vision. No explicit section headers.

**is_uncredited flag:** Available on character appearances for parity with credit system.

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
  is_uncredited (boolean), archivist_note, created_at
```

**Continuity on character records:**
- Character's Continuity field controls visibility on character browse page under toggle
- Appearance filtering on character page works through the linked entry's continuity
- "Both" entries always visible regardless of toggle state

**Continuity badge:** Displayed on character page and persona page. Simple badge: Canon / Legends / Both. Style TBD in Claude Design phase.

#### 3.2.11 Cover Handling
**[DECIDED]**

The cover is NOT a Segment. It is a property of the Issue — handled through the Cover Upload field and the Cover department in Issue Credits (Product Scope). Variant covers, facsimiles, and reprint editions handled at Issue level, not Segment level.

#### 3.2.12 Variant Covers
**[TBD — deferred to Sprint 4+]**

Structure supports it. UI and workflow not yet designed.

#### 3.2.13 Bulk Add / Bulk Edit
**[TBD — deferred to Sprint 4+]**

Known requirements:
- Available on Series Hub pages
- Bulk add: multiple Issues in sequence without full page reload per issue
- Bulk edit: shared fields across multiple selected Issues simultaneously

---

## 4. Global Features

### 4.1 Navigation
**[TBD — full structure]**

Known requirements:
- **[Add New Media]** button always visible — leads to Pillar selection
- **Canon/Legends toggle** always visible
- Each Pillar leads to its own creation form

### 4.2 Creator Pages
**[TBD — layout and contents]**

Known requirements:
- Every Creator has a dedicated canonical page
- Shows all credits across all Pillars and all Segments
- Filterable by: Pillar, Role, Era, Canon Status
- Sortable by: Release Date, In-Universe Date
- Pseudonym Page: distinct page (own URL) per alias, links back to canonical Creator Page

### 4.3 Publisher and Imprint Pages
**[TBD — layout and contents]**

Known requirements:
- Every Publisher and Imprint has a dedicated page
- Shows all Issues/Editions released

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
**[TBD — full field list per Pillar]**

Known core fields:
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
  id, name, department_id, created_at

-- role_alias reserved for future use (Film/TV/Games)
```

### 5.2 Comics Pillar Tables (Sprint 2)

```sql
comic_series
  id, title, series_type, continuity, era_id,
  is_timeline_spanning (boolean, default false),
  publisher_id, imprint_id, age_rating,
  start_year, end_year, synopsis,
  created_at, updated_at

comic_issue
  id, series_id, issue_number, issue_title,
  release_date, cover_date,
  designation, physical_binding, trim_size,
  pages, price, upc_isbn,
  synopsis, cover_image,
  wookieepedia_url,
  created_at, updated_at

external_link
  id, issue_id, url, label, created_at

comic_segment
  id, issue_id, segment_type, sort_order,
  title, colors, pages,
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
  is_uncredited (boolean),
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
- `contribution_log.old_value` and `new_value` stored as JSON diffs
- `role_name` stored directly on credit record (not a foreign key) because roles are freetext with department-scoped memory, not a fixed controlled vocabulary

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
| 999 | Visions (Non-Continuity) | Stories not bound by primary Canon timeline |

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
| 999 | Infinities (Non-Continuity) | Parodies and What If scenarios |


---

## 6. Build Order

### Sprint 1 — Foundation
**Goal:** Flask runs. Database connects. Audit log works. All reference tables exist with fuzzy search.

1. Flask app factory, config, `.env` file
2. SQLite connection, Flask-Migrate initialised
3. **Contribution Log model — build before any other model**
4. `user_preferences` table (toggle state)
5. Reference tables: Era, Publisher, Imprint, Creator, CreatorAlias, Character, CharacterPersona, Department
6. Fuzzy match search endpoint for all reference tables
7. Inline creation behavior on all autocomplete fields

### Sprint 2 — Comics Pillar: Data
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

*Before Sprint 3: resolve TBD — Work-Level Credit taxonomy (product owner in progress)*
*Before Sprint 3: resolve TBD — Navigation structure*

1. Series Creation Form
2. Series Hub Page with issue grid and cover inheritance
3. Issue Form — two-column layout, all fields, rich text synopsis
4. Story Breakdown section — Issue Credits zone + Segment blocks
5. ADD and IMPORT buttons with modal
6. Compilation workflow
7. Autocomplete + fuzzy match + inline creation for Creator, Publisher, Character
8. Pseudonym display and Pseudonym Page routing
9. Uncredited flag display
10. Contribution Log display on entry pages
11. Canon/Legends toggle in navigation

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

- Issue-to-issue cross-reference / referenced comics mechanism (LOCG-style)
- Role Alias system for Film/TV/Games credit terminology normalisation
- Character appearance type expansion beyond Main/Supporting/Cameo/Vision
- Timeline visualisation (in-universe chronological view)
- Auto-populate fields from Wookieepedia URL
- Custom reading/watch order lists
- Database backup and restore UI
- Dark/light theme toggle
- Related media suggestions

---

## 8. TBD Registry

| # | Item | Blocking | Notes |
|---|------|---------|-------|
| 1 | Work-Level Credit taxonomy — departments and roles per Pillar | Sprint 3 | Product owner in progress |
| 2 | Variant cover workflow and UI | Sprint 4+ | Structure supports it |
| 3 | Bulk add / bulk edit UI | Sprint 4+ | Requirements known |
| 4 | Creator page layout and contents | Sprint 4 | Requirements known |
| 5 | Publisher/Imprint page layout | Sprint 4 | Requirements known |
| 6 | Character page layout and contents | Sprint 4 | Requirements known |
| 7 | Navigation structure beyond Add New Media + toggle | Sprint 3 | |
| 8 | Personal tracking fields per Pillar | Sprint 3 | Core fields known |
| 9 | Series membership primary vs. companion definition | Sprint 6+ | Field reserved |
| 10 | Television Pillar full specification | Sprint 5 | Structure decided |
| 11 | Film, Books, Audio, Games, Manga, Periodicals specs | Sprint 5+ | Structure decided |
| 12 | Manga tankōbon collection system | Sprint 5+ | Acknowledged complexity |
| 13 | Placeholder icon style and Pillar accent colors | Sprint 3 | Claude Design phase |
| 14 | Issue Credits zone visual distinction from Segment credits | Sprint 3 | Claude Design phase |
| 15 | Continuity badge visual style | Sprint 3 | Claude Design phase |
| 16 | Legends era list | Sprint 2 | RESOLVED -- see section 5.4 |
