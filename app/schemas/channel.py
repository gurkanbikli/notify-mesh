from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.channel import ChannelProvider, ChannelStatus


class ChannelCreate(BaseModel):
    project_id: UUID
    name: str
    provider: ChannelProvider
    config: dict


class ChannelUpdate(BaseModel):
    name: str | None = None
    config: dict | None = None
    status: ChannelStatus | None = None


class ChannelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    name: str
    provider: ChannelProvider
    status: ChannelStatus
    last_used_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ChannelDetailResponse(ChannelResponse):
    config: dict
