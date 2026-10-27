from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
    UsersOut,
    UsersRegister,
    UsersUpdate,
)
from app.services.users import (
    authenticate_user_srv,
    disable_user_srv,
    get_user_by_email_srv,
    get_users_srv,
    register_user_srv,
    update_user_srv,
)

router = APIRouter(prefix="/v1/users", tags=["users"])


@router.get("/", response_model=List[UsersOut])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin_or_instructor)],
    email: Optional[str] = Query(None),
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    role_name: Optional[str] = Query(None),
):
    try:
        users = get_users_srv(db=db, email=email, first_name=first_name, last_name=last_name, role_name=role_name)
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    if "Admin" in current_user.roles:
        return [UsersOut.model_validate(u) for u in users]
    return [UsersInstructorOut.model_validate(u) for u in users]


@router.get("/me", response_model=UsersOut)
def get_my_info(
    current_user: Annotated[Users, Depends(require_active_user)],
):
    return current_user


@router.get("/{email}", response_model=UsersOut)
def get_user_by_email(
    email: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin_or_instructor)],
):
    try:
        user = get_user_by_email_srv(db=db, email=email)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="No user found with the given email")
    if "Admin" in current_user.roles:
        return UsersOut.model_validate(user)
    return UsersInstructorOut.model_validate(user)


@router.patch("/{email}", response_model=UsersOut)
def update_user(
    email: str,
    user_data: UsersUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
):
    caller_email = current_user.email
    is_admin = "Admin" in current_user.roles
    if not is_admin and caller_email != email:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource")

    schema = UsersAdminUpdate if is_admin else UsersUpdate
    try:
        user = update_user_srv(db=db, email=email, data=user_data.model_dump(exclude_unset=True))
    except EmailAlreadyExists:
        raise HTTPException(status_code=409, detail="The email given is already registered")
    except UserNotFound:
        raise HTTPException(status_code=404, detail="No user found with the given email")
    return UsersOut.model_validate(user)


@router.delete("/{email}", response_model=UsersOut)
def delete_user(
    email: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        user = disable_user_srv(db=db, email=email)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="No user found with the given email")
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
    db: Annotated[Session, Depends(get_db)],
    email: str,
    password: str,
):
    try:
        user = authenticate_user_srv(db=db, email=email, password=password)
    except AuthError:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided or are invalid")
    except UserNotFound:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided or are invalid")

    if not user.status:
        raise HTTPException(status_code=403, detail="User account is disabled")

    from app.auth.tokens import create_access_token

    roles = [role.name for role in user.roles] if user.roles else ["User"]
    access_token = create_access_token(
        subject=user.email,
        roles=roles,
        status=user.status,
    )
    return {
        "msg": "Login successful",
        "access_token": access_token,
        "user": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roles": roles,
        },
    }
