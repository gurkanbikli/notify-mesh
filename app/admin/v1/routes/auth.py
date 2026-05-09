from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentAdmin
from app.core.security import create_access_token, verify_password
from app.models.admin_user import AdminUser, AdminUserStatus
from app.schemas.admin_user import AdminUserResponse

router = APIRouter(tags=["auth"])

DB = Annotated[AsyncSession, Depends(get_db)]


@router.post("/login")
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DB):
    result = await db.execute(select(AdminUser).where(AdminUser.email == form.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if user.status != AdminUserStatus.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid email or password")
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    return {"access_token": create_access_token(str(user.id), user.role), "token_type": "bearer"}


@router.get("/me", response_model=AdminUserResponse)
async def me(current_admin: CurrentAdmin):
    return current_admin
