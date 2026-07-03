# Cleanup checklist

Work through each item below. Check off when decided (keep, archive, delete, or merge elsewhere).

**Core app** (not on this list): `main.py`, `parser.py`, `flashcard.py`, `spaced_repetition.py`, `storage.py`, `test_algorithm.py`, `data/*.txt` deck sources, `README.md`, `.gitignore`.

---

## Root — scratch & queue files

Not loaded by the app (`parser.py` only reads `data/*.txt`). Likely candidates to merge into decks or archive.

| Status | Path | Notes |
|--------|------|-------|
| [ ] | `mexican_stuff.txt` | ~154 lines — Mexican food notes, mixed EN/ES |
| [ ] | `more_spanish_phrases.txt` | ~108 lines — phrase ideas, mixed EN/ES |
| [ ] | `stories_and_other.txt` | ~235 lines — personal story prompts |

---

## Root — reference dumps (`Z_*`)

Large offline word/phrase lists. Never parsed by the app.

| Status | Path | Notes |
|--------|------|-------|
| [ ] | `Z_SPANISH.txt` | ~4,274 lines |
| [ ] | `Z_ENGLISH.txt` | ~658 lines |
| [ ] | `Z_spanish2000.txt` | ~2,932 lines |
| [ ] | `Z_spanish_phrases1000.txt` | ~1,620 lines |
| [ ] | `Z_oscar_cuenca.txt` | ~96 lines |

---

## Root — helper data (not a deck)

| Status | Path | Notes |
|--------|------|-------|
| [ ] | `verbs.csv` | ~76 lemmas — reference list for building `data/verbs.txt` blocks |

---

## Root — media & archives

| Status | Path | Notes |
|--------|------|-------|
| [ ] | `IMG_2943.JPG` | Photo |
| [ ] | `IMG_3402.png` | Photo |
| [ ] | `IMG_3884.PNG` | Photo |
| [ ] | `Screenshot 2026-06-15 131011.png` | Screenshot |
| [ ] | `Screenshot 2026-06-15 131016.png` | Screenshot |
| [ ] | `Screenshot 2026-06-15 131019.png` | Screenshot |
| [ ] | `Screenshot 2026-06-15 131021.png` | Screenshot |
| [ ] | `Screenshot 2026-06-15 131023.png` | Screenshot |
| [ ] | `Photos-3-001.zip` | Photo archive |
| [ ] | `Photos-3-001 (1)/` | Extracted photos (12 files) |
| [ ] | `spicy-and-albures.zip` | Archive |
| [ ] | `Propuesta de Plan de Pruebas e Inspección Aisladores 3AP1 FG 1S (Sarah García).pdf` | PDF (unrelated to app) |

---

## Root — folders

| Status | Path | Notes |
|--------|------|-------|
| [ ] | `Z_SpanishVocab/` | 37 screenshot PNGs — source material for vocab extraction |
| [ ] | `.cursor/` | Cursor agent skills (`init`, `spanish`, `english`) |
| [ ] | `__pycache__/` | Python bytecode — safe to delete anytime |

---

## `data/` — deck files to review

These **are** loaded by the app, but many are legacy, empty, or redundant with the simplified workflow. Decide per deck: keep active, archive, or remove.

| Status | Deck | Lines | Cards (JSON) | Notes |
|--------|------|-------|--------------|-------|
| [ ] | `spanish_vocab.txt` | ~5,660 | ~2,823 | **Main long vocab list** — keep content, revisit presentation |
| [ ] | `verbs.txt` | ~758 | ~379 | Grammar/conjugation deck |
| [ ] | `english_vocab.txt` | ~288 | ~144 | English mirror deck |
| [ ] | `english_jokes.txt` | ~126 | ~63 | |
| [ ] | `DOP.txt` | ~112 | ~56 | Direct/indirect object pronouns |
| [ ] | `nicknames.txt` | ~50 | ~25 | |
| [ ] | `F1.txt` | ~20 | ~10 | |
| [ ] | `bye.txt` | ~20 | ~10 | |
| [ ] | `long_phrases.txt` | ~10 | ~5 | |
| [ ] | `lawsofpower.txt` | ~4 | ~2 | |
| [ ] | `spanish_flirting.txt` | ~2 | ~1 | |
| [ ] | `english_flirting.txt` | 0 | 0 | Empty — still shows in deck menu |
| [ ] | `english_idioms.txt` | 0 | 0 | Empty |
| [ ] | `english_insults.txt` | 0 | 0 | Empty |
| [ ] | `english_stories.txt` | 0 | 0 | Empty |
| [ ] | `spanish_idioms.txt` | 0 | 0 | Empty |
| [ ] | `spanish_insults.txt` | 0 | 0 | Empty |
| [ ] | `spanish_jokes.txt` | 0 | 0 | Empty |
| [ ] | `spanish_stories.txt` | 0 | 0 | Empty — intended active deck on remote |

---

## `data/decks/` — orphans & generated state

JSON is **auto-generated** from `data/*.txt` on startup (gitignored). Review progress is stored here locally.

| Status | Path | Notes |
|--------|------|-------|
| [x] | `data/decks/spanish_phrases.json` | **Orphan** — archived 74 phrases to `Z_spanish_phrases1000.txt`; JSON removed |
| [ ] | `data/decks/*.json` (all others) | Local review progress — don't delete unless resetting a deck |

---

## Git / remote

| Status | Item | Notes |
|--------|------|-------|
| [x] | GitHub repo renamed | `Memory-And-Recall-Flashcards` → `MemoryFlashcards` |
| [ ] | Local branch vs `origin/master` | Local is **7 commits behind** remote (remote has simplified deck structure) |
| [ ] | Deleted in working tree | `spanish_foods.txt` (was tracked, now deleted locally) |

---

## Remote-only files (not in local checkout)

Present on `origin/master` if you pull — decide whether to adopt.

| Status | Path | Notes |
|--------|------|-------|
| [ ] | `PhrasesQueue.txt` | Scratch queue for phrases |
| [ ] | `StoriesQueue.txt` | Scratch queue for stories |
| [ ] | `data/spanish_phrases.txt` | ~200 lines — simplified active deck |
| [ ] | `.cursor/skills/translate/SKILL.md` | Replaces separate spanish/english skills on remote |
| [ ] | `LatinArtists.txt` | Reference list |
