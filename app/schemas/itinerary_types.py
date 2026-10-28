from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ItineraryTypesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str


class ItineraryTypesOut(ItineraryTypesBase):
    id: Optional[UUID] = None


class ItineraryTypesUpdate(BaseModel):
    id: Optional[UUID] = None
    type: Optional[str] = None


class ItineraryTypesCreate(BaseModel):
    type: str
