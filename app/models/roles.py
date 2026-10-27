from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from .associations import users_have_roles
from ..database import Base


class Roles(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = Column(String, nullable=False, unique=True)

    users: Mapped[list["Users"]] = relationship("Users", secondary=users_have_roles, back_populates="roles")

    def __repr__(self):
        return f"<Role name={self.name}>"
