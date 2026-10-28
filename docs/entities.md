<!-- Load when: Adding or editing an SQLAlchemy entity -->

# Entities — SQLAlchemy Models

All models inherit from `app.database.Base` (SQLAlchemy 2.0 `DeclarativeBase`). One model per file under `app/models/`.

## Pattern

```python
from datetime import date
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from ..database import Base


class AirportCodes(Base):
    __tablename__ = 'airport_codes'
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = Column(String(3), unique=True)
```

Key rules:
- Table name via `__tablename__` (snake_case, plural)
- Primary key `id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)`
- `Users` additionally has `uuid: Mapped[str] = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)` — used as JWT `sub`
- Relationships via `db.relationship` with `back_populates` on both sides; many-to-many uses association tables in `app/models/associations.py`
- Soft-delete on `Users`: `status: Mapped[bool] = Column(Boolean, nullable=False)` + `disabled_at: Mapped[date] = Column(Date)`
- `Mapped[...]` type annotations required on all columns

## Example — Users model

See `app/models/users.py`:
- Columns: `id`, `uuid`, `first_name`, `last_name`, `email`, `password`, `phone_number`, `created_at`, `disabled_at`, `address`, `status`
- Relationships: `balance` (1:1), `roles` (many:many via `users_have_roles`), `flight_sessions` (many:many via `users_have_flight_sessions`)

## Example — Planes model

See `app/models/planes.py`:
- Columns: `id`, `brand`, `model`, `registration`, `category`, `acquisition_date`, `consumption_per_hour`, `fare`, `description`, `plane_status_id`
- Relationships: `itinerary`, `plane_status`
