from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin, require_active_user
from app.database import get_db
from app.errors import RoleNotFound, UserNotFound
from app.models import Users
from app.schemas import RolesOut, RolesUpdate
from app.services.roles import (
    add_user_role_srv,
    del_user_role_srv,
    get_role_by_name_srv,
    get_roles_srv,
    get_user_roles_srv,
)

router = APIRouter(prefix="/v1/roles", tags=["roles"])


@router.get("/", response_model=List[RolesOut])
def list_roles(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    roles = get_roles_srv(db=db)
    return roles


@router.get("/me", response_model=List[RolesOut])
def get_my_roles(
    current_user: Annotated[Users, Depends(require_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    roles = get_user_roles_srv(db=db, email=current_user.email)
    return roles


@router.get("/{email}", response_model=List[RolesOut])
def get_user_roles(
    email: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        roles = get_user_roles_srv(db=db, email=email)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="No user found with the given email")
    return roles


@router.post("/{email}/{role}", response_model=List[RolesOut], status_code=status.HTTP_201_CREATED)
def add_user_role(
    email: str,
    role: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        roles = add_user_role_srv(db=db, email=email, role_name=role)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="No user found with the given email")
    except RoleNotFound:
        raise HTTPException(status_code=404, detail="Role not found")
    return roles


@router.delete("/{email}/{role}", response_model=List[RolesOut])
def delete_user_role(
    email: str,
    role: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    """The User role cannot be revoked (business rule)."""
    try:
        roles = del_user_role_srv(db=db, email=email, role_name=role)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="No user found with the given email")
    except RoleNotFound:
        raise HTTPException(status_code=404, detail="Role not found")
    return roles
