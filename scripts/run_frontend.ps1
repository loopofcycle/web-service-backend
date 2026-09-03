$ErrorActionPreference = "Stop"
$frontend = Join-Path (Split-Path $PSScriptRoot -Parent) "web-service-frontend"
Set-Location $frontend
npm run dev
