# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
#Requires -Version 7.0
<#
.SYNOPSIS
  Proves on this PC that Task Scheduler starts a failed launch again by itself (D00 T07 §4).
.DESCRIPTION
  Registers one scratch task, \Office\office-retry-selftest, with the settings install.ps1 gives the real tasks
  (New-OfficeTaskSettings, at the one-minute interval Task Scheduler allows as its shortest), and a working
  directory that does not exist: the 0x8007010B the real tasks ended with on 2026-11-09, before run.py started.
  It never touches a task tasks.json lists.

  Pass 1, recovery: the task is started once; the script waits for Task Scheduler to start it again unasked,
  then creates the directory and waits for the next retry to write its marker file.
  Pass 2, the limit: the directory stays missing; the launches are counted until none has come for two and a
  half intervals, and the count must be one start plus RestartCount retries.

  The task, its directory and its marker are removed however the script ends. Exit 0 when both passes hold,
  1 when one does not, with every launch printed as it is seen.
#>
[CmdletBinding()]
param([ValidateRange(1, 5)][int]$RestartCount = 3)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
. (Join-Path $PSScriptRoot 'task-settings.ps1')

$folder = '\Office\'
$name = 'office-retry-selftest'
$scratch = Join-Path ([System.IO.Path]::GetTempPath()) "office-retry-selftest-$PID"
$marker = "$scratch.marker.txt"
$intervalSeconds = 60  # Task Scheduler's shortest restart interval

function Get-Launch {
  $info = Get-ScheduledTask -TaskPath $folder -TaskName $name | Get-ScheduledTaskInfo
  '{0:HH:mm:ss} 0x{1:X}' -f $info.LastRunTime, $info.LastTaskResult
}

function Register-Selftest {
  $action = New-ScheduledTaskAction -Execute (Join-Path $env:SystemRoot 'System32\cmd.exe') `
      -Argument "/c echo ran> `"$marker`"" -WorkingDirectory $scratch
  $settings = New-OfficeTaskSettings -TimeoutMinutes 5 -RestartCount $RestartCount -RestartMinutes 1
  $user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
  $principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
  Register-ScheduledTask -TaskPath $folder -TaskName $name -Action $action -Settings $settings `
      -Principal $principal -Force | Out-Null
  $stored = (Get-ScheduledTask -TaskPath $folder -TaskName $name).Settings
  Write-Host "registered $folder$name; read back: RestartCount $($stored.RestartCount), RestartInterval $($stored.RestartInterval)"
  if ($stored.RestartCount -ne $RestartCount -or $stored.RestartInterval -ne 'PT1M') {
    throw "Task Scheduler stored RestartCount $($stored.RestartCount) and RestartInterval $($stored.RestartInterval), not $RestartCount and PT1M"
  }
}

function Remove-Selftest {
  Unregister-ScheduledTask -TaskPath $folder -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
  Remove-Item -LiteralPath $marker -Force -ErrorAction SilentlyContinue
  Remove-Item -LiteralPath $scratch -Recurse -Force -ErrorAction SilentlyContinue
}

# Watches the task until $Until returns true or $Seconds pass; returns the distinct launches seen, in order.
function Watch-Launches([int]$Seconds, [scriptblock]$Until) {
  $seen = [System.Collections.Generic.List[string]]::new()
  $deadline = (Get-Date).AddSeconds($Seconds)
  while ((Get-Date) -lt $deadline) {
    $launch = Get-Launch
    if (-not $seen.Contains($launch)) {
      $seen.Add($launch)
      Write-Host "  launch $($seen.Count): $launch"
    }
    if (& $Until $seen) { break }
    Start-Sleep -Seconds 3
  }
  return , $seen
}

$failed = $false
try {
  Remove-Selftest  # nothing of an earlier, interrupted run is left behind

  Write-Host 'Pass 1, recovery: the working directory is missing, then appears.'
  Register-Selftest
  Start-ScheduledTask -TaskPath $folder -TaskName $name
  $first = Watch-Launches (3 * $intervalSeconds) { param($seen) $seen.Count -ge 2 }
  if ($first.Count -lt 2) {
    Write-Host 'FAILED: Task Scheduler did not start the failed launch again.' -ForegroundColor Red
    $failed = $true
  } elseif (@($first | Where-Object { $_ -notmatch ' 0x8007010B$' })) {
    Write-Host "FAILED: the launches did not fail with 0x8007010B: $($first -join ', ')" -ForegroundColor Red
    $failed = $true
  } else {
    New-Item -ItemType Directory -Path $scratch -Force | Out-Null
    Write-Host "  the directory now exists; waiting for the next retry"
    $after = Watch-Launches (3 * $intervalSeconds) { param($seen) Test-Path -LiteralPath $marker }
    if (Test-Path -LiteralPath $marker) {
      Write-Host "  the retry ran: marker written, last launch $(Get-Launch)"
    } else {
      Write-Host 'FAILED: no retry ran once the directory existed.' -ForegroundColor Red
      $failed = $true
    }
  }
  Remove-Selftest

  Write-Host "Pass 2, the limit: the directory stays missing; one start and $RestartCount retries are expected."
  Register-Selftest
  Start-ScheduledTask -TaskPath $folder -TaskName $name
  $quietSince = Get-Date
  $counted = 0
  $all = Watch-Launches (($RestartCount + 4) * $intervalSeconds) {
    param($seen)
    if ($seen.Count -ne $script:counted) { $script:counted = $seen.Count; $script:quietSince = Get-Date }
    ((Get-Date) - $script:quietSince).TotalSeconds -gt 2.5 * $intervalSeconds
  }
  $expected = 1 + $RestartCount
  if ($all.Count -eq $expected) {
    Write-Host "  $($all.Count) launches, then none for $([int](2.5 * $intervalSeconds)) seconds: the limit holds"
  } else {
    Write-Host "FAILED: $($all.Count) launches were seen, not $expected." -ForegroundColor Red
    $failed = $true
  }
} finally {
  Remove-Selftest
  $left = Get-ScheduledTask -TaskPath $folder -TaskName $name -ErrorAction SilentlyContinue
  Write-Host "scratch task removed: $(-not $left)"
}
if ($failed) { exit 1 }
Write-Host 'Both passes hold: a failed launch is started again by Task Scheduler, up to the limit.'
exit 0
