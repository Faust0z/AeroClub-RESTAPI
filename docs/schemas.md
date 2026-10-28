<!-- Load when: Adding or editing a Pydantic schema -->

# Schemas — Pydantic v2 Models

All schemas live under `app/schemas/`. One file per resource. Import patterns:
- Input schemas: `*Create`, `*Register`, `*Update`
- Output schemas: `*Out` (role-specific variants where needed, e.g. `UsersAdminOut`, `UsersInstructorOut`)

## Pattern

```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Annotated, Optional


class RolesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class RolesOut(RolesBase):
    pass


class RolesCreate(BaseModel):
    name: str


class RolesUpdate(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
```

Key rules:
- `ConfigDict(from_attributes=True)` on all `*Out` schemas to serialize from SQLAlchemy ORM objects
- `load_only`/`dump_only` replaced by separate input/output models (no `load_only` concept)
- Password fields use `Annotated[str, Field(min_length=8)]` for validation
- Pydantic v2: `model_config`, `model_validate`, `model_dump`
- Forward references (e.g. `UsersOut.roles: List["RolesOut"]`) resolved via `model_rebuild()` in `app/schemas/__init__.py`
- `EmailStr` for email fields

## Example — Users schemas

See `app/schemas/users.py`:
- `UsersRegister`: input, password `min_length=8`
- `UsersOut`, `UsersInstructorOut`, `UsersAdminOut`: output variants with role-specific fields
- `UsersUpdate`, `UsersAdminUpdate`: partial update schemas (all fields optional)
- `UsersLogin`: `email: EmailStr`, `password: str`

## Example — Planes schemas

See `app/schemas/planes.py`:
- `PlanesBase`: shared fields with `from_attributes=True`
- `PlanesOut`, `PlanesCreate`, `PlanesUpdate`
