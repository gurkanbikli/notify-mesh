import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ChannelProvider(str, enum.Enum):
    slack = "slack"
    teams = "teams"
    discord = "discord"
    telegram = "telegram"


class ChannelStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class Channel(BaseModel):
    __tablename__ = "channels"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(255))
    provider: Mapped[ChannelProvider] = mapped_column(Enum(ChannelProvider, name="channelprovider"))
    config_encrypted: Mapped[str] = mapped_column(Text)
    status: Mapped[ChannelStatus] = mapped_column(
        Enum(ChannelStatus, name="channelstatus"), default=ChannelStatus.active
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
