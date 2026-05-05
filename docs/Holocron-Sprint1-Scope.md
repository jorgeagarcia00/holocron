# Holocron — Sprint 1 Scope
**Version:** 1.0
**Status:** Ready to build
**Audience:** You (Jorge) and Claude Code
**Last Updated:** May 4, 2026

---

## What Sprint 1 Is

Sprint 1 builds the foundation. No forms. No UI. No pages a user can browse.

When Sprint 1 is done, the app runs at localhost:5000, connects to a database, and has all the reference tables and core infrastructure that every future feature will be built on top of. You will not be able to add a comic series through the browser yet. That comes in Sprint 2 and 3.

**The test for "Sprint 1 is done":** Flask runs without errors. All migrations run cleanly. The Contribution Log records an entry when you create a test record via the Flask shell. All reference tables exist and can be queried.

---

## What Gets Built — In This Order

### 1. Project structure and Flask app factory
Claude Code proposes the full folder structure first. You review and approve before any files are created.

Standard Flask layout:
```
holocron/
  app/
    __init__.py        ← app factory (create_app function)
    models/            ← one file per model group
    routes/            ← one file per route group
    templates/         ← Jinja2 HTML files
    static/            ← CSS, images
  data/                ← SQLite database file lives here
  docs/                ← PRD, roadmap, guidelines
  migrations/          ← Alembic migration files
  .env                 ← environment variables (not committed)
  .env.example         ← committed template
  CLAUDE.md            ← Claude Code reads this every session
  requirements.txt
  config.py
```

### 2. Database connection and Flask-Migrate
SQLite connected via Flask-SQLAlchemy. Flask-Migrate initialised. First migration run (empty, just proves the pipeline works).

### 3. Contribution Log — BUILD THIS FIRST, BEFORE ANY OTHER MODEL
Every subsequent model will write to this table. It must exist before anything else.

```python
class ContributionLog(db.Model):
    id
    timestamp           # datetime, auto
    action_type         # 'create', 'edit', 'delete'
    record_type         # e.g. 'creator', 'comic_series'
    record_id           # integer ID of affected record
    old_value           # JSON, nullable
    new_value           # JSON, nullable
    archivist_note      # text, nullable
```

Logging middleware: a reusable function that any model's create/edit/delete can call to write a log entry automatically.

### 4. User Preferences table
One row, always. Stores the Canon/Legends toggle state.

```python
class UserPreferences(db.Model):
    id
    continuity_filter   # 'canon', 'legends', 'both' — default 'both'
```

On app startup: if no row exists, create one with defaults.

### 5. Reference tables — all of these in Sprint 1

**Era**
```python
class Era(db.Model):
    id, name, continuity, 
    in_universe_date_start, in_universe_date_end
```
Seed with Canon era list on first run. Legends era list TBD — leave blank for now.

Canon eras to seed:
- The Dawn of the Jedi
- The Age of the Republic — High Republic Era
- The Age of the Republic — Fall of the Jedi
- The Age of the Rebellion — Reign of the Empire
- The Age of the Rebellion — Age of Rebellion
- The New Republic Era
- The Rise of the First Order
- The New Jedi Order
- Multiple Eras *(special value for entries spanning multiple eras)*
- Unknown

**Publisher**
```python
class Publisher(db.Model):
    id, name, slug, created_at, updated_at
```

**Imprint**
```python
class Imprint(db.Model):
    id, name, slug, publisher_id, created_at, updated_at
```

**Creator**
```python
class Creator(db.Model):
    id, name, slug, bio, image, created_at, updated_at
```

**CreatorAlias**
```python
class CreatorAlias(db.Model):
    id, alias_name, canonical_creator_id,
    alias_type,   # 'pseudonym', 'studio', 'name_variation'
    notes, created_at
```

**Character**
```python
class Character(db.Model):
    id, baseline_name, slug,
    continuity,   # 'canon', 'legends', 'both'
    bio, image, created_at, updated_at
```

**CharacterPersona**
```python
class CharacterPersona(db.Model):
    id, persona_name, slug, baseline_character_id,
    continuity,
    first_appearance_segment_id,   # nullable FK, add constraint later
    image, notes, created_at
```

**Department**
```python
class Department(db.Model):
    id, name, pillar, scope   # scope: 'story' or 'product'
```

Seed with Comics departments:
- Writers (pillar: comics, scope: story)
- Artists (pillar: comics, scope: story)
- Editors (pillar: comics, scope: story)
- Cover (pillar: comics, scope: product)
- Production (pillar: comics, scope: product)
- Lucasfilm (pillar: comics, scope: product)

### 6. Fuzzy search endpoint
A single reusable search endpoint that accepts a query string and a record type, returns matching records. Used by all autocomplete fields throughout the app.

Endpoint: `GET /api/search?q=<query>&type=<record_type>`
Record types: creator, publisher, imprint, character, character_persona, era

Fuzzy matching: case-insensitive, handles partial matches and common misspellings. Use Python `rapidfuzz` library or similar.

### 7. Inline creation behavior
When an autocomplete field receives a value that doesn't match any existing record, a "Create new [type]: [value]" option appears at the bottom of the dropdown. Selecting it creates the record and returns its ID to the form field.

---

## What Sprint 1 Does NOT Include

- Any Comic Series, Issue, or Segment models — that's Sprint 2
- Any forms a user fills in — that's Sprint 3
- Any pages beyond a basic "it works" home page
- Tailwind styling beyond making the app render without errors
- The Canon/Legends toggle UI — the table exists, the UI comes in Sprint 3
- Any filtering or search UI — Sprint 4+

---

## How to Run Sprint 1 With Claude Code

**Starting the session:**
```
claude
```
Then say:
```
Read CLAUDE.md and docs/Holocron-PRD-v2.md. 
We are starting Sprint 1. Before building anything, 
propose the full folder structure for review.
```

**Before each numbered item above:**
```
/grill-me
I want to build [item]. Grill me on the requirements.
```

**After each item works:**
```
git add .
git commit -m "feat: [short description]"
git push
```

**The rule:** One item at a time. Build it. Test it. Commit it. Move to the next.

---

## Definition of Done for Sprint 1

- [ ] Flask app starts with `flask run` — no errors
- [ ] `flask db upgrade` runs all migrations cleanly
- [ ] `contribution_log` table exists in database
- [ ] `user_preferences` table exists with one row (continuity_filter = 'both')
- [ ] All 8 reference tables exist: Era, Publisher, Imprint, Creator, CreatorAlias, Character, CharacterPersona, Department
- [ ] Era table seeded with Canon eras
- [ ] Department table seeded with 6 Comics departments
- [ ] Fuzzy search endpoint returns results for a test query
- [ ] Inline creation creates a new record and returns its ID
- [ ] All of the above committed to GitHub
- [ ] CLAUDE.md updated with Sprint 1 completion note and any conventions established
