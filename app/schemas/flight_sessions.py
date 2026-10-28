from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class FlightSessionsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    issued_date: date
    observations: Optional[str] = None
    flight_session_identifier: int


class FlightSessionsOut(FlightSessionsBase):
    id: Optional[UUID] = None
    itineraries: List[dict] = []


class FlightSessionsCreate(BaseModel):
    user_email: str
    instructor_email: Optional[str] = None
    issued_date: date
    observations: Optional[str] = None
    itineraries: List[dict]
