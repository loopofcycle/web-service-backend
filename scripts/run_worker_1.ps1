$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..
celery --app=worker.celery_tasks.celery_app worker --loglevel=INFO -P gevent -n worker_1@%h --pool=solo -E
