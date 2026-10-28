from datetime import datetime

from app.models import FlightSessions
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, UUID
from sqlalchemy.orm import Mapped, relationship
import uuid

from .associations import itinerary_has_airport_codes
from ..database import Base


class Itineraries(Base):
    __tablename__ = 'itineraries'
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    departure_time: Mapped[datetime] = Column(DateTime, nullable=False)
    arrival_time: Mapped[datetime] = Column(DateTime, nullable=False)
    landings_amount: Mapped[int] = Column(Integer, nullable=False)
    observations: Mapped[str] = Column(Text)
    itinerary_type_id: Mapped[int] = Column(ForeignKey('itinerary_types.id'))
    plane_id: Mapped[int] = Column(ForeignKey('planes.id'))
    invoice_id: Mapped[int] = Column(ForeignKey('flight_sessions.id'))

    airport_codes: Mapped[list["AirportCodes"]] = relationship('AirportCodes', secondary=itinerary_has_airport_codes,
                                                               back_populates="itineraries")
    flight_sessions: Mapped["FlightSessions"] = relationship(back_populates="itineraries")
    itinerary_type: Mapped["ItineraryTypes"] = relationship(back_populates="itineraries")
    plane: Mapped["Planes"] = relationship(back_populates="itinerary")

    def __repr__(self):
        return f"<departure_time={self.departure_time} arrival_time={self.arrival_time} landing_number={self.landings_amount}>"
