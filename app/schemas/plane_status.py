from typing import Optional

from pydantic import BaseModel, ConfigDict


class PlaneStatusBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    state: str


class PlaneStatusOut(PlaneStatusBase):
    id: Optional[int] = None


class PlaneStatusUpdate(BaseModel):
    id: Optional[int] = None
    state: Optional[str] = None


class PlaneStatusCreate(BaseModel):
    state: str
