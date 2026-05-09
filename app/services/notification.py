import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey
from app.models.channel import Channel, ChannelStatus
from app.models.notification_log import NotificationLog, NotificationLogStatus
from app.models.organization import Organization, OrganizationStatus
from app.models.project import Project, ProjectStatus
from app.providers import REGISTRY
from app.providers.base import SendResult
from app.schemas.notification import ChannelResult, SendNotificationRequest, SendNotificationResponse


async def send_notification(
    body: SendNotificationRequest,
    api_key: ApiKey,
    db: AsyncSession,
) -> SendNotificationResponse:
    project = await _get_active_project(api_key.project_id, db)
    await _get_active_organization(project.organization_id, db)
    channels = await _get_active_channels(project.id, db)

    if not channels:
        db.add(NotificationLog(
            project_id=project.id,
            channel_id=None,
            api_key_id=api_key.id,
            provider=None,
            title=body.title,
            message=body.message,
            status=NotificationLogStatus.skipped,
            error_message="No active channels found",
        ))
        await db.commit()
        return SendNotificationResponse(sent=0, failed=0, skipped=1, results=[])

    sent = failed = skipped = 0
    results: list[ChannelResult] = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        for channel in channels:
            provider_fn = REGISTRY.get(channel.provider)

            if provider_fn is None:
                send_result = SendResult(
                    status=NotificationLogStatus.skipped,
                    request_payload=None,
                    provider_response=None,
                    error_message=f"Provider '{channel.provider}' is not yet supported",
                    duration_ms=None,
                )
                skipped += 1
            else:
                send_result = await provider_fn(client, channel, body.title, body.message)
                if send_result.status == NotificationLogStatus.success:
                    sent += 1
                else:
                    failed += 1

            db.add(NotificationLog(
                project_id=project.id,
                channel_id=channel.id,
                api_key_id=api_key.id,
                provider=channel.provider,
                title=body.title,
                message=body.message,
                status=send_result.status,
                request_payload=send_result.request_payload,
                provider_response=send_result.provider_response,
                error_message=send_result.error_message,
                duration_ms=send_result.duration_ms,
            ))
            results.append(ChannelResult(
                channel_id=channel.id,
                channel_name=channel.name,
                provider=channel.provider,
                status=send_result.status,
                error_message=send_result.error_message,
                duration_ms=send_result.duration_ms,
            ))

    await db.commit()
    return SendNotificationResponse(sent=sent, failed=failed, skipped=skipped, results=results)


async def _get_active_project(project_id, db: AsyncSession) -> Project:
    project = await db.get(Project, project_id)
    if project is None or project.deleted_at is not None or project.status != ProjectStatus.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Project is not active")
    return project


async def _get_active_organization(organization_id, db: AsyncSession) -> None:
    org = await db.get(Organization, organization_id)
    if org is None or org.deleted_at is not None or org.status != OrganizationStatus.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization is not active")


async def _get_active_channels(project_id, db: AsyncSession) -> list[Channel]:
    result = await db.execute(
        select(Channel).where(
            Channel.project_id == project_id,
            Channel.status == ChannelStatus.active,
        )
    )
    return list(result.scalars().all())
