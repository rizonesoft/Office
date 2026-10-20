#Requires -Version 7.0
<#
.SYNOPSIS
  Registers the Office automations in Windows Task Scheduler, under \Office\.
.DESCRIPTION
  Reads every task from tasks.json (the one list; nothing here names a task) and registers it to run
  `pythonw.exe .conclave\automations\run.py <name>` from this repository, as the signed-in user, only while
  that user is logged on (no stored password). Idempotent: re-run it after editing tasks.json. A task in the
  \Office\ folder that tasks.json no longer lists is unregistered.

  Settings on every task: start when available (a run missed while the PC was off fires at the next chance,
  as systemd's Persistent=true does), ignore a new start while one runs, an execution limit five minutes past
  the task's timeout, and run on battery. Daily and weekly tasks carry a five-minute random delay.
.EXAMPLE
  pwsh .conclave/automations/install.ps1
  pwsh .conclave/automations/install.ps1 -Uninstall
  pwsh .conclave/automations/install.ps1 -DryRun     # print what would be registered and removed, change nothing
#>
[CmdletBinding()]
param([switch]$Uninstall, [switch]$DryRun)
$ErrorActionPreference = 'Stop'

$here = $PSScriptRoot
$repo = (Resolve-Path (Join-Path $here '..\..')).Path
# Validate the whole manifest with the runner's own rules before any task is read, registered or removed, so a
# bad folder or name can never point the installer at someone else's tasks.
$python = (Get-Command python.exe -ErrorAction Ignore).Source
if (-not $python) { throw 'python.exe is not on PATH; install Python 3 for Windows first' }
& $python (Join-Path $here 'run.py') --validate
if ($LASTEXITCODE -ne 0) { throw 'tasks.json is not valid; nothing was changed' }
$manifest = Get-Content -Raw -Path (Join-Path $here 'tasks.json') | ConvertFrom-Json
$folder = '\Office\'
if ($manifest.folder -ne $folder) { throw "tasks.json folder must be $folder; nothing was changed" }
$existing = @(Get-ScheduledTask | Where-Object TaskPath -eq $folder)

if ($DryRun -and $Uninstall) {
  foreach ($task in $existing) { Write-Host "would remove $folder$($task.TaskName)" }
  Write-Host "$($existing.Count) task(s) under $folder; nothing changed"
  return
}

if ($DryRun) {
  $listed = @($manifest.tasks | ForEach-Object { $_.name })
  foreach ($task in $manifest.tasks) { Write-Host "would register $folder$($task.name)" }
  foreach ($task in $existing) { if ($listed -notcontains $task.TaskName) { Write-Host "would remove $folder$($task.TaskName)" } }
  Write-Host "$($manifest.tasks.Count) task(s) listed in tasks.json; nothing changed"
  return
}

if ($Uninstall) {
  foreach ($task in $existing) { Unregister-ScheduledTask -TaskPath $folder -TaskName $task.TaskName -Confirm:$false }
  Write-Host "Removed $($existing.Count) task(s) from $folder"
  return
}

$pythonw = (Get-Command pythonw.exe -ErrorAction Ignore).Source  # absent is the throw below
if (-not $pythonw) { throw 'pythonw.exe is not on PATH; install Python 3 for Windows first' }
$runner = Join-Path $here 'run.py'
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited

foreach ($task in $manifest.tasks) {
  $action = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$runner`" $($task.name)" -WorkingDirectory $repo
  $trigger = $task.trigger
  if ($null -ne $trigger.every_minutes) {
    # One run shortly after each logon (no repetition), and one repeating schedule from install onward that
    # keeps ticking across logons. Two repeating triggers would fire the task twice per interval.
    $every = New-TimeSpan -Minutes $trigger.every_minutes
    $logon = New-ScheduledTaskTrigger -AtLogOn -User $user
    $logon.Delay = "PT$($trigger.at_logon_delay_minutes)M"
    $t = @($logon, (New-ScheduledTaskTrigger -Once -At (Get-Date).Add($every) -RepetitionInterval $every))
  } elseif ($null -ne $trigger.daily_at) {
    $t = New-ScheduledTaskTrigger -Daily -At $trigger.daily_at -RandomDelay (New-TimeSpan -Minutes 5)
  } else {
    $t = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $trigger.weekly -At $trigger.at -RandomDelay (New-TimeSpan -Minutes 5)
  }
  $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew `
      -ExecutionTimeLimit (New-TimeSpan -Minutes ($task.timeout_minutes + 5)) `
      -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
  Register-ScheduledTask -TaskPath $folder -TaskName $task.name -Description $task.description `
      -Action $action -Trigger $t -Settings $settings -Principal $principal -Force | Out-Null
}

$listed = @($manifest.tasks | ForEach-Object { $_.name })
foreach ($task in $existing) {
  if ($listed -notcontains $task.TaskName) {
    Unregister-ScheduledTask -TaskPath $folder -TaskName $task.TaskName -Confirm:$false
    Write-Host "Removed $($task.TaskName): tasks.json no longer lists it"
  }
}
# Filtered rather than -TaskPath: the folder does not exist until a task is registered, and -TaskPath on a
# missing folder is an error, which would fail an install of an empty task list on a clean machine.
$now = @(Get-ScheduledTask | Where-Object TaskPath -eq $folder)
if ($now.Count -eq 0) { Write-Host "No tasks registered under $folder" }
else { $now | Get-ScheduledTaskInfo | Select-Object TaskName, NextRunTime, LastRunTime, LastTaskResult | Format-Table -AutoSize }
