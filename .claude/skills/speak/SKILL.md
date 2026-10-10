---
name: speak
description: Transcribe an English speaking recording and coach it toward concise, articulate speech — filler, word-search stalls, sharper vocabulary, tighter sentences. Use when the user invokes /speak or says "transcribe my latest English" or drops a recording of himself speaking English.
---

# speak

The English twin of `/hablar`. Same pipeline, different target. He is a native speaker, so
nothing is *missing* — the words are there, they're just slow to arrive, and the silence
gets filled with "um". The goal is to sound like someone who speaks well: no filler, the
precise word, said once.

**Status: scaffold.** Created 2026-10-09 with `/hablar`, before either had a week of use.
Lock it in from what `/hablar`'s first week taught. Don't add steps he didn't use.

## Steps

1. **Find the audio.** Newest audio file in `~/Downloads`:
   `ls -t ~/Downloads | rg -i '\.(m4a|mp3|wav|aac|caf|ogg|opus)$' | head -1`. Say which.
2. **Transcribe it — keep the filler.** whisper drops "um" and "uh" by default, which hides
   the main thing being measured. Prompt it to keep them, and keep timestamps so long
   pauses show:
   ```
   ffmpeg -loglevel error -y -i <file> -ar 16000 -ac 1 <scratch>/a.wav
   whisper-cli -m ~/.local/share/whisper/ggml-large-v3-turbo.bin -l en -f <scratch>/a.wav \
     --prompt "Um, uh, like, you know, so, I mean — he talks naturally with fillers."
   ```
   Not yet verified that the prompt makes whisper keep fillers. Check on the first run.
3. **Coach it.** Give back exactly these, nothing more:
   - **The count.** Fillers per minute (um, uh, like, you know, so, kind of, I mean) and the
     two he leans on most. One line. This is the number to watch fall week over week.
   - **Upgrades — a table.** `You said | Sharper | Why`. Vague or long phrasings that have a
     precise word or a shorter shape: "a lot of stuff went wrong" → "it unraveled". Prefer
     words an articulate person actually says out loud over SAT words nobody speaks.
   - **His point, said tight.** What he meant, in as few sentences as it takes. Usually half
     the length.
4. **New words become cards.** Any upgrade word he wouldn't have reached for goes to
   `data/english.txt` under the `/english` rules (definition prompt → word answer).
5. **Hand back the redo.** Say it again with a **silent pause** wherever an "um" was — a
   pause sounds deliberate, filler sounds lost. Then 4/3/2: retell in shorter time each round.

## Don't

- Flag every "so" or "like". Mark the habit, not each instance.
- Make him sound written. Spoken English uses short sentences and contractions; articulate
  is not formal.
