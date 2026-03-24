from enum import Enum
from typing_extensions import Self
from pydantic import BaseModel, model_validator


class CategoryRequest(BaseModel):
    name: str
    number: str | None = None
    label: str | None = None


class FamilyFileStatus(Enum):
    PENDING = 'pending'
    MISSING = 'missing'
    UPDATED = 'updated'
    SYNCHRONIZED = 'synchronized'
    DELETED = 'deleted'
    IN_PROGRESS = 'in_progress'
    FAILED = 'failed'


class FamilyFileRequest(BaseModel):
    id: str | None = None
    title: str | None = None
    status: str | None = None
    category: str | None = None
    path: str | None = None
    updated_at: str | None = None
    size: int | None = None


class TaskStatus(Enum):
    PLANNED = 'PLANNED'
    IN_PROGRESS = 'IN_PROGRESS'
    EXECUTED = 'EXECUTED'

    PENDING = 'PENDING'
    RECEIVED = 'RECEIVED'
    STARTED = 'STARTED'
    RETRY = 'RETRY'
    FAILURE = 'FAILURE'
    SUCCESS = 'SUCCESS'
    REVOKED = 'REVOKED'


class TaskRequest(BaseModel):
    status: str
    file_id: str | None = None
    file_title: str | None = None
    revit_app: str | None = None
    priority: int | None = None
    queue: str | None = None
    process_pid: str | None = None
    celery_status: str | None = None
    celery_task_id: str | None = None


class AdminCommand(BaseModel):
    user: str
    password: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        superuser = {
            'user': 'igor',
            'password': 'eliseev'
        }
        if self.user != superuser['user'] or self.password != superuser['password']:
            raise ValueError('you cant touch it')
        return self


class Response(BaseModel):
    message: str
    data: list | dict

    def as_dict(self):
        return {'message': self.message, 'data': self.data}
