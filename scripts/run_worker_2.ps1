Set-Location "C:\Users\Eliseev.I\projects\revit_manager_app\backend"
.\.venv\Scripts\Activate.ps1
celery --app=worker.celery_tasks.app worker --loglevel=INFO -P gevent -n worker_2@%h --queues=worker_2 --pool=solo
