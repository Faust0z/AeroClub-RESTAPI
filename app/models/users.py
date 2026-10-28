import uuid
from datetime import date

from app.models import FlightSessions
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import Mapped, relationship

from .associations import users_have_roles, users_have_flight_sessions
from ..database import Base


class Users(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uuid: Mapped[str] = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)
    first_name: Mapped[str] = Column(String, nullable=False)
    last_name: Mapped[str] = Column(String, nullable=False)
    email: Mapped[str] = Column(String, nullable=False, unique=True)
    password: Mapped[str] = Column(String, nullable=False)
    phone_number: Mapped[str] = Column(String, nullable=False)
    created_at: Mapped[date] = Column(Date, nullable=False)
    disabled_at: Mapped[date] = Column(Date)
    address: Mapped[str] = Column(String)
    status: Mapped[bool] = Column(Boolean, nullable=False)

    balance: Mapped["Balances"] = relationship(back_populates="user")
    roles: Mapped[list["Roles"]] = relationship("Roles", secondary=users_have_roles, back_populates="users")
    flight_sessions: Mapped[list["FlightSessions"]] = relationship("FlightSessions",
                                                                     secondary=users_have_flight_sessions,
                                                                     back_populates="users")

    def __repr__(self):
        return f"<first_name={self.first_name} email={self.email}>"
