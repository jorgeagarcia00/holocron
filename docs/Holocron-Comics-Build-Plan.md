# Holocron — Comics Build Plan (Part 2 handoff)

Written 2026-10-09 from the Part 2 design brainstorm. Audience: Jorge (product owner, not a developer) and Claude Code.
Companion files: `docs/Holocron-PRD.md` (spec), `CLAUDE.md`, `docs/history/part1-cleanup-handoff.md` (Phase B queue, referenced below as "B#n").

**Status labels used here.** DECIDED = Jorge explicitly approved. DRAFT = Jorge leans this way or reserved the right to change his mind. Nothing in this plan may be written into the PRD as [DECIDED] unless it is labelled DECIDED in Appendix A. Jorge: change any label you disagree with before Claude Code applies it.

---

## How to run each stage (plain steps)

0. **Put this file in the repo first.** Save it as `docs/Holocron-Comics-Build-Plan.md` in your Holocron folder (it does not sync there by itself) and commit it. Claude Code can only read it from there.
1. **Back up first.** Copy `data/holocron.db` somewhere safe (Stage 1 adds a one-command backup; until then, copy the file by hand). Everything in the database today is test data, so mistakes are cheap, but get in the habit.
2. **One stage per Claude Code session.** Open Claude Code in the Holocron folder and paste the prompt shown at the top of the stage.
3. **Claude Code builds only that stage**, commits as it goes, then stops and reports what changed.
4. **You test using the "Check it yourself" list.** Start the app the way you normally do (localhost:5000). Each item is something you can do in the browser, no code reading. Stage 0 has nothing to run, so you just read the PRD.
5. **If something is off, or a question comes up that is not answered here, stop and bring it back to the planning chat.** Do not let Claude Code guess on design.
6. **When a stage passes,** ask Claude Code to commit anything left over and push to GitHub, tell the planning chat, then `/clear` and start the next stage. (Pressing Sync now in the Project only refreshes the PRD and docs the Project can see, not your code.)

Rules for every stage: edit only what the stage names; commit after each numbered step; never mark anything [DECIDED] that is not DECIDED in Appendix A; a stage that needs a database change must say so before running it.

**Stage order, in one line:** 0 PRD → 1 cleanups → 2 database foundations → 3a series form → 3b issue form → 3c import (reprints) → 4 Issue View → 4b edit/delete issue → 5 series page → 6 collected-edition page → 7 bulk tools and printed series name → 8 clean slate.

**What exists today (so you know what is new):** only the Create Series form, the Series page (covers are not clickable), the Create Issue form, and the home page. There is **no page for a single issue, no way to edit or delete a series or an issue, and the Import button is switched off**. Stages 3a–4b build those.

---

## Confirmed answers (Jorge, 2026-10-09)

Jorge confirmed all six. Item 6 (Edit history) is approved as the simple version for now; its full design is pinned in Appendix B. Anything marked **(confirmed by Jorge 2026-10-09)** in a stage refers to one of these.

1. **Delete (Stage 4b and 7):** if you delete an issue whose stories are reprinted in a collected edition, the site blocks it and names the collections. Suggested: yes.
2. **Stats row (Stage 5):** "Read x/y" and "Own x/y" count original issues, annuals and one-shots, not collected editions (same rule as the creators strip). Suggested: yes.
3. **Names are not links yet (Stage 4–6):** creator and character pages don't exist (they are Sprint 4), so names are plain text for now and become links when those pages are built. The count numbers still open the simple issue list. Suggested: yes.
4. **Diary link (Stage 4):** until the navigation is designed, the top bar gets a plain "Diary" link. Suggested: yes.
5. **Headshots (Stage 4–6):** every headshot is a silhouette for now; there is no photo upload in this plan. Suggested: yes.
6. **Edit history (Stage 3a, 4b):** each entry shows the date, "created" or "edited", what changed (old → new) and your Note. Suggested: yes.

---

## Safety and usage tips for Claude Code sessions

These are suggestions for Jorge, not design decisions. Details were checked against the official Claude Code docs on 2026-10-09; commands can change between versions, so if one doesn't work, type `/help`.

### Which model, and how to check it
- **Check the model:** type `/status` (shows the active model and account).
- **Change it:** `/model` opens a picker (Enter = switch and save as default; `s` = this session only). `/model sonnet` also works.
- **Suggested use (adjust as you like):**

| Stage | Suggested model | Why |
|---|---|---|
| 0, 1 | Sonnet, lower thinking effort (`/effort`) | Documents and small fixes |
| 2 | `opusplan` | Opus plans (use plan mode), Sonnet builds; this is the riskiest stage |
| 3a | Sonnet | Contained form work |
| 3b | Sonnet, or `opusplan` if the plan looks complicated | Many moving parts |
| 3c | `opusplan` | Reprint links touch several tables |
| 4, 4b, 5, 6 | Sonnet, starting in plan mode | Page building |
| 7, 8 | Sonnet | Bulk tools, reset |

- Don't leave Opus as your everyday default; it is the usual cause of unexpectedly high usage.

### Keeping usage down
- **One stage per session**, then `/clear` before the next. Claude Code re-sends the whole conversation with each message, so long sessions cost more with every reply. If you want to return to a session later, `/rename` it first, then `/resume`.
- **`/usage`** shows token use (and plan limits on a subscription). **`/context`** shows what is taking up space. **`/compact`** summarizes a long session; it is itself a large request, so prefer a fresh `/clear` between unrelated tasks.
- **Idle gaps cost more.** After a break of an hour or more, the first message reloads the whole conversation. Start fresh rather than resuming an old, long session.
- **Paste only the stage prompt**, not the whole plan; Claude Code reads the file itself.
- **Keep prompts specific** ("Do Stage 3a only"), not vague ("improve the forms").
- **Keep `CLAUDE.md` short** (roughly under 200 lines). Long workflow instructions belong in skills, which load only when needed. Tell the planning chat if you want a skill proposed.

### Guardrails while building
- **Back up before Stage 2 and before Stage 8** (Stage 1 adds a one-command backup).
- **Start big stages in plan mode** (press Shift+Tab until it says plan mode). Claude Code proposes an approach and waits for you. Read it before approving.
- **Ask for plain English before any database change:** "Tell me what this change does to my data before you run it."
- **Commit after each numbered step.** If a step goes wrong, `/rewind` (or press Esc twice) restores the conversation and the code to an earlier point.
- **Press Esc the moment it heads the wrong way** rather than letting it finish.
- **Test small and often:** after each stage, work through its "Check it yourself" list before starting the next stage.
- **If a question comes up that this plan doesn't answer, stop and ask the planning chat.** Claude Code should not decide design.
- **Never let Claude Code mark anything [DECIDED]** that is not DECIDED in Appendix A.

Sources: [Model configuration](https://code.claude.com/docs/en/model-config), [Manage costs effectively](https://code.claude.com/docs/en/costs).

---

## Stage 0 — Put the decisions into the PRD (documents only, no app code)

**Prompt:** "Read `docs/Holocron-Comics-Build-Plan.md` and `CLAUDE.md`. Do Stage 0 only: apply Appendix A to `docs/Holocron-PRD.md`, surgically, using the status labels exactly as given. Add a Change Log row per decision group dated 2026-10-09. Then stop."

What it does
- Applies the decision register (Appendix A) to the PRD at the sections it names, and adds the pinned list (Appendix B) to §7 and the TBD registry as new open rows.
- Bumps the PRD to v0.5.

Check it yourself
- Open the PRD, find the Change Log, and read the new rows.
- Confirm DRAFT items are labelled DRAFT and the pinned items are in §7 or the TBD registry.

---

## Stage 1 — Safe cleanups (no design dependence)

**Prompt:** "Do Stage 1 only. Items are from Phase B in `docs/history/part1-cleanup-handoff.md`: #1, #4, #5, #12, #13, #14, #15, #16. Commit after each."

What it does
1. **B#1** Era names: "Visions" and "Infinities" (drop "(Non-Continuity)"), including existing rows.
2. **B#4** Series page order: by release date, ties broken by a proper issue-number order (½, 1, 1.AU…). Series cover = earliest regular issue that has a cover.
3. **B#5** Dates show as "Oct 3, 2026"; cover dates as "Dec 2026".
4. **B#12** Rename the form label "Container Credits" to "Product Credits".
5. **B#13** Series synopsis is shown as plain text with line breaks (no raw formatting code).
6. **B#14** Add "Senior Editor" to the Production roles.
7. **B#15** Delete the dead `/api/eras-options` route and its partial.
8. **B#16** One-command dated backup of the database and cover images. Claude Code will ask you where to save backups. Suggested: a folder outside OneDrive (a database file that is being synced while the app runs can cause trouble). The backup folder is added to `.gitignore`.

Check it yourself
- Era dropdown shows "Visions" and "Infinities".
- A series with issues 1, ½ and 1.AU lists them in a sensible order.
- Dates look like "Oct 3, 2026" everywhere; cover dates like "Dec 2026".
- Run the backup command; confirm a dated copy appears.
- The old "Container Credits" label is gone.

---

## Stage 2 — Foundations underneath (database changes; the only visible change is how issue numbers and titles behave)

This is the stage with the most weight. It reshapes how data is stored while everything is still test data. Ask Claude Code to explain each database change in plain English before running it.

**Prompt:** "Do Stage 2 only. Before changing anything, tell me in plain English what each database change will do. Then do them in the order listed, one commit each."

What it does
1. **Issue numbers and titles (B#2).** Issue # applies to regular issues only. For annuals, one-shots, collected editions and graphic novels, the text goes in the title and the number stays empty. The issue-number column must allow "empty". Names display as in PRD §3.2.4: "TPB", "HC", "(Digital)" added automatically (never typed); a one-shot or collected edition may have no subtitle. Add a hint under the box: leave blank if there is no subtitle; never type TPB or HC.
2. **Series-type rules (B#3).** Regular series cannot hold graphic novel issues; collections and graphic novels cannot use the "comic" format; the form and the server must agree.
3. **Volume.** New optional whole-number field on series. Empty = no tag.
4. **One flexible credits list (DRAFT).** Credits point at "a story, an issue, or later a TV episode, film, game…" instead of only comic stories and issues. Existing test credits are carried across. The credit gains the three attributes: *uncredited*, *credited as* (a saved alias of that person), and *note* (free text, e.g. "pages 9-10").
5. **Aliases follow the person (DECIDED).** `credit.alias_id` is wired up so a credit can say "credited as" one of the person's saved aliases.
6. **B#8** Remove "uncredited" from character appearances.
7. **Your personal layer, stored in one flexible list (DRAFT).** Two new lists that can point at any product (comic issue now; film, book, game later): (a) **marks**: Read / Own / Wish, independent, one row per product per mark; (b) **log entries**: product, date, "I've read this before" flag. Nothing on screen yet.
8. **Archivist Note storage (B#9, storage part).** The contribution log can hold an optional note per entry.
9. **Duplicate rule.** A second issue with the same series, number and type is refused. Plain-English check in code first; a database-level guard only if it can't wrongly block a legitimate case.
10. **Edit history needs old and new values.** When a series or issue is edited, the contribution log must store what each changed field was before and after (plus the Archivist Note). Stages 3a and 4b display it.

Check it yourself
- App still starts, existing test series and issues still open.
- Adding a one-shot or collected edition: the box does not fill the "Issue #"; the typed text becomes the title, shown as "… TPB" or "… HC" as appropriate.
- You see no new pages. If anything else visible changed, tell the planning chat.
- Ask Claude Code to show you the old test credits still attached to the right stories.

Stop and come back here if: Claude Code proposes a different credit or marks shape than the flexible lists above (they were chosen to keep one creator page and one Diary across all media).

---

## Stage 3 — The forms

### 3a. Series form + Edit series

**Prompt:** "Do Stage 3a only: rebuild the Series form per the layout below and add Edit series using the same form."

Layout, top to bottom (all DECIDED unless noted)
1. Publisher (dropdown, "+ Add new…" at the bottom) and Imprint (dropdown showing only the chosen publisher's imprints, with "+ Add new…").
2. Title, full width.
3. Series Type (dropdown) and **Vol. #** (small number box, blank by default).
4. Continuity and Era. If Continuity is "Both", a second Era dropdown appears. "Multiple Eras" stays in the Era dropdown for now.
5. Start Year, End Year (typed), **Age Rating** (dropdown: All Ages, T, T+, M).
6. Synopsis (large).
7. Notes (this is the Archivist Note: a short comment saying why you made or changed this; saved with that edit only, empty each time you open the form; visible only in Edit history).
8. Create and Cancel.

Behaviour
- New publishers or imprints are saved only when you press Create Series (no leftovers if you cancel). Same name typed twice resolves to one record, ignoring capital letters.
- End Year earlier than Start Year is refused. Clearer wording for era errors.
- The existing Series page gets an **Edit ▾** menu in place of the greyed-out Edit button (Stage 5 rebuilds the page and keeps the menu): *Edit* (opens this form pre-filled; saving it records a log entry with old → new values and your Note) and *Edit history* (a simple read-only list: date, "created" or "edited", what changed old → new, and the Note).
- Age rating on the series is a suggestion only: a new issue preselects it but can change it.

Check it yourself
- Create a series with a brand-new publisher; cancel halfway through a second one: no stray publisher appears.
- Create a series with Volume 2: "Vol. 2" shows next to publisher and years.
- Edit a series, type a Note, open Edit history: the note is there.

### 3b. Issue form fixes

**Prompt:** "Do Stage 3b only: Phase B #6, #7, #9 (form part), #10, #11, plus the items below."

What it does
1. **B#6** Credit rows need a creator AND a role; otherwise show an error and do not save. Character appearance type defaults to Main, so no rows are silently dropped.
2. **B#7** New characters made inside the form take the issue's continuity.
3. **B#11** Nothing is created at the moment you pick "+ Create…". New creators, characters, roles, publishers and links are created when you save the form, together with the log entry. The same new name used twice in one form becomes one record.
4. **B#10** Log the events that are currently missed (auto-created roles, links).
5. When the form shows an error, everything you typed in the Story Breakdown is kept (today it is lost).
6. **Credit "···" dialog (DECIDED).** Three options, any combination: *Uncredited*; *As…* (pick one of the person's saved names or add a new one, which is saved as a name of that person; greyed out while Uncredited is ticked); *Note* (free text). Typing an alias in the creator box finds the real person. Everything shows under the name: headshot → role → name → attributes.
7. **Duplicate issues are blocked (DECIDED)** with a message and a link to the existing issue.
8. **Archivist Note** box at the end of the issue form (B#9), saved with that entry.
9. The form shows the series' age rating preselected (Jorge can change it per issue).

(Editing and deleting an existing issue come later, in Stage 4b, because there is no issue page to open them from yet.)

Check it yourself
- Leave a role empty on a credit: you get an error and your typing is not lost.
- Add a character without choosing a type: it saves as Main.
- Add a credit as "Uncredited" and another with a "credited as" name and a "pages 9-10" note.
- Try to add a second "Series #7": it is refused with a link to the existing one.
- Start creating a new creator inside the form, then cancel: no stray creator remains.

### 3c. Import (reprints and collected editions)

**Prompt:** "Do Stage 3c only. First check what already exists for the Import button and for the reprint links between stories (it is switched off today and the PRD lists it as open). Explain your plan to me in plain English, then build."

Why this stage exists: the Collected-edition page (Stage 6) and the "Reprints" box (Stage 4) both depend on being able to import existing stories into another issue. Today the Import button on the issue form is switched off.

What it does
- The **Import** button on the Story Breakdown opens a window where you pick an existing story (search by series, issue or story title) and add it to the issue you are entering, in the order you place it.
- The imported story keeps a link to the original and records a **Reproduction type** (Reprint, Remaster, Excerpt, Compilation; see PRD §2.5). Only plain 1:1 reprints are handled for now.
- Changes to the original story (credits, characters, title, cover) show up on every issue that reprints it. **Before building, Claude Code must explain in plain English how it will do this** (a live link to the original versus a copy that is kept in sync) and why. Suggested: a live link, with edits allowed on the reprint only where it is not a 1:1 copy.
- Credit notes and the "uncredited" and "credited as" attributes come along with the credit.
- Non-story material (galleries, text pages, introductions) can be added as its own segment type in the breakdown.

Check it yourself
- Create a collected edition and import two stories from two different issues; they appear in the order you placed them.
- Save, reopen: the order and the links are kept.
- Open one original issue and confirm it records that it is reprinted in the collection (you will see this on screen in Stage 4).

---

## Stage 4 — Issue View (the page for one issue)

**Prompt:** "Do Stage 4 only: build the Issue View exactly as described in this stage (and Appendix A row 12). It is a new page; there is none today. Make the Read / Own / Wish / Log strip fully working, and build the basic Diary page described here."

What it does (all DECIDED)
- **Left column:** cover; below it the strip **Read | Own | Wish | Log**; below that a reserved empty area (variants, whole-issue reprints, editions come later). Cover date as a small label above the cover, level with the top line.
- **Main column:** top line *Publisher · Imprint · Type*; Continuity and Era badges at top right (plain text for now); title (series-name part clickable) and release date; Prev / Next arrows with a middle "view series" button; **Edit ▾** menu.
- **Synopsis,** then a details strip showing only fields that have values, in form order, links as icons, labelled "Age rating".
- **Product credits** in three groups (Cover, Production, Lucasfilm): headshot slots in a row (room for 8–10 per row, with a small gap between groups), role above the name, attributes (uncredited, credited as, note) under the name. Silhouettes only for now (no photo upload in this plan) and names are plain text until creator pages exist (confirmed by Jorge 2026-10-09).
- **Contents:** numbered story blocks, first one open; header "Title / Type · pages"; a tag "B&W" or "Color & B&W" only when not full colour. Inside: Creators row, Editors row, Characters row with one continuity badge and the role bar.
- **Reprints (n):** a collapsible box (cover, title, release date) listing every collected edition or issue that reprints this one's stories (filled from Stage 3c's links).
- **Edit ▾ menu:** *Edit* and *Edit history* open the pages built in Stage 4b (until then they are shown but inactive); *Add new variant cover* is shown but inactive.
- **Marks and Log:** Read / Own / Wish toggle independently on the product (never on stories). *Log* opens a small pop-up with **date** (defaults to today) and **"I've read this before"** only. Saving a log ticks Read if it wasn't. Deleting every log entry never unticks Read. You can tick Read without logging. There are no Read / Own / Wish list pages yet; you see your marks on the issue page and (from Stage 5) the series page.
- **Basic Diary page:** a plain "Diary" link in the top bar (confirmed by Jorge 2026-10-09) opens a list of your log entries, newest first (cover, title, date, "read before" if ticked). Each entry can be edited (date, "read before") or deleted. Stage 7 adds sorting.
- Edits to an original story (credits, cover, characters, title) flow to every collected edition that reprints it.

Check it yourself
- Open an issue; click Read, Own, Wish; reload: the state is kept.
- Click Log, save: Read becomes ticked and the entry is on the Diary page. Log a second time: the box offers "I've read this before".
- Delete every Diary entry for that issue: Read stays ticked.
- Open an original issue that was imported into a collected edition (Stage 3c): its Reprints box lists the collection.
- (Editing a story's credit comes in Stage 4b.)

---

## Stage 4b — Edit and delete an issue

**Prompt:** "Do Stage 4b only: Edit issue, Delete issue and Edit history for issues, from the Issue View's Edit ▾ menu."

What it does
- **Edit:** the same form as creating an issue, pre-filled with everything already saved (series, number/title, dates, format, Story Breakdown segments, credits with their attributes, characters, links, the order of segments, imported stories). Saving writes a log entry with old → new values and your Archivist Note.
- **Edit history:** the same read-only list as for series.
- **Delete** sits at the end of the form with a confirmation. If the issue's stories are reprinted in a collected edition, Delete is blocked with a message naming the collections (confirmed by Jorge 2026-10-09). Marks and log entries for a deleted issue are deleted with it.
- A change to an original story shows on every collected edition that reprints it (confirms the Stage 3c link works).

Check it yourself
- Edit an issue's credit: save, reopen: it changed. The Edit history shows old → new and your Note.
- Edit a story that is reprinted in a collection: after Stage 6 you will see the change there too; for now check the Reprints box still lists the collection.
- Try to delete an original issue that is reprinted in a collection: it is blocked with a clear message.
- Delete an issue that is not reprinted anywhere: it is gone after you confirm.

---

## Stage 5 — Series page

**Prompt:** "Do Stage 5 only: rebuild the Series page exactly as described in this stage (and Appendix A rows 13 and 14). Keep the Edit ▾ menu from Stage 3a."

What it does
- Faint line at the very top: **comic series · regular series** (small, set apart).
- Then **Publisher/Imprint · Vol. N · years**, the series title (large), Continuity/Era icons (text for now), **Edit ▾**, a bigger synopsis.
- **Stats row:** Read x/y and Own x/y (no Wish count), and **+ Add Issue**. x = how many you've marked; y = the number of original issues, annuals and one-shots in the series (collected editions are not counted) (confirmed by Jorge 2026-10-09). A One-Shot series still limits itself to one issue.
- **Tabs: Creators | Cover | Editors | Characters** (Creators open by default; the site remembers your last choice; one collapse arrow). Top 8 by count: issues credited in (original issues, annuals and one-shots only; collected editions never count; Production and Lucasfilm are left out; characters count Main and Supporting only). Each card: headshot (silhouette), role line (not for characters), name, count, years. Creator and character pages don't exist yet (Sprint 4), so names are plain text for now; the number opens a simple clickable list of those issues (popup design pinned) (confirmed by Jorge 2026-10-09). A person with several roles shows them together ("Writer, Penciler"); an alias credit counts for the real person.
- **Sections:** Issues (n), Annuals, One-Shots, Collected Editions, each collapsible, same card design. Covers are clickable.
- **Slim toolbar above the issues:** **Sort** (Release date oldest first, which is the default; newest first; Issue number low to high; high to low), **Filter** (All, Read, Unread, Owned, Not owned, Wish), **Select** (turns on checkboxes; the actions come in Stage 7), **Search** (matches issue number and title within this series). No grid/list switch. The toolbar applies to the section it sits above, and its choices reset when you leave the page.
- **Cover cards (DRAFT hybrid):** small always-visible state dots for Read / Own / Wish; the full icon bar (Read, Own, Wish, Log) on hover; a checkbox on hover in Select mode.
- Labels say "TPB", never "TP".

Check it yourself
- Click any cover: it opens the issue.
- Mark an issue Read from the series page; the Read count updates.
- Sort and filter; type in Search.
- The creators strip shows the right names for a series where you've entered credits; collected editions don't add to counts.

---

## Stage 6 — Collected edition page

**Prompt:** "Do Stage 6 only: the collected-edition page exactly as described in this stage (and Appendix A row 15). It is the Issue View from Stage 4 with a different Contents area."

What it does
- Same as the Issue View (cover, strip, product credits, details) with these Contents changes:
- **Overview** (a collapsible row, open by default): "# stories", then tabs **Creators | Editors | Characters** (no Cover tab). Summary of the most-credited people and most-featured characters across the stories in the book. Small count under each name; ties fall back to book order. Counts use story-type segments only.
- **Story list** (like a table of contents): numbered circles in book order; the original issue's title, story title, release date, type, pages, and the original's cover thumbnail; collapsed by default; click to expand and see that story's Creators, Editors, Characters only.
- **Non-story material** (galleries, text pages, introductions) is a segment type you can add in the breakdown. It is numbered like everything else, shown by default, and can be hidden with a toggle. It can have credits but never counts in the Overview.
- **Expand all / Collapse all** buttons.
- Everything here follows the originals: if you change an original story or its issue, this page updates.
- Only straightforward 1:1 reprints are handled; unusual cases come later.

Check it yourself
- Build a collection from two issues' stories: the list shows 1, 2 in the order you entered them.
- Expand a story: creators, editors and characters appear.
- Change a credit on the original issue: the collection updates.
- Add a "gallery" non-story item: it gets a number, appears by default, hides with the toggle, and does not change "# stories".

---

## Stage 7 — Bulk tools, printed series name, Diary

**Prompt:** "Do Stage 7 only."

What it does
- **Select mode** on the series page: checkboxes (plus "select all"); a bar offers *Mark Read / Own / Wish*, *Set printed series name*, and *Delete* (with confirmation). Delete follows the Stage 4b rule: an issue reprinted in a collected edition cannot be deleted, and the message names the collections (confirmed by Jorge 2026-10-09).
- **Printed series name (DRAFT, to be built; Jorge reserves judgment):** an issue can show a different series-name piece than its series (e.g. issues 46–84 of one series printed as "Star Wars: Republic"). Settable per issue and, in bulk, for selected issues. Search and the series page still treat it as one series.
- **Diary page upgrades:** sort options (newest or oldest first, by series) on the basic Diary from Stage 4. No ratings, notes, tags or likes (maybe-list).

Check it yourself
- Select five issues and set a printed series name: their titles change, the series stays one series.
- Log an issue; open the Diary: it's there.

---

## Stage 8 — Clean slate, then real entry

1. Back up (Stage 1 command).
2. **B#17:** reset the database to empty and remove the test cover files (`git rm` them).
3. Enter your first real series by hand, end to end, following `docs/Holocron-Data-Entry-Guide.md`.
4. Tell the planning chat what felt slow, confusing or wrong. That feeds the next design round.

Suggested but not decided: ask Claude Code to add one small automatic check per stage (does each page load without an error) so a later change can't quietly break an earlier one. Jorge decides.

---

# Appendix A — Decision register (the PRD update note)

| # | Decision | Status | Suggested PRD section |
|---|---|---|---|
| 1 | Holocron is a complete catalogue with a personal layer on top; comics are the current build scope; spreadsheet import is out of scope | DECIDED | §1.1 |
| 2 | Read / Own / Wish are independent marks on products only (never on stories); Read can be set without logging; applies across pillars | DECIDED | §4.6 |
| 3 | Log pop-up has date + "I've read this before" only; creates a Diary entry; auto-ticks Read; deleting entries never unticks Read. Notes, tags, rating, like, review go to the maybe-list | DECIDED | §4.6 |
| 4 | Marks and log entries live in one flexible list that can point at any product | DRAFT | §5 |
| 5 | Volume: optional whole-number box on the series, blank = no tag, shown "Vol. N" next to publisher and years | DECIDED | §3.2.2 |
| 6 | Collected editions are a section on the same series page; "Collection" series type stays | DECIDED | §3.2.3 |
| 7 | Series form order and fields as in Stage 3a; publisher/imprint dropdowns with "+ Add new", imprint filtered by publisher, saved on Create; Series Notes = Archivist Note saved per edit and shown only in Edit history; years typed (auto-years later) | DECIDED | §3.2.2, §2.9 |
| 8 | Series age rating is a suggestion; new issues preselect it but can change it | DECIDED | §3.2.2, §3.2.4 |
| 9 | One flexible credits list for all media | DRAFT | §5, §2.4 |
| 10 | Credit attributes: Uncredited, As… (alias from the person's saved names; greyed out if Uncredited), Note (free text, always travels with the story, edited manually). Display order: headshot → role → name → attributes | DECIDED | §3.2.8, §2.7 |
| 11 | Duplicate issue (same series + number + type) is blocked with a link to the existing one | DECIDED | §3.2.4 |
| 12 | Issue View layout (Stage 4), Edit ▾ menu (Edit, Add new variant cover [inactive], Edit history), Delete at end of the form, Product Credits groups, Contents blocks, Reprints box, cascade of source edits to collections | DECIDED (including the delete-blocking rule, temporary Diary link, plain-text names and silhouette headshots, confirmed 2026-10-09) | §3.2.x (new Issue View subsection) |
| 13 | Series page layout, stats row (Read/Own only), Creators/Cover/Editors/Characters tabs with the counting rules in Stage 5, sections, slim toolbar (Sort, Filter, Select, Search; no grid/list), series-type line | DECIDED (layout); DRAFT (top-8-by-count ranking; Main/Supporting-only character counts) | §3.2.3 |
| 14 | Hybrid cover icons (state dots always, icon bar on hover) | DRAFT (Jorge may change) | §3.2.3 |
| 15 | Collected-edition page: Overview row (Creators/Editors/Characters, story-type segments only, small counts), numbered story list in book order, non-story segments numbered and hideable, Expand/Collapse all | DECIDED | §3.2.x |
| 16 | Printed series name (per-issue override, bulk set) | DRAFT (to be built; Jorge reserves judgment) | §3.2.2 |
| 17 | Publisher/imprint/creator registry with pages and duplicate-merge is a long-term goal; forms use simple pick-or-add until then | DRAFT / TBD | §4.2–4.3, §8 |

# Appendix B — Pinned (not for this build)

- Issue-list popup design (from the creators/characters numbers).
- Icons for Continuity, Era and Wish.
- Look of the Read/Own stats; progress display.
- Sidebar filters and sorting (LOCG-style), filters by creator or character.
- Smarter ranking for the Featured strip; manual pins.
- Maybe-list for the Log: notes/review, tags, rating, like.
- Ratings, "currently reading", dedicated Read / Own / Wish list pages, Diary filters.
- Stats counting rules (LOCG-style: unique vs all, by story / format, persona vs individual).
- Variants and multiple editions; whole-issue reprints area; footer/bottom area; "Duplicate as new issue".
- American-edition tag for internationally-first releases.
- Years filled in automatically from issue dates.
- Better handling of products spanning several eras.
- Publisher/imprint/creator registry, merge tool, alias tools (settings topic); how other pillars (film, TV, books, games) present publishers and credits, since their lists will be longer.
- Unusual reprint cases beyond 1:1.
- Full design of Edit history and its mechanics (the simple old → new list is the first version).
- Design of the Import feature and of the issue and collected-edition forms (to be brainstormed before Stages 3b, 3c, 4b and 6).
- Creator and character pages (Sprint 4); until then names are not links.
- Headshot photo upload for creators and characters (everything is a silhouette for now).
- Pages to browse your Read / Own / Wish lists (marks show only on issue and series pages until then).
- Final navigation design (the Diary link in the top bar is temporary).
- Backups and syncing: the database lives inside OneDrive; revisit where the live database file should be kept.
- Browse/sort sidebar and home page, Calendar and Dashboard, settings and maintenance tools, URL scheme/slugs, cover thumbnails, search speed, tests, announced releases, definition of MVP.
