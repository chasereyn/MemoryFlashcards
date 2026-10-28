---
name: english
description: Grow the English speaking deck from his word bullets or his notes on a speaker he admires. Use when the user invokes /english, pastes a "VOCAB" list, or hands over English words or phrases he wants to be able to say.
---

# english

Draft cards from his list, wait for his approval, then append them to the bottom of
`data/english.txt`.

Two turns, no ceremony: **draft → he approves or edits → write.** No preamble, no plan.

## What this deck is for

He is a native speaker. Nothing is missing — the words are there, they are just slow to
arrive, so he pauses mid-sentence hunting for them. The goal is to **speak articulately**,
the way Grant Sanderson does: the precise everyday word at the right moment, and framing
moves that structure a thought and buy thinking time.

Not SAT words. A word belongs here only if an articulate person actually says it out loud
(`conflate`, `judicious`, `hand-wavy`) — not words you only meet in print (`pyrrhic`). The
ladder in `CLAUDE.md` applies: the old level-1 word list was deleted 2026-10-17 and purged
from git history. Never rebuild it.

## Input is always a list

`/english` takes bullets — words he reached for and couldn't find, or notes from a talk or
video by someone who speaks well. There is no other mode. If the message has no list, ask
for one in a single line; do not invent cards, and do not go looking for a word list.

If a transcript is in `transcripts/`, read the line in context before writing the card —
notes are often fragments.

**One bullet = one card.** Never expand a word into several senses. Never merge two.
A parenthetical gloss in a bullet — `pronounced (greater in intensity)` — pins the sense he
means. **That gloss wins.**

## Two card types

The deck prompts with a cue and answers with what has to come out of his mouth.

**Word cards — definition → word.** For single words.

- **The definition must cue exactly one word.** If three words would satisfy the prompt, the
  card trains nothing — tighten it until only his word fits.
- **Tag the part of speech, always** — `(n)`, `(v)`, `(adj)`, `(adv)`. It is half the cue.
- **Adverbs cue on their shape.** Open an `-ly` prompt with "in a … way".
- **Plain words, one clause, lowercase.** No sentence-final period. Never define a word using
  the word or an obvious relative of it.

**Move cards — situation → phrase.** For signposting moves and idioms.

- The prompt is the **moment you'd say it**, not a definition: "you're about to admit a
  real downside of your own idea before moving on" → "Let's be real, ..."
- Tag it `(move)` or `(idiom)` so the shape of the answer is part of the cue.
- The answer is the phrase as he'd say it, short, with `...` where his own words continue.

Check the new cards against each other and the deck. Two prompts that would summon the same
answer will collide in review — sharpen one until they separate, and say so.

## Turn 1 — the draft

**Check for duplicates first** against the whole of `data/english.txt`, case-insensitively,
on the answer side. Drop a bullet that's already a card and say so.

Print one numbered table — **# | Prompt | Answer | Note** — and stop. The note is for the
exceptions only: a sense you had to pick, two cards you pulled apart, a word that's more
written than spoken. **Write nothing to the file in this turn.**

## Turn 2 — write what he approved

Apply exactly what he said; where he defers, take the draft's own suggestions. Then write.

## Writing to the file

Only ever `data/english.txt`. The other decks in `data/` are not grown by this skill.

1. **Append at the bottom only.** Never insert mid-file, never reorder, never rewrite an
   existing card unless he asks.
2. **Prompt on top, answer below.** Always an even number of lines. Blank line between
   cards, blank line after the last card.
3. **LF line endings, UTF-8** (`.gitattributes` pins LF).
4. **Never touch `data/decks/*.json`.** Auto-managed and gitignored.

Rules 1 and 2 are not style — `parser.py` pairs consecutive non-empty lines from the top of
the file and hashes `term|definition` for the card ID. An odd-line insertion mid-file
re-pairs every card after it, changes every ID, and silently wipes review progress.

After writing, run
`python3 -c "from parser import parse_text_file; print(len(parse_text_file('data/english.txt')))"`
and confirm the count rose by exactly the number of cards written. Update the `english.txt`
row in `CLAUDE.md` to the new count. Then one line: how many were added, and the new count.

Do not commit, and do not offer to. If he asks for a commit, commit and push in one step.
