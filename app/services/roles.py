from app.models.roles import Roles
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..errors import RoleNotFound
from ..models import Users


def get_roles_srv(db: Session) -> list[Roles]:
    return db.scalars(select(Roles)).all()


def get_role_by_name_srv(db: Session, name: str) -> Roles:
    role = db.execute(select(Roles).where(Roles.name == name)).scalar_one_or_none()
    if not role:
        raise RoleNotFound
    return role


def get_user_roles_srv(db: Session, email: str) -> list[Roles]:
    from .users import get_user_by_email_srv  # To avoid circular import issues
    user = get_user_by_email_srv(db=db, email=email)
    return user.roles


def add_user_role_srv(db: Session, email: str, role_name: str) -> list[Roles]:
    from .users import get_user_by_email_srv  # To avoid circular import issues
    user = get_user_by_email_srv(db=db, email=email, include_roles=True)
    role = get_role_by_name_srv(db=db, name=role_name)

    if role not in user.roles:
        user.roles.append(role)
        db.commit()
    return user.roles


def del_user_role_srv(db: Session, email: str, role_name: str) -> list[Roles]:
    from .users import get_user_by_email_srv  # To avoid circular import issues
    user = get_user_by_email_srv(db=db, email=email)
    role = get_role_by_name_srv(db=db, name=role_name)

    if role in user.roles:
        user.roles.remove(role)
        db.commit()
    return user.roles
