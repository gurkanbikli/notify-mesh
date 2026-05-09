import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentAdmin
from app.core.security import generate_temp_password, hash_password
from app.models.admin_user import AdminUser
from app.schemas.admin_user import (
    AdminUserCreate,
    AdminUserCreateResponse,
    AdminUserResetPasswordResponse,
    AdminUserResponse,
    AdminUserUpdate,
)

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[AdminUserResponse])
async def list_admin_users(db: DB, skip: int = 0, limit: int = 100):
    result = await db.execute(select(AdminUser).order_by(AdminUser.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()


@router.post("", response_model=AdminUserCreateResponse, status_code=201)
async def create_admin_user(body: AdminUserCreate, db: DB):
    temp_password = generate_temp_password()
    user = AdminUser(
        email=body.email,
        hashed_password=hash_password(temp_password),
        first_name=body.first_name,
        last_name=body.last_name,
        role=body.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return AdminUserCreateResponse(
        **AdminUserResponse.model_validate(user).model_dump(),
        temporary_password=temp_password,
    )


@router.get("/{id}", response_model=AdminUserResponse)
async def get_admin_user(id: uuid.UUID, db: DB):
    user = await db.get(AdminUser, id)
    if user is None:
        raise HTTPException(status_code=404, detail="Admin user not found")
    return user


@router.post("/{id}/reset-password", response_model=AdminUserResetPasswordResponse)
async def reset_admin_user_password(id: uuid.UUID, db: DB):
    user = await db.get(AdminUser, id)
    if user is None:
        raise HTTPException(status_code=404, detail="Admin user not found")
    new_password = generate_temp_password()
    user.hashed_password = hash_password(new_password)
    await db.commit()
    return AdminUserResetPasswordResponse(new_password=new_password)


@router.patch("/{id}", response_model=AdminUserResponse)
async def update_admin_user(id: uuid.UUID, body: AdminUserUpdate, db: DB, current_admin: CurrentAdmin):
    user = await db.get(AdminUser, id)
    if user is None:
        raise HTTPException(status_code=404, detail="Admin user not found")
    updates = body.model_dump(exclude_unset=True)
    if "role" in updates and updates["role"] != user.role and current_admin.id == id:
        raise HTTPException(status_code=403, detail="You cannot change your own role")
    for key, value in updates.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user
