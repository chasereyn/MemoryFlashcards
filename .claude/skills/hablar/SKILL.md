---
name: hablar
description: Transcribe a spoken-Spanish recording, correct it to natural CDMX Spanish, and turn every gap into a card. Use when the user invokes /hablar, says "transcribe my latest", or drops a voice recording of himself speaking Spanish.
---

# hablar

Speaking practice. He records 3–5 minutes about his day without stopping, and says the
English word out loud whenever he hits a gap. This skill finds those gaps and patches them.

**Status: scaffold.** He is running the loop by hand for the first week (from 2026-10-09).
Tighten this file from what those sessions actually needed. Don't add steps he didn't use.

## Why

Input is not his problem. Output is. **The gap only shows when you try:** he can only say
what he has already said, and a gap stays invisible until a real attempt hits it. Flashcards
patch gaps someone already found. This skill is what finds them.

## Steps

1. **Find the audio.** The newest audio file in `~/Downloads` (he Tailscales it over from his
   phone). Say which file you picked. Don't glob several extensions — zsh aborts on the
   first one with no match. Use `ls -t ~/Downloads | rg -i '\.(m4a|mp3|wav|aac|caf|ogg|opus)$' | head -1`.
2. **Transcribe it.** Convert, then run whisper.cpp in Spanish:
   ```
   ffmpeg -loglevel error -y -i <file> -ar 16000 -ac 1 <scratch>/a.wav
   whisper-cli -m ~/.local/share/whisper/ggml-large-v3-turbo.bin -l es -f <scratch>/a.wav -nt
   ```
   The English words he drops in will come out garbled or translated. Read for them.
3. **Correct it.** Give back exactly three things, and nothing more:
   - **Gaps.** Every spot where he dropped in English, stalled, or talked around a word.
   - **Wrong forms.** Gender, conjugation, missing article, word-for-word calques. **A table**
     — `You said | Say | Why` — one short line of why per row. He reads it in the chat thread.
   - **His story, said right.** The natural CDMX version of what he *meant*, at his level.
     Not a polished essay. Short sentences he can actually say.
   If a word looks like a whisper mishearing rather than his mistake, ask; don't correct it.
   Whisper drops the pauses and question marks of him prompting himself — `que más hable con
   Sarah` was `¿Qué más? … Hablé con Sarah.` Read a stray `que más`/`y qué` as that first.
4. **Gaps become cards.** Add them to the top of `data/spanish.txt` under the `/spanish`
   rules (one gap = one card, even line count, dedupe first).
5. **Hand back the redo.** Tell him to read the corrected story once, then retell it without
   looking in 4 minutes, then in 3. Tomorrow's recording starts by retelling this one.

## Don't

- Rewrite his story into Spanish he couldn't say. The point is the next attempt, not
  a perfect transcript.
- Correct more than about ten things in one go. Pick the ones that recur or block meaning.
