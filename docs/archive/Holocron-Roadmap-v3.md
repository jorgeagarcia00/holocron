> **ARCHIVED 2026-10-08 — historical record only. Superseded by docs/Holocron-Workflow.md. Do not use as a spec.**

# Holocron — Environment Setup & Project Roadmap
**Version:** 0.3
**Audience:** You (Jorge)
**Last Updated:** May 4, 2026
**Current state:** Design complete for Comics Pillar. Environment partially set up. No code written yet.

---

## Where Are You Right Now?

Find yourself and start from there. Don't repeat steps you've already done.

- [ ] **Phase 0** — Verifying existing tools (VS Code, Git, Python, Node)
- [ ] **Phase 1** — Installing Claude Code and uv
- [ ] **Phase 2** — NotebookLM Star Wars research
- [ ] **Phase 3** — Visual design in Claude Design
- [ ] **Phase 4** — Project scaffolding (the one-time project setup)
- [ ] **Phase 5** — Active development (the repeating loop)

---

## Phase 0 — Verify Existing Tools
*~30 minutes. One-time.*

### Step 0.1 — Check VS Code version
Help → About. Need version 1.90 or later.
Update: Help → Check for Updates, or download fresh from https://code.visualstudio.com

### Step 0.2 — Audit VS Code extensions
Open Extensions panel: **Ctrl+Shift+X**

| Extension | Publisher | Search term |
|-----------|-----------|-------------|
| Python | Microsoft | `Python ms-python` |
| Pylance | Microsoft | `Pylance ms-python` |
| SQLite Viewer | Florian Klampfer | `SQLite Viewer qwtel` |
| GitLens | GitKraken | `GitLens gitkraken` |
| Tailwind CSS IntelliSense | Tailwind Labs | `Tailwind bradlc` |

Update all: Extensions panel → **...** → Check for Extension Updates

### Step 0.3 — Check Git
```
git --version
```
If error: download from https://git-scm.com/download/win (choose VS Code as default editor).

Configure identity (safe to re-run):
```
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git config --global credential.helper wincred
```

> **2FA on GitHub?** You need a Personal Access Token. GitHub → Settings → Developer Settings → Personal Access Tokens → Generate new token → `repo` scope. Use as password when Git prompts.

### Step 0.4 — Check Python
```
python --version
```
Need 3.12.x. If older or missing: https://python.org/downloads — **tick "Add python.exe to PATH"** on first installer screen.

### Step 0.5 — Check Node.js
```
node --version
npm --version
```
If missing: LTS from https://nodejs.org, accept all defaults.

---

**Phase 0 complete when:** VS Code 1.90+, all 5 extensions, Git configured, Python 3.12, Node.js — all print version numbers.

---

## Phase 1 — Install AI and Build Tools
*~45 minutes. One-time.*

### Step 1.1 — Install uv
```
pip install uv
```
If "uv is not recognized" after install — close and reopen VS Code completely.

If still failing, use the direct Windows installer:
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Then close and reopen VS Code. Verify:
```
uv --version
```

> **Important:** "uv is not recognized" is a PATH error — Windows doesn't know where to find uv yet. It has nothing to do with your project folder. Closing and reopening VS Code fixes it 90% of the time.

### Step 1.2 — Install Claude Desktop
Download from: https://claude.ai/download
Sign in with Claude Pro account. Gives access to Claude Design at https://claude.ai/design.

### Step 1.3 — Install Claude Code
```
npm install -g @anthropic-ai/claude-code
```
Launch it:
```
claude
```
Type `/login` → follow browser prompt → connect Claude Pro account.
Test that it responds. Type `/exit` to close.

---

**Phase 1 complete when:** `uv --version`, Claude Desktop installed and signed in, `claude` command works.

---

## Phase 2 — Star Wars Knowledge Base
*~1–2 hours. Do before designing or building.*

### Step 2.1 — Create NotebookLM notebook
Go to: https://notebooklm.google.com
Create notebook: **"Holocron — Star Wars Canon Reference"**

### Step 2.2 — Add sources
- Wookieepedia articles: timeline, canon policy, Legends policy, list of Star Wars media
- Official Star Wars site pages (starwars.com)
- Reference books you own
- Your own notes document: what you own, what you want to track

### Step 2.3 — Run these queries and save all answers

- "What are all distinct Star Wars media formats — list every type"
- "What metadata is unique to each format?"
- "What is the canon/Legends split and when did it happen?"
- "What are all named eras in Star Wars canon and their date ranges?"
- **"What are all named eras in Star Wars Legends and their date ranges?"** ← This answer fills TBD #16 in the PRD

Save all answers. The Legends era list specifically needs to go into the PRD before Sprint 2.

---

**Phase 2 complete when:** Notebook exists, all queries run, Legends era list saved and ready to add to PRD.

---

## Phase 3 — Visual Design
*~2–4 hours. Do before Sprint 3 UI work. Can be done after Phase 4 if you want to start building sooner.*

### Step 3.1 — Open Claude Design
https://claude.ai/design

Opening context:
> "I'm building a personal local app called Holocron to track Star Wars multimedia. Dark-themed, cover-art forward, information-dense — like Letterboxd crossed with League of Comic Geeks. Single user, no login. Please start with the main collection dashboard."

### Step 3.2 — Design these screens in order
1. Collection dashboard (home page grid)
2. Series Hub page (comic series with issue grid)
3. Issue / Entry page (all metadata, credits, story breakdown)
4. Add / Edit form (two-column layout: image left, fields right)
5. Creator canonical page
6. Character baseline page
7. Filter / browse interface

Reference the PRD section 3.2.4 for the Issue form field layout when designing screen 4.

### Step 3.3 — Export
- Handoff bundle (for Claude Code to implement from)
- PDF (for Claude Project reference)

Save to: `Documents\holocron-design\`

---

**Phase 3 complete when:** All 7 screens prototyped, handoff bundle and PDF exported.

---

## Phase 4 — Project Scaffolding
*~1.5 hours. One-time. The most important phase before building starts.*

### Step 4.1 — Create GitHub repository
https://github.com → + → New repository
- Name: `holocron`
- Visibility: Private
- Tick: Add a README file

Copy the HTTPS URL.

### Step 4.2 — Clone into VS Code
**Ctrl+Shift+P** → `Git: Clone` → paste URL → choose `C:\Projects\`

### Step 4.3 — Create virtual environment
```
uv venv
.venv\Scripts\activate
```
You must see `(.venv)` before doing anything else. Activate every session.

```
uv pip install flask flask-sqlalchemy flask-migrate python-dotenv rapidfuzz
uv pip freeze > requirements.txt
```

### Step 4.4 — Set up Tailwind
```
npm init -y
npm install -D tailwindcss
npx tailwindcss init
```

Update `tailwind.config.js`:
```javascript
content: ["./app/templates/**/*.html"],
```

Create `app/static/css/input.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 4.5 — Install skills

**Install now:**
```
npx skills@latest add mattpocock/skills/grill-me
npx skills@latest add mattpocock/skills/write-a-prd
npx skills@latest add mattpocock/skills/git-guardrails-claude-code
npx skills@latest add mattpocock/skills/ubiquitous-language
```

**Install after Sprint 2:**
```
npx skills@latest add mattpocock/skills/tdd
```

**Install after Sprint 4:**
```
npx skills@latest add mattpocock/skills/improve-codebase-architecture
```

| Skill | Purpose |
|-------|---------|
| `grill-me` | Interviews you before every feature |
| `write-a-prd` | Turns interview into written spec |
| `git-guardrails-claude-code` | Blocks destructive git commands |
| `ubiquitous-language` | Maintains LANGUAGE.md glossary |
| `tdd` | Test-driven development (add after Sprint 2) |
| `improve-codebase-architecture` | Code quality review (add after Sprint 4) |

### Step 4.6 — Create docs folder and add project documents
```
mkdir docs
```
Copy these files into docs/:
- `Holocron-PRD-v2.md`
- `Holocron-Sprint1-Scope.md`
- `Holocron-User-Guidelines.md`
- This roadmap file

### Step 4.7 — Write CLAUDE.md
Create `CLAUDE.md` in the project root. Ask Claude (in your Project) to write it based on the PRD. It must contain:

**What the app is:**
Holocron — personal, locally-hosted, single-user archival database for Star Wars multimedia. Runs at localhost:5000. No authentication. No external APIs.

**Tech stack:**
Flask, Flask-SQLAlchemy, SQLite (data/holocron.db), Flask-Migrate, Jinja2, Tailwind CSS, htmx (Sprint 3+), rapidfuzz (fuzzy search)

**Always do:**
- Read PRD in docs/ before building any feature
- Use Flask-Migrate for ALL schema changes — never edit database directly
- Build Contribution Log logging into every model create/edit/delete
- Commit after every working feature
- Run `/grill-me` before building any feature
- Update LANGUAGE.md after terminology decisions

**Never do:**
- Install React, Vue, or any JavaScript framework
- Call external APIs
- Hardcode Star Wars data in Python (use database seeding instead)
- Skip migrations — even tiny field additions need a migration file
- Build features marked [TBD] in the PRD without asking the product owner

**Current sprint:** Sprint 1 — Foundation
**Reference:** docs/Holocron-Sprint1-Scope.md

### Step 4.8 — Create Claude Project
In claude.ai → create Project called "Holocron"

Upload to Project knowledge:
- `CLAUDE.md`
- `Holocron-PRD-v2.md`
- PDF design exports from Phase 3
- Your saved NotebookLM answers

Use this Project for ALL planning conversations going forward.

### Step 4.9 — First commit
```
git add .
git commit -m "project scaffold: flask, tailwind, skills, docs, CLAUDE.md"
git push
```

Verify files appear on GitHub.

---

**Phase 4 complete when:** Project folder exists, venv active, packages installed, 4 skills installed, docs/ folder with all documents, CLAUDE.md written, Claude Project created with documents uploaded, first commit pushed.

Note: Tailwind v4 installed by default breaks npx tailwindcss init. 
Use npx tailwindcss@3 to compile:
npx tailwindcss@3 -i app/static/css/input.css -o app/static/css/output.css

---

## Phase 5 — Day-to-Day Workflow
*The repeating loop for every feature.*

### Session startup (every time)
```
.venv\Scripts\activate          ← terminal 1
claude                          ← terminal 1, after venv active
flask run                       ← terminal 2 (new tab)
```

Say to Claude Code:
```
Read CLAUDE.md and docs/Holocron-PRD-v2.md.
Tell me the current state of the project before we start.
```

SQLite note: always name FK constraints in migrations — 
batch_alter_table crashes on unnamed constraints. 
Claude Code handles this automatically if reminded.

Open `localhost:5000` in browser.

---

### Feature workflow (every feature, no exceptions)

**1. Grill Me**
```
/grill-me
I want to build [feature]. Grill me on the requirements.
```

**2. Write the spec**
```
/write-a-prd
```
Commit it:
```
git add . && git commit -m "docs: spec for [feature]"
```

**3. Update vocabulary (after terminology decisions)**
```
/ubiquitous-language
```

**4. Review plan before building**
```
Here is the spec for [feature]. Don't build yet — 
tell me your plan and which files you'll modify.
```

**5. Build and test**
Claude Code writes code. You test in browser. Describe adjustments in plain English.

**6. Commit**
```
git add .
git commit -m "feat: [description]"
git push
```

---

### End of session
```
git add . && git commit -m "wip: [description]" && git push
```
Ask Claude Code: *"Summarise what we built today and known issues."*
Paste summary at bottom of CLAUDE.md with today's date.

---

### Which tool for what

| Situation | Tool | Model |
|-----------|------|-------|
| Resolving a TBD, design decision | Claude chat (Project) | Sonnet |
| Hard architecture question | Claude chat (Project) | Opus |
| Designing a screen | Claude Design | — |
| Building a specced feature | Claude Code | Sonnet |
| Debugging a specific error | Claude Code | Sonnet |
| Something deeply broken | Claude Code → chat | Opus |
| Star Wars canon research | NotebookLM | — |

**Rule:** Think in chat. Build in Claude Code. Never paste large code blocks into chat — Claude Code reads files directly.

---

## Sprint Overview

| 1 | Foundation — Flask, DB, audit log, reference tables | ✓ Complete |
| 2 | Comics data models | ✓ Complete |
| 3 | Comics UI — all forms and pages | Navigation structure (TBD #7) — TBD #1 and #16 resolved |
| 4 | Creator, Publisher, Character pages | None |
| 5 | Television Pillar | TV metadata spec (TBD #11) |
| 6+ | Remaining Pillars, cross-pillar features | Per-Pillar specs |

---

## Quick Reference — Commands

### Every session
```bash
.venv\Scripts\activate
claude
flask run                    # second terminal tab
```

### Git
```bash
git status
git add .
git commit -m "feat: ..."
git push
git log --oneline
```

### Flask-Migrate
```bash
flask db migrate -m "description"    # after model change
flask db upgrade                     # apply migration
flask db downgrade                   # roll back one
flask db history                     # see all migrations
```

### Claude Code skills
```
/grill-me                            before every feature
/write-a-prd                         after interview
/ubiquitous-language                 after terminology decisions
/tdd                                 after Sprint 2
/improve-codebase-architecture       after Sprint 4
/model opus                          hard problems
/model sonnet                        building
/clear                               fresh context
/exit                                close Claude Code
```

---

## Tool Map

| Tool | Role in Holocron |
|------|-----------------|
| Claude chat (Holocron Project) | Planning, decisions, TBD resolution |
| Claude Code | Writing code, migrations, debugging |
| Claude Design | UI prototyping before Sprint 3 |
| VS Code | File viewing, terminal |
| Git + GitHub | Version control, cloud backup |
| NotebookLM | Star Wars canon research |
| Flask (flask run) | Running app at localhost:5000 |
| SQLite Viewer (VS Code ext.) | Browsing database visually |

---

## Your Open Decisions (Before Sprint 3)

These must be resolved before Sprint 3 starts. They don't block Sprint 1 or 2.

| Decision | What's needed | How to resolve |
|----------|--------------|----------------|
| Navigation structure | Full nav layout beyond Add New Media + toggle | In progress — Claude Project chat |
| TV Pillar metadata | Field list for Series, Season, Episode forms | Same process as Comics — Grill Me session |

---

*Keep this document updated. After any sprint, mark completed items.*
*After any design decision, update the PRD.*
*After any session, update CLAUDE.md with what was built.*
