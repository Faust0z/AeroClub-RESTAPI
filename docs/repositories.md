<!-- Load when: Adding or editing data access -->

# Repositories — Data Access

All repository classes live under `app/repositories/`. One class per SQLAlchemy model. Services instantiate repositories and call their methods.

## Pattern

```python
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Roles


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Roles]:
        return self.db.scalars(select(Roles)).all()

    def get_by_name(self, name: str) -> Optional[Roles]:
        return self.db.execute(select(Roles).where(Roles.name == name)).scalar_one_or_none()

    def add(self, role: Roles) -> Roles:
        self.db.add(role)
        self.db.commit()
        return role

    def update(self, role: Roles) -> Roles:
        self.db.commit()
        return role

    def delete(self, role: Roles) -> None:
        self.db.delete(role)
        self.db.commit()
```

Key rules:
- Constructor takes `db: Session`, stores as `self.db`
- Read methods: `db.execute(select(Model).where(...)).scalar_one_or_none()` or `db.scalars(select(Model)).all()`
- Write methods: `self.db.add(obj)`, `self.db.commit()`, `self.db.delete(obj)`
- `flush()` available for flush-without-commit (used in billing)
- Return ORM models, not schemas

## Example — RoleRepository

See `app/repositories/roles.py`:
- `get_all()`, `get_by_name()`, `add()`, `update()`, `delete()`

## Example — UserRepository

See `app/repositories/users.py`:
- `get_by_id(user_id, include_roles=False)`, `get_by_email(email, include_roles=False)`, `get_all(...)`, `add()`, `update()`, `delete()`, `flush()`
- Uses `joinedload(Users.roles)` for eager loading relationships
