---
name: mexican
description: Expands trailing notes in MemoryFlashcards `data/decks/mexican.tsv` into TSV flashcard rows (name or English prompt, vivid English definition) for Mexican food, culture, geography, history, and brands. Use when editing the mexican deck, converting scratch lists about Mexico, or adding cards for Sarah, family trips, and Mexican cultural context.
disable-model-invocation: true
---

# Mexican deck (`data/decks/mexican.tsv`)

## Project context

MemoryFlashcards stores deck content as **TSV** in `data/decks/`. Each line is one card:

- Column 1 = **term** (shown first in review — usually the dish name, place, person, or English prompt)
- Column 2 = **definition** (answer — vivid **English** description)

Review progress lives in `data/progress/mexican.tsv` (auto-managed — do not edit).

Unlike `spanish.tsv`, this deck is **not** English → Spanish. It is **Mexican cultural knowledge**: foods, places, gods, artists, brands, and customs described in English so the user can recall what each thing is.

## Card format (one item = one line)

```
name or prompt	English description
```

- Optional header row: `term	definition`
- **Append** new rows at the **tail** of the file
- Tab separation only

## Style (match the deck)

- **Food:** dish name → sensory English description (ingredients, texture, how it's eaten, regional note if relevant)
- **Places / geography:** proper name → what/where it is; include legend or context when iconic (Popocatépetl, Teotihuacán)
- **People / gods:** name → role and why they matter (Los Tres Grandes, Tlaloc, etc.)
- **Brands / local refs:** name → what it is (Pollo Feliz, Pineda Covalin, La Puerta Metepec)
- **Slang / culture:** term → plain English gloss (`guache`, `huachicol`, `esquite`)
- Fix obvious typos from scratch notes; preserve intent
- Skip section headers, empty lines, and personal meta-notes (report those to the user instead of cardifying)

## Workflow when the user adds material

1. Open `data/decks/mexican.tsv` and find **trailing orphans** or raw scratch at the end.
2. Convert each item to **one tab-separated row** unless the user asks for splits.
3. Prefer **name → description** over question format when the scratch list uses dish/place names.
4. Add a **small** set of high-value extras only when the user says to (Día de los Muertos, mariachi, etc.) — do not bulk-fill generic tourism cards.
5. Do **not** rewrite unrelated rows; only extend or fix the tail.

## Quick reference example

```
pozole	spicy Mexican soup with pork, hominy, radish, cabbage, and lime — often red, white, or green
Tlaloc	Aztec god of rain, lightning, and fertility — goggled eyes, jade offerings, tied to agriculture
tacos al pastor	spit-roasted marinated pork shaved into tortillas with pineapple, onion, and cilantro — trompo style
```

After editing, `python main.py` syncs on startup — new rows get default progress; existing ids keep their review history.
