from typing import Optional, List, Union, Any

from pydantic import (
    AnyUrl,
    field_validator,
    # model_validator,
    Field,
    ConfigDict
)
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Обязательные поля
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram bot token")
    DATABASE_URL: AnyUrl = Field(..., description="Database connection URL")

    # Опциональные поля
    TELEGRAM_ADMINS: List[str] = Field(
        default_factory=list,
        description="List of admin user IDs"
    )
    DIRECTORS_CHAT_ID: Optional[Union[str, int]] = Field(
        None,
        description="Director chat ID (numeric) or username (e.g., @groupname)"
    )
    PLACEHOLDER_QR_URL: AnyUrl = Field(
        "https://via.placeholder.com/300x300?text=QR",
        description="Placeholder QR code URL"
    )
    ALPHACRM_API_KEY: Optional[str] = Field(
        None,
        description="Alpha CRM API key"
    )

    # Валидаторы, можно доработать, пока что простые
    @field_validator("TELEGRAM_BOT_TOKEN")
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        if not v or ':' not in v:
            raise ValueError("Invalid bot token format. Must contain ':'")

        token_parts = v.split(':')
        if len(token_parts) != 2 or not token_parts[0].isdigit():
            raise ValueError("Invalid bot token structure")
        return v.strip()

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: AnyUrl) -> AnyUrl:
        allowed_schemes: set[str] = {
            "postgresql+asyncpg",
            "postgresql",
            "postgres"
        }
        if str(v.scheme) not in allowed_schemes:
            raise ValueError(
                f"sUnsupported database scheme. Use: {', '.join(allowed_schemes)}"
            )
        return v

    @field_validator("TELEGRAM_ADMINS", mode="before")
    @classmethod
    def parse_telegram_admins(cls, v: Any) -> List[str] | List:
        if isinstance(v, str):
            # Remove brackets, quotes and split by comma
            cleaned = v.strip('[]').replace('"', '').replace("'", '')
            if cleaned:
                return [item.strip() for item in cleaned.split(',') if item.strip()]
            return []
        elif isinstance(v, list):
            return [str(item) for item in v if item]
        return []

    @field_validator("DIRECTORS_CHAT_ID", mode="before")
    @classmethod
    def validate_director_chat_id(cls, v: Any) -> Optional[Union[str, int]]:
        if v is None or str(v).strip().lower() in ("null", "none", ''):
            return None

        v_str = str(v).strip()
        if v_str.startswith('@'):
            # Validate username format
            if len(v_str) < 3:  # Minimum @a
                raise ValueError("Username too short")
            if not v_str[1:].replace('_', '').isalnum():
                raise ValueError(
                    "Invalid username format. Only letters, numbers and \
                    underscores allowed"
                )
            return v_str
        else:
            # Try to convert to integer for chat ID
            try:
                return int(v_str)
            except ValueError:
                raise ValueError(
                    "Chat ID must be numeric or start with @ for usernames"
                )

    @field_validator("PLACEHOLDER_QR_URL")
    @classmethod
    def validate_qr_url(cls, v: AnyUrl) -> AnyUrl:
        if "placeholder.com" in str(v) and '300x300' not in str(v):
            raise ValueError("Placeholder QR should be 300x300 size")
        return v

    # Pydantic v2 configuration
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Custom warning class
class SecurityWarning(UserWarning):
    """Security-related warnings"""
    pass


settings = Settings()
