import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..models import Users, Roles


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID, include_roles: bool = False) -> Optional[Users]:
        stmt = select(Users).where(Users.uuid == user_id)
        if include_roles:
            stmt = stmt.options(joinedload(Users.roles))
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def get_by_email(self, email: str, include_roles: bool = False) -> Optional[Users]:
        stmt = select(Users).where(Users.email == email)
        if include_roles:
            stmt = stmt.options(joinedload(Users.roles))
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def get_all(
        self,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role_name: Optional[str] = None,
        include_inactive: bool = False,
        include_roles: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Users]:
        stmt = select(Users)
        if include_roles:
            stmt = stmt.options(joinedload(Users.roles))

        if email:
            stmt = stmt.where(Users.email.ilike(f"%{email}%"))
        if first_name:
            stmt = stmt.where(Users.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.where(Users.last_name.ilike(f"%{last_name}%"))
        if role_name:
            stmt = stmt.join(Users.roles).where(Roles.name.ilike(f"%{role_name}%"))
        if not include_inactive:
            stmt = stmt.where(Users.status != 0)
        stmt = stmt.offset(skip).limit(limit)
        return self.db.execute(stmt).unique().scalars().all()

    def add(self, user: Users) -> Users:
        self.db.add(user)
        self.db.commit()
        return user

    def update(self, user: Users) -> Users:
        self.db.commit()
        return user

    def delete(self, user: Users) -> None:
        self.db.delete(user)
        self.db.commit()

    def flush(self) -> None:
        self.db.flush()
