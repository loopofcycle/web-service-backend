Set-Location "C:\Users\eliseev_i\source\repos\web-service-backend"
celery --app=worker.celery_tasks.celery_app worker --loglevel=INFO -P gevent -n worker_1@%h --pool=solo -E
