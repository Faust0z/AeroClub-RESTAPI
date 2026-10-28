import uuid
from typing import Tuple

from sqlalchemy.orm import Session

from app.models import Roles
from app.repositories import RoleRepository, UserRepository
from app.schemas import RolesOut
from ..errors import RoleNotFound, UserNotFound


def get_roles_srv(db: Session, skip: int = 0, limit: int = 100) -> list[RolesOut]:
    repo = RoleRepository(db)
    stmt = repo.get_all(skip=skip, limit=limit)
    roles = db.execute(stmt).unique().scalars().all()
    return [RolesOut.model_validate(r) for r in roles]


def get_role_by_name_srv(db: Session, name: str) -> Roles:
    repo = RoleRepository(db)
    role = repo.get_by_name(name=name)
    if not role:
        raise RoleNotFound
    return role


def get_user_roles_srv(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[RolesOut]:
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id=user_id, include_roles=True)
    if not user:
        from ..errors import UserNotFound
        raise UserNotFound
    return [RolesOut.model_validate(r) for r in user.roles]


def add_user_role_srv(db: Session, user_id: uuid.UUID, role_name: str) -> list[RolesOut]:
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    user = user_repo.get_by_id(user_id=user_id, include_roles=True)
    if not user:
        from ..errors import UserNotFound
        raise UserNotFound
    role = role_repo.get_by_name(name=role_name)
    if not role:
        raise RoleNotFound

    if role not in user.roles:
        user.roles.append(role)
        user_repo.update(user)
    return [RolesOut.model_validate(r) for r in user.roles]


def del_user_role_srv(db: Session, user_id: uuid.UUID, role_name: str) -> list[RolesOut]:
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    user = user_repo.get_by_id(user_id=user_id)
    if not user:
        from ..errors import UserNotFound
        raise UserNotFound
    role = role_repo.get_by_name(name=role_name)
    if not role:
        raise RoleNotFound

    if role in user.roles:
        user.roles.remove(role)
        user_repo.update(user)
    return [RolesOut.model_validate(r) for r in user.roles]
