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

## The ladder

Where cards come from, and what "learned" means. Agreed 2026-10-17; this is the mindset to
bring into every session here.

> **A card is learned when it comes out of his mouth, unprompted, in a real conversation.**
> Rating it a 4 is not learned. The deck only keeps a phrase warm until that happens.

| Level | What he does | What it finds |
|---|---|---|
| 1 | Memorize vocab lists | Someone else's idea of what matters. **Retired** with the bulk deck, 2026-10-16. Do not go back. |
| 2 | Watch a Mexican vlog, note what he understood but would never have said, run `/spanish` on the notes | Gaps he didn't know he had — phrases he'd never heard of (*pásenlo bonito*, *-ito* on everything, *seamos sinceros*) |
| 2.5 | Rewatch a small **rewatch set** without captions; **shadow** — pause and repeat a line out loud, matching its rhythm | Parsing speed, and the mouth learning the music. Listening is already his strong side, so this is light and occasional |
| 2→3 | **Retell the vlog** — from his notes, tell it back out loud in Spanish for 3–5 minutes, record it, run `/hablar` | Gaps he hits while talking about something he just heard said well. Turns level 2 into level 3 without needing a partner on the phone |
| 3 | Harvest his own conversations — calls with Sarah, `/hablar` recordings ([SPEAKING.md](SPEAKING.md)) | Gaps he hit — what he reached for and couldn't say. The most valuable cards there are |
| 4 | Use a card on purpose — pick 2–3 recent ones before a call and say them for real | Nothing new. It closes the loop, and it is the definition of learned |

The levels don't replace each other. Level 2 tells him what natives say; level 3 tells him
what *he* needs to say. The best cards are where those meet — a vlog phrase that turns out to
be exactly what he needed a week later.

**Depth over breadth.** A phrase learned inside a scene he has watched many times comes with
its context, tone and rhythm, which a card can't carry. So vlogs come in two kinds:

- **New vlogs** — watched once, mined for notes, retold, done.
- **The rewatch set** — 3–5 Mexican vlogs he loves, rewatched over a few weeks: with
  captions, then without, then shadowing a stretch of each. Rotate one out when it stops
  teaching anything. The transcripts live in `transcripts/` (gitignored — never commit them;
  the repo is public).

**Pick vlogs by topic from his life** — family dinners, CDMX neighborhoods, weddings, markets,
road trips — so the vocabulary is the vocabulary he'll need. Mexican speakers first; anything
else gets its regionalisms flagged.

**Where the time goes.** Most of it talking with Sarah (levels 3–4). About one new vlog a week
(level 2, mined, then retold), plus the rewatch set. The deck is a short daily review that
serves all of it.

**Where this came from.** Mostly his own experience, sharpened 2026-10-17 by the Language
Lords video "How I Got Fluent In Spanish In 44 Days" (youtube.com/watch?v=z8FACVD9vz4). Taken
from it: depth over breadth (his "10 by 10" — the same few videos, many times), retelling a
video aloud from notes, shadowing, and topics from your own life. Left out on purpose: his
8-hour days, TED talks as a source (formal, not CDMX), memorizing verb lists, and dropping
flashcards — the deck stays as the cheap thing that keeps phrases warm.

**The capture habit.** One or two words per call, typed into Keep mid-call — even a single
English word is enough for `/spanish` to rebuild the phrase. That is a few hundred personal
cards in a few months.

**For agents:** before proposing anything, ask which level it serves, and prefer whatever
pushes toward 3 and 4. Never propose rebuilding level 1.

## The same ladder, in English

He is a native speaker who wants to **speak articulately** — fewer long pauses hunting for a
word, the precise word when it matters. Same problem as Spanish in a milder form: he
recognizes far more words than he produces. Agreed 2026-10-17, starting slowly.

**The model is Grant Sanderson (3Blue1Brown).** What makes him sound well-spoken is *not*
zero filler — he says "um" and "you know" and restarts sentences. It is:

1. **Signposting** — saying how he's thinking before he thinks it: *broadly speaking*, *on
   the flip side*, *bear with me here*, *to be clear*. These buy a second of thought and
   sound deliberate, not lost.
2. **Precise everyday words**, not SAT words — *disillusioned*, *watered down*,
   *conflate*, *hand-wavy*.
3. **Concrete stories** that carry an abstract point (he explains math teaching through
   King Midas).
4. **Light idioms**, used sparingly.

| Level | English version |
|---|---|
| 1 | Word lists. **Retired** — the old 102-card list was deleted 2026-10-17 and purged from git history |
| 2 | Mine speakers he admires — note the words and moves he understood but wouldn't have produced, run `/english` |
| 2.5 | Shadow them — read a paragraph of the transcript aloud at their pace |
| 2→3 | Retell a talk in his own words for 3 minutes, record it, run `/speak` |
| 3 | His own speech — recordings, meetings, explaining things at work — through `/speak` |
| 4 | Use a mined move on purpose in a real conversation this week |

`english.txt` holds two card types (rules in `.claude/skills/english/SKILL.md`): **word
cards** (definition → word) and **move cards** (the moment you'd say it → the phrase).

## No reserve

There is deliberately no staging area, no parked-deck folder, and no reserve file. Every card
lives in a deck under `data/`. The old 8,300-card bulk deck was deleted 2026-10-16 and purged
from git history at his request — it is not recoverable and should not be rebuilt.

## The daily loop

Chase keeps a running list of words and phrases in Google Keep during the day, then pastes it
into Claude Code and runs `/spanish`. Vlog notes go through the same skill. The skill drafts
a card for each bullet, he approves or edits the draft, and only then are the cards appended
to the **bottom** of `data/spanish.txt`. Review happens in the CLI, not here.

`/spanish` only ever works from a list. There is no mode that invents cards or pulls them
from a source file — that mode existed, and removing it was the point.

During review, **`d`** deletes the card from its `.txt` file instantly — no confirm, he does
not hit it by accident — and **`f`** moves it out of the deck into `flagged.txt` in the repo
root (`deck | term = definition`, one per line) with no rating; the session just continues.
When he says "fix my flagged cards", rewrite each one so the prompt asks for exactly one
answer, append it to the **bottom** of its deck file (the same way `/spanish` does), and
remove its line from `flagged.txt`. A fixed card is a new card; its old progress is gone.

The loop only fills up if he is **attempting to speak**. The Keep list is downstream of the
speaking habit, not a substitute for it.

The deck opens itself at **20:30 every night** in a tab of his main Ghostty, with no dialog.
That launcher lives **outside this repo**: `~/.local/bin/flashcards-nightly`, called by the
`local.day-clock` launch agent through `~/.local/bin/day-hook`, logging to
`~/.local/state/flashcards/nightly.log`. It is documented in `~/Developer/Focuses/Mac/flows.md`;
change it there, not here. **Hyper+E** opens the deck by hand. It exists because the review
habit is the part that actually decays, not the card supply.

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
| `.claude/skills/english/` | The `/english` skill — words and speaker notes → word cards and move cards |
| `.claude/skills/hablar/` | The `/hablar` skill — voice recording → whisper transcript → corrections → gap cards. Scaffold; being shaped by hand from 2026-10-09 |
| `.claude/skills/speak/` | The `/speak` skill — English twin of `/hablar`: filler count, sharper words, tighter phrasing. Scaffold |
| `SPEAKING.md` | The speaking plan — situation, the invariant, the daily recording loop, 4/3/2 |

## Decks

All decks live flat in `data/`. There is no parking lot and no archive.

| Deck | Cards | Direction | Grown by |
|------|-------|-----------|----------|
| `spanish.txt` | 536 | English prompt → Spanish answer | **The working deck**, rebuilt 2026-10-16: his 100 personal cards first, then 368 conversational formulas (greetings, goodbyes, thanks, reactions, table and hosting phrases, fillers) pulled out of the old bulk deck before it was deleted, then 70 mined from a Cuenca vlog (2026-10-17). `/spanish` appends his bullets at the bottom. New cards should come from real conversation — his own, `/hablar`, and Mexican vlogs he mines by hand — not from lists. |
| `mexican.txt` | 386 | English prompt → Spanish answer | Fixed. CDMX slang, flirting, and food/culture terms. |
| `english.txt` | 0 | **Cue → word or phrase** | Restarted from empty 2026-10-17. `/english` — words he reached for, and notes on speakers he admires. Articulate speaking, unrelated to Spanish. |

`english.txt` cues differently on purpose: Spanish trains *producing the phrase* from an
English cue; English trains *recalling the word or move* from its meaning or its moment, so
the definition or situation is on top and the word or phrase is the answer.

`mexican.txt` folds in what used to be three files. Its food and culture cards were
originally written Spanish-on-top as a glossary and were **flipped** during the merge, so the
English description is the prompt and the Spanish term is the answer — same production
direction as every other Spanish deck.

**New cards are capped at 20 per deck per day** (`NEW_CARDS_PER_DAY` in
`spaced_repetition.py`, added 2026-10-04). A never-rated card waits until a slot opens; the
first rating stamps `introduced` with the date, and that date is what the cap counts. New cards
enter in deck-file order, so the top of a `.txt` file is what arrives next. Due reviews are
never capped. Before the cap, every new card was due at once — dropping 500 cards into a deck
made a 500-card session, and that is what killed the previous deck. Every new card goes at
the **bottom** (his call, 2026-10-17): he works through the deck in order, so new cards
queue behind the ones already there. Moving a card within the file does not reset its
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

## Do not

- Edit `data/decks/*.json` by hand
- **Insert or reorder cards mid-file.** `parser.py` pairs consecutive non-empty lines from
  the top and hashes `term|definition` for the card ID. An odd-line insertion re-pairs every
  card below it, changes every ID, and silently wipes review progress for the whole deck.
  Append at the tail, always in even line counts.
- Bulk-rewrite register (tú/usted) on old cards without being asked
- Bulk-import vocabulary lists, or rebuild an archive to pull cards from
