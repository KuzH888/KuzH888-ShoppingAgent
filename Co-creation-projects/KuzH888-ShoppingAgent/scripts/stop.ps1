[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeFile = Join-Path $projectRoot ".runtime\processes.json"

if (-not (Test-Path -LiteralPath $runtimeFile -PathType Leaf)) {
    Write-Host "No tracked KuzMall processes were found."
    Write-Host "If services were started manually, close their terminal windows manually."
    exit 0
}

$runtime = Get-Content -LiteralPath $runtimeFile -Raw | ConvertFrom-Json
$startedAt = [datetime]::Parse($runtime.started_at).ToUniversalTime().AddSeconds(-2)
$handledIds = [System.Collections.Generic.HashSet[int]]::new()

foreach ($entry in @(
    @{ Name = "frontend listener"; Id = $runtime.frontend_listener_pid },
    @{ Name = "frontend"; Id = $runtime.frontend_pid },
    @{ Name = "backend listener"; Id = $runtime.backend_listener_pid },
    @{ Name = "backend"; Id = $runtime.backend_pid }
)) {
    if ($null -eq $entry.Id) {
        continue
    }
    $processId = [int]$entry.Id
    if (-not $handledIds.Add($processId)) {
        continue
    }
    $trackedProcess = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($null -eq $trackedProcess) {
        Write-Host "[OK] $($entry.Name) was already stopped."
        continue
    }
    if ($trackedProcess.StartTime.ToUniversalTime() -lt $startedAt) {
        Write-Warning "Skipped PID $($entry.Id) because it is older than this KuzMall run."
        continue
    }
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Stopped $($entry.Name)."
}

Remove-Item -LiteralPath $runtimeFile -Force
Write-Host "KuzMall tracked services have been stopped."
