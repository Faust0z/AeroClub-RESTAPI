# AeroClub REST API — AI Agent Guidance

AeroClub is a RESTful API for managing aviation training center operations: user authentication, role-based access control, financial ledger accounting, and flight session billing.

## Stack

| Layer | Technology |
|-------|------------|
| Language/Runtime | Python 3.12 |
| Web Framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 (sync) |
| Serialization | Pydantic v2 |
| Authentication | PyJWT (JWT), bcrypt for passwords |
| Database | PostgreSQL (production), SQLite (test) |
| Migrations | Alembic |
| Server | Uvicorn |
| Tests | pytest |

## Architecture

`Router → Service → Repository → SQLAlchemy Models`

- Routers: `app/routers/*.py` — HTTP layer, FastAPI `APIRouter`, dependency injection
- Services: `app/services/*.py` — business logic, accepts `db: Session` + DTOs, returns ORM models
- Repositories: `app/repositories/*.py` — SQLAlchemy 2.0 queries, one per model
- Models: `app/models/*.py` — SQLAlchemy 2.0 `DeclarativeBase` subclasses
- Schemas: `app/schemas/*.py` — Pydantic v2 models, `ConfigDict(from_attributes=True)`
- Auth: `app/auth/` — PyJWT encode/decode, `OAuth2PasswordBearer`, bcrypt
- Config: `app/config/settings.py` — Pydantic `BaseSettings` from `.env`

## Hard Invariants

- Sync SQLAlchemy 2.0 only — no async/asyncpg
- PyJWT for JWT encode/decode — no `fastapi-jwt-auth`
- `passlib` replaced by `bcrypt` directly for password hashing
- FastAPI default response envelope — no `{"data": ...}` wrapper
- Offset-based pagination (`skip`/`limit`) on list endpoints
- Pydantic v2 schemas for all request/response validation — no raw `dict` bodies
- One repository per SQLAlchemy model in `app/repositories/`
- Role-based access control via FastAPI `Depends` — `get_current_user`, `require_admin`, `require_instructor`, `require_admin_or_instructor`, `require_active_user`
- JWT `sub` claim = user UUID (string), not email
- Role checks enforced in FastAPI dependencies, not in services
- No compression middleware (gzip/brotli) — deferred

## Pointer Table

| Task | Read first |
|------|------------|
| Adding/editing an entity | `docs/entities.md` |
| Adding/editing a Pydantic schema | `docs/schemas.md` |
| Adding/editing an API route | `docs/routers.md` |
| Adding/editing business logic | `docs/services.md` |
| Adding/editing data access | `docs/repositories.md` |
| Changing auth/JWT/RBAC | `docs/auth.md` |
| Adding/editing error handling | `docs/errors.md` |
| Adding/editing tests | `docs/tests.md` |
| Improving OpenAPI/docs | `docs/openapi.md` |
