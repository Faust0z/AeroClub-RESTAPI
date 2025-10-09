from app.models.roles import Roles
from ..errors import RoleNotFound
from ..extensions import db


def get_roles_srv() -> list[Roles]:
    return db.session.scalars(db.select(Roles)).all()


def get_role_by_name_srv(name: str) -> Roles:
    role = db.session.execute(db.select(Roles).where(Roles.name == name)).scalar_one_or_none()
    if not role:
        raise RoleNotFound
    return role


def get_user_roles_srv(email: str) -> list[Roles]:
    from .users import get_user_by_email_srv  # To avoid circular import issues
    user = get_user_by_email_srv(email=email)
    return user.roles


def add_user_role_srv(email: str, role_name: str) -> list[Roles]:
    from .users import get_user_by_email_srv  # To avoid circular import issues
    user = get_user_by_email_srv(email=email, include_roles=True)
    role = get_role_by_name_srv(name=role_name)

    if role not in user.roles:
        user.roles.append(role)
        db.session.commit()
    return user.roles


def del_user_role_srv(email: str, role_name: str) -> list[Roles]:
    from .users import get_user_by_email_srv  # To avoid circular import issues
    user = get_user_by_email_srv(email=email)
    role = get_role_by_name_srv(name=role_name)

    if role in user.roles:
        user.roles.remove(role)
        db.session.commit()
    return user.roles
