#!/bin/bash
# run_reminder.sh — launchd entry point for the 20:30 flashcard nudge.
#
# Posts a notification, then a dialog with "Start" / "Skip tonight". Start opens Terminal
# with `python3 main.py` already running in the repo, so there is no gap between the
# reminder and the deck.
#
# Safe to run by hand:
#   DRY_RUN=1 FORCE=1 bash scripts/reminder/run_reminder.sh   # prints the decision, shows nothing
#   FORCE=1 bash scripts/reminder/run_reminder.sh             # real prompt, ignores the guards
#
# Guards, in order: not already handled this evening · current time inside the 20:00-03:59
# window. FORCE=1 skips both. The window is what makes fire-on-wake safe — if the Mac was
# asleep at 20:30 and the lid opens at 2pm the next day, launchd runs this and it exits.

REPO="/Users/ChaseReynolds/Developer/MemoryFlashcards"
PY="/opt/homebrew/bin/python3"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/ChaseReynolds"

STATE="$HOME/.local/state/memoryflashcards"
STAMP="$STATE/last-prompt"
mkdir -p "$STATE"

hour=$(date +%H)
# The "evening" a run belongs to. A fire at 00:30 still belongs to yesterday evening,
# so the once-per-night stamp does not reset at midnight.
if [ "$hour" -lt 4 ]; then
    evening=$(date -v-1d +%F)
else
    evening=$(date +%F)
fi

log="$STATE/reminder.log"
say() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$log"; }

if [ -z "$FORCE" ]; then
    if [ -f "$STAMP" ] && [ "$(cat "$STAMP")" = "$evening" ]; then
        say "skip: already handled the evening of $evening"; exit 0
    fi
    # 20:00-03:59 only. Outside that, this is a stale fire-on-wake, not a reminder.
    if [ "$hour" -lt 20 ] && [ "$hour" -ge 4 ]; then
        say "skip: $(date +%H:%M) is outside the 20:00-03:59 window"; exit 0
    fi
fi

if [ -n "$DRY_RUN" ]; then
    say "dry run: would prompt for the evening of $evening"; exit 0
fi

say "prompt: evening of $evening"

/usr/bin/osascript -e 'display notification "Say the answers out loud." with title "Spanish — 30 minutes" sound name "Glass"' >/dev/null 2>&1

# Two plain buttons so neither path returns an AppleScript error. `giving up after` keeps
# the dialog from sitting on screen forever if he is not at the desk.
answer=$(/usr/bin/osascript 2>/dev/null <<'APPLESCRIPT'
set r to display dialog "Time for Spanish." & return & return & "Say every answer out loud before you flip the card. Speed is the score, not whether you recognized it." with title "MemoryFlashcards" buttons {"Skip tonight", "Start"} default button "Start" with icon note giving up after 600
if gave up of r then
    return "gaveup"
else
    return button returned of r
end if
APPLESCRIPT
)

case "$answer" in
    Start)
        echo "$evening" > "$STAMP"
        say "start: opening Terminal in $REPO"
        /usr/bin/osascript >/dev/null 2>&1 <<APPLESCRIPT
tell application "Terminal"
    activate
    do script "cd '$REPO' && '$PY' main.py"
end tell
APPLESCRIPT
        ;;
    "Skip tonight")
        echo "$evening" > "$STAMP"
        say "skipped by request"
        ;;
    gaveup|"")
        # No stamp written on purpose: nobody was at the keyboard, so the next wake inside
        # the window is allowed to ask again.
        say "no answer (timed out or dialog failed) — leaving tonight unstamped"
        ;;
    *)
        say "unexpected answer: $answer"
        ;;
esac
exit 0
