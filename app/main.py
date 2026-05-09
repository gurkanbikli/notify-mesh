from fastapi import FastAPI

from app.admin.app import admin_app
from app.api.app import api_app
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Manage, route and control notifications across multiple providers from a single platform.",
    version="0.1.0",
    debug=settings.debug,
)

app.mount(settings.api_v1_prefix, api_app)
app.mount(settings.admin_v1_prefix, admin_app)
