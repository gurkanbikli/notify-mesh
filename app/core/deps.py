from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token, verify_api_key
from app.models.admin_user import AdminUser
from app.models.api_key import ApiKey, ApiKeyStatus

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/v1/auth/login")
_api_key_bearer = HTTPBearer()


async def get_current_admin(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AdminUser:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise exc
    try:
        from uuid import UUID
        uid = UUID(user_id)
    except ValueError:
        raise exc
    user = await db.get(AdminUser, uid)
    if user is None or not user.status == "active":
        raise exc
    return user


CurrentAdmin = Annotated[AdminUser, Depends(get_current_admin)]


async def get_current_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_api_key_bearer)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiKey:
    raw_key = credentials.credentials
    result = await db.execute(select(ApiKey).where(ApiKey.key_prefix == raw_key[:8]))
    api_key = next(
        (k for k in result.scalars().all() if verify_api_key(raw_key, k.key_hash)),
        None,
    )
    if api_key is None or api_key.status != ApiKeyStatus.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    api_key.last_used_at = datetime.now(timezone.utc)
    return api_key


CurrentApiKey = Annotated[ApiKey, Depends(get_current_api_key)]
