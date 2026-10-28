from sqlalchemy import Column, Integer, String, UUID
from sqlalchemy.orm import Mapped, relationship
import uuid

from ..database import Base


class PlaneStatus(Base):
    __tablename__ = "plane_status"
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state: Mapped[str] = Column(String, unique=True)

    plane: Mapped[list["Planes"]] = relationship(back_populates="plane_status")

    def __repr__(self):
        return f"State=<{self.state}>"
