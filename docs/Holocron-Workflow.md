# Holocron — Workflow Playbook
**For:** Jorge (not for Claude Code)  
**Replaces:** the old Roadmap (archived in `docs/archive/`)  
**Last updated:** October 8, 2026

How to run a work session on Holocron, step by step. Rules for Claude Code live in `CLAUDE.md`; the spec lives in `docs/Holocron-PRD.md`; how to fill in forms lives in `docs/Holocron-Data-Entry-Guide.md`.

---

## Where each document lives (and which copy wins)

| Document | Job |
|---|---|
| `docs/Holocron-PRD.md` | What we are building |
| `CLAUDE.md` | Rules and conventions for Claude Code |
| `CONTEXT.md` | Glossary — the exact words we use |
| `docs/adr/` | Why we decided something (one short file per big decision) |
| `docs/history/DEVLOG.md` | Dated history of what was built |
| `docs/Holocron-Data-Entry-Guide.md` | How you fill in the forms consistently |
| `docs/archive/` | Retired documents. History only — never a spec |

**The repo copy is the source of truth.** The claude.ai Project holds a snapshot so the planning chat knows the current state. Whenever a document changes in the repo, re-upload it to the Project at the end of the session (and delete the old version there). Old versions are never kept as extra files — git remembers them.

---

## Session startup (every time)

1. Open the `holocron` folder in VS Code.
2. Terminal 1: activate the environment, then start Claude Code
   ```
   .venv\Scripts\activate
   claude
   ```
3. Terminal 2 (new tab): `flask run`, then open `localhost:5000`.
4. Tell Claude Code:
   > Read CLAUDE.md. Tell me the current state of the project before we start.

If you have been away a while, do a read-only check first: `git status`, confirm `(.venv)` shows, and let Claude Code report before anything gets built.

---

## The feature loop

1. **Think in the planning chat** (the Holocron Project). Bring the question; reach a decision; ask for a short "PRD update note" describing the change.
2. **Update the PRD in the repo.** Give the note to Claude Code: "Apply this to docs/Holocron-PRD.md surgically — only the sections named. Add a line to the changelog." Nothing is marked [DECIDED] unless you approved it.
3. **Plan before building.** Tell Claude Code: "Here is the spec for [feature]. Don't build yet — tell me your plan and which files you'll modify." Use `/grill-with-docs` if the feature is fuzzy.
4. **Build and test.** Claude Code writes the code; you try it in the browser and describe changes in plain English.
5. **Commit.** `git add .`, then `git commit -m "feat: ..."`, then `git push`.

One feature at a time. Build it, test it, commit it, then move on.

## End of session

1. Commit and push: `git add . && git commit -m "wip: ..." && git push`
2. Ask Claude Code: "Append a short dated entry to docs/history/DEVLOG.md and update Current State in CLAUDE.md."
3. **Re-upload any changed documents to the claude.ai Project** (PRD, CLAUDE.md, CONTEXT.md, and so on) and delete the old copies there.

---

## Which tool for what

| Situation | Tool |
|---|---|
| Resolving a design question or TBD | Claude chat (Holocron Project) |
| A hard architecture question | Claude chat, strongest model |
| Building a specced feature | Claude Code |
| Debugging a specific error | Claude Code |
| Star Wars canon research | NotebookLM |
| Visual design of screens | Claude Design — **not yet done**; the emoji pillar icons are placeholders |

Rule of thumb: think in chat, build in Claude Code. Don't paste large blocks of code into chat — Claude Code reads files directly.

## Working rules for Claude (both in chat and in Claude Code)

- Nothing is called [DECIDED] without your explicit approval.
- LOCG and GCD inform the design; they are not copied.
- Foundation-level decisions come with their consequences explained first.
- Incomplete input is never silently dropped — it produces an error.

---

## Command cheat sheet

**Flask-Migrate (database changes)**
```
flask db migrate -m "description"   # after changing a model
flask db upgrade                    # apply it
flask db downgrade                  # roll back one step
flask db history                    # list all migrations
```

**Git**
```
git status
git add .
git commit -m "feat: ..."
git push
git log --oneline
```

**Tailwind (after adding new classes to a template)**
```
npx tailwindcss -i app/static/css/input.css -o app/static/css/output.css
```

**Claude Code**
```
/grill-with-docs   interview before a feature, updating docs as terms get settled
/grill-me          interview before a feature
/zoom-out          step back and explain how a piece of code fits the whole
/model             switch models
/clear             fresh context
/exit              close
```

## Backups

Your entries live in `data/holocron.db` (not in git) and cover images in `app/static/uploads/`. A one-command dated backup is queued for setup before real data entry begins. Until it exists, do not start real entries.

## Tools you use

Claude chat (planning), Claude Code (building), VS Code, Git + GitHub (code history), NotebookLM (canon research), SQLite Viewer extension (browse the database), Flask (`flask run`).
