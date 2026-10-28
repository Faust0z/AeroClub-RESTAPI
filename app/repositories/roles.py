from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Roles


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return select(Roles)

    def get_by_name(self, name: str) -> Optional[Roles]:
        return self.db.execute(select(Roles).where(Roles.name == name)).scalar_one_or_none()

    def add(self, role: Roles) -> Roles:
        self.db.add(role)
        self.db.commit()
        return role

    def update(self, role: Roles) -> Roles:
        self.db.commit()
        return role

    def delete(self, role: Roles) -> None:
        self.db.delete(role)
        self.db.commit()
