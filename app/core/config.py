import os
import pathlib
import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    FRONTEND_HOST: str = "http://172.16.251.163:5004/"

    # paths
    APP_PATH: str = os.path.join(pathlib.Path(
        __file__).parent.parent.parent.resolve())

    # *rfa files (family files) storage paths
    MOUNTED_STORAGE_PATH: str = os.path.join("data", "rvt_files")
    SERVER_STORAGE_PATH: str = "C:\\Users\\eliseev_i\\Yandex.Disk\\_revit_library"

    # revit and db settings for export
    RSN_INI_PATH: str = "C:\\ProgramData\\Autodesk\\Revit Server 2024\\Config\\RSN.ini"
    ADDINS_PATH: str = "C:\\Users\\eliseev_i\\AppData\\Roaming\\Autodesk\\REVIT\\Addins"
    PARAMETERS_CONFIG_PATH: str = os.path.join(ADDINS_PATH, "params_to_add.xml")
    REVIT_STARTUP_CONFIG_PATH: str = os.path.join(ADDINS_PATH, "revit_startup_config.json")
    TASK_JSON_PATH: str = os.path.join(ADDINS_PATH, "tasks")

    # celery settings
    CELERY_WORKER_NAME: str = "celery_tasks"
    BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_QUEUES: list = [
        'worker_1',
        'worker_2',
    ]
    
    CATEGORIES_JSON_PATH: str = os.path.join(
        APP_PATH, 'service', 'configs', 'revit_categories_full.json')
    
    # revit settings for pdf print
    REVIT_EXPORT_PATH: str = os.path.join(APP_PATH, 'pdf_exported')

    # export config
    REVIT_EXPORT_MODE: str = "sync"
    EXPORT_TIMEOUT: int = 3600

    # CONFIG_PATH: str = os.path.join(
    #     APP_PATH, 'backend', 'service', 'configs', 'config.json')
    
    # DB_SCHEME_PATH: str = os.path.join(
    #     APP_PATH, 'backend', 'service', 'configs', 'db_scheme.json')

    # DB_DATA_SOURCE: str = 'SB-REVIT-DB'

    # # db connection
    # DB_NAME: str = 'db_pg'
    # DB_PORT: str = '5432'
    # DB_CONTAINER: str = 'db'

    @computed_field
    @property
    # Optional: use @cached_property if the value is expensive to compute and shouldn't change after the first access
    # @cached_property
    def DB_URL(self) -> URL:
        connection_string = URL.create(drivername="postgresql+asyncpg",
                   username="admin",
                   password="hotcoolaid",
                   host="db",
                   port=5432,
                   database="db_pg")

        # connection_string = "postgresql+asyncpg://admin:hotcoolaid@db:5432/db_pg"
        return connection_string


settings = Settings()
