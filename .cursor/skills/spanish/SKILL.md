---
name: spanish
description: Appends vocabulary to MemoryFlashcards `data/decks/spanish.tsv` as TSV flashcard rows (English prompt, Spanish answer, one card per line), matching the deck's tone and punctuation. Use when editing or extending the main Spanish vocab deck.
disable-model-invocation: true
---

# Spanish vocab deck (`data/decks/spanish.tsv`)

## Project context

MemoryFlashcards stores deck content as **TSV** in `data/decks/`. Each line is one card:

- Column 1 = **term** (English prompt shown in review)
- Column 2 = **definition** (Spanish answer)

`parser.py` reads this file; review progress lives separately in `data/progress/spanish.tsv` (auto-managed — do not edit).

There is **no** six-line minimal-swap pattern here — unlike `data/decks/english.tsv`, this deck is strictly **one English prompt + one Spanish answer per line**.

## Card format (one item = one line)

```
English prompt	Spanish answer
```

- Optional header row: `term	definition`
- **Append** new rows at the **tail** of the file
- Use tab separation; if a field contains a tab, the CSV writer would quote it (rare)

## Spanish-side style (match the file)

- **Phrases and fixed expressions:** often **lowercase** (e.g. `no tengo tiempo`, `espero no abrumarte`), unless **¿** / **¡** are required.
- **Countable nouns:** usually include article where the English cue has one or the deck uses `el` / `la` / `los` / `las` (`el buzón`, `la lluvia de ideas`).
- **Adjectives** as glosses can appear **without** article if adjacent cards do (`lluvioso`, `profundo`).
- **Political / group labels:** `los izquierdistas`, `los derechistas`; adjectives like `liberal`, `conservador` for single-word labels.
- **Ambiguous English** (e.g. “update”): split into **two rows** — `update (noun)	la actualización` and `to update	actualizar` — when both senses are common.

## Workflow when adding cards

1. Open `data/decks/spanish.tsv` and append at the **tail**.
2. Write **one tab-separated row per card** (English prompt → Spanish answer).
3. Match **Latin American–leaning** usage already in the deck (`manejar`, `pasale`, etc.).
4. Fix obvious English typos in new rows unless the user wants slang spellings preserved.
5. Do **not** rewrite unrelated rows unless asked.

## Quick reference example

```
mailbox	el buzón
I'm joking	estoy bromeando
Who's laughing now?	¿quién se ríe ahora?
```

After editing, `python main.py` syncs on startup — new rows get default progress; existing ids keep their review history.
