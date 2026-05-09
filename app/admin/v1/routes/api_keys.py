import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import generate_api_key
from app.models.api_key import ApiKey, ApiKeyStatus
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreateResponse, ApiKeyResponse, ApiKeyUpdate

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[ApiKeyResponse])
async def list_api_keys(db: DB, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(ApiKey).order_by(ApiKey.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.post("", response_model=ApiKeyCreateResponse, status_code=201)
async def create_api_key(body: ApiKeyCreate, db: DB):
    raw_key, key_prefix, key_hash = generate_api_key()
    api_key = ApiKey(
        project_id=body.project_id,
        name=body.name,
        key_prefix=key_prefix,
        key_hash=key_hash,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    return ApiKeyCreateResponse(
        **ApiKeyResponse.model_validate(api_key).model_dump(),
        full_key=raw_key,
    )


@router.get("/{id}", response_model=ApiKeyResponse)
async def get_api_key(id: uuid.UUID, db: DB):
    api_key = await db.get(ApiKey, id)
    if api_key is None:
        raise HTTPException(status_code=404, detail="API key not found")
    return api_key


@router.patch("/{id}", response_model=ApiKeyResponse)
async def update_api_key(id: uuid.UUID, body: ApiKeyUpdate, db: DB):
    api_key = await db.get(ApiKey, id)
    if api_key is None or api_key.status == ApiKeyStatus.revoked:
        raise HTTPException(status_code=404, detail="API key not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(api_key, key, value)
    await db.commit()
    await db.refresh(api_key)
    return api_key


@router.delete("/{id}", status_code=204)
async def revoke_api_key(id: uuid.UUID, db: DB):
    api_key = await db.get(ApiKey, id)
    if api_key is None or api_key.status == ApiKeyStatus.revoked:
        raise HTTPException(status_code=404, detail="API key not found")
    api_key.status = ApiKeyStatus.revoked
    api_key.revoked_at = datetime.now(timezone.utc)
    await db.commit()
