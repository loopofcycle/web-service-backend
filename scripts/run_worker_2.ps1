$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..
celery --app=worker.celery_tasks.celery_app worker --loglevel=INFO -P gevent -n worker_2@%h --queues=worker_2 --pool=solo -E
