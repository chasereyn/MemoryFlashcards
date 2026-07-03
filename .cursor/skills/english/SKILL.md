---
name: english
description: Expands trailing words or phrases in MemoryFlashcards `data/english.txt` into full flashcard blocks (gloss, headword, two parallel example lines) with a single minimal lexical swap. Use when editing the English deck, appending vocabulary to `english.txt`, or matching the project's minimal-swap paired-sentence pattern.
disable-model-invocation: true
---

# English deck (`data/english.txt`)

## Project context

In the MemoryFlashcards app, `parser.py` builds cards from **consecutive non-empty lines**: line 1 = prompt, line 2 = answer, blank lines are skipped between pairs. Each logical "English deck" block therefore produces **two** synced cards: (gloss → headword) and (plain example → example with target).

## Block format (one vocabulary item)

Repeat this shape for each word or phrase. **One blank line** between the headword and the examples, and **one blank line** after the second example before the next item.

1. **Gloss** — short definition or usage note (dictionary-style is typical; informal items may use a short topic label or `(informal)` note, consistent with the rest of the file).
2. **Headword** — the exact word or fixed phrase being learned (as in the file today: single line, no leading "to " unless the deck already uses infinitives that way for that entry).
3. *(blank line)*
4. **Example A** — full sentence using a plain word, phrase, or periphrasis that the headword will replace.
5. **Example B** — **the same sentence** as A with **only** the intended span swapped for the headword (or idiom). Everything else stays the same: same clauses, punctuation, and order. Adjust only **determiners or agreement** when grammar requires it (e.g. *a/an*, *is/are*), not a full rewrite.
6. *(blank line)*

## Minimal-swap rule (critical)

- **Prefer:** identical sentence frames; second line differs by **one substitution** (the gloss’s plain wording → headword).
- **Avoid:** composing a second sentence from scratch; that trains recall of a different line, not use of the headword in the same frame.
- **Multiword headwords:** swap in the whole fixed phrase as one unit.
- If a truly minimal swap is impossible, get as close as the rest of the deck does for tricky idioms—still maximize overlap between lines.

## Workflow when the user adds material at the end

1. Open `data/english.txt` and find **trailing headwords** (or rough notes) after the last complete block.

2. For **each** orphaned line or note, **replace or expand** into a full **six-line** block (lines 1–2, blank, 4–5, blank) per the format above.

3. **Match the deck’s voice:** concise glosses, neutral or lightly informal tone matching nearby cards; same use of sentence-initial capitals and final periods as neighboring examples.

4. Do **not** change unrelated cards; only extend or fix the tail the user is working on.

5. After edits, mentally verify: for every block, lines 4 and 5 should be **parallel** with **one deliberate substitution** for the target.

## Quick reference example

```
very bad
abysmal

The team's performance was terrible in last night's game.
The team's performance was abysmal in last night's game.
```
