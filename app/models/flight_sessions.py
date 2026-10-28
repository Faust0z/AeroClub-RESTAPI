from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, Text, UUID
from sqlalchemy.orm import Mapped, relationship
import uuid

from .associations import users_have_flight_sessions
from ..database import Base


class FlightSessions(Base):
    __tablename__ = "flight_sessions"
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flight_session_identifier: Mapped[int] = Column(Integer, nullable=False)
    issued_date: Mapped[date] = Column(Date, nullable=False)
    observations: Mapped[str] = Column(Text, nullable=True)
    transaction_id: Mapped[int] = Column(ForeignKey("transactions.id"))

    users: Mapped[list["Users"]] = relationship("Users", secondary=users_have_flight_sessions,
                                                  back_populates="flight_sessions")
    transactions: Mapped[list["Transactions"]] = relationship(back_populates="flight_sessions")
    itineraries: Mapped[list["Itineraries"]] = relationship(back_populates="flight_sessions")

    def __repr__(self):
        return f"<issued_date={self.issued_date} flight_session_identifier={self.flight_session_identifier}>"
