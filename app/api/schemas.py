from enum import Enum
from typing_extensions import Self
from pydantic import BaseModel, model_validator

from app.core.config import settings


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


class AdminCommand(BaseModel):
    user: str
    password: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if not settings.ADMIN_USER or not settings.ADMIN_PASSWORD:
            raise ValueError('admin credentials are not configured')
        if self.user != settings.ADMIN_USER or self.password != settings.ADMIN_PASSWORD:
            raise ValueError('you cant touch it')
        return self


class Response(BaseModel):
    message: str
    data: list | dict

    def as_dict(self):
        return {'message': self.message, 'data': self.data}
