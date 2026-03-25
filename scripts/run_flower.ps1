Set-Location "C:\Users\eliseev_i\source\repos\web-service-backend"
celery --app=worker.celery_tasks.celery_app flower --port=5000
