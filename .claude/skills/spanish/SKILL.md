---
name: spanish
description: Grow the Spanish deck by translating a list of bullets into cards. Use when the user invokes /spanish, pastes a "FLASHCARDS" list, or hands over words/phrases they want to learn in Spanish.
---

# spanish

Draft English→Spanish cards from his list, wait for his approval, then append them to the
bottom of `data/spanish.txt`.

Two turns, no ceremony: **draft → he approves or edits → write.** No preamble, no plan.

## Input is always a list

`/spanish` takes bullets — pasted from Google Keep (sometimes headed `FLASHCARDS`), or his
notes from watching a vlog. There is no other mode. If the message has no list, ask for one
in a single line; do not invent cards, and do not go looking for a source to pull from.

Bullets are unstructured — English only, Spanish only, a pair he already wrote, or a
half-heard fragment from a video. Normalize each into **English on top, Spanish below**:

| Bullet form | What to do |
|---|---|
| English only — `Shark` | Translate to Spanish |
| Spanish only — `Todos los demás` | Write the English prompt for it, fix spelling/accents |
| A pair — `aqui entrenos - between you and me` | **His pair wins.** Only reorder to English-first and fix accents. Do not "improve" the translation. |
| A fragment from a video — `buen condition fisica` | These are notes, not cards. Turn each into the phrase or short sentence he'd actually say (`Más te vale venir en buena condición física`). If a transcript is in `transcripts/`, read the line in context first — notes are often misspelled or misheard. |

**One bullet = one card.** Never expand a bullet into several related cards. Never merge two.
The one exception is a note that is plainly two notes run together (`bien tipico mal humor`)
— split it and say so in the note column.

## Write for the mouth, not the eye

The deck exists so he can *say* these, fast, in a real conversation. That shapes the
Spanish side:

- **CDMX usage over neutral-textbook or Spain forms.** `carro` not `coche`, `depa` not
  `apartamento`, `chido` not `guay`.
- **Flag every regionalism that isn't Mexican, and give the Mexican form.** Vlogs are often
  Venezuelan, Colombian, Argentine or Spanish: `nevera` → `refri`, `ya va` → `aguanta`,
  `-ico` diminutives → `-ito`, `¿cómo me le va?` → `¿cómo le va?`. Anything that is harmless
  elsewhere but crude in Mexico (`coger`) gets a loud warning.
- **Mild slang only.** Prefer the Mexican word a fiancée's family uses at dinner over the one
  that would make them wince. Note when a phrase has a second meaning in Mexico
  (`te prende`).
- **Mark narrator register.** Words a vlogger reads to camera but nobody says in
  conversation (`cuya`, `condecoró`) — say so and suggest dropping them.
- **`tú` by default.** Infer `usted` only from clear context; it's rare.
- **The register he'd actually use** — casual, contracted, spoken. `Ahorita voy` beats
  `Voy a ir en este momento`.
- **Keep the English prompt specific enough to cue one answer.** A vague prompt trains
  nothing, because any of five phrases would satisfy it.

## Ambiguous bullets — ask in the draft

If a bullet cannot become one card without guessing — a reference you can't resolve, a
fragment that isn't in the transcript, a word whose meaning depends on context you don't
have — leave it out of the table and ask about it below the table, all in one batch.

A merely *ambiguous translation* (two valid CDMX words for one thing) is not a question —
draft your best pick and note the alternative.

## Turn 1 — the draft

**Check for duplicates first** against the whole of `data/spanish.txt`, accent- and
case-insensitively, on the Spanish side. A bullet that's already a card is dropped from the
table and listed under it.

Print one numbered table — **# | English prompt | Spanish | Note** — and stop. The note column
is for the interesting exceptions only: a Mexican swap (mark it 🇲🇽), a regionalism, a
second meaning, a narrator-register word, a misheard caption. Most rows have no note.
Under the table: dropped duplicates in one line, then the batched questions. **Write nothing
to the file in this turn.**

## Turn 2 — write what he approved

He answers with approvals, edits, drops, or "however you recommend". Apply exactly that —
where he defers, take the suggestions the notes made (drop what you flagged as droppable).
Then write.

## Writing to the file

Only ever `data/spanish.txt`. The other decks in `data/` are not grown by this skill.

1. **Append at the bottom of the file only.** He works through the deck in order and wants
   new cards to queue up behind the ones already there. Keep the batch in the order he gave
   it. Never insert mid-file, never reorder existing cards, never rewrite an existing card
   unless he asks (changing a card's text resets its progress).
2. **Always an even number of lines.** Blank line between cards, blank line after the last
   card.
3. **LF line endings, UTF-8.** Match the existing file (`.gitattributes` pins LF).
4. **Never touch `data/decks/*.json`.** Auto-managed and gitignored.

Rules 1 and 2 are not style — `parser.py` pairs consecutive non-empty lines from the top of
the file and hashes `term|definition` for the card ID. An odd-line insertion mid-file
re-pairs every card after it, changes every ID, and silently wipes review progress for the
whole deck. After writing, parse the file and confirm the count rose by exactly the number
of cards written.

Then one line: how many were added, and the new card count.

Do not commit, and do not offer to. He commits when he wants to. If he asks for a commit,
**commit and push to the remote in the same step.**
