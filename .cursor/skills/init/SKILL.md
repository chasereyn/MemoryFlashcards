---
name: init
description: Onboards agents to the MemoryFlashcards repo — personal Spanish flashcard CLI, TSV storage, architecture, decks, review algorithm, and content philosophy. Use when the user runs /init or asks to get up to speed on this project.
disable-model-invocation: true
---

# MemoryFlashcards — Project Init

When invoked, treat this skill as your baseline context for this repo. Do **not** re-explore from scratch unless the user asks or you need fresh file contents. Confirm you are oriented, then wait for the user's task.

## What this repo is

**MemoryFlashcards** is a **personal Spanish flashcard CLI** — not a generic language app.

- **Content:** TSV files in `data/decks/` (one card per line: `term\tdefinition`)
- **Progress:** TSV files in `data/progress/` (review metadata, gitignored — user does not edit)
- **Stack:** Python 3.11+, stdlib only, no dependencies

Run: `python main.py` → pick a deck → English prompt → reveal Spanish → rate 1–4.

See `STORAGE.md` for file format and sync behavior.

## Philosophy (owner intent)

- **Context over grammar** — whole phrases/stories, not rule drills.
- **Personal over generic** — Sarah, family, Mexico trips, real stories they'll tell.
- **Mexican Spanish** — natural MX choices, neutral register, light touch (no heavy slang).
- **Daily habit over marathons** — 25 cards/day cap on large decks; show up every day.
- **Keep the long vocab list** — `spanish.tsv` is the big cob deck (~8000 cards); presentation may evolve, but the content stays.

Root scratch files (`Z_SpanishVocab/`) are **not** loaded by the app — reference/queue material only. (`Z_SPANISH.txt` and `Z_ENGLISH.txt` were merged into decks and deleted.)

## People & themes

- **Sarah** — girlfriend, Mexico City; **tú** for phrases to her.
- **Her parents (especially mom)** — in-laws in Mexico; **usted** for questions to/about them.
- **Themes:** family, CDMX/Sinaloa trips, food, feelings, couple life, work stories.

## Architecture

| File | Role |
|------|------|
| `main.py` | Entry point, deck menu, review session, rating UI, in-session re-insertion |
| `parser.py` | Parses `data/decks/*.tsv` → flashcards (MD5 id from `term\|definition`) |
| `flashcard.py` | Card model + serialization helpers |
| `spaced_repetition.py` | Session-based SRS, daily limit, queue prioritization |
| `storage.py` | Load/save progress TSV, sync content ↔ progress on startup |
| `test_algorithm.py` | SRS logic tests |
| `test_sync.py` | Sync tests (critical — run after storage changes) |

**Sync** (`storage.sync_all_decks` on startup): preserve progress for matching ids, add new cards from deck TSV, remove deleted cards.

## Active decks (`data/decks/`)

| Deck | ~Cards | Notes |
|------|--------|-------|
| `spanish.tsv` | 8250+ | Main vocab cob list — one English prompt, one Spanish answer per line |
| `verbs.tsv` | 370 | Grammar/conjugation — construction-first example sentences |
| `english.tsv` | 375+ | English vocabulary — minimal-swap paired sentences (see `english` skill) |
| `DOP.tsv` | 56 | Direct/indirect object pronouns |
| `numbers.tsv` | 100 | Spanish numbers 1–100 (digit → Spanish) |
| `jokes.tsv` | 195+ | English jokes |
| `flirt.tsv` | 60 | Pick-up lines, pet names, couple talk |
| `chistes.tsv` | 40 | Spanish wordplay jokes |
| `longphrases.tsv` | 5 | |
| `lawsofpower.tsv` | 48 | The 48 Laws of Power (number → law) |
| `mexican.tsv` | 158 | Mexican food, culture, traditions, geography, history, brands (English descriptions — not phrase deck) |

Only `data/decks/*.tsv` become decks. Progress mirrors deck names in `data/progress/`.

## Card format (default deck)

```
term	definition
Roof	Tejado
I'm joking	estoy bromeando
```

Header row `term\tdefinition` is optional. Append new rows at the **tail** only unless asked otherwise.

## Review algorithm

Session-based (not Anki SM-2). Cards must **finish the session** (reach rating 4) before long-term scheduling applies.

**Ratings:** 1=Hard, 2=Medium-Hard, 3=Medium, 4=Easy (session complete).

**Session rules:**
- Progress **1 → 2 → 3 → 4** within a session (can drop back to 1).
- Ratings **1–3** keep the card in session; only **4** completes it for today.
- **First rating** drives long-term metadata when you hit 4 — not the last rating.
- Re-insertion (fixed distances, not % of deck):
  - **1:** random position 2–5 ahead
  - **2:** 10–25 cards ahead
  - **3:** 20–40 cards ahead
  - **4:** done; exponential backoff on consecutive easy sessions

**Daily limit:** `DEFAULT_DAILY_LIMIT = 25` in `spaced_repetition.py`. Max **25 new due cards** introduced per deck per day (fixed pool; no refill when one completes). Active in-session cards always included. Reinsertions from 1–3 do not consume extra slots.

**Queue order:** active session (struggling first) → **shuffled due cards** (daily cap 25).

**Deck menu:** shows `Today: N` and `Total: N`. Set `SHOW_BACKLOG_IN_MENU = True` in `main.py` to also show overdue backlog count.

## How to help

- **Extend content** at the **tail** of deck TSV files — do not rewrite existing cards unless asked.
- **Spanish vocab:** use the `spanish` skill for `data/decks/spanish.tsv`.
- **English vocab:** use the `english` skill for `data/decks/english.tsv`.
- **Mexican culture deck:** use the `mexican` skill for `data/decks/mexican.tsv`.
- **Code:** match existing style; minimal diffs; no over-engineering.
- **Windows:** PowerShell — chain with `;`, not `&&`.
- **Git:** commit only when explicitly asked.

## Do not

- Edit files in `data/progress/` by hand.
- Re-add removed bloat decks without being asked.
- Bulk-rewrite register (tú/usted) on old cards without being asked.

## Related skills

| Skill | When |
|-------|------|
| `spanish` | Appending/formatting `data/decks/spanish.tsv` |
| `english` | Appending/formatting `data/decks/english.tsv` |
| `mexican` | Appending/formatting `data/decks/mexican.tsv` |
| `init` | This file — project orientation |

## After /init

Reply briefly that you understand MemoryFlashcards and are ready. Mention: TSV decks in `data/decks/`, progress in `data/progress/`, session SRS with 25/day cap, and tail-only edits. Ask what they want to work on.
