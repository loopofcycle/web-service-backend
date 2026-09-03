$ErrorActionPreference = "Stop"
$scripts = Join-Path $PSScriptRoot ""

Start-Process powershell.exe -ArgumentList "-NoExit -File `"$(Join-Path $scripts 'run_worker_1.ps1')`""
Start-Process powershell.exe -ArgumentList "-NoExit -File `"$(Join-Path $scripts 'run_worker_2.ps1')`""
Start-Process powershell.exe -ArgumentList "-NoExit -File `"$(Join-Path $scripts 'run_flower.ps1')`""

$frontend = Join-Path (Split-Path $PSScriptRoot -Parent) "web-service-frontend"
if (Test-Path $frontend) {
    Start-Process powershell.exe -ArgumentList "-NoExit -Command `"Set-Location '$frontend'; npm run dev`""
}
