[CmdletBinding()]
param(
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $projectRoot "frontend"
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$runtimeRoot = Join-Path $projectRoot ".runtime"
$logRoot = Join-Path $projectRoot "outputs\logs"
$runtimeFile = Join-Path $runtimeRoot "processes.json"
$runStartedAt = (Get-Date).ToUniversalTime()

function Get-ListenerProcessId {
    param([int]$Port)

    foreach ($line in @(netstat -ano -p TCP)) {
        if ($line -match "^\s*TCP\s+127\.0\.0\.1:$Port\s+\S+\s+LISTENING\s+(\d+)\s*$") {
            return [int]$Matches[1]
        }
    }
    return $null
}

function Test-KuzMallApi {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2
        return $health.status -eq "ok" -and $health.service -eq "KuzH888 ShoppingAgent API"
    }
    catch {
        return $false
    }
}

function Test-KuzMallFrontend {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:5173/" -TimeoutSec 2
        return $response.StatusCode -eq 200 -and $response.Content -match "KuzMall"
    }
    catch {
        return $false
    }
}

function Wait-UntilReady {
    param(
        [scriptblock]$Probe,
        [string]$ServiceName,
        [System.Diagnostics.Process]$Process,
        [int]$Attempts = 40
    )

    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        if (& $Probe) {
            return
        }
        if ($null -ne $Process -and $Process.HasExited) {
            throw "$ServiceName failed to start. Check outputs/logs for details."
        }
        Start-Sleep -Milliseconds 500
    }
    throw "$ServiceName did not become ready within 20 seconds. Check outputs/logs for details."
}

if (-not (Test-Path -LiteralPath $pythonExe -PathType Leaf)) {
    throw "Project Python was not found at $pythonExe. Create the .venv and install requirements first."
}
if (-not (Test-Path -LiteralPath (Join-Path $frontendRoot "node_modules") -PathType Container)) {
    throw "Frontend dependencies are missing. Run 'npm install' inside the frontend folder first."
}

$npmCommand = Get-Command "npm.cmd" -ErrorAction Stop
New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null

$backendProcess = $null
$frontendProcess = $null
$startedProcesses = [System.Collections.Generic.List[System.Diagnostics.Process]]::new()

try {
    if (Test-KuzMallApi) {
        Write-Host "[OK] FastAPI is already running at http://127.0.0.1:8000"
    }
    else {
        $backendProcess = Start-Process `
            -FilePath $pythonExe `
            -ArgumentList @("-m", "uvicorn", "src.api.app:app", "--host", "127.0.0.1", "--port", "8000") `
            -WorkingDirectory $projectRoot `
            -RedirectStandardOutput (Join-Path $logRoot "backend.stdout.log") `
            -RedirectStandardError (Join-Path $logRoot "backend.stderr.log") `
            -WindowStyle Hidden `
            -PassThru
        $startedProcesses.Add($backendProcess)
        Wait-UntilReady -Probe ${function:Test-KuzMallApi} -ServiceName "FastAPI backend" -Process $backendProcess
        Write-Host "[OK] FastAPI started at http://127.0.0.1:8000"
    }

    if (Test-KuzMallFrontend) {
        Write-Host "[OK] Vite is already running at http://127.0.0.1:5173"
    }
    else {
        $frontendProcess = Start-Process `
            -FilePath $npmCommand.Source `
            -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1", "--port", "5173") `
            -WorkingDirectory $frontendRoot `
            -RedirectStandardOutput (Join-Path $logRoot "frontend.stdout.log") `
            -RedirectStandardError (Join-Path $logRoot "frontend.stderr.log") `
            -WindowStyle Hidden `
            -PassThru
        $startedProcesses.Add($frontendProcess)
        Wait-UntilReady -Probe ${function:Test-KuzMallFrontend} -ServiceName "Vite frontend" -Process $frontendProcess
        Write-Host "[OK] Vite started at http://127.0.0.1:5173"
    }

    $runtime = [ordered]@{
        started_at = $runStartedAt.ToString("o")
        backend_pid = if ($null -ne $backendProcess) { $backendProcess.Id } else { $null }
        backend_listener_pid = if ($null -ne $backendProcess) { Get-ListenerProcessId -Port 8000 } else { $null }
        frontend_pid = if ($null -ne $frontendProcess) { $frontendProcess.Id } else { $null }
        frontend_listener_pid = if ($null -ne $frontendProcess) { Get-ListenerProcessId -Port 5173 } else { $null }
    }
    $runtime | ConvertTo-Json | Set-Content -LiteralPath $runtimeFile -Encoding utf8

    & (Join-Path $PSScriptRoot "check.ps1")

    if (-not $NoBrowser) {
        Start-Process "http://127.0.0.1:5173/"
    }

    Write-Host ""
    Write-Host "KuzMall is ready. Run scripts\stop.ps1 when you finish."
}
catch {
    foreach ($process in $startedProcesses) {
        if (-not $process.HasExited) {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
    }
    throw
}
