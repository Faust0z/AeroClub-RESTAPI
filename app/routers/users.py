import uuid
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
    require_admin,
    require_admin_or_instructor,
    require_active_user,
)
from app.database import get_db
from app.errors import (
    AppError,
    EmailAlreadyExists,
    UserNotFound,
    AuthError,
    PermissionDenied,
    PermissionDeniedDisabledUser,
)
from app.models import Users
from app.schemas import (
    UsersAdminOut,
    UsersAdminUpdate,
    UsersInstructorOut,
    UsersLogin,
    UsersOut,
    UsersRegister,
    UsersUpdate,
)
from app.services.users import (
    authenticate_user_srv,
    disable_user_srv,
    get_user_by_email_srv,
    get_user_by_id_srv,
    get_users_srv,
    register_user_srv,
    update_user_srv,
)

router = APIRouter(prefix="/v1/users", tags=["users"])


@router.get("/", response_model=Page[UsersOut])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin_or_instructor)],
    email: Optional[str] = Query(None),
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    role_name: Optional[str] = Query(None),
):
    stmt = get_users_srv(
        db=db,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role_name=role_name,
    )
    return paginate(db, stmt)


@router.get("/me", response_model=UsersOut)
def get_my_info(
    current_user: Annotated[Users, Depends(require_active_user)],
):
    return current_user


@router.get("/{user_id}", response_model=UsersOut)
def get_user_by_id(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin_or_instructor)],
):
    try:
        user = get_user_by_id_srv(db=db, user_id=user_id)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
    if any(r.name == "Admin" for r in current_user.roles):
        return UsersOut.model_validate(user)
    return UsersInstructorOut.model_validate(user)


@router.patch("/{user_id}", response_model=UsersOut)
def update_user(
    user_id: uuid.UUID,
    user_data: UsersUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
):
    caller_id = current_user.uuid
    is_admin = any(r.name == "Admin" for r in current_user.roles)
    if not is_admin and caller_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource")

    schema = UsersAdminUpdate if is_admin else UsersUpdate
    try:
        user = update_user_srv(db=db, user_id=current_user.uuid, data=user_data.model_dump(exclude_unset=True))
    except EmailAlreadyExists:
        raise HTTPException(status_code=409, detail="The email given is already registered")
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
    return UsersOut.model_validate(user)


@router.delete("/{user_id}", response_model=UsersOut)
def delete_user(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        user = disable_user_srv(db=db, user_id=current_user.uuid)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
    return UsersOut.model_validate(user)


@router.post("/register", response_model=UsersOut, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UsersRegister,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        user = register_user_srv(db=db, data=user_data.model_dump())
    except EmailAlreadyExists:
        raise HTTPException(status_code=409, detail="The email given is already registered")
    return UsersOut.model_validate(user)


@router.post("/login")
def login(
    login_data: UsersLogin,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        user = authenticate_user_srv(db=db, email=login_data.email, password=login_data.password)
    except AuthError:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided or are invalid")
    except UserNotFound:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided or are invalid")

    if not user.status:
        raise HTTPException(status_code=403, detail="User account is disabled")

    from app.auth.tokens import create_access_token

    roles = [role.name for role in user.roles] if user.roles else ["User"]
    access_token = create_access_token(
        subject=str(user.uuid),
        roles=roles,
        status=user.status,
    )
    return {
        "msg": "Login successful",
        "access_token": access_token,
        "user": {
            "uuid": str(user.uuid),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roles": roles,
        },
    }
