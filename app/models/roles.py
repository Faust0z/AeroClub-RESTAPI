from sqlalchemy import Column, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import Mapped, relationship
import uuid

from .associations import users_have_roles
from ..database import Base


class Roles(Base):
    __tablename__ = 'roles'
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String, nullable=False, unique=True)

    users: Mapped[list["Users"]] = relationship("Users", secondary=users_have_roles, back_populates="roles")

    def __repr__(self):
        return f"<Role name={self.name}>"
