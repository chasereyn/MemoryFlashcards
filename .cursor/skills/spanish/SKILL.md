---
name: spanish
description: Converts trailing orphan words or phrases in CCC `data/spanish_vocab.txt` into parser-ready flashcard pairs (English prompt, Spanish answer, blank line between cards), matching the deck’s tone and punctuation. Use when appending vocabulary to `spanish_vocab.txt`, formatting a raw scratch list at the file tail, or syncing notes into the Spanish vocab deck.
disable-model-invocation: true
---

# Spanish vocab deck (`data/spanish_vocab.txt`)

## Project context

The CCC app’s `parser.py` pairs **consecutive non-empty lines**: line 1 = **term** (shown as the English prompt in review), line 2 = **definition** (Spanish). Blank lines separate cards. There is **no** six-line minimal-swap pattern here—unlike `data/english.txt`, this file is strictly **one English line, one Spanish line, one blank line** per card.

## Card format (one item)

1. **English** — word, gloss, or full sentence/question as the prompt (match neighboring cards: sentence case when the deck uses it; fragments allowed if the deck already uses them, e.g. trailing `...`).
2. **Spanish** — natural translation or target line (see style rules below).
3. **Blank line** before the next card.

## Spanish-side style (match the file)

- **Phrases and fixed expressions:** often **lowercase** in this deck (e.g. `no tengo tiempo`, `espero no abrumarte`), unless Spanish convention clearly expects a leading **¿** / **¡** for questions or exclamations.
- **Countable / lexical nouns:** usually include article where the English cue has one or where the deck uses `el` / `la` / `los` / `las` (`el buzón`, `la lluvia de ideas`).
- **Adjectives** as glosses can appear **without** article if adjacent cards do (`lluvioso`, `profundo`, `empinado`).
- **Political / group labels:** `los izquierdistas`, `los derechistas`; adjectives like `liberal`, `conservador` when the English cue is a single word label.
- **Ambiguous English** (e.g. “update”): split into **two cards** with cues like `update (noun)` / `la actualización` and `to update` / `actualizar`, or one card with the dominant sense if the user prefers a single gloss—default to **noun + verb** when both are common in the wild.

## Workflow when the user adds material at the end

1. Open `data/spanish_vocab.txt` and find **trailing orphans**: consecutive English lines (or mixed notes) **without** a Spanish line paired on the next non-empty line in the usual pattern.
2. For **each** orphan, **replace the scratch list** with full **two-line** pairs plus **blank lines** between cards.
3. **Infer missing Spanish** that is concise, idiomatic, and appropriate to the project’s **Latin American–leaning** usage already visible in the deck (`manejar`, `pasale`, etc.). Prefer widely understood terms; if a term is region-sensitive (e.g. infrastructure vocabulary), pick a sensible default and optionally note alternates only when disambiguation matters to the user.
4. **Light English cleanup** is allowed for clarity (e.g. fix `wont` → `won’t`, normalize “u” → “you” in study prompts) unless the user explicitly wants slang spellings preserved—when in doubt, keep their voice.
5. Do **not** rewrite unrelated cards; only normalize the **tail** the user is extending (and fix duplicate paste errors only if the user asks).

## Quick reference example

```
mailbox
el buzón

I'm joking
estoy bromeando

```
