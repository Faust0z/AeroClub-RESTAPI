from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class AirportCodesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str


class AirportCodesOut(AirportCodesBase):
    id: Optional[int] = None


class AirportCodesCreate(BaseModel):
    code: str


class AirportCodesUpdate(BaseModel):
    id: Optional[int] = None
    code: str
