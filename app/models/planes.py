from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from ..database import Base


class Planes(Base):
    __tablename__ = 'planes'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    registration: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String, nullable=False)
    acquisition_date: Mapped[date] = mapped_column(Date, nullable=False)
    consumption_per_hour: Mapped[int] = mapped_column(Integer, nullable=False)
    fare: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    plane_status_id: Mapped[int] = mapped_column(ForeignKey('plane_status.id'))

    itinerary: Mapped[list["Itineraries"]] = relationship(back_populates="plane")
    plane_status: Mapped["PlaneStatus"] = relationship(back_populates="plane")

    def __repr__(self):
        return (f"<Plane "
                f"id={self.id} "
                f"model='{self.model}' "
                f"consumption_per_hour={self.consumption_per_hour}>")
