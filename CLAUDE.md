# MemoryFlashcards

Personal **Spanish flashcard CLI**. Python 3.11+, stdlib only.

Run: `python main.py` → pick a deck → English prompt → reveal Spanish → rate 1–4.

## Why this repo exists

Chase is 23, is engaged to a Mexican woman, and has a lopsided problem: he **understands** spoken
native Spanish at roughly 85%, and can barely **produce** a sentence. Years of classroom
Spanish trained recognition — multiple choice, fill in the blank, translate this line — and
every one of those gives you the answer's shape in advance. Listening does the same: the
sound arrives and the brain only has to match it. Speaking gives you none of that. You start
from nothing and have to build the word, the gender, the conjugation and the word order in
about half a second.

So the goal of this repo is narrow and specific: **sound fluent in everyday Mexico City
conversation** with his fiancée, her family, and their friends. Not pass a test. Not read
a novel. Not name animals.

Three consequences that should drive every decision here:

- **Every card is a production drill.** The prompt is the cue, the answer is what has to come
  out of his mouth. A card he silently recognizes and flips past has trained the one skill he
  already has too much of. Cards are meant to be *said out loud*.
- **Personal beats generic, always.** A phrase he wished he could say yesterday is worth more
  than fifty words off a vocabulary list, because fluent speech is mostly prefabricated
  chunks and the useful chunks are the ones his own life keeps demanding.
- **Small beats complete.** This is a tool, not a place to live. It should stay something he
  can read, edit, and finish in thirty minutes a day.

There is deliberately no staging area and no parked-deck folder. The one exception is
`spanish-deck-reserve.txt` in the root: the 4,279 cards of the old 8,294-card bulk deck that did
**not** make the cut on 2026-10-04. It is for browsing, one card per line (`English = Spanish`),
and the app never reads it. Do not import from it in bulk; see **Decks**.

## The daily loop

Chase keeps a running list of words and phrases in Google Keep during the day, then pastes it
into Claude Code and runs `/spanish`. The skill translates each bullet and adds it to the
top of `data/spanish.txt`. Claude's whole job is that insert. Review happens in the CLI, not here.

`/spanish` only ever works from a list. There is no mode that invents cards or pulls them
from a source file — that mode existed, and removing it was the point.

The loop only fills up if he is **attempting to speak**. The Keep list is downstream of the
speaking habit, not a substitute for it.

A launchd agent nudges him at **20:30 every night** and, on a click, opens Ghostty with the
deck already running — see `scripts/reminder/README.md`. It exists because the review habit is
the part that actually decays, not the card supply.

## Storage

| What | Where | Editable? |
|------|-------|-----------|
| Card content | `data/*.txt` — term + definition pairs, blank line between cards | ✅ yes |
| Progress state | `data/decks/*.json` — auto-managed, gitignored | ❌ **never edit by hand** |

**Sync on startup:** preserves progress for matching ids, adds new cards from txt,
removes deleted cards.

## Architecture

| File | Role |
|------|------|
| `main.py` | Entry point, deck menu, review session |
| `parser.py` | Parses `data/*.txt` → flashcards |
| `flashcard.py` | Card model |
| `spaced_repetition.py` | Session-based SRS, queue prioritization |
| `storage.py` | JSON load/save, sync txt ↔ json on startup |
| `progress.py` | Home-screen bars (new / learning / solid at 21+ days), day streak from `data/decks/history.json` |
| `test_algorithm.py` | SRS logic tests |
| `.claude/skills/spanish/` | The `/spanish` skill — bullets → cards |
| `.claude/skills/english/` | The `/english` skill — words → definition-prompt cards |
| `scripts/reminder/` | launchd agent: 20:30 nightly nudge → opens the deck. See its README. |

## Decks

All decks live flat in `data/`. There is no parking lot and no archive.

| Deck | Cards | Direction | Grown by |
|------|-------|-----------|----------|
| `spanish.txt` | 4,000 | English prompt → Spanish answer | `/spanish` adds his daily bullets at the top. Rebuilt 2026-10-04 from the old personal deck (67), `core.txt` (400, merged in and deleted), 81 new basics (colors, numbers, family, core verbs…), and the best of the old 8,294-card bulk deck by word frequency. Basics sit at the top so they arrive first. |
| `mexican.txt` | 386 | English prompt → Spanish answer | Fixed. CDMX slang, flirting, and food/culture terms. |
| `verbs.txt` | 370 | English prompt → Spanish answer | Hand-maintained. Grammar-construction sentences. |
| `english.txt` | 102 | **Definition prompt → word answer** | `/english` — his word bullets. Vocabulary recall, unrelated to Spanish. |
| `slang.txt` | 111 | **Definition prompt → word answer** | Fixed. Gen Z / teen slang from a WeAreTeachers list, one-time import. |

`english.txt` runs the opposite direction on purpose: Spanish trains *producing the phrase*
from an English cue, English trains *recalling the word* from its meaning, so the definition
is on top and the word is the answer. `/english` grows it the same way `/spanish` grows the
Spanish deck — he pastes words, the skill writes the definition prompt for each one.

`mexican.txt` folds in what used to be three files. Its food and culture cards were
originally written Spanish-on-top as a glossary and were **flipped** during the merge, so the
English description is the prompt and the Spanish term is the answer — same production
direction as every other Spanish deck.

**New cards are capped at 20 per deck per day** (`NEW_CARDS_PER_DAY` in
`spaced_repetition.py`, added 2026-10-04). A never-rated card waits until a slot opens; the
first rating stamps `introduced` with the date, and that date is what the cap counts. New cards
enter in deck-file order, so the top of a `.txt` file is what arrives next. Due reviews are
never capped. Before the cap, every new card was due at once — dropping 500 cards into a deck
made a 500-card session, and that is what killed the previous deck. `/spanish` inserts at the
top so his own phrases jump the line. Moving a card within the file does not reset its
progress — only editing its text does.

## Review algorithm

Session-based (**not** Anki SM-2). Cards must reach rating **4** to complete a session.

Ratings: 1=Hard, 2=Medium-Hard, 3=Medium, 4=Easy

- Progress **1 → 2 → 3 → 4** within a session (can drop back to 1)
- **First rating** drives long-term scheduling when you hit 4
- Re-insertion: 1 → positions 2–5; 2 → 10–25 ahead; 3 → 20–40 ahead; 4 → done
- All due review cards appear in session; never-seen cards are capped at 20 per deck per day

## Content philosophy

- **Context over grammar** — phrases and stories, not rule drills
- **Personal over generic** — real people, family, Mexico trips, real stories
- **Mexico City Spanish** — prefer CDMX usage over neutral-textbook or Spain forms
- **`tú` by default** — infer `usted` only from clear context; it's rare
- **Minimal by design** — plain txt decks you can read and edit without being overwhelmed
- **Prefer a habit to a feature.** When something could be fixed either by changing how he
  uses the tool or by adding code, lead with the habit. The learning happens out loud in his
  life, not in the app.

## Conventions

- **Extend content at the tail** of `data/*.txt`. Do not rewrite existing cards unless asked.
- macOS, zsh, BSD userland. Chain with `&&`; `sed -i` needs an explicit argument (`sed -i ''`).
- Commit only when explicitly asked — and a yes to the commit offer means **commit and push**
  in the same step.

## Do not

- Edit `data/decks/*.json` by hand
- **Insert or reorder cards mid-file.** `parser.py` pairs consecutive non-empty lines from
  the top and hashes `term|definition` for the card ID. An odd-line insertion re-pairs every
  card below it, changes every ID, and silently wipes review progress for the whole deck.
  Append at the tail, always in even line counts.
- Bulk-rewrite register (tú/usted) on old cards without being asked
- Bulk-import vocabulary lists, or rebuild an archive to pull cards from
