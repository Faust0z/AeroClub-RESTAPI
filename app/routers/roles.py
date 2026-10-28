import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Body
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin, require_active_user
from app.database import get_db
from app.errors import RoleNotFound, UserNotFound
from app.models import Users
from app.schemas import RolesOut
from app.services.roles import (
    add_user_role_srv,
    del_user_role_srv,
    get_role_by_name_srv,
    get_roles_srv,
    get_user_roles_srv,
)

router = APIRouter(prefix="/v1/roles", tags=["roles"])


@router.get("/", response_model=Page[RolesOut])
def list_roles(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    stmt = get_roles_srv(db=db)
    return paginate(db, stmt)


@router.get("/me", response_model=List[RolesOut])
def get_my_roles(
    current_user: Annotated[Users, Depends(require_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    roles = get_user_roles_srv(db=db, user_id=current_user.uuid)
    return roles


@router.get("/{user_id}", response_model=List[RolesOut])
def get_user_roles(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        roles = get_user_roles_srv(db=db, user_id=user_id)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
    return roles


@router.post("/{user_id}", response_model=List[RolesOut], status_code=status.HTTP_201_CREATED)
def add_user_role(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
    role: str = Body(..., embed=True),
):
    try:
        roles = add_user_role_srv(db=db, user_id=user_id, role_name=role)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
    except RoleNotFound:
        raise HTTPException(status_code=404, detail="Role not found")
    return roles


@router.delete("/{user_id}", response_model=List[RolesOut])
def delete_user_role(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
    role: str = Body(..., embed=True),
):
    """The User role cannot be revoked (business rule)."""
    try:
        roles = del_user_role_srv(db=db, user_id=user_id, role_name=role)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
    except RoleNotFound:
        raise HTTPException(status_code=404, detail="Role not found")
    return roles
