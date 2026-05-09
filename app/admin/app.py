from fastapi import FastAPI

from app.admin.v1.router import router as v1_router

admin_app = FastAPI(
    title="notify-mesh · Admin",
    version="1.0.0",
)

admin_app.include_router(v1_router)
