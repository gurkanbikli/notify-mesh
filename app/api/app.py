from fastapi import FastAPI

from app.api.v1.router import router as v1_router

api_app = FastAPI(
    title="notify-mesh · API",
    version="1.0.0",
)

api_app.include_router(v1_router)
