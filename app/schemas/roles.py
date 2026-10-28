from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RolesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class RolesOut(RolesBase):
    pass


class RolesUpdate(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None


class RolesCreate(BaseModel):
    name: str
