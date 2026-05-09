import enum
import uuid

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum

from app.models.base import ImmutableBaseModel
from app.models.channel import ChannelProvider


class NotificationLogStatus(str, enum.Enum):
    success = "success"
    failed = "failed"
    skipped = "skipped"


class NotificationLog(ImmutableBaseModel):
    __tablename__ = "notification_logs"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    channel_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("channels.id"), nullable=True)
    api_key_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("api_keys.id"))
    provider: Mapped[ChannelProvider | None] = mapped_column(Enum(ChannelProvider, name="channelprovider"), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[NotificationLogStatus] = mapped_column(
        Enum(NotificationLogStatus, name="notificationlogstatus")
    )
    request_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    provider_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
