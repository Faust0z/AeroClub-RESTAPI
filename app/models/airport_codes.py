from sqlalchemy import Column, Integer, String, UUID
from sqlalchemy.orm import Mapped, relationship
import uuid

from .associations import itinerary_has_airport_codes
from ..database import Base


class AirportCodes(Base):
    __tablename__ = 'airport_codes'
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = Column(String(3), unique=True)

    itineraries: Mapped[list["Itineraries"]] = relationship("Itineraries", secondary=itinerary_has_airport_codes,
                                                              back_populates="airport_codes")

    def __repr__(self):
        return f"<code={self.code}>"
