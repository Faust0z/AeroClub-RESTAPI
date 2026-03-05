from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash, check_password_hash

from .roles import get_role_by_name_srv
from ..errors import EmailAlreadyExists, UserNotFound, AuthError
from ..extensions import db
from ..models import Users, Roles, Balances


def get_users_srv(email: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None,
                  role_name: Optional[str] = None, include_inactive: bool = False) -> list[Users]:
    stmt = db.select(Users).options(joinedload(Users.roles))

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

    return db.session.execute(stmt).unique().scalars().all()


def get_user_by_email_srv(email: str = None, include_roles: bool = False) -> Users:
    stmt = db.select(Users).where(Users.email == email)
    if include_roles:
        stmt = stmt.options(joinedload(Users.roles))

    user = db.session.execute(stmt).unique().scalar_one_or_none()
    if not user:
        raise UserNotFound
    return user


def update_user_srv(email: str, data: dict) -> Users:
    user = get_user_by_email_srv(email=email)

    try:
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise EmailAlreadyExists
    return user


def disable_user_srv(email) -> Users:
    user = get_user_by_email_srv(email)

    user.status = False
    user.disabled_at = datetime.now(timezone.utc)
    db.session.commit()
    return user


def register_user_srv(user: Users) -> Users:
    user.password = generate_password_hash(user.password)
    user.created_at = date.today()
    user.roles = get_role_by_name_srv("User")
    user.status = True
    user.balance = Balances(balance=0, user_id=user.id)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        raise EmailAlreadyExists

    return user


def authenticate_user_srv(email: str, password: str) -> Users:
    user = get_user_by_email_srv(email=email)
    if not check_password_hash(user.password, password=password):
        raise AuthError
    return user
