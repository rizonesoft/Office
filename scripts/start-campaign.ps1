# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
#Requires -Version 7.0
<#
.SYNOPSIS
  Starts the unattended process-plan campaign in Claude Code, with its goal set.
.DESCRIPTION
  The desktop shortcut "Rizonesoft Office campaign" runs this file. It changes to the repository, runs the same
  host readiness check the campaign runs first (scripts/check-campaign-host.py, without the email), and then
  starts an interactive Claude Code session on the latest Opus (the 'opus' model alias, never a pinned version)
  that skips permission prompts and opens with a /goal: the plan
  finished to 100 percent through the process-plan skill, or the campaign ended by its own park.

  Starting it is the operator's word to start or resume the campaign. When a guard file from an earlier session
  exists, it says whose it is and waits for Enter before the new session takes the run over, because two
  sessions must never write to one tree.

  It heals a session that died (owner decision 21, docs/specs/2026-10-23-campaign-scope-design.md): when Claude
  Code exits while the run guard is still held, it waits 30 seconds, repeats the host check and starts a new
  session with the same goal, which takes the run over. A run that ended by its own rules holds no guard, so the
  launcher stops; five sessions ending inside an hour stop it too, and closing the window stops everything.

  The owner controls it with two desktop shortcuts (owner, 2026-11-10): "Rizonesoft Office campaign" starts it
  and "Rizonesoft Office campaign - Stop" stops it. Stop writes a stop request (build/campaign-stop-request) that
  the campaign honours at its next section boundary, ending the run cleanly, and that keeps this launcher from
  starting another session; answering NOW to its question also ends the running session at once, with its whole
  process tree. Starting again removes the request.
.EXAMPLE
  pwsh scripts/start-campaign.ps1
  pwsh scripts/start-campaign.ps1 -DryRun            # run the checks and print the command, start nothing
  pwsh scripts/start-campaign.ps1 -InstallShortcut   # create or refresh the two desktop shortcuts for this clone
  pwsh scripts/start-campaign.ps1 -Stop              # ask the campaign to stop (the Stop shortcut runs this)
  pwsh scripts/start-campaign.ps1 -Stop -Now         # stop it immediately, without the question
#>
[CmdletBinding()]
param([switch]$DryRun, [switch]$InstallShortcut, [switch]$Stop, [switch]$Now, [ValidateRange(1, 3600)][int]$RestartSeconds = 30,
      # The program that ends a process tree. Only the tests pass another one, to see a failed stop reported.
      [string]$TaskKillPath = (Join-Path $env:SystemRoot 'System32\taskkill.exe'))

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

if ($InstallShortcut) {
    # Every path comes from where this clone, PowerShell and the desktop are on this PC; none is written here.
    $link = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Rizonesoft Office campaign.lnk'
    $shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($link)
    $shortcut.TargetPath = (Get-Process -Id $PID).Path
    $shortcut.Arguments = "-NoLogo -NoExit -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    $shortcut.WorkingDirectory = $root
    $shortcut.IconLocation = "$(Join-Path $root 'assets\icons\windows\rizonesoft-office.ico'),0"
    $shortcut.Description = 'Start the unattended Rizonesoft Office campaign in Claude Code'
    $shortcut.WindowStyle = 3
    $shortcut.Save()
    Write-Host "Shortcut written: $link"

    $stopLink = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Rizonesoft Office campaign - Stop.lnk'
    $stopShortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($stopLink)
    $stopShortcut.TargetPath = (Get-Process -Id $PID).Path
    $stopShortcut.Arguments = "-NoLogo -NoExit -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Stop"
    $stopShortcut.WorkingDirectory = $root
    $stopShortcut.IconLocation = "$(Join-Path $root 'assets\icons\windows\rizonesoft-office.ico'),0"
    $stopShortcut.Description = 'Stop the unattended Rizonesoft Office campaign'
    $stopShortcut.Save()
    Write-Host "Shortcut written: $stopLink"
    exit 0
}

# The stop request and the record of the launcher that is running, both under the ignored build folder.
$stopFile = Join-Path $root 'build/campaign-stop-request'
$launcherFile = Join-Path $root 'build/campaign-launcher.json'

function Get-LiveLauncher {
    # The launcher the record names, when it is still running: the process number and its start time must both
    # match, so a process that merely reuses the number is never taken for a launcher. Otherwise nothing.
    if (-not (Test-Path -LiteralPath $launcherFile)) { return $null }
    try { $record = Get-Content -LiteralPath $launcherFile -Raw | ConvertFrom-Json } catch { return $null }
    if (-not $record -or -not $record.pid) { return $null }
    # ConvertFrom-Json turns the recorded text into a date by itself, so both sides are compared as instants.
    $recorded = if ($record.started -is [datetime]) { $record.started } else {
        try { [datetime]::Parse("$($record.started)", [cultureinfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::RoundtripKind) } catch { $null }
    }
    $process = Get-Process -Id $record.pid -ErrorAction SilentlyContinue
    if ($process -and $recorded -and $process.StartTime.ToUniversalTime().Ticks -eq $recorded.ToUniversalTime().Ticks) { return $process }
    return $null
}

if ($Stop) {
    New-Item -ItemType Directory -Force -Path (Join-Path $root 'build') | Out-Null
    Set-Content -LiteralPath $stopFile -Value ([DateTime]::UtcNow.ToString('o'))
    Write-Host 'Stop requested. The campaign ends its run at the next section boundary and no new session starts.'
    $answer = if ($Now) { 'NOW' } else { Read-Host 'Press Enter to let the current section finish, or type NOW to stop immediately' }
    if ($answer -ceq 'NOW') {
        $process = Get-LiveLauncher
        if (-not $process) {
            Write-Host 'No running launcher was found, so there was nothing to end.'
            exit 0
        }
        & $TaskKillPath /T /F /PID $process.Id | Out-Null
        $killExit = $LASTEXITCODE
        # Believe the process, not the exit code alone: the stop is reported only once the launcher is gone.
        $gone = $process.WaitForExit(15000)
        if ($killExit -ne 0 -or -not $gone) {
            Write-Host "NOT stopped: the launcher (process $($process.Id)) could not be ended (exit $killExit). It may be running elevated: run this Stop from an elevated window, or close the campaign window. The stop request stands, so it will still end at the next section boundary." -ForegroundColor Red
            exit 1
        }
        Write-Host 'Stopped now: the running session and everything it started were ended. Work that was not committed stays in the tree; the next start takes the run over.'
    }
    exit 0
}

$Host.UI.RawUI.WindowTitle = 'Rizonesoft Office campaign'

# The lock is taken as the first statement inside one try that runs to the end of the file, so nothing can
# happen between taking it and being sure it is given back: a normal end, an exit, an error anywhere below
# (writing the record included), or Ctrl+C at a prompt all pass through the finally. The shortcut's window
# stays open afterwards (-NoExit), and a lock it still held would refuse the next start.
function Remove-OwnRecord {
    # Only this launcher's own record is removed, never one another launcher wrote. The lock is released here too,
    # by closing it, and not left to the end of the process: the shortcut keeps its window open (-NoExit) after
    # the launcher has finished, and a lock still held by that idle window would refuse the next start.
    $live = Get-LiveLauncher
    if ($live -and $live.Id -eq $PID) { Remove-Item -LiteralPath $launcherFile -Force -ErrorAction SilentlyContinue }
    if ($script:launcherLock) {
        $script:launcherLock.Dispose()
        $script:launcherLock = $null
    }
}
function Exit-Launcher([int]$Code) {
    if (-not $DryRun) { Remove-OwnRecord }
    exit $Code
}
try {
# Starting is the owner's word, so a stop request left from before is removed here, first, before any step that
# takes time: from this line on, a request that appears is a stop of THIS start and is never erased. The launcher
# is recorded at the same moment, so Stop can end it during the checks below as well as during a session. A record
# left behind by an exit is harmless: Stop matches the start time as well as the process number.
if (-not $DryRun) {
    # One launcher at a time, decided by the operating system and not by a check followed by a write: this launcher
    # opens the lock file for itself alone and keeps it open until it exits, so of two starts at the same moment
    # exactly one gets it, and Windows releases it when the process ends however it ends. The loser touches nothing
    # of the winner: not its record and not the stop request.
    New-Item -ItemType Directory -Force -Path (Join-Path $root 'build') | Out-Null
    try {
        $script:launcherLock = [System.IO.File]::Open((Join-Path $root 'build/campaign-launcher.lock'),
            [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    } catch [System.IO.IOException] {
        $other = Get-LiveLauncher
        $which = if ($other) { " (process $($other.Id))" } else { '' }
        Write-Host "Not started: a campaign launcher is already running$which. Use the Stop shortcut first, or close its window." -ForegroundColor Red
        exit 3
    }
    Remove-Item -LiteralPath $stopFile -Force -ErrorAction SilentlyContinue
    $self = Get-Process -Id $PID
    Set-Content -LiteralPath $launcherFile -Value (@{ pid = $PID; started = $self.StartTime.ToUniversalTime().ToString('o') } | ConvertTo-Json -Compress)
}
function Test-StopRequested {
    if (-not (Test-Path -LiteralPath $stopFile)) { return $false }
    Write-Host ''
    Write-Host 'Stopped on your request. Run the start shortcut to carry on.'
    return $true
}

$missing = @('claude', 'python', 'git', 'gh', 'node') | Where-Object { -not (Get-Command $_ -ErrorAction SilentlyContinue) }
if ($missing) {
    Write-Host "Not started: not on PATH: $($missing -join ', ')" -ForegroundColor Red
    Exit-Launcher 2
}

# The campaign's own first check, shown here so a host that is not ready costs no session and no park commit.
python scripts/check-campaign-host.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host 'Not started: apply the fixes above, then run this shortcut again.' -ForegroundColor Red
    Exit-Launcher 1
}

$guard = Join-Path $root 'build/claude-campaign-guard.json'
if (Test-Path -LiteralPath $guard) {
    $held = Get-Content -LiteralPath $guard -Raw | ConvertFrom-Json
    Write-Host ''
    Write-Host "A campaign guard exists: session $($held.session_id), run file $($held.run_file)." -ForegroundColor Yellow
    Write-Host 'If that session is still open in another window, close THIS window: one tree takes one writer.'
    if (-not $DryRun) {
        Read-Host 'Press Enter to take the run over in a new session' | Out-Null
    }
}

# One line, no double quotes: it is passed to claude.exe as a single argument. /goal allows 4,000 characters.
$goal = '/goal Rizonesoft Office is finished: every row of todo/implementation-plan.md is stamped (python scripts/todo-graph.py query stats shows verified equal to total), every phase has its closeout, CI is green on the pushed HEAD, and each of the six apps has its draft release. Until then, work as an unattended campaign: run the process-plan skill (.claude/skills/process-plan/SKILL.md) now and follow it exactly, with its Unattended rules (never ask a question; decide, record and carry on), its run guard and heartbeat, its host readiness check and its CI watch, working as the lead AGENTS.md (Subagents) describes: hand each section''s build and each round of review fixes to the section-writer agent in a fresh context, use the Sonnet readers for facts and suites, call the Fable principal-implementer only from review round 8 with a serious finding open, when a fixed finding returns, or for an architecture decision record, and read every change and run every gate yourself. Aim for excellence in every section: this must be the best product in its class, measurably better than Microsoft Office and never a clone (docs/product-principles.md), with no shortcut taken where the harder, better version is possible. Act with full autonomy, as the owner would and better: decide what can be worked out instead of asking, improve the plan, skills, agents, tools and methods whenever they could be better, repair the run''s own failures at their cause, and never plan less because something is hard or no competitor does it. The operator started this session from the desktop shortcut: that is the operator''s word to start or resume the campaign, and to take over a guard left by an earlier session with acquire --handover. The goal also counts as met when the campaign has ended by its own rules: a column-0 PARKED line stands in the run file and campaign_guard.py end has run, because every remaining row waits on the owner, the operator, a third party or a host that is not ready, or CI could not be made green inside its recovery budget. In that case finish with a report of each leftover row and what the owner must do to release it.'

if ($goal.Length -gt 4000) { throw "the goal is $($goal.Length) characters; /goal allows 4000" }

# Sign in with the one-year token (claude setup-token), so the run does not end when the interactive sign-in does.
# It comes from the repository's own untracked env file, .secrets/office.env, which python scripts/import-secrets.py
# fills from the Conclave vault (owner, 2026-11-10: the repository is self-contained). The launcher never reads the
# vault or runs the import itself: importing is the operator's explicit step. The token is read into this process's
# environment only and never printed. Without it the session uses the interactive sign-in, so a missing token
# never stops a start.
$tokenName = 'CLAUDE_CODE_OAUTH_TOKEN'
$secretsFile = Join-Path $root '.secrets/office.env'
function Read-StoredToken {
    if (-not (Test-Path -LiteralPath $secretsFile)) { return $null }
    foreach ($line in Get-Content -LiteralPath $secretsFile) {
        if ($line -cmatch "^$tokenName=(sk-ant-oat[0-9]{2}-[A-Za-z0-9_-]{40,})\s*$") { return $Matches[1] }
    }
    return $null
}
# A token inherited from the shell that started this window is dropped first: the session signs in with the
# repository's own token or interactively, never with whatever the machine's environment happened to hold.
Remove-Item Env:CLAUDE_CODE_OAUTH_TOKEN -ErrorAction SilentlyContinue
$token = Read-StoredToken
if ($token) {
    $env:CLAUDE_CODE_OAUTH_TOKEN = $token
    Write-Host 'Sign-in: the one-year token from .secrets/office.env.'
} else {
    Write-Host 'Sign-in: the interactive one (no token in .secrets/office.env; run python scripts/import-secrets.py).' -ForegroundColor Yellow
}
$token = $null

# The lead is the latest Opus (owner, 2026-11-10, after the three-way measurement of that day: Opus building alone
# cost less than half of Fable alone, and Fable coordinating workers cost the most). It hands each section's build
# to the Opus section writer in a fresh context and calls Fable only where AGENTS.md (Subagents) says. 'opus' is
# Claude Code's alias for the newest Opus model, so a new release is picked up at the next start with no edit here;
# never pin a version such as claude-opus-5-5.
$model = 'opus'

if ($DryRun) {
    if (Test-Path -LiteralPath $stopFile) { Write-Host 'A stop request is present; a real start removes it.' }
    Write-Host ''
    Write-Host "Would run in ${root}:"
    Write-Host "claude --model $model --dangerously-skip-permissions `"$goal`""
    exit 0
}

$started = [System.Collections.Generic.List[datetime]]::new()
while ($true) {
    # Checked immediately before every launch: a stop asked for during the checks above, or during the wait and
    # the host check below, must never be followed by a new session.
    if (Test-StopRequested) { break }
    $started.Add((Get-Date))
    claude --model $model --dangerously-skip-permissions $goal
    if (Test-StopRequested) { break }
    if (-not (Test-Path -LiteralPath $guard)) {
        Write-Host ''
        Write-Host 'The campaign ended by its own rules: no run guard is held. Run this shortcut to start it again.'
        break
    }
    if (@($started | Where-Object { $_ -gt (Get-Date).AddHours(-1) }).Count -ge 5) {
        Write-Host ''
        Write-Host 'Stopped: five sessions ended inside an hour with the run still open. Read the last one before starting again.' -ForegroundColor Red
        break
    }
    Write-Host ''
    Write-Host "The session ended with the run still open. A new session starts in $RestartSeconds seconds; use the Stop shortcut, close this window or press Ctrl+C to stop." -ForegroundColor Yellow
    Start-Sleep -Seconds $RestartSeconds
    python scripts/check-campaign-host.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host ''
        Write-Host 'Not restarted: apply the fixes above, then run this shortcut again.' -ForegroundColor Red
        break
    }
}
} finally {
    Remove-OwnRecord
}
