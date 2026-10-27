from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class TransactionsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    amount: Decimal
    issued_date: date
    description: Optional[str] = None


class TransactionsAdminOut(TransactionsBase):
    id: Optional[int] = None
    payment_type: Optional[str] = None


class TransactionsPublicOut(TransactionsBase):
    id: Optional[int] = None
    payment_type: Optional[str] = None


class TransactionsCreate(BaseModel):
    amount: Decimal
    issued_date: date
    description: Optional[str] = None
    payment_type_id: Optional[int] = None
    balance_id: Optional[int] = None
