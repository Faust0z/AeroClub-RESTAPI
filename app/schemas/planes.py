from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlanesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    brand: str
    model: str
    registration: str
    category: str
    acquisition_date: date
    fare: Decimal
    consumption_per_hour: int
    description: Optional[str] = None
    plane_status_id: Optional[int] = None


class PlanesOut(PlanesBase):
    id: Optional[UUID] = None


class PlanesUpdate(BaseModel):
    id: Optional[UUID] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    registration: Optional[str] = None
    category: Optional[str] = None
    acquisition_date: Optional[date] = None
    fare: Optional[Decimal] = None
    consumption_per_hour: Optional[int] = None
    description: Optional[str] = None
    plane_status_id: Optional[int] = None


class PlanesCreate(BaseModel):
    brand: str
    model: str
    registration: str
    category: str
    acquisition_date: date
    fare: Decimal
    consumption_per_hour: int
    description: Optional[str] = None
    plane_status_id: Optional[int] = None
