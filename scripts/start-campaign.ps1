# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
#Requires -Version 7.0
<#
.SYNOPSIS
  Starts the unattended process-plan campaign in Claude Code or Google Antigravity, with its goal set.
.DESCRIPTION
  The desktop shortcuts "Office Claude campaign" (-Runner claude, the default) and "Office Carbon campaign"
  (-Runner agy) run this file. It changes to the repository, runs the same host readiness check the campaign runs
  first (scripts/check-campaign-host.py, without the email), and then starts an interactive session that skips
  permission prompts and opens with a /goal: the plan finished to 100 percent through the process-plan skill, or
  the campaign ended by its own park. Claude Code runs on the latest Opus (the 'opus' model alias, never a pinned
  version) at medium effort, signed in with the one-year token; Antigravity runs on Gemini 4 Carbon at medium
  with its own account, following .agents/rules/antigravity-runtime-and-safety.md. One launcher runs at a time,
  whichever runner it starts, and a run left open by one runner is taken over by the other the same way.

  Starting it is the operator's word to start or resume the campaign. When a guard file from an earlier session
  exists, it says whose it is and waits for Enter before the new session takes the run over, because two
  sessions must never write to one tree.

  A run starts only when the owner starts it (owner, 2026-11-12; decision 43 in
  docs/specs/2026-10-23-campaign-scope-design.md, which replaces decision 21). Nothing outside this window starts
  or resumes a session: no scheduled task and no watchdog. The only timer is the session's own heartbeat, which
  lives inside the open session, nudges it when it goes idle and dies with it. Inside the window, when a session exits
  cleanly (exit 0) while the run guard is still held, the launcher waits 30 seconds, repeats the host check and
  starts the next session with the same goal. A session that crashed or ended with an error is not started again:
  the launcher stops and says why. A run that ended by its own rules holds no guard, so the launcher stops; five
  sessions ending inside an hour stop it too. Closing the window ends everything the campaign started: the
  launcher holds a Windows job object that ends every process in it when the window's process goes.

  The desktop shortcuts start it, in a normal window. There is no Stop shortcut
  (owner, 2026-11-11): the operator stops the campaign by asking the session to stop cleanly, or with -Stop below.
  -Stop writes a stop request (build/campaign-stop-request) that the campaign honours at its next section
  boundary, ending the run cleanly, and that keeps this launcher from starting another session; answering NOW to
  its question also ends the running session at once, with its whole process tree. Starting again removes the
  request.
.EXAMPLE
  pwsh scripts/start-campaign.ps1
  pwsh scripts/start-campaign.ps1 -DryRun            # run the checks and print the command, start nothing
  pwsh scripts/start-campaign.ps1 -Runner agy        # the same campaign in Google Antigravity on Gemini 4 Carbon
  pwsh scripts/start-campaign.ps1 -InstallShortcut   # create or refresh both desktop shortcuts for this clone
  pwsh scripts/start-campaign.ps1 -Stop              # ask the campaign to stop at its next section boundary
  pwsh scripts/start-campaign.ps1 -Stop -Now         # stop it immediately, without the question
#>
[CmdletBinding()]
param(# The campaign runner: Claude Code (`claude`) or Google Antigravity on Gemini 4 Carbon (`agy`).
      [ValidateSet('claude', 'agy')][string]$Runner = 'claude',
      [switch]$DryRun, [switch]$InstallShortcut, [switch]$Stop, [switch]$Now, [ValidateRange(1, 3600)][int]$RestartSeconds = 30,
      # The program that ends a process tree. Only the tests pass another one, to see a failed stop reported.
      [string]$TaskKillPath = (Join-Path $env:SystemRoot 'System32\taskkill.exe'))

$ErrorActionPreference = 'Stop'
# Every native command's exit is read from $LASTEXITCODE below, so a failing one must never throw instead, whatever
# the shell that started this file prefers (a failed bootstrap must not end the start; D00 T04 §4, round 1).
$PSNativeCommandUseErrorActionPreference = $false
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

if ($InstallShortcut) {
    # Every path comes from where this clone, PowerShell and the desktop are on this PC; none is written here.
    # One shortcut for each runner (owner, 2026-11-12). Each carries the suite icon with its runner's badge in the
    # corner, rendered for this PC by scripts/campaign-icon.py into the user's own application data folder. A
    # runner's mark is its company's trademark and is not kept in this repository: when marks\<name>.svg exists in
    # that folder it is drawn in the badge, and without it the badge carries the runner's colour alone.
    $desktop = [Environment]::GetFolderPath('Desktop')
    $local = Join-Path $env:LOCALAPPDATA 'RizonesoftOffice'
    New-Item -ItemType Directory -Force -Path $local | Out-Null
    $plain = Join-Path $root 'assets\icons\windows\rizonesoft-office.ico'
    $shortcuts = @(
        @{ Runner = 'claude'; Name = 'Office Claude campaign'; Icon = 'office-campaign-claude.ico'; Fill = '#D97757'; Mark = 'claude.svg'
           Description = 'Start the unattended Rizonesoft Office campaign in Claude Code' },
        @{ Runner = 'agy'; Name = 'Office Carbon campaign'; Icon = 'office-campaign-carbon.ico'; Fill = '#4C8DF6'; Mark = 'gemini.svg'
           Description = 'Start the unattended Rizonesoft Office campaign in Google Antigravity on Gemini 4 Carbon' }
    )
    foreach ($s in $shortcuts) {
        $icon = Join-Path $local $s.Icon
        python (Join-Path $PSScriptRoot 'campaign-icon.py') $icon $s.Fill (Join-Path $local "marks\$($s.Mark)")
        if ($LASTEXITCODE -ne 0) {
            Write-Host "The badged icon for '$($s.Name)' could not be rendered (python -m pip install -r scripts/requirements.txt, then this again); the shortcut carries the plain suite icon." -ForegroundColor Yellow
            $icon = $plain
        }
        $link = Join-Path $desktop "$($s.Name).lnk"
        $shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($link)
        $shortcut.TargetPath = (Get-Process -Id $PID).Path
        $shortcut.Arguments = "-NoLogo -NoExit -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Runner $($s.Runner)"
        $shortcut.WorkingDirectory = $root
        $shortcut.IconLocation = "$icon,0"
        $shortcut.Description = $s.Description
        # 1 is a normal window (3 would open it maximised); owner, 2026-11-11.
        $shortcut.WindowStyle = 1
        $shortcut.Save()
        Write-Host "Shortcut written: $link"
    }
    # The one shortcut this file wrote before the runners had one each started Claude Code without saying so.
    $old = Join-Path $desktop 'Rizonesoft Office campaign.lnk'
    if (Test-Path -LiteralPath $old) {
        Remove-Item -LiteralPath $old
        Write-Host "Removed the earlier shortcut: $old"
    }
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

$runnerName = @{ claude = 'Claude Code'; agy = 'Google Antigravity (Gemini 4 Carbon)' }[$Runner]
$Host.UI.RawUI.WindowTitle = @{ claude = 'Office Claude campaign'; agy = 'Office Carbon campaign' }[$Runner]

# The lock is taken as the first statement inside one try that runs to the end of the file, so nothing can
# happen between taking it and being sure it is given back: a normal end, an exit, an error anywhere below
# (writing the record included), or Ctrl+C at a prompt all pass through the finally. The shortcut's window
# stays open afterwards (-NoExit), and a lock it still held would refuse the next start.
function Stop-CampaignProcesses {
    # Everything the campaign started, ended by the job it was born into: before the next session starts, and before
    # this launcher gives up the lock while its window stays open (the shortcut's -NoExit), so no process of an
    # ended session is ever still writing when another start is admitted (decision 43).
    if (-not $script:campaignJob -or $script:campaignJob -eq [IntPtr]::Zero) { return }
    $left = [Office.CampaignJob]::EndOthers($script:campaignJob, 20)
    if ($left -ne 0) {
        Write-Host "Some of what the campaign started could not be ended ($left); close this window to end it." -ForegroundColor Red
    }
}
function Remove-OwnRecord {
    # Only this launcher's own record is removed, never one another launcher wrote. The lock is released here too,
    # by closing it, and not left to the end of the process: the shortcut keeps its window open (-NoExit) after
    # the launcher has finished, and a lock still held by that idle window would refuse the next start.
    Stop-CampaignProcesses
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
        Write-Host "Not started: a campaign launcher is already running$which. Ask its session to stop, run this file with -Stop, or close its window." -ForegroundColor Red
        exit 3
    }
    # Closing the window ends everything the campaign started (owner, 2026-11-12; decision 43). This process joins
    # a job object that Windows ends, with every process in it, when its last handle closes; this process holds the
    # only handle, so however the window goes (closed, ended, a crash) the session and all it started go with it,
    # including a child that left the console. Every process started from here on is born into the job.
    if (-not ('Office.CampaignJob' -as [type])) {
        Add-Type -Namespace Office -Name CampaignJob -MemberDefinition @'
[DllImport("kernel32.dll", SetLastError = true)] static extern IntPtr CreateJobObject(IntPtr attributes, string name);
[DllImport("kernel32.dll", SetLastError = true)] static extern bool SetInformationJobObject(IntPtr job, int infoClass, IntPtr info, uint length);
[DllImport("kernel32.dll", SetLastError = true)] static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);
[DllImport("kernel32.dll")] static extern IntPtr GetCurrentProcess();
[DllImport("kernel32.dll")] static extern uint GetCurrentProcessId();
[DllImport("kernel32.dll", SetLastError = true)] static extern bool QueryInformationJobObject(IntPtr job, int infoClass, IntPtr info, uint length, IntPtr returned);
[DllImport("kernel32.dll", SetLastError = true)] static extern IntPtr OpenProcess(uint access, bool inherit, uint pid);
[DllImport("kernel32.dll", SetLastError = true)] static extern bool TerminateProcess(IntPtr process, uint exitCode);
[DllImport("kernel32.dll", SetLastError = true)] static extern uint WaitForSingleObject(IntPtr handle, uint milliseconds);
[DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr handle);
// Ends every process in the job except this one, and returns how many are still there after `seconds`.
public static int EndOthers(IntPtr job, int seconds) {
    const int room = 4096;                              // process numbers read at once
    int size = 8 + room * IntPtr.Size;                  // JOBOBJECT_BASIC_PROCESS_ID_LIST
    IntPtr list = Marshal.AllocHGlobal(size);
    try {
        uint self = GetCurrentProcessId();
        DateTime deadline = DateTime.UtcNow.AddSeconds(seconds);
        while (true) {
            if (!QueryInformationJobObject(job, 3, list, (uint)size, IntPtr.Zero)) return -1;
            int listed = Marshal.ReadInt32(list, 4), others = 0;
            for (int i = 0; i < listed; i++) {
                uint pid = (uint)Marshal.ReadIntPtr(list, 8 + i * IntPtr.Size).ToInt64();
                if (pid == self) continue;
                others++;
                IntPtr process = OpenProcess(0x00100001, false, pid);   // SYNCHRONIZE | PROCESS_TERMINATE
                if (process == IntPtr.Zero) continue;
                TerminateProcess(process, 1);
                WaitForSingleObject(process, 2000);
                CloseHandle(process);
            }
            if (others == 0 || DateTime.UtcNow > deadline) return others;
        }
    } finally { Marshal.FreeHGlobal(list); }
}
// Returns the job's handle, which the caller keeps for the life of the process, or zero with the Win32 error.
public static IntPtr Join(out int error) {
    error = 0;
    IntPtr job = CreateJobObject(IntPtr.Zero, null);
    if (job == IntPtr.Zero) { error = Marshal.GetLastWin32Error(); return IntPtr.Zero; }
    int size = IntPtr.Size == 8 ? 144 : 112;          // JOBOBJECT_EXTENDED_LIMIT_INFORMATION
    IntPtr info = Marshal.AllocHGlobal(size);
    try {
        for (int i = 0; i < size; i++) Marshal.WriteByte(info, i, 0);
        Marshal.WriteInt32(info, 16, 0x2000);          // LimitFlags: JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if (!SetInformationJobObject(job, 9, info, (uint)size) || !AssignProcessToJobObject(job, GetCurrentProcess())) {
            error = Marshal.GetLastWin32Error(); return IntPtr.Zero;
        }
    } finally { Marshal.FreeHGlobal(info); }
    return job;
}
'@
    }
    $jobError = 0
    $script:campaignJob = [Office.CampaignJob]::Join([ref]$jobError)
    if ($script:campaignJob -eq [IntPtr]::Zero) {
        Write-Host "Not started: this window could not be made the owner of what the campaign starts (Windows error $jobError), so closing it would leave processes running." -ForegroundColor Red
        Exit-Launcher 4
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

$missing = @($Runner, 'python', 'git', 'gh', 'node') | Where-Object { -not (Get-Command $_ -ErrorAction SilentlyContinue) }
if ($missing) {
    Write-Host "Not started: not on PATH: $($missing -join ', ')" -ForegroundColor Red
    Exit-Launcher 2
}

# The pinned build tools (D00 T04 §4). The bootstrap runs before the host check, and a failure never stops a start:
# a section that needs a tool runs the bootstrap itself and fails at its own gate. A dry run installs nothing.
if ($DryRun) {
    Write-Host 'Build tools: a real start runs python scripts/bootstrap-tools.py first.'
} else {
    python scripts/bootstrap-tools.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build tools: the bootstrap failed (exit $LASTEXITCODE); the start goes on, and a section that needs a tool runs it again at its own gate." -ForegroundColor Yellow
    }
}
# The installed tools' folders go first on this process's PATH, which the session and everything it starts inherit
# (never the user's PATH). After a partial bootstrap --bin-dirs still prints every usable folder and exits 1: each
# printed folder is kept, and each problem it reports is shown, never put on PATH.
$toolDirs = @(python scripts/bootstrap-tools.py --bin-dirs 2>&1 | ForEach-Object {
    if ($_ -is [System.Management.Automation.ErrorRecord]) { Write-Host "Build tools: $_" -ForegroundColor Yellow }
    elseif ("$_" -and (Test-Path -LiteralPath "$_" -PathType Container)) { "$_" }
})
function Test-Holds([string]$Folder, [string]$Program) {
    if (-not $Folder) { return $false }
    try { return [System.IO.File]::Exists([System.IO.Path]::Combine($Folder, $Program)) } catch { return $false }
}
$env:PATH = (@($toolDirs) + @($env:PATH -split ';' | Where-Object { $_ })) -join ';'
$pinnedClangd = @($toolDirs | Where-Object { Test-Holds $_ 'clangd.exe' })
# Settings for this session only, layered over .claude/settings.json by claude's --settings.
$sessionArgs = @()
if ($Runner -ne 'claude') {
    # The clangd-lsp plugin and its setting are Claude Code's; another runner takes no session settings from here.
} elseif ($pinnedClangd) {
    Write-Host "clangd: $(Join-Path $pinnedClangd[0] 'clangd.exe')"
} else {
    # The clangd-lsp plugin would start whichever clangd PATH gives, so without the pinned one it is switched off
    # for this session: the plugin's own setting, and PATH stays whole for every other command.
    $sessionSettings = Join-Path $root 'build/campaign-session-settings.json'
    New-Item -ItemType Directory -Force -Path (Join-Path $root 'build') | Out-Null
    $partial = "$sessionSettings.tmp"
    Set-Content -LiteralPath $partial -Value '{"enabledPlugins": {"clangd-lsp@claude-plugins-official": false}}'
    Move-Item -LiteralPath $partial -Destination $sessionSettings -Force
    $sessionArgs = @('--settings', $sessionSettings)
    Write-Host 'clangd: none (the pinned clangd is not installed: run python scripts/bootstrap-tools.py). The clangd-lsp plugin is off for this session, so no other clangd is used.' -ForegroundColor Yellow
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
$goal = '/goal Rizonesoft Office is finished: every row of todo/implementation-plan.md is stamped (python scripts/todo-graph.py query stats shows verified equal to total), every phase has its closeout, CI is green on the pushed HEAD, and each of the six apps has its draft release. Until then, work as an unattended campaign: run the process-plan skill (.claude/skills/process-plan/SKILL.md) now and follow it exactly, with its Unattended rules (never ask a question; decide, record and carry on), its run guard and heartbeat, its host readiness check and its CI watch, working as the lead AGENTS.md (Subagents) describes: build each section and each round of review fixes yourself in this session, use the Sonnet readers for facts and suites (no agent writes: every section, every round of review fixes and every architecture decision record is yours to build), and run every gate yourself. Aim for excellence in every section: this must be the best product in its class, measurably better than Microsoft Office and never a clone (docs/product-principles.md), with no shortcut taken where the harder, better version is possible. Act with full autonomy, as the owner would and better: decide what can be worked out instead of asking, improve the plan, skills, agents, tools and methods whenever they could be better, repair the run''s own failures at their cause, and never plan less because something is hard or no competitor does it. The operator started this session from the desktop shortcut: that is the operator''s word to start or resume the campaign, and to take over a guard left by an earlier session with acquire --handover. The goal also counts as met when the campaign has ended by its own rules, in one of two ways. First, an operator stop: the operator asked for a stop, in words in this session or through build/campaign-stop-request, campaign_guard.py end --reason operator-stop has run and the stop is recorded in the run file. An operator stop is always honoured: the goal is then met, so report where the run stands and end the turn, and do not start or continue any work after it. Second, a park: a column-0 PARKED line stands in the run file and campaign_guard.py end has run, because every remaining row waits on the owner, the operator, a third party or a host that is not ready, or CI could not be made green inside its recovery budget. After a park finish with a report of each leftover row and what the owner must do to release it.'

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
$token = if ($Runner -eq 'claude') { Read-StoredToken } else { $null }
if ($Runner -ne 'claude') {
    # Antigravity signs in with its own local Google account; Claude's token is never put in its environment.
    Write-Host "Sign-in: $runnerName's own account on this PC."
} elseif ($token) {
    $env:CLAUDE_CODE_OAUTH_TOKEN = $token
    Write-Host 'Sign-in: the one-year token from .secrets/office.env.'
} else {
    Write-Host 'Sign-in: the interactive one (no token in .secrets/office.env; run python scripts/import-secrets.py).' -ForegroundColor Yellow
}
$token = $null

# The lead model is the measurement's verdict, never a choice made here (owner decision 30; D00 T03 §37):
# scripts/measure-modes.py decide stores it in .conclave/operating-mode.json as a Claude Code alias, so a new release
# of that family is picked up at the next start with no edit; never pin a version such as claude-opus-5-5. The lead
# builds each section itself whichever model it is (owner, 2026-11-11; AGENTS.md, Subagents). 'opus' is the fallback
# for a missing or unreadable verdict: the 2026-11-10 measurement's winner.
$model = 'opus'
$modeFile = Join-Path $root '.conclave/operating-mode.json'
$modeSource = 'the fallback (no readable verdict)'
if (Test-Path -LiteralPath $modeFile) {
    try {
        $stored = (Get-Content -LiteralPath $modeFile -Raw | ConvertFrom-Json).model
        # Only an alias reaches the command line: anything else in the file is ignored, never passed to claude.
        if ($stored -is [string] -and $stored -match '^[a-z][a-z0-9-]{0,39}$') {
            $model = $stored
            $modeSource = '.conclave/operating-mode.json'
        }
    } catch {
        $modeSource = 'the fallback (the verdict file does not parse)'
    }
}
# Claude Code runs at medium effort (owner, 2026-11-12). Antigravity's model name carries its effort; it is the
# writer the owner named for that runner, Gemini 4 Carbon at medium, and the measured verdict above is Claude's alone.
$effort = 'medium'
$carbon = 'gemini-4-carbon-medium'
if ($Runner -eq 'claude') { Write-Host "Lead model: $model at $effort effort, from $modeSource" }
else { Write-Host "Lead model: $carbon in $runnerName" }

if ($DryRun) {
    if (Test-Path -LiteralPath $stopFile) { Write-Host 'A stop request is present; a real start removes it.' }
    Write-Host ''
    Write-Host "Would run in ${root}:"
    if ($Runner -eq 'claude') {
        Write-Host ((@('claude', '--model', $model, '--effort', $effort, '--dangerously-skip-permissions') + $sessionArgs + "`"$goal`"") -join ' ')
    } else {
        Write-Host ((@('agy', '--model', $carbon, '--dangerously-skip-permissions', '-i', "`"$goal`"")) -join ' ')
    }
    exit 0
}

$started = [System.Collections.Generic.List[datetime]]::new()
while ($true) {
    # Checked immediately before every launch: a stop asked for during the checks above, or during the wait and
    # the host check below, must never be followed by a new session.
    if (Test-StopRequested) { break }
    $started.Add((Get-Date))
    if ($Runner -eq 'claude') {
        claude --model $model --effort $effort --dangerously-skip-permissions @sessionArgs $goal
    } else {
        # -i runs the opening prompt and keeps the conversation open, as Claude Code does with its prompt argument.
        agy --model $carbon --dangerously-skip-permissions -i $goal
    }
    $sessionExit = $LASTEXITCODE
    Stop-CampaignProcesses  # a session that ended leaves nothing running, whatever follows
    if (Test-StopRequested) { break }
    if (-not (Test-Path -LiteralPath $guard)) {
        Write-Host ''
        Write-Host 'The campaign ended by its own rules: no run guard is held. Run this shortcut to start it again.'
        break
    }
    # A run starts only when the owner starts it (owner, 2026-11-12; decision 43): the next session follows in this
    # window only after a clean exit. A session that crashed or ended with an error is never started again here.
    if ($sessionExit -ne 0) {
        Write-Host ''
        Write-Host "Stopped: the session ended with exit $sessionExit (a crash or an error) while the run was still open. Nothing starts it again: read what it last said, then run this shortcut to carry on." -ForegroundColor Red
        break
    }
    if (@($started | Where-Object { $_ -gt (Get-Date).AddHours(-1) }).Count -ge 5) {
        Write-Host ''
        Write-Host 'Stopped: five sessions ended inside an hour with the run still open. Read the last one before starting again.' -ForegroundColor Red
        break
    }
    Write-Host ''
    Write-Host "The session ended cleanly with the run still open. A new session starts in $RestartSeconds seconds; close this window or press Ctrl+C to stop." -ForegroundColor Yellow
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
