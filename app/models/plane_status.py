from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from ..database import Base


class PlaneStatus(Base):
    __tablename__ = "plane_status"
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    state: Mapped[str] = Column(String, unique=True)

    plane: Mapped[list["Planes"]] = relationship(back_populates="plane_status")

    def __repr__(self):
        return f"State=<{self.state}>"
