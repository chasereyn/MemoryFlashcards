# Registers a daily 8:30 AM Task Scheduler job for MemoryFlashcards.
# Runs when the user is logged on (required for interactive CLI).
# If 8:30 is missed (PC off or signed out), StartWhenAvailable runs it at next logon/boot.

$ErrorActionPreference = "Stop"

$TaskName = "MemoryFlashcards Daily Review"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$RunScript = Join-Path $PSScriptRoot "run_flashcards.cmd"

if (-not (Test-Path $RunScript)) {
    Write-Error "Missing launcher: $RunScript"
}

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$Action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$RunScript`"" `
    -WorkingDirectory $RepoRoot

$Trigger = New-ScheduledTaskTrigger -Daily -At "8:30AM"

$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 4)

$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Daily Spanish flashcard review at 8:30 AM (window stays open after Ctrl+C)"

Write-Host "Installed scheduled task: $TaskName"
Write-Host "  Time: daily at 8:30 AM"
Write-Host "  Launcher: $RunScript"
Write-Host "  If missed: runs at next logon/boot (StartWhenAvailable)"
Write-Host ""
Write-Host "To test now: Start-ScheduledTask -TaskName '$TaskName'"
