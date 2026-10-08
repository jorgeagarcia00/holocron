# Holocron — Data Entry Guide
**For:** Jorge  
**Status:** First draft (PRD TBD #21). Grows as decisions are made. Not yet exhaustive.  
**Last updated:** October 8, 2026

Rules for entering data consistently. Where a rule is already in the PRD it is repeated here in plain form. Rules marked *(coming)* describe how the app will behave once the queued fixes are built — until then, follow the rule by hand.

## Golden rules
- **Defer to the publisher.** Enter what the official publisher printed. Your opinions go in Personal Notes. If the publisher made a known misprint, enter the correct value and explain why in the Archivist Note.
- **Standard role names beat literal ones.** Enter "Colorist", not "Color Artist" or "Colors by".
- **Pick from the autocomplete whenever a match appears.** Typing a new name creates a new record. If you type "Dark Horse" when "Dark Horse Comics" already exists, you get two publishers.
- **American releases first.** International editions are added only by exception.

## Series
- **Series Type** decides which issue types are allowed:
  - Regular Series → Regular Issue, Annual, One-Shot, Collected Edition
  - One-Shot → a single One-Shot issue only
  - Collection → Collected Editions only
  - Graphic Novel → Graphic Novels only (any number of them)
- **Continuity:** Canon, Legends, or Both. *Both* means the story is valid in both continuities (like the Lucas films) — it does not mean "mixed". One record covers both.
- **Era:** Canon → one Canon era. Legends → one Legends era. Both → one of each. Pick "Multiple Eras" if the series spans several.

## Issues
- **Issue # (Regular Issues only):** type the number only — `1`, not `#1`. The screen adds the `#`.
- **Title box (Annual, One-Shot, Collected Edition, Graphic Novel):** type the title or label only.
  - Leave it **blank** if the book has no subtitle. The app shows "Series Title TPB" or "Series Title HC" using the Format dropdown.
  - Never type "TP", "TPB" or "HC" in the title — Format supplies that.
  - A One-Shot with the same name as its series: leave the title blank.
- **Format:** Collection and Graphic Novel series cannot use "Comic".
- **Dates:** type the release date as numbers, mm/dd/yyyy. The site shows it as "Oct 3, 2026". **Cover date** is month and year only; it displays as "Dec 2026".
- **Order on the Series Hub:** by release date; issue number breaks ties.

## Credits
- **Product Credits** are about the physical book: cover artist, editor-in-chief, collection editor, Lucasfilm staff. They never travel with an imported story.
- **Story credits** are about the story: writer, penciler, inker, colorist, letterer, story editors. They live on the segment and travel when the segment is imported.
- Every credit row needs **both a creator and a role**. *(coming: an incomplete row will stop the save with an error. Until then incomplete rows are silently skipped.)*
- One person with two roles = two rows.
- Collected editions follow the same rules as any other issue — add whatever story and credits that edition really has.
- **Page notes / descriptive notes on a credit** (such as "pages 1, 5" or "framing sequence") are planned as an optional free-text note. *(coming — design pending)*

## Characters
- Pick the character from the autocomplete. Choosing a persona (e.g. Darth Vader) fills in the baseline character too.
- **Appearance type defaults to Main.** Change it for Supporting, Cameo or Vision when that's what the character is:
  - Main — heavy speaking role, pivotal to the story
  - Supporting — present and interactive, not the focus
  - Cameo — brief appearance, minimal interaction
  - Vision — Force ghost, flashback, dream, illusion, clone, or construct
- A character created on the spot inherits the issue's continuity. *(coming; until then it's saved as "Both" — correct it by hand.)*

## Notes
- **Archivist Note** *(coming)*: an optional box at the end of a form. Use it when you correct a publisher error or want to record why something is entered a certain way. It is saved with the log entry.

## Open rule questions (to settle in design sessions)
Outlier entries (retitled series, collections with non-standard names), aliases and pen names, uncredited work, an "American edition of an international-first release" tag.
