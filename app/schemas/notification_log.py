from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.channel import ChannelProvider
from app.models.notification_log import NotificationLogStatus


class NotificationLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    channel_id: UUID | None
    api_key_id: UUID
    provider: ChannelProvider | None
    title: str | None
    message: str
    status: NotificationLogStatus
    request_payload: dict | None
    provider_response: dict | None
    error_message: str | None
    duration_ms: int | None
    created_at: datetime
