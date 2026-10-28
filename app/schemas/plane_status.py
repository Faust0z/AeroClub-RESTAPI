from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlaneStatusBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    state: str


class PlaneStatusOut(PlaneStatusBase):
    id: Optional[UUID] = None


class PlaneStatusUpdate(BaseModel):
    id: Optional[UUID] = None
    state: Optional[str] = None


class PlaneStatusCreate(BaseModel):
    state: str
