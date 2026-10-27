from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BalancesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: Decimal


class BalancesOut(BalancesBase):
    user_id: Optional[int] = None


class BalancesUpdate(BaseModel):
    id: Optional[int] = None
    balance: Optional[Decimal] = None
