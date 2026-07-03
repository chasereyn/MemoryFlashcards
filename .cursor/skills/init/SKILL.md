---
name: init
description: Onboards agents to the MemoryFlashcards repo — personal Spanish flashcard system, architecture, content philosophy, decks, queues, and review algorithm. Use when the user runs /init or asks to get up to speed on this project.
disable-model-invocation: true
---

# MemoryFlashcards — Project Init

When invoked, treat this skill as your baseline context for this repo. Do **not** re-explore from scratch unless the user asks or you need fresh file contents. Confirm you are oriented, then wait for the user's task.

## What this repo is

**MemoryFlashcards** is a **personal Spanish flashcard CLI** — not a generic language app. TSV files in `data/decks/` are the source of truth for card content; `data/progress/` stores review progress. Python 3.11+, **stdlib only**, no dependencies.

Run: `python main.py` → pick a deck → review (English prompt → reveal Spanish → rate 1–4).

## Philosophy (owner intent)

Read `README.md` for full detail. Core rules:

- **Context over grammar** — memorize whole phrases/stories, not rules.
- **Essentials over volume** — daily phrases they'll actually say, not vocab hoarding.
- **Personal over generic** — stories about the owner's life, Sarah, family, Mexico trips — things they'll really tell people.
- **Mexican Spanish** — light touch, natural MX choices, neutral register, no heavy slang.
- **Thin decks** — ~10–20 active cards per deck; quality beats quantity.

**Daily rhythm:** 5–10 phrases + 1 personal story. Scratch in queue files, merge into decks when translated.

## People & themes

- **Sarah** — girlfriend, Mexico City; **tú** for phrases to her.
- **Her parents (especially mom)** — in-laws in Mexico; **usted** for questions to/about them.
- **Themes:** family history, CDMX/Sinaloa trips, house visits, couple expectations, food, feelings, small talk, work/life stories.

For translation register and deck formatting rules, use the **`translate`** skill (`.cursor/skills/translate/SKILL.md`) — do not duplicate those rules here unless the task is translation.

## Architecture

| File | Role |
|------|------|
| `main.py` | Entry point, deck menu, review session, rating UI, in-session re-insertion |
| `parser.py` | Parses `data/*.txt` → flashcards (consecutive non-empty line pairs; MD5 id from `term\|definition`) |
| `flashcard.py` | Card model + JSON serialization |
| `spaced_repetition.py` | Session-based SRS (not Anki SM-2) |
| `storage.py` | Load/save JSON, sync text → JSON on startup |
| `test_algorithm.py` | Tests for SRS logic |

**Sync behavior** (`storage.sync_all_decks` on startup): preserve cards in both text + JSON (keeps progress), add new from text, remove deleted from text.

## Decks & content files

| Path | Purpose |
|------|---------|
| `data/spanish_phrases.txt` | Short phrases — **full English line** as prompt |
| `data/spanish_stories.txt` | Personal stories — **2–3 word trigger** as prompt, full Spanish paragraph as answer |
| `data/decks/spanish_phrases.json` | Review metadata for phrases |
| `data/decks/spanish_stories.json` | Review metadata for stories |
| `PhrasesQueue.txt` | Scratch — English phrase ideas awaiting translation |
| `StoriesQueue.txt` | Scratch — story ideas awaiting translation |

**Card format** (both decks):

```
English prompt
Spanish answer

Next English prompt
Next Spanish answer
```

Only `data/*.txt` files become decks. Root files like `LatinArtists.txt`, `spanish_foods.txt` are reference lists, not wired into the app.

## Review algorithm (session-based)

Unlike SM-2, cards must **finish the session** before long-term scheduling applies.

**Ratings:** 1=Hard, 2=Medium-Hard, 3=Medium, 4=Easy (session complete).

**Session rules:**
- Must progress **1 → 2 → 3 → 4** within a session (can drop back to 1; then climb again).
- Ratings **1–3** keep the card in session; only **4** removes it for today.
- **First rating** drives long-term metadata when you finally hit 4 — not the last rating.
- Re-insertion uses **fixed distances** (not % of deck size):
  - **1:** random position 2–5 ahead
  - **2:** 10–25 cards ahead
  - **3:** 20–40 cards ahead
  - **4:** done; exponential backoff on consecutive easy sessions

**Prioritization:** active session cards (struggling) first, then due cards by difficulty and age.

## How to help

- **Extend content** at the **tail** only — do not rewrite existing cards unless asked.
- **Translate** queue/deck orphans with `/translate` skill.
- **Code changes:** match existing style; minimal diffs; no over-engineering.
- **Windows:** PowerShell — chain with `;`, not `&&`.
- **Git:** commit only when explicitly asked.

## Do not

- Re-add deleted bloat (old english vocab decks, joke decks, technical word lists, endless single-word cards).
- Split into grammar exercises or vocab-count optimization.
- Bulk-rewrite register (tú/usted) on old cards without being asked.
- Add new deck types unless the user asks (README mentions optional future decks: flirting, insults, idioms — only after essentials are solid).

## Related skills

| Skill | When |
|-------|------|
| `translate` | Adding/translating phrase or story cards |
| `init` | This file — project orientation |

## After /init

Reply briefly that you understand MemoryFlashcards and are ready. Mention you know: personal Spanish decks, two active decks, queue → translate → merge workflow, session SRS, and tail-only edits. Ask what they want to work on.
