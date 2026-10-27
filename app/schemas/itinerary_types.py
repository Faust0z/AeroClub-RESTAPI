from typing import Optional

from pydantic import BaseModel, ConfigDict


class ItineraryTypesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str


class ItineraryTypesOut(ItineraryTypesBase):
    id: Optional[int] = None


class ItineraryTypesUpdate(BaseModel):
    id: Optional[int] = None
    type: Optional[str] = None


class ItineraryTypesCreate(BaseModel):
    type: str
