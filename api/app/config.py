from typing import List

from pydantic import Field, SecretStr, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "KIBERone app"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000

    # CORS
    cors_origin: List[str] = ["*"]
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = Field(..., alias="DATABASE_URL")
    
    # API Tokens
    backend_api_token: str = Field(alias="BACKEND_API_TOKEN")
    alfacrm_api_key: str = Field(..., alias="ALFACRM_API_KEY")
    alfacrm_base_url: HttpUrl = Field(..., alias="ALFACRM_BASE_URL")

    # Telegram
    telegram_bot_token: SecretStr = Field(..., alias="TELEGRAM_BOT_TOKEN")
    directors_chat_id: str = Field(..., alias="DIRECTORS_CHAT_ID")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
