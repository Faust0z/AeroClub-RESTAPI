from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from .roles import get_role_by_name_srv
from ..errors import EmailAlreadyExists, UserNotFound, AuthError
from ..models import Users, Roles, Balances


def get_users_srv(db: Session, email: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None,
                  role_name: Optional[str] = None, include_inactive: bool = False) -> list[Users]:
    stmt = select(Users).options(joinedload(Users.roles))

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

    return db.execute(stmt).unique().scalars().all()


def get_user_by_email_srv(db: Session, email: Optional[str] = None, include_roles: bool = False) -> Users:
    stmt = select(Users).where(Users.email == email)
    if include_roles:
        stmt = stmt.options(joinedload(Users.roles))

    user = db.execute(stmt).unique().scalar_one_or_none()
    if not user:
        raise UserNotFound
    return user


def update_user_srv(db: Session, email: str, data: dict) -> Users:
    user = get_user_by_email_srv(db=db, email=email)

    try:
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyExists
    return user


def disable_user_srv(db: Session, email: str) -> Users:
    user = get_user_by_email_srv(db=db, email=email)

    user.status = False
    user.disabled_at = datetime.now(timezone.utc)
    db.commit()
    return user


def register_user_srv(db: Session, data: dict) -> Users:
    from app.auth.dependencies import get_password_hash

    user = Users(**data)
    user.password = get_password_hash(user.password)
    user.created_at = date.today()
    user.roles = get_role_by_name_srv(db, "User")
    user.status = True
    user.balance = Balances(balance=0, user_id=user.id)

    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyExists

    return user


def authenticate_user_srv(db: Session, email: str, password: str) -> Users:
    from app.auth.dependencies import verify_password

    user = get_user_by_email_srv(db=db, email=email)
    if not verify_password(password, user.password):
        raise AuthError
    return user
