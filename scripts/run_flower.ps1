Set-Location "C:\Users\Eliseev.I\projects\revit_manager_app\backend"
.\.venv\Scripts\Activate.ps1
celery -A worker.celery_tasks.app flower --port=5005
