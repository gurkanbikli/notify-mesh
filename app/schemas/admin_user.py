from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.admin_user import AdminUserRole, AdminUserStatus


class AdminUserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: AdminUserRole


class AdminUserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    status: AdminUserStatus | None = None
    role: AdminUserRole | None = None


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    first_name: str
    last_name: str
    status: AdminUserStatus
    role: AdminUserRole
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AdminUserCreateResponse(AdminUserResponse):
    temporary_password: str


class AdminUserResetPasswordResponse(BaseModel):
    new_password: str
