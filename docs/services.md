<!-- Load when: Adding or editing business logic -->

# Services — Business Logic

All service functions live under `app/services/`. One file per resource. Services receive `db: Session` and input data (dict or Pydantic model), return SQLAlchemy ORM models (routers convert to schemas).

## Pattern

```python
import uuid
from sqlalchemy.orm import Session

from app.repositories import UserRepository
from app.schemas import UsersOut
from ..errors import UserNotFound


def get_user_by_id_srv(db: Session, user_id: uuid.UUID) -> Users:
    repo = UserRepository(db)
    user = repo.get_by_id(user_id=user_id)
    if not user:
        raise UserNotFound
    return user
```

Key rules:
- First argument: `db: Session`
- Instantiate repository: `repo = UserRepository(db)`
- Call repo methods for data access
- Raise domain exceptions from `app.errors` (e.g. `UserNotFound`, `EmailAlreadyExists`)
- Return ORM models, **not** Pydantic schemas (routers handle serialization)
- Password hashing: import `get_password_hash` from `app.auth.dependencies`
- Password verification: import `verify_password` from `app.auth.dependencies`
- Do NOT perform authorization checks — those belong in FastAPI dependencies

## Example — Users service

See `app/services/users.py`:
- `get_users_srv`, `get_user_by_email_srv`, `get_user_by_id_srv`
- `update_user_srv`, `disable_user_srv`, `register_user_srv`, `authenticate_user_srv`

## Example — Flight sessions service

See `app/services/flight_sessions.py`:
- Complex billing: `create_flight_session_srv` creates itineraries, calculates cost with `decimal.Decimal`, creates debit transaction atomically
- Cost calculation: `__calculate_itinerary_cost` — rounds up to 0.1h blocks, quantizes to 2 decimals
