from fastapi import APIRouter, Depends

from app.admin.v1.routes import (
    admin_users,
    api_keys,
    auth,
    channels,
    customer_users,
    notification_logs,
    organizations,
    projects,
)
from app.core.deps import get_current_admin

router = APIRouter()

_protected = {"dependencies": [Depends(get_current_admin)]}


@router.get("/health")
async def admin_health_check():
    return {"status": "ok"}


router.include_router(auth.router, prefix="/auth")
router.include_router(organizations.router, prefix="/organizations", tags=["organizations"], **_protected)
router.include_router(admin_users.router, prefix="/admin-users", tags=["admin-users"], **_protected)
router.include_router(customer_users.router, prefix="/customer-users", tags=["customer-users"], **_protected)
router.include_router(projects.router, prefix="/projects", tags=["projects"], **_protected)
router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"], **_protected)
router.include_router(channels.router, prefix="/channels", tags=["channels"], **_protected)
router.include_router(notification_logs.router, prefix="/notification-logs", tags=["notification-logs"], **_protected)
