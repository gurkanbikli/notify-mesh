from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentApiKey
from app.schemas.notification import SendNotificationRequest, SendNotificationResponse
from app.services.notification import send_notification

router = APIRouter(tags=["notifications"])

DB = Annotated[AsyncSession, Depends(get_db)]


@router.post("/send", response_model=SendNotificationResponse)
async def send_notification_endpoint(
    body: SendNotificationRequest,
    api_key: CurrentApiKey,
    db: DB,
):
    return await send_notification(body, api_key, db)
