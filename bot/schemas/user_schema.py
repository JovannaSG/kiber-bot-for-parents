from typing import Optional

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]
    focus_group: Optional[str] = Field(
        default=None,
        description="Фокус-группа ученика"
    )
    balance: float
    lessons_paid: int
    cyberons: int
