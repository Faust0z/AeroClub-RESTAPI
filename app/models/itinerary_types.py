from sqlalchemy import Column, Integer, String, UUID
from sqlalchemy.orm import Mapped, relationship
import uuid

from ..database import Base


class ItineraryTypes(Base):
    __tablename__ = 'itinerary_types'
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = Column(String, unique=True)

    itineraries: Mapped[list["Itineraries"]] = relationship(back_populates="itinerary_type")

    def __repr__(self):
        return f"type=<{self.type}>"
