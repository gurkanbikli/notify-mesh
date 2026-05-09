import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.notification_log import NotificationLog
from app.schemas.notification_log import NotificationLogResponse

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[NotificationLogResponse])
async def list_notification_logs(db: DB, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(NotificationLog)
        .order_by(NotificationLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{id}", response_model=NotificationLogResponse)
async def get_notification_log(id: uuid.UUID, db: DB):
    log = await db.get(NotificationLog, id)
    if log is None:
        raise HTTPException(status_code=404, detail="Notification log not found")
    return log
