from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PaymentTypesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str
    details: Optional[str] = None


class PaymentTypesOut(PaymentTypesBase):
    id: Optional[int] = None


class PaymentTypesUpdate(BaseModel):
    id: Optional[int] = None
    type: Optional[str] = None
    details: Optional[str] = None


class PaymentTypesCreate(BaseModel):
    type: str
    details: Optional[str] = None
