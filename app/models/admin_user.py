import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class AdminUserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    locked = "locked"


class AdminUserRole(str, enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    support = "support"


class AdminUser(BaseModel):
    __tablename__ = "admin_users"

    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    status: Mapped[AdminUserStatus] = mapped_column(
        Enum(AdminUserStatus, name="adminuserstatus"), default=AdminUserStatus.active
    )
    role: Mapped[AdminUserRole] = mapped_column(
        Enum(AdminUserRole, name="adminuserrole")
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
