import time

import httpx

from app.core.security import decrypt_config
from app.models.channel import Channel
from app.models.notification_log import NotificationLogStatus
from app.providers.base import SendResult


async def send(
    client: httpx.AsyncClient,
    channel: Channel,
    title: str | None,
    message: str,
) -> SendResult:
    config = decrypt_config(channel.config_encrypted)
    webhook_url = config.get("webhook_url")

    if not webhook_url:
        return SendResult(
            status=NotificationLogStatus.failed,
            request_payload=None,
            provider_response=None,
            error_message="Missing webhook_url in channel config",
            duration_ms=0,
        )

    text = f"*{title}*\n{message}" if title else message
    request_payload = {"text": text}

    start = time.monotonic()
    try:
        resp = await client.post(webhook_url, json=request_payload)
        duration_ms = int((time.monotonic() - start) * 1000)
        provider_response = {"status_code": resp.status_code, "body": resp.text}

        if resp.status_code == 200:
            return SendResult(NotificationLogStatus.success, request_payload, provider_response, None, duration_ms)

        return SendResult(
            NotificationLogStatus.failed,
            request_payload,
            provider_response,
            f"Slack returned HTTP {resp.status_code}",
            duration_ms,
        )
    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        return SendResult(NotificationLogStatus.failed, request_payload, None, str(exc), duration_ms)
