from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from ..database import Base


class ItineraryTypes(Base):
    __tablename__ = 'itinerary_types'
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = Column(String, unique=True)

    itineraries: Mapped[list["Itineraries"]] = relationship(back_populates="itinerary_type")

    def __repr__(self):
        return f"type=<{self.type}>"
