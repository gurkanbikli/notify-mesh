from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerUserCreate(BaseModel):
    organization_id: UUID
    email: EmailStr


class CustomerUserUpdate(BaseModel):
    email: EmailStr | None = None
    is_active: bool | None = None


class CustomerUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
