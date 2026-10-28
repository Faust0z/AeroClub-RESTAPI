from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AirportCodesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str


class AirportCodesOut(AirportCodesBase):
    id: Optional[UUID] = None


class AirportCodesCreate(BaseModel):
    code: str


class AirportCodesUpdate(BaseModel):
    id: Optional[UUID] = None
    code: str
