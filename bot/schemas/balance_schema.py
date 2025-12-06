from pydantic import BaseModel


class BalanceResponse(BaseModel):
    focus_group: str
    balance_rub: float
    lessons_paid: int
    cyberons_balance: int
