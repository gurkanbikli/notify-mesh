from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    app_name: str = "notify-mesh"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    admin_v1_prefix: str = "/admin/v1"
    database_url: str = "mysql+asyncmy://username:password@host:port/database"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    channel_encryption_key: str = "base64_encryption_key"


settings = Settings()
