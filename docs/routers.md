<!-- Load when: Adding or editing an API route -->

# Routers — FastAPI APIRouter

All routes live under `app/routers/`. One `APIRouter` per resource, mounted in `app/main.py`.

## Pattern

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database import get_db
from app.schemas import RolesOut
from app.services.roles import get_roles_srv

router = APIRouter(prefix="/v1/roles", tags=["roles"])


@router.get("/", response_model=List[RolesOut])
def list_roles(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    roles = get_roles_srv(db=db)
    return roles
```

Key rules:
- Router prefix = `"/v1/<resource>"`, `tags=["<resource>"]`
- Routes are plain functions (not `async` unless doing async I/O)
- `db: Annotated[Session, Depends(get_db)]` injects SQLAlchemy session
- `current_user: Annotated[Users, Depends(require_admin)]` enforces auth/RBAC
- Convert ORM models to schemas with `UsersOut.model_validate(user)` before returning
- Error handling: catch `AppError` subclasses, raise `HTTPException(status_code=e.status_code, detail=e.detail)`
- Pagination: `skip: int = Query(0, ge=0)`, `limit: int = Query(100, ge=1, le=1000)` on list endpoints

## Auth dependencies

| Dependency | Requires |
|------------|----------|
| `get_current_user` | Valid JWT, active account |
| `require_admin` | `Admin` role |
| `require_instructor` | `Instructor` role |
| `require_admin_or_instructor` | `Admin` or `Instructor` |
| `require_active_user` | Valid JWT only (active account) |

JWT `sub` = user UUID (string), not email.

## Example — Users router

See `app/routers/users.py`:
- `POST /v1/users/register` (public)
- `POST /v1/users/login` (public, returns JWT)
- `GET /v1/users/me` (own profile)
- `GET /v1/users/{user_id}`, `PATCH /v1/users/{user_id}`, `DELETE /v1/users/{user_id}` (Admin/self)
