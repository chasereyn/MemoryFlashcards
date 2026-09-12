---
name: english
description: Grow the English vocabulary deck by writing a definition for each word he gives. Use when the user invokes /english, pastes a "VOCAB" list, or hands over English words he wants to remember.
---

# english

Append definition→word cards to the tail of `data/english.txt`, print what was added, stop.

This is a 30-second workflow. No preamble, no plan, no approval gate. Do the work.

## Input is always a list

`/english` takes bullets — usually words he hit while reading, sometimes headed `VOCAB`.
There is no other mode. If the message has no list, ask for one in a single line; do not
invent cards, and do not go looking for a word list to pull from.

**One bullet = one card.** Never expand a word into several senses. Never merge two words.

Sometimes a bullet carries a parenthetical that pins the sense he means —
`pronounced (greater in intensity)`. **That gloss wins.** Define that sense and ignore the
commoner one.

## The deck runs backwards on purpose

Every Spanish deck here prompts in English and answers in Spanish. This one prompts with a
**definition** and answers with the **word**, because the skill being trained is recall:
he knows what he means, and the word will not come.

That inverts what a good definition looks like:

- **The definition must cue exactly one word.** A dictionary entry describes a word. A card
  prompt has to *summon* it. If three words would satisfy the prompt, the card trains nothing
  — tighten it until only his word fits.
- **Tag the part of speech, always** — `(n)`, `(v)`, `(adj)`, `(adv)`. It is half the cue.
  Without it he answers `solemn` to a prompt whose answer is `solemnly` and marks himself
  wrong.
- **Adverbs cue on their shape.** Open an `-ly` prompt with "in a … way" so the grammatical
  form is part of what's being asked for.
- **Plain words, one clause, lowercase.** No sentence-final period. "struck with a sudden
  helpless infatuation" beats "afflicted by an abrupt and overwhelming romantic attraction."
  Never define a word using the word, or an obvious relative of it.

Check the new cards against each other before writing. Two words that land on near-identical
prompts — `undisturbed` and `isolated` — will collide in review. Sharpen one until they
separate, and say so in the output.

## Writing to the file

Only ever `data/english.txt`. The other decks in `data/` are not grown by this skill.

Append directly. The rules:

1. **Append at the tail only.** Never insert mid-file, never reorder, never rewrite an
   existing card unless he asks.
2. **Definition on top, word below.** Always an even number of lines. Blank line between
   cards, blank line before the first appended card.
3. **CRLF line endings, UTF-8.** Match the existing file. A heredoc piped through
   `awk '{printf "%s\r\n", $0}'` is the reliable way to get them on BSD userland.
4. **Never touch `data/decks/*.json`.** Auto-managed and gitignored.
5. **Check for duplicates first** against the whole of `data/english.txt`, case-insensitively,
   on the word side. Drop a bullet that's already a card and say which prompt it already has.

Rules 1 and 2 are not style — `parser.py` pairs consecutive non-empty lines from the top of
the file and hashes `term|definition` for the card ID. An odd-line insertion mid-file
re-pairs every card after it, changes every ID, and silently wipes review progress for the
whole deck.

## Verify before reporting

Run `python3 -c "from parser import parse_text_file; print(len(parse_text_file('data/english.txt')))"`
and confirm the count rose by exactly the number of cards you appended. A count that is off
by one means the file has an odd line somewhere and every card below it has lost its history.

Then update the `english.txt` row in `CLAUDE.md` to the new count.

## Output

Print a compact table of what was appended — word and the prompt you wrote for it — plus a
short note only where one is genuinely useful (a dropped duplicate, a sense you had to pick
between, two cards you had to pull apart). Say the old and new card counts in one line.

Do not commit on your own. Offer it in one line at the end — and when he says yes,
**commit and push to the remote in the same step.** A yes to "commit?" is a yes to pushing;
never leave the commit sitting local.
