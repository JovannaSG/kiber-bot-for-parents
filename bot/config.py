from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl, field_validator


class Settings(BaseSettings):
    # --- Telegram ---
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    telegram_admins: list[str] = Field(..., alias="TELEGRAM_ADMINS")
    directors_chat_id: str = Field(..., alias="DIRECTORS_CHAT_ID")

    # --- Backend ---
    backend_api_url: HttpUrl = Field(..., alias="BACKEND_API_URL")
    backend_api_token: str = Field(..., alias="BACKEND_API_TOKEN")

    # --- PostgreSQL ---
    database_url: str = Field(..., alias="DATABASE_URL")

    # --- AlfaCRM ---
    alfacrm_api_key: str = Field(..., alias="ALFACRM_API_KEY")
    alfacrm_base_url: HttpUrl = Field(..., alias="ALFACRM_BASE_URL")

    # --- Misc ---
    placeholder_qr_url: HttpUrl = Field(..., alias="PLACEHOLDER_QR_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
