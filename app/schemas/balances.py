from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BalancesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: Decimal


class BalancesOut(BalancesBase):
    user_id: Optional[int] = None


class BalancesUpdate(BaseModel):
    id: Optional[UUID] = None
    balance: Optional[Decimal] = None
