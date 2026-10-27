from datetime import datetime, timedelta, timezone

import jwt
from pydantic import BaseModel

from app.config.settings import settings


class TokenPayload(BaseModel):
    sub: str
    roles: list[str]
    status: bool
    exp: int


def create_access_token(
    subject: str,
    roles: list[str],
    status: bool,
    expires_delta: timedelta | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode = {
        "sub": subject,
        "roles": roles,
        "status": status,
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return TokenPayload(**payload)
