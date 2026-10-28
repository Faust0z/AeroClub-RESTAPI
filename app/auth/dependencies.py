import bcrypt
import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload

from app.auth.tokens import decode_token, TokenPayload
from app.database import get_db
from app.models import Users

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/users/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Users:
    try:
        payload: TokenPayload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(Users).options(joinedload(Users.roles)).filter(Users.uuid == uuid.UUID(payload.sub)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    return user


def require_admin(user: Annotated[Users, Depends(get_current_user)]) -> Users:
    if not any(r.name == "Admin" for r in user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user


def require_instructor(user: Annotated[Users, Depends(get_current_user)]) -> Users:
    if not any(r.name == "Instructor" for r in user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Instructor role required")
    return user


def require_admin_or_instructor(user: Annotated[Users, Depends(get_current_user)]) -> Users:
    if not any(r.name in ("Admin", "Instructor") for r in user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Instructor role required")
    return user


def require_active_user(user: Annotated[Users, Depends(get_current_user)]) -> Users:
    return user
