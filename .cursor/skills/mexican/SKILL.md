---
name: mexican
description: Appends rows to MemoryFlashcards `data/decks/mexican.tsv` (name or English prompt, vivid English definition) for Mexican food, culture, traditions, geography, history, and brands. Use when editing the mexican deck. Do NOT add general Spanish vocabulary or English→Spanish phrase pairs here — those belong in `spanish.tsv`.
disable-model-invocation: true
---

# Mexican deck (`data/decks/mexican.tsv`)

## Project context

MemoryFlashcards stores deck content as **TSV** in `data/decks/`. Each line is one card:

- Column 1 = **term** (shown first in review — usually the dish name, place, person, or English prompt)
- Column 2 = **definition** (answer — vivid **English** description)

Review progress lives in `data/progress/mexican.tsv` (auto-managed — do not edit).

Unlike `spanish.tsv`, this deck is **not** English → Spanish. It is **Mexican cultural knowledge** described in English so the user can recall what each thing is.

**In scope:** foods, dishes, drinks, places, geography, gods, artists, holidays/traditions, brands, customs, and cultural references tied to Mexico.

**Out of scope (use `spanish.tsv` instead):** general vocabulary, conversational phrases, slang one-liners, proverbs as language cards, and anything that is primarily “English prompt → Spanish answer” for daily speech.

## Card format (one item = one line)

```
name or prompt	English description
```

- Optional header row: `term	definition`
- **Append** new rows at the **tail** of the file
- Tab separation only

## Style (match the deck)

- **Food / drink:** dish name → sensory English description (ingredients, texture, how it's eaten, regional note)
- **Places / geography:** proper name → what/where it is; legend or context when iconic
- **People / gods / history:** name → role and why they matter
- **Traditions / holidays:** custom or object → what it is and how it fits Mexican culture (Día de los Muertos, lotería, piñata)
- **Brands / local refs:** name → what it is
- **Cultural gloss (in English):** only when defining a *thing* (e.g. `huachicol` as fuel theft phenomenon), not when the card is really a phrase to produce in Spanish

## Workflow when adding cards

1. Open `data/decks/mexican.tsv` and append at the **tail**.
2. Convert each item to **one tab-separated row** unless the user asks for splits.
3. Prefer **name → description** over question format for dishes, places, and people.
4. Route **slang, phrases, and speech** to `spanish.tsv`, not this deck.
5. Do **not** rewrite unrelated rows unless asked.

## Quick reference example

```
pozole	spicy Mexican soup with pork, hominy, radish, cabbage, and lime — often red, white, or green
Tlaloc	Aztec god of rain, lightning, and fertility — goggled eyes, jade offerings, tied to agriculture
tacos al pastor	spit-roasted marinated pork shaved into tortillas with pineapple, onion, and cilantro — trompo style
```

After editing, `python main.py` syncs on startup — new rows get default progress; existing ids keep their review history.
