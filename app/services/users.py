import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Users
from app.repositories import UserRepository
from app.schemas import (
    UsersAdminOut,
    UsersAdminUpdate,
    UsersInstructorOut,
    UsersOut,
    UsersRegister,
    UsersUpdate,
)
from ..errors import EmailAlreadyExists, UserNotFound, AuthError


def get_users_srv(
    db: Session,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    role_name: Optional[str] = None,
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> list[Users]:
    repo = UserRepository(db)
    users = repo.get_all(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role_name=role_name,
        include_inactive=include_inactive,
        include_roles=True,
        skip=skip,
        limit=limit,
    )
    return users


def get_user_by_email_srv(db: Session, email: str) -> Users:
    repo = UserRepository(db)
    user = repo.get_by_email(email=email)
    if not user:
        raise UserNotFound
    return user


def get_user_by_id_srv(db: Session, user_id: uuid.UUID) -> Users:
    repo = UserRepository(db)
    user = repo.get_by_id(user_id=user_id)
    if not user:
        raise UserNotFound
    return user


def update_user_srv(db: Session, user_id: uuid.UUID, data: dict) -> Users:
    repo = UserRepository(db)
    user = repo.get_by_id(user_id=user_id)
    if not user:
        raise UserNotFound

    try:
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        repo.update(user)
    except IntegrityError:
        repo.db.rollback()
        raise EmailAlreadyExists
    return user


def disable_user_srv(db: Session, user_id: uuid.UUID) -> Users:
    repo = UserRepository(db)
    user = repo.get_by_id(user_id=user_id)
    if not user:
        raise UserNotFound

    user.status = False
    user.disabled_at = datetime.now(timezone.utc)
    repo.update(user)
    return user


def register_user_srv(db: Session, data: dict) -> Users:
    from app.auth.dependencies import get_password_hash

    repo = UserRepository(db)
    user_data = data.copy()
    user_data["password"] = get_password_hash(user_data["password"])
    user = Users(**user_data)
    from .roles import get_role_by_name_srv

    user.roles = [get_role_by_name_srv(db, "User")]
    user.status = True
    from app.models import Balances
    user.balance = Balances(balance=0, user_id=user.uuid)

    try:
        repo.add(user)
    except IntegrityError:
        repo.db.rollback()
        raise EmailAlreadyExists
    return user


def authenticate_user_srv(db: Session, email: str, password: str) -> Users:
    from app.auth.dependencies import verify_password

    repo = UserRepository(db)
    user = repo.get_by_email(email=email)
    if not user:
        raise UserNotFound
    if not verify_password(password, user.password):
        raise AuthError
    return user
