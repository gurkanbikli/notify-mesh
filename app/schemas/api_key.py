from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.api_key import ApiKeyStatus


class ApiKeyCreate(BaseModel):
    project_id: UUID
    name: str


class ApiKeyUpdate(BaseModel):
    name: str | None = None


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    name: str
    key_prefix: str
    status: ApiKeyStatus
    last_used_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ApiKeyCreateResponse(ApiKeyResponse):
    full_key: str
