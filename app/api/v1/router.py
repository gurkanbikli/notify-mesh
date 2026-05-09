from fastapi import APIRouter

from app.api.v1.routes.notifications import router as notifications_router

router = APIRouter()

router.include_router(notifications_router, prefix="/notifications")


@router.get("/health")
async def health_check():
    return {"status": "ok"}
