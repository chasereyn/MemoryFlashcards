# Nightly nudge — launchd, every night at 20:30

**`com.memoryflashcards.reminder`** posts a notification and a dialog at **20:30 every night**.
"Start" opens Ghostty with `python3 main.py` already running in this repo; "Skip tonight"
stamps the night and goes away. Installed 2026-09-10.

| File | What |
|------|------|
| `run_reminder.sh` | The wrapper. Guards (not already handled tonight, inside the 20:00-03:59 window), then notification → dialog → Ghostty. Logs to `~/.local/state/memoryflashcards/reminder.log`. |
| `com.memoryflashcards.reminder.plist` | The launchd agent. **Source of truth** — edit here, then reinstall. |

Runtime state lives outside the repo, in `~/.local/state/memoryflashcards/` — the once-a-night
stamp and the log. Nothing to gitignore.

## What happens when the lid is closed

- **Asleep at 20:30** (lid closed, still powered): launchd fires the job **when the Mac wakes**.
  That is the behavior you want for a reminder aimed at a human — it shows up when you are
  actually at the keyboard, not to an empty room.
- **The catch:** without a guard, opening the lid at 2pm the next day would fire a flashcard
  reminder at 2pm. Hence the **20:00-03:59 window** in the script. Outside it, the job runs and
  exits in one line.
- **Shut down at 20:30**: launchd does not replay missed calendar jobs across a boot.
  `RunAtLoad` covers it — the job fires at login and the guards decide.
- **Do not** add `sudo pmset repeat wake` here. It would wake a closed laptop to show a dialog
  at a dark screen in another room. The brief automation wants that because it does unattended
  work; this one needs a human, so waking the machine buys nothing.

## Install / reinstall *(after editing the plist)*

```bash
cp scripts/reminder/com.memoryflashcards.reminder.plist ~/Library/LaunchAgents/
launchctl bootout   gui/$(id -u)/com.memoryflashcards.reminder 2>/dev/null
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.memoryflashcards.reminder.plist
launchctl list | grep memoryflashcards      # confirm it registered
```

The repo tracks the agent but does not install it; the copy in `~/Library/LaunchAgents/` is
what runs. Removing that copy is what disables it — `bootout` alone is undone at next login.

## Run it by hand

```bash
DRY_RUN=1 FORCE=1 bash scripts/reminder/run_reminder.sh   # prints the decision, shows nothing
FORCE=1 bash scripts/reminder/run_reminder.sh             # real prompt, ignores the guards
launchctl kickstart gui/$(id -u)/com.memoryflashcards.reminder   # what launchd does at 20:30
tail -5 ~/.local/state/memoryflashcards/reminder.log
```

## Change the time

Edit `Hour`/`Minute` in the plist **and** the window in `run_reminder.sh` if the new time falls
outside 20:00-03:59, then reinstall. The two have to agree or the job will fire and immediately
guard itself out.

## Remove

```bash
launchctl bootout gui/$(id -u)/com.memoryflashcards.reminder
rm ~/Library/LaunchAgents/com.memoryflashcards.reminder.plist
```

## Things to know

- **The plist and the script hard-code absolute paths.** launchd does not expand `~`.
- **launchd's PATH is nearly empty.** The script sets its own and calls
  `/opt/homebrew/bin/python3` (3.14.7) outright — `python` does not exist on this machine and
  `/usr/bin/python3` is 3.9.6.
- **Ghostty, not Terminal.app.** On macOS the Ghostty CLI cannot launch the app, so the
  supported form is `open -na Ghostty --args --wait-after-command=true -e /bin/bash -lc "cd …
  && python3 main.py"`. `-e` swallows the command and every argument after it, and
  `--wait-after-command=true` leaves the window up when `main.py` exits or crashes, so an
  error is readable instead of flashing away.
- **A timeout does not stamp the night.** If the dialog gives up after 10 minutes, no stamp is
  written, so the next wake inside the window is allowed to ask again. Clicking either button
  does stamp it.
- **The dialog may not steal focus.** The notification is the backstop — it lands in
  Notification Center either way.
