# Speaking

The plan for turning understanding into speech — in Spanish first, English alongside.
Written 2026-10-09, the night the recording loop first worked.

## Where things stand

**Spanish.** Input is strong. Native vlogs land at ~98% with captions and ~70% without.
Output is weak. Mid-sentence, one missing word stops everything — *meatballs*, *green
onions*, *lean* in "lean into each other". He still translates in his head.

This is not a contradiction. Listening hands you the finished sentence and context fills the
holes. Speaking hands you nothing, and needs every word. Years of input with almost no
output built exactly the skill that was practiced.

**English.** Native, but says "um" a lot, spends too long reaching for the right word, and
wants to sound articulate: no filler, the precise word, said once.

## Same problem, two outfits

Both are **retrieval speed under live pressure**.

- **Spanish** — the bottleneck is *missing pieces*. The word was never produced, so it can't
  be retrieved.
- **English** — the pieces exist. The bottleneck is *how the pause is handled*. "Um" is a
  habit of filling silence to hold the floor. The fix is a silent pause.
- **Shared** — in both languages the words he *recognizes* far outnumber the words he
  *reaches for*. `english.txt` and `spanish.txt` are both production drills for that gap.

## The invariant

> **The gap only shows when you try.**

You can only say what you've already said. Input doesn't reveal gaps — the sentence arrives
whole. A gap stays invisible until a real attempt runs into it. Flashcards patch gaps that
were already found; the speaking loop is what finds them.

Reps alone aren't enough. Repetition without correction plateaus and locks in wrong forms.
The driving variable is **attempts + feedback**, not attempts.

## The loop

About 30 minutes a day. Spanish ~20, English ~5–10.

1. **Record 3–5 minutes about the day. Never stop.** Hit a gap → say the English word out
   loud and keep going. That marks the gap for free.
2. **Phone → Tailscale → `~/Downloads`.**
3. **Run `/hablar` (Spanish) or `/speak` (English).** Transcribes locally with whisper,
   returns the gaps, a table of wrong forms, and the story said right.
4. **Gaps become cards** — top of `spanish.txt`, or `english.txt` for English upgrades.
5. **The redo — 4/3/2.** Read the corrected story once. Then retell it *without looking*,
   faster each round: 4 minutes, 3, 2 (or proportionally shorter for a short story). The
   shrinking clock forces whole phrases instead of word-by-word translation. This is Paul
   Nation's 4/3/2 fluency technique.
6. **Next day, start by retelling yesterday's story.** Spaced repetition for sentences.

## Rules for the recording

- **Never stop.** A stall is a gap; say it in English and move on.
- **Talk around a gap.** Fluent speakers rarely have every word — they describe it.
  No *lean*? *Que los dos se apoyen.* That is a skill, and it gets trained here.
- **English: a silence instead of an "um".** A pause sounds deliberate. Filler sounds lost.

## The real limit

The recording is rehearsal. The end state is talking — Sarah, her mom, their friends.
Ten minutes a day of Spanish-only conversation with someone who will hand over the missing
word beats any app. The loop exists to make those ten minutes better.

## Philosophy

- **Habit over feature.** First week (2026-10-09 → 10-16) runs by hand. Skills get locked in
  from what was actually used, not what seemed useful.
- **Production, not recognition.** Every card is said out loud.
- **Personal over generic.** The phrase he needed yesterday beats fifty from a list.
- **Small.** Thirty minutes. Read it, do it, done.
