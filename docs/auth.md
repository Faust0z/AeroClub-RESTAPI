<!-- Load when: Changing auth, JWT, or RBAC -->

# Authentication — PyJWT + FastAPI Dependencies

Authentication lives under `app/auth/`. Stateless JWT with PyJWT, bcrypt for passwords, role-based access via FastAPI `Depends`.

## Pattern

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.tokens import decode_token
from app.database import get_db
from app.models import Users

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/users/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Users:
    payload: TokenPayload = decode_token(token)
    user = db.query(Users).filter(Users.uuid == payload.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.status:
        raise HTTPException(status_code=403, detail="Account disabled")
    return user


def require_admin(user: Annotated[Users, Depends(get_current_user)]) -> Users:
    if "Admin" not in user.roles:
        raise HTTPException(status_code=403, detail="Admin role required")
    return user
```

Key rules:
- JWT `sub` claim = user UUID (string), not email
- Token contains claims: `sub`, `roles` (list), `status` (bool), `exp`
- `create_access_token(subject, roles, status, expires_delta)` in `app/auth/tokens.py`
- `decode_token(token)` → `TokenPayload` Pydantic model
- Password hashing: `get_password_hash(password)` → bcrypt hash string
- Password verification: `verify_password(plain, hashed)` → bool
- Role checks in FastAPI `Depends` chain, **not** in services
- Role names: `"User"`, `"Instructor"`, `"Admin"` (cumulative: Admin > Instructor > User)

## Example — Login flow

See `app/routers/users.py` `login()`:
1. Verify email/password via `authenticate_user_srv`
2. Check `user.status`
3. Call `create_access_token(subject=str(user.uuid), roles=roles, status=user.status)`
4. Return `{"msg", "access_token", "user": {...}}`

## TokenPayload model

See `app/auth/tokens.py`:
```python
class TokenPayload(BaseModel):
    sub: str
    roles: list[str]
    status: bool
    exp: int
```
