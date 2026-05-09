import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decrypt_config, encrypt_config
from app.models.channel import Channel
from app.schemas.channel import ChannelCreate, ChannelDetailResponse, ChannelResponse, ChannelUpdate

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


def _to_detail(channel: Channel) -> ChannelDetailResponse:
    return ChannelDetailResponse(
        **ChannelResponse.model_validate(channel).model_dump(),
        config=decrypt_config(channel.config_encrypted),
    )


@router.get("", response_model=list[ChannelResponse])
async def list_channels(db: DB, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Channel).order_by(Channel.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.post("", response_model=ChannelDetailResponse, status_code=201)
async def create_channel(body: ChannelCreate, db: DB):
    channel = Channel(
        project_id=body.project_id,
        name=body.name,
        provider=body.provider,
        config_encrypted=encrypt_config(body.config),
    )
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    return _to_detail(channel)


@router.get("/{id}", response_model=ChannelDetailResponse)
async def get_channel(id: uuid.UUID, db: DB):
    channel = await db.get(Channel, id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return _to_detail(channel)


@router.patch("/{id}", response_model=ChannelDetailResponse)
async def update_channel(id: uuid.UUID, body: ChannelUpdate, db: DB):
    channel = await db.get(Channel, id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    updates = body.model_dump(exclude_unset=True)
    if "config" in updates:
        channel.config_encrypted = encrypt_config(updates.pop("config"))
    for key, value in updates.items():
        setattr(channel, key, value)
    await db.commit()
    await db.refresh(channel)
    return _to_detail(channel)


@router.delete("/{id}", status_code=204)
async def delete_channel(id: uuid.UUID, db: DB):
    channel = await db.get(Channel, id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    await db.delete(channel)
    await db.commit()
