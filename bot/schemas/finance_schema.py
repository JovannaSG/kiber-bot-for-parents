from typing import List, Literal

from pydantic import BaseModel


class FinanceRecord(BaseModel):
    id: int
    type: Literal["payment", "charge", "cyberons_add", "cyberons_sub"]
    amount: float
    title: str
    created_at: str


class FinanceHistory(BaseModel):
    items: List[FinanceRecord]
