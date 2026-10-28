from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PaymentTypesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str
    details: Optional[str] = None


class PaymentTypesOut(PaymentTypesBase):
    id: Optional[UUID] = None


class PaymentTypesUpdate(BaseModel):
    id: Optional[UUID] = None
    type: Optional[str] = None
    details: Optional[str] = None


class PaymentTypesCreate(BaseModel):
    type: str
    details: Optional[str] = None
