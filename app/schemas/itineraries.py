from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ItinerariesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    departure_time: datetime
    arrival_time: datetime
    landings_amount: int
    observations: Optional[str] = None


class ItinerariesOut(ItinerariesBase):
    id: Optional[int] = None
    itinerary_type: Optional[str] = None
    plane: Optional[str] = None
    airport_codes: List[str] = []


class ItinerariesCreate(BaseModel):
    departure_time: datetime
    arrival_time: datetime
    landings_amount: int
    observations: Optional[str] = None
    itinerary_type: str
    plane_registration: str
    airport_codes: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_time_range(self) -> "ItinerariesCreate":
        if self.departure_time >= self.arrival_time:
            raise ValueError("Arrival time must be later than departure time.")
        return self
