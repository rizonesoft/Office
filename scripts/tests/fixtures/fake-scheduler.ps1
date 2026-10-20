# Stand-ins for the ScheduledTasks commands, so the real install.ps1 can be tested without touching Task Scheduler.
$ErrorActionPreference = 'Stop'
function Get-ScheduledTask { param($TaskPath)
  $all = @((Get-Content -Raw $env:FAKE_EXISTING | ConvertFrom-Json) | ForEach-Object { [pscustomobject]@{TaskPath = $_.path; TaskName = $_.name} })
  if ($PSBoundParameters.ContainsKey('TaskPath')) {
    $hit = @($all | Where-Object TaskPath -eq $TaskPath)
    if ($hit.Count -eq 0) { throw "No MSFT_ScheduledTask objects found with property 'TaskPath' equal to '$TaskPath'" }
    return $hit
  }
  $all }
function New-ScheduledTaskAction { param($Execute, $Argument, $WorkingDirectory) [pscustomobject]@{Execute = $Execute; Argument = $Argument} }
function New-ScheduledTaskTrigger { param([switch]$AtLogOn, $User, [switch]$Once, $At, $RepetitionInterval, [switch]$Daily, [switch]$Weekly, $DaysOfWeek, $RandomDelay)
  [pscustomobject]@{AtLogOn = [bool]$AtLogOn; Once = [bool]$Once; Daily = [bool]$Daily; Weekly = [bool]$Weekly; Repeat = "$RepetitionInterval"; Delay = $null; Days = "$DaysOfWeek"; At = "$At"} }
function New-ScheduledTaskSettingsSet { param([switch]$StartWhenAvailable, $MultipleInstances, $ExecutionTimeLimit, [switch]$AllowStartIfOnBatteries, [switch]$DontStopIfGoingOnBatteries)
  [pscustomobject]@{Limit = "$ExecutionTimeLimit"; Instances = "$MultipleInstances"} }
function New-ScheduledTaskPrincipal { param($UserId, $LogonType, $RunLevel) [pscustomobject]@{LogonType = "$LogonType"} }
function Register-ScheduledTask { param($TaskPath, $TaskName, $Description, $Action, $Trigger, $Settings, $Principal, [switch]$Force)
  Add-Content $env:FAKE_LOG (ConvertTo-Json -Compress -Depth 5 @{op = 'register'; path = $TaskPath; name = $TaskName; triggers = @($Trigger); limit = $Settings.Limit; logon = $Principal.LogonType}) }
function Unregister-ScheduledTask { param($TaskPath, $TaskName, [switch]$Confirm)
  Add-Content $env:FAKE_LOG (ConvertTo-Json -Compress @{op = 'unregister'; path = $TaskPath; name = $TaskName}) }
  $left = @((Get-Content -Raw $env:FAKE_EXISTING | ConvertFrom-Json) | Where-Object { -not ($_.path -eq $TaskPath -and $_.name -eq $TaskName) })
  ConvertTo-Json -InputObject $left -Compress | Set-Content $env:FAKE_EXISTING
function Get-ScheduledTaskInfo { param([Parameter(ValueFromPipeline)]$InputObject) process { [pscustomobject]@{TaskName = $InputObject.TaskName; NextRunTime = $null; LastRunTime = $null; LastTaskResult = 0} } }
& $env:FAKE_SCRIPT @args
