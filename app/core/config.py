import os
import pathlib
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field
from sqlalchemy.engine import URL


_APP_PATH = pathlib.Path(__file__).resolve().parents[2]
_ENV_FILE = _APP_PATH / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    FRONTEND_HOST: str = "http://localhost"
    CORS_ORIGINS: str = "http://localhost,http://localhost:80,http://127.0.0.1"

    # Public URL used in API responses (download/preview links)
    PUBLIC_API_BASE_URL: str = "http://localhost:5000"
    # Internal URL used by Celery workers talking back to the API
    INTERNAL_API_BASE_URL: str = "http://localhost:5000"

    APP_PORT: int = 5000
    FLOWER_PORT: int = 5555

    ADMIN_USER: str = Field(default="")
    ADMIN_PASSWORD: str = Field(default="")
    # Shared secret for worker / Revit plugin / service write APIs
    API_SERVICE_TOKEN: str = Field(default="")

    POSTGRES_USER: str = Field(default="admin")
    POSTGRES_PASSWORD: str = Field(default="")
    POSTGRES_HOST: str = Field(default="db")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str = Field(default="db_pg")

    APP_PATH: str = str(_APP_PATH)
    CONFIGS_FOLDER: str = str(_APP_PATH / "service" / "configs")
    CATEGORIES_JSON_PATH: str = str(
        _APP_PATH / "service" / "configs" / "revit_categories_full.json"
    )
    SP_FILE_PATH: str = str(_APP_PATH / "service" / "configs" / "ФОП2021.txt")
    PARAMETERS_CONFIG_PATH: str = str(
        _APP_PATH / "service" / "configs" / "params_to_add.xml"
    )
    REVIT_STARTUP_CONFIG_PATH: str = str(
        _APP_PATH / "service" / "configs" / "revit_startup_config.json"
    )

    MOUNTED_STORAGE_PATH: str = r"/data/rvt_files"
    SERVER_STORAGE_PATH: str = Field(
        default=r"C:\Users\loopo\YandexDisk\_revit_library"
    )

    RSN_INI_PATH: str = r"C:\ProgramData\Autodesk\Revit Server 2024\Config\RSN.ini"
    ADDINS_PATH: str = Field(
        default=r"C:\Users\loopo\AppData\Roaming\Autodesk\REVIT\Addins"
    )

    CELERY_WORKER_NAME: str = "celery_tasks"
    BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_QUEUES: list = [
        "worker_1",
        "worker_2",
    ]

    REVIT_EXPORT_MODE: str = "sync"
    EXPORT_TIMEOUT: int = 3600

    @computed_field
    @property
    def TASKS_FOLDER(self) -> str:
        return os.path.join(self.ADDINS_PATH, "tasks")

    @computed_field
    @property
    def REVIT_EXPORT_PATH(self) -> str:
        return os.path.join(self.APP_PATH, "pdf_exported")

    @computed_field
    @property
    def cors_origin_list(self) -> list[str]:
        origins = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        frontend = self.FRONTEND_HOST.rstrip("/")
        if frontend and frontend not in origins:
            origins.append(frontend)
        return origins

    @computed_field
    @property
    def DB_URL(self) -> URL:
        if not self.POSTGRES_PASSWORD:
            raise ValueError(
                "POSTGRES_PASSWORD is not set. Copy .env.example to .env and set secrets."
            )
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        )


settings = Settings()
