$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$flowerPort = 5555
if (Test-Path .\.env) {
    Get-Content .\.env | ForEach-Object {
        if ($_ -match '^\s*FLOWER_PORT\s*=\s*(.+)\s*$') {
            $flowerPort = $Matches[1].Trim()
        }
    }
}

Write-Host "Starting Flower on port $flowerPort (API stays on APP_PORT, default 5000)"
celery --app=worker.celery_tasks.celery_app flower --port=$flowerPort
