from uuid import UUID

from pydantic import BaseModel

from app.models.channel import ChannelProvider
from app.models.notification_log import NotificationLogStatus


class SendNotificationRequest(BaseModel):
    title: str | None = None
    message: str


class ChannelResult(BaseModel):
    channel_id: UUID
    channel_name: str
    provider: ChannelProvider
    status: NotificationLogStatus
    error_message: str | None = None
    duration_ms: int | None = None


class SendNotificationResponse(BaseModel):
    sent: int
    failed: int
    skipped: int
    results: list[ChannelResult]
