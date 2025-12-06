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
    alfacrm_api_key: SecretStr = Field(
        ...,
        alias="ALFACRM_API_KEY",
        description="ключ API для авторизации в системе"
    )
    alfacrm_hostname: str = Field(
        ...,
        alias="ALFACRM_HOSTNAME",
        description="клиентский идентификатор, являющийся Hostname в URL \
            для доступа в систему. \
            Например, для https://demo.s20.online это demo.s20.online"
    )
    alfacrm_branch_id: int = Field(
        ...,
        alias="ALFACRM_BRANCH_ID",
        description="ID филиала, в который происходит обращение"
    )
    alfacrm_email: str = Field(
        ...,
        alias="ALFACRM_EMAIL",
        description="e-mail пользователя для авторизации в системе"
    )

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
