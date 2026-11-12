# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
# The settings every Office scheduled task is registered with, in one place: install.ps1 uses them for the real
# tasks and check-task-retry.ps1 for its scratch task, so what is proved is what is installed (D00 T07 §4).

# A launch that fails before run.py starts (2026-11-09: 0x8007010B twice, two minutes after Windows logged that it
# was out of virtual memory) is started again by Task Scheduler itself: RestartCount more attempts, RestartMinutes
# apart. Task Scheduler takes no interval under one minute.
$OfficeTaskRestartCount = 3
$OfficeTaskRestartMinutes = 10

function New-OfficeTaskSettings {
  param([Parameter(Mandatory)][int]$TimeoutMinutes,
        [int]$RestartCount = $OfficeTaskRestartCount,
        [int]$RestartMinutes = $OfficeTaskRestartMinutes)
  New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew `
      -ExecutionTimeLimit (New-TimeSpan -Minutes ($TimeoutMinutes + 5)) `
      -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
      -RestartCount $RestartCount -RestartInterval (New-TimeSpan -Minutes $RestartMinutes)
}
