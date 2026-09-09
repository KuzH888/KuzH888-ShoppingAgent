[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$apiBase = "http://127.0.0.1:8000"
$frontendUrl = "http://127.0.0.1:5173/"
$sessionId = "prototype-check-$([guid]::NewGuid().ToString('N'))"

try {
    $health = Invoke-RestMethod -Uri "$apiBase/health" -TimeoutSec 5
    if ($health.status -ne "ok") {
        throw "Backend health status was not ok."
    }

    $catalogue = Invoke-RestMethod -Uri "$apiBase/api/products" -TimeoutSec 5
    if ($catalogue.total -lt 2) {
        throw "At least two products are required for the prototype check."
    }

    $models = Invoke-RestMethod -Uri "$apiBase/api/models" -TimeoutSec 5
    if ($models.models.Count -lt 1) {
        throw "No selectable model was returned by the backend."
    }

    $policies = Invoke-RestMethod -Uri "$apiBase/api/policies" -TimeoutSec 5
    if ($policies.policies.Count -lt 1) {
        throw "No store policy was returned by the backend."
    }

    $firstId = $catalogue.products[0].id
    $secondId = $catalogue.products[1].id
    $body = @{
        session_id = $sessionId
        message = "Compare $firstId and $secondId"
        model_id = $models.default_model
    } | ConvertTo-Json
    $chat = Invoke-RestMethod `
        -Uri "$apiBase/api/chat" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 10
    if ($chat.result.type -ne "comparison") {
        throw "Assistant comparison check failed."
    }

    $frontend = Invoke-WebRequest -Uri $frontendUrl -TimeoutSec 5
    if ($frontend.StatusCode -ne 200 -or $frontend.Content -notmatch "KuzMall") {
        throw "Frontend response did not contain the expected KuzMall page."
    }

    [pscustomobject]@{
        status = "ready"
        backend = "$apiBase (v$($health.version))"
        frontend = $frontendUrl
        mode = if ($health.simulation_mode) { "simulation" } else { "live" }
        products = $catalogue.total
        models = $models.models.Count
        policies = $policies.policies.Count
        assistant_check = "comparison passed"
    } | Format-List
}
finally {
    try {
        Invoke-RestMethod -Uri "$apiBase/api/sessions/$sessionId" -Method Delete -TimeoutSec 3 | Out-Null
    }
    catch {
        # The disposable diagnostic session may not exist if an earlier check failed.
    }
}
