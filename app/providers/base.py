from dataclasses import dataclass
from typing import Awaitable, Callable

import httpx

from app.models.channel import Channel
from app.models.notification_log import NotificationLogStatus


@dataclass
class SendResult:
    status: NotificationLogStatus
    request_payload: dict | None
    provider_response: dict | None
    error_message: str | None
    duration_ms: int | None


ProviderFn = Callable[[httpx.AsyncClient, Channel, str | None, str], Awaitable[SendResult]]
