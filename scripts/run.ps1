$backScriptPath = "C:\Users\Eliseev.I\projects\revit_manager_app\scripts\run_backend.ps1"
Start-Process powershell.exe -ArgumentList "-NoExit -File `"$backScriptPath`""
$frontScriptPath = "C:\Users\Eliseev.I\projects\revit_manager_app\scripts\run_worker_1.ps1"
Start-Process powershell.exe -ArgumentList "-NoExit -File `"$frontScriptPath`""
$frontScriptPath = "C:\Users\Eliseev.I\projects\revit_manager_app\scripts\run_worker_2.ps1"
Start-Process powershell.exe -ArgumentList "-NoExit -File `"$frontScriptPath`""
# $frontScriptPath = "C:\Users\Eliseev.I\projects\revit_manager_app\scripts\run_worker_3.ps1"
# Start-Process powershell.exe -ArgumentList "-NoExit -File `"$frontScriptPath`""
$frontScriptPath = "C:\Users\Eliseev.I\projects\revit_manager_app\scripts\run_frontend.ps1"
Start-Process powershell.exe -ArgumentList "-NoExit -File `"$frontScriptPath`""

Start-Sleep -Seconds 10

$backScriptPath = "C:\Users\Eliseev.I\projects\revit_manager_app\scripts\run_flower.ps1"
Start-Process powershell.exe -ArgumentList "-NoExit -File `"$backScriptPath`""
        