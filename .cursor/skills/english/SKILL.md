---
name: english
description: Expands trailing words or phrases in MemoryFlashcards `data/decks/english.tsv` into TSV flashcard rows using the gloss/headword + minimal-swap paired-sentence pattern (two rows per vocabulary item). Use when editing the English deck or matching the project's minimal-swap example pattern.
disable-model-invocation: true
---

# English deck (`data/decks/english.tsv`)

## Project context

MemoryFlashcards stores deck content as **TSV** in `data/decks/`. Each **line** is one synced flashcard (`term\tdefinition`).

The English deck uses a **four-line logical block** that becomes **two TSV rows** (two cards per vocabulary item):

| Row | term (prompt) | definition (answer) |
|-----|---------------|---------------------|
| 1 | Gloss | Headword |
| 2 | Plain example sentence | Same sentence with headword swapped in |

Review progress is in `data/progress/english.tsv` — do not edit.

## Block format (one vocabulary item = two TSV rows)

1. **Row 1 — gloss → headword**
   - **term:** short definition or usage note
   - **definition:** the exact word or fixed phrase being learned

2. **Row 2 — minimal-swap example pair**
   - **term:** full sentence using plain wording
   - **definition:** **the same sentence** with **only** the target span swapped for the headword (adjust determiners/agreement only when grammar requires it)

## Minimal-swap rule (critical)

- **Prefer:** identical sentence frames; second line differs by **one substitution**.
- **Avoid:** composing a second sentence from scratch.
- **Multiword headwords:** swap in the whole fixed phrase as one unit.

## Workflow when the user adds material at the end

1. Open `data/decks/english.tsv` and find **trailing headwords** or rough notes after the last complete block.
2. For each item, add **two tab-separated rows** per the format above.
3. **Match the deck's voice:** concise glosses, neutral tone, same capitalization/punctuation as neighbors.
4. Do **not** change unrelated rows; only extend or fix the tail.
5. Verify: row 2's term and definition are **parallel** with **one deliberate substitution**.

## Quick reference example

```
very bad	abysmal
The team's performance was terrible in last night's game.	The team's performance was abysmal in last night's game.
to make (something) suitable for a new use or purpose; modify	adapt
The tool was changed to work in the new system.	The tool was adapted to work in the new system.
```

After editing, sync runs on `python main.py` startup — new rows get default progress; unchanged ids keep review history.
