# MemoryFlashcards

A personal spaced-repetition flashcard CLI with automatic syncing and a session-based review algorithm, built for effective vocabulary and phrase learning.

## Quick Start

1. **Add your vocabulary**: Create TSV files in `data/decks/`. One card per line — tab-separated prompt and answer:
   ```
   term	definition
   Roof	Tejado
   Step aside!	Golpe avisa!
   ```

2. **Run the program**:
   ```bash
   python main.py
   ```

3. **Select a deck** and start reviewing!

That's it! No setup required—just add your vocabulary and run the program.

## Features

### Automatic Syncing

The system automatically syncs deck content (`.tsv`) with progress storage on startup. It:
- **Preserves** cards that exist in both (keeps your progress and review history)
- **Adds** new cards from text files
- **Removes** cards that you've deleted from text files

Your review progress is never lost—only the source content (text files) is synced, while all learning metadata stays intact.

### Session-Based Algorithm

Unlike traditional spaced repetition systems (like Anki's SM-2), this uses a **session-based approach** designed to prevent gaming and improve retention:

**Rating System:**
- **1 = Hard/Repeat**: Reappears randomly in positions 2-5 (stays in session)
- **2 = Medium-Hard**: Reappears 10-25 cards ahead (fixed range, stays in session)
- **3 = Medium**: Reappears 20-40 cards ahead (fixed range, stays in session)
- **4 = Easy**: Completed for session (removed from queue, scheduled for future review)

**Key Features:**

**First Impression Matters** - Your **first rating** determines difficulty adjustment, not your final rating. If you struggle initially (1-3) but eventually rate it 4, the algorithm still recognizes the initial difficulty. This prevents easy cards from being scheduled too far out due to momentary lapses.

**Session Completion Required** - Cards rated 1-3 stay in session until rated 4. This ensures active recall rather than passive recognition and prevents gaming the system (you can't just see the answer and rate it "easy").

**Sequential Rating Progression** - Ratings must progress sequentially (1→2→3→4), preventing you from skipping from "Hard" directly to "Easy". This encourages gradual mastery and prevents premature completion. If you rate a card 3, then forget it and rate it 1, you'll need to progress through 1→2→3→4 again. New cards (never seen in the session) can still be rated 1-4 freely.

**Fixed-Distance Reinsertion** - Unlike proportional systems that can bury struggling cards thousands of positions back in large decks, fixed distances work identically for 20 cards or 3000+ cards. Hard cards reappear randomly in positions 2-5 (not immediately) to force cognitive refocusing—the unpredictable brief gap prevents short-term/muscle memory from masquerading as true learning.

**Smart Prioritization** - Active session cards (struggling) appear first, prioritized by attempts and difficulty. Well-mastered cards fade into the background with exponential backoff (consecutive easy sessions multiply intervals exponentially).

**Adaptive Difficulty Tracking** - Struggle history is tracked separately from intervals, ensuring difficult material gets frequent reviews even when intervals suggest otherwise.

**Daily Session Limit** - Large decks cap at **25 cards introduced per day** (configurable via `DEFAULT_DAILY_LIMIT` in `spaced_repetition.py`). Active in-session cards are always included; reinsertions from ratings 1–3 do not pull extra cards from the backlog. Remaining due cards stay queued for future days — show up daily rather than marathon sessions. Set `SHOW_BACKLOG_IN_MENU = True` in `main.py` to display the full overdue count in the deck menu.

## Verbs deck

`data/decks/verbs.tsv` is **hand-maintained** (nothing in `main.py` overwrites it). It contains topic blocks you add over time: e.g. preterite (yo / 3sg / 3pl / tú-questions), then optional grammar-pattern blocks (**llevar** + gerund, **seguir** + gerund, **acabar de** + infinitive, **soler** + infinitive, etc.).

**When adding a new construction block (for you or a future editor):**

- Use `verbs.csv` as the **lemma list**; pick **~20** verbs that sound **natural** with that pattern. Skip odd collocations.
- **Append** new pairs to the end of `data/decks/verbs.tsv`—**do not** delete or replace existing blocks.
- **Format** matches other decks: one line English (prompt), one line Spanish (answer), blank line between cards.
- **Vary** subjects (I, tú, él/ella, we, they, inanimate “subject”), and mix in **DOP/IO** and **reflexive** clitics when the pattern allows.
- Reuse the same **short narrative style** as earlier cards in the file so the deck stays consistent.

## English deck (`data/english.txt`)

Cards often use a gloss, headword, then **two example lines**. Prefer the **same sentence** twice: first with a plain word or phrase, second with only the **headword** (or fixed idiom) substituted in. Full rewrites train a second line from scratch; **minimal swaps** train actually using the word in a familiar frame.

## File Structure

```
data/
  ├── decks/
  │   ├── spanish_vocab.tsv     # Deck content — edit this (one card per line)
  │   └── verbs.tsv
  └── progress/                 # Review state (auto-managed, gitignored)
      ├── spanish_vocab.tsv
      └── verbs.tsv
```

Edit files in `data/decks/` to add or remove cards. Progress in `data/progress/` is managed automatically.

## Requirements

- Python 3.11+

No dependencies required—uses only Python standard library.

