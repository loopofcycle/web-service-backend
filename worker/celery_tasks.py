import os
import asyncio
import httpx
import requests
from celery.app import Celery

from app.core.config import settings
from app.api.schemas import FamilyFileStatus

from service.base import ProcessStatus
from service.revit_runner import RevitRunner


celery_app = Celery(
    settings.CELERY_WORKER_NAME,
    broker=settings.BROKER_URL,
    backend=settings.BROKER_URL
)


@celery_app.task(name="process_family")
def run_task(family_id):
    print(f'received task for file {family_id}')
    return asyncio.run(family_sync_task(family_id))


@celery_app.task(name="process_batch")
def process_batch(list_of_id):
    for family_id in list_of_id:
        print(f"Processing {family_id}")
        asyncio.run(family_sync_task(family_id))
    
    return True
        


async def family_sync_task(family_id: str):
    update_url = 'http://localhost/api/v1/families/update'
    get_url = 'http://localhost/api/v1/families/get'

    # get file info
    get_response = requests.get(url=get_url, params={"family_id": family_id}, timeout=5)
    if get_response.status_code != 200:
        print(f'failed to receive data for id={family_id}, status={get_response.status_code}')
        return False
    
    # find file in storage
    relative_path = get_response.json()['data']['path']
    file_path = os.path.join(settings.SERVER_STORAGE_PATH, relative_path)
    if not os.path.exists(file_path):
        print(f'family not found in storage')
        update_response = requests.post(url=update_url, 
                      json={"id": family_id, "status": FamilyFileStatus.FAILED.value},
                      timeout=5)
        print(update_response.json())
        return False

    # update file status
    update_response = requests.post(url=update_url, 
                             json={"id": family_id, "status": FamilyFileStatus.IN_PROGRESS.value},
                             timeout=5)
    print(update_response.json())

    # run revit
    revit_runner = RevitRunner(
        runner_config={
            "revit_config_path": os.path.join(settings.TASK_JSON_PATH, f'task_{family_id}.json'),
            "timeout": settings.EXPORT_TIMEOUT,
            "rsn_file_path": settings.RSN_INI_PATH,
        },
        revit_config={
            "StartupApp": "add_shared_parameters",
            "ParametersConfig": settings.PARAMETERS_CONFIG_PATH,
            "TargetFilePath": file_path,
            "FileID": family_id,
            "ExportMode": settings.REVIT_EXPORT_MODE,
        },
    )
    report = await revit_runner.run_process()

    # update file status
    if report['process_result'] == ProcessStatus.FINISHED.value:
        file_status = FamilyFileStatus.SYNCHRONIZED.value
    else:
        file_status = FamilyFileStatus.FAILED.value
    final_response = requests.post(url=update_url, 
                  json={"id": family_id, "status": file_status},
                  timeout=5)
    print(final_response.json())

    revit_runner.log(f'celery task executed, report: {report}')
    return True

