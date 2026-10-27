# Flask → FastAPI Migration Specifications

Project: AeroClub REST API  
Source: `AeroClub-RESTAPI/` (Flask 3.1.2, SQLAlchemy 2.0, Marshmallow 4, Flask-JWT-Extended)  
Target: FastAPI, sync SQLAlchemy 2.0, Pydantic v2, PyJWT, FastAPI default responses/errors  
Constraint: **No code edits in this phase — planning only.**

---

## 1. Migration decisions (locked)

| Decision | Value |
|---|---|
| Auth library | PyJWT (encode/decode manually), no `fastapi-jwt-auth` |
| DB mode | Sync SQLAlchemy 2.0 + psycopg2-binary, no async |
| Scope | All 10 resources, including 6 currently-missing controllers |
| Response envelope | FastAPI defaults (drop `{"data": ...}` wrapper) |
| Error envelope | FastAPI defaults (`HTTPException`), drop custom timestamp/path envelope |
| Password hashing | FastAPI default (`passlib[bcrypt]` / `bcrypt`), drop werkzeug |
| App factory | Optional thin `create_app()`; single `FastAPI()` instance acceptable |
| Port | 5000 → 8000 (uvicorn standard) |

---

## 2. Target architecture

```
app/
├── main.py                 # FastAPI instance, router registration, middleware
├── config/
│   └── settings.py         # Pydantic BaseSettings (.env via python-dotenv)
├── database.py             # SQLAlchemy engine, sessionmaker, DeclarativeBase, get_db()
├── auth/
│   ├── __init__.py
│   ├── dependencies.py     # get_current_user, require_role, oauth2_scheme
│   └── tokens.py           # create_access_token, decode_token (PyJWT)
├── routers/
│   ├── __init__.py
│   ├── users.py
│   ├── transactions.py
│   ├── roles.py
│   ├── balances.py
│   ├── planes.py           # new (currently missing)
│   ├── flight_sessions.py  # new (currently missing)
│   ├── airport_codes.py    # new (currently missing)
│   ├── payment_types.py    # new (currently missing)
│   ├── itinerary_types.py  # new (currently missing)
│   └── plane_status.py     # new (currently missing)
├── services/               # keep files, change signature to accept db: Session
├── schemas/                # rewrite: Pydantic v2 models (replace Marshmallow)
├── models/                 # keep SQLAlchemy models, switch base to DeclarativeBase
├── exceptions.py           # domain exceptions -> HTTPException mapping
└── dependencies.py         # get_db() session dependency
```

## 3. Requirements.txt target

Remove:
- Flask, flask-cors, Flask-JWT-Extended, Flask-Migrate, Flask-SQLAlchemy
- marshmallow, marshmallow-sqlalchemy
- werkzeug (hashing only; keep if needed elsewhere), blinker, itsdangerous

Add:
- fastapi, uvicorn[standard]
- pydantic, pydantic-settings
- pyjwt, passlib[bcrypt], python-multipart

Keep:
- SQLAlchemy, alembic, psycopg2-binary, python-dotenv, faker, tzdata, typing_extensions

## 4. Configuration (`app/config/settings.py`)

Pydantic v2 `BaseSettings`:

```text
DB_URI: str
SECRET_KEY: str
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS: int = 24
DEBUG: bool = False
CORS_ORIGINS: list[str] = []
```

Loads `.env` via `python-dotenv` / pydantic-settings env_file. Missing `DB_URI` / `SECRET_KEY` raises configuration error at import.

## 5. Database (`app/database.py` + `app/models/`)

- SQLAlchemy 2.0 `DeclarativeBase` (standalone, not `flask_sqlalchemy`).
- `engine = create_engine(DB_URI)`, `SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)`.
- `get_db()`: generator yielding `SessionLocal()`, closing in `finally`.
- Models: keep column definitions and relationships; change base import from `flask_sqlalchemy.SQLAlchemy.Model` to local `DeclarativeBase`; association tables use standalone `Table(metadata=Base.metadata)`.
- No `db.create_all()` at startup; rely on alembic migrations (`db/migrations/`).
- Remove `Flask-Migrate`; run alembic CLI directly.

## 6. Authentication (`app/auth/`)

- `create_access_token(subject: str, roles: list[str], status: bool, expires_delta: timedelta)` → PyJWT `HS256`, claims: `sub`=email, `roles`, `status`, `exp`.
- `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/users/login")`.
- `get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db))`:
  - decode JWT (PyJWT), raise `HTTPException(401)` on invalid/expired.
  - fetch user by email; raise `HTTPException(404)` if missing, `HTTPException(403)` if `status is False`.
  - return user object.
- Role dependencies:
  - `require_active_user = Depends(get_current_user)`
  - `require_admin(user: Users = Depends(get_current_user))` → 403 if "Admin" not in user.roles
  - `require_instructor(...)`, `require_admin_or_instructor(...)`
- Password: `passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")` for hash/verify.

## 7. Schemas (`app/schemas/`) — Pydantic v2 rewrite

For each resource, define:
- `*Create` / `*Register` (input)
- `*Update` (input, partial)
- `*Out` / `*Response` (output)
- Role-specific outputs where needed (`UsersAdminOut`, `UsersInstructorOut`, `UsersOut`).

Drop `load_only`/`dump_only` distinctions; use separate input/output models instead. Pydantic handles validation and returns 422 automatically on invalid input (FastAPI default).

## 8. Services (`app/services/`)

Keep existing business logic; adapt signatures:

```text
# Before (Flask-SQLAlchemy global session)
def get_users_srv(email=None, ...) -> list[Users]:
    stmt = db.select(Users) ...
    return db.session.execute(stmt).unique().scalars().all()

# After (sync SQLAlchemy, session injected)
def get_users_srv(db: Session, email=None, ...) -> list[Users]:
    stmt = select(Users) ...
    return db.execute(stmt).unique().scalars().all()
```

Services do NOT call `Depends`; they receive `db: Session` as a normal argument. Routers call `Depends(get_db)` and pass the session.

Preserve:
- `decimal.Decimal` cost math, 6-minute ceiling blocks, ROUND_HALF_UP quantization.
- Atomic single-commit flight session + transaction billing.
- `generate_password_hash`/`check_password_hash` → `CryptContext.hash` / `CryptContext.verify`.
- Soft-delete (`status=False`, `disabled_at`).
- `User` role cannot be revoked business rule.

## 9. Routers (`app/routers/`) — one APIRouter per resource

Pattern per router:

```text
router = APIRouter(prefix="/v1/<resource>", tags=["<resource>"])

@router.get("/")
def list_items(db: Session = Depends(get_db), current_user: Users = Depends(require_admin)):
    items = service.get_items_srv(db=db, ...)
    return items  # FastAPI serializes via response_model or returns list directly
```

Use `response_model=List[ItemOut]` or return ORM models with `from_attributes=True` Pydantic config.

Endpoints to implement (derived from existing Flask controllers + missing resources):

### users (`/v1/users`)
- `GET /` — list users, query filters (email, first_name, last_name, role_name), Admin/Instructor only, role-dependent output schema.
- `GET /me` — own profile, active account required.
- `GET /{email}` — user by email, Admin/Instructor only.
- `PATCH /{email}` — update, active account required; Admin or self.
- `DELETE /{email}` — disable (soft-delete), Admin only.
- `POST /register` — public, hash password, create User role + zero Balance.
- `POST /login` — public, verify password, return JWT.

### transactions (`/v1/transactions`)
- `GET /` — list with filters, Admin only.
- `GET /me` — own transactions, active account.
- `GET /{email}` — user transactions, Admin only.
- `POST /{email}` — create transaction, Admin only.

### roles (`/v1/roles`)
- `GET /` — list roles, Admin only.
- `GET /me` — own roles, active account.
- `GET /{email}` — user roles, Admin only.
- `POST /{email}/{role}` — add role, Admin only (User role cannot be revoked rule applies to delete).
- `DELETE /{email}/{role}` — remove role, Admin only.

### balances (`/v1/balances`)
- `GET /` — list with min/max balance filters, Admin only.
- `GET /{email}` — user balance, Admin only.
- `GET /me` — own balance, active account.

### planes (`/v1/planes`) — new
- `GET /`, `GET /{id}`, `POST /`, `PATCH /{id}`, `DELETE /{id}` (Admin for writes).

### flight_sessions (`/v1/flight_sessions`) — new
- `GET /` with filters, `GET /me`, `GET /{id}`, `POST /` (atomic billing), Admin for list/detail-by-id.

### airport_codes (`/v1/airport_codes`) — new
- Standard CRUD.

### payment_types (`/v1/payment_types`) — new
- Standard CRUD.

### itinerary_types (`/v1/itinerary_types`) — new
- Standard CRUD.

### plane_status (`/v1/plane_status`) — new
- Standard CRUD.

## 10. Error handling

- Raise `fastapi.HTTPException(status_code=..., detail=...)` from routers/services.
- Domain exceptions (`UserNotFound`, `EmailAlreadyExists`, `PermissionDenied`, `FlightSessionNotFound`, `BadTimeInput`, etc.) either:
  - subclass `HTTPException` directly, or
  - are plain exceptions caught by a single exception handler mapping to `HTTPException`.
- Pydantic validation errors → FastAPI default 422 (no custom Marshmallow handler).
- No `{"error", "message", "status", "path", "timestamp"}` envelope (FastAPI default `{"detail": ...}`).

## 11. CORS (`app/main.py`)

```text
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 12. Entry point (`app/main.py` or `main.py`)

```text
app = FastAPI()
app.add_middleware(CORSMiddleware, ...)
app.include_router(users.router)
...
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run via `uvicorn main:app --reload` (or `python main.py`).

## 13. Seed script (`database_filler.py`)

- Import `SessionLocal` from `app.database`.
- Wrap seed logic in `with SessionLocal() as db:` and pass `db` to model operations.
- Remove `create_app()` / Flask app context usage.
- Keep all seed data (roles, users, planes, airport codes, payment types, itinerary types, plane status, random users).

## 14. Docker / ops

- `Dockerfile`: `EXPOSE 8000`, `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`, Python 3.12 (drop 3.9-alpine inconsistency).
- `docker-compose.yml`: api port `8000:8000`, env vars unchanged (`DB_URI`, `SECRET_KEY`, `CORS_ORIGINS`, `DEBUG`).
- `README.md`: update stack table (FastAPI, Pydantic, PyJWT, uvicorn), local setup (`pip install -r requirements.txt`, `uvicorn main:app`), port 8000.

## 15. Migration sequence (incremental)

1. Add new deps to `requirements.txt`; create `app/database.py`, `app/config/settings.py`, `app/dependencies.py`.
2. Create `app/auth/` (tokens + dependencies).
3. Rewrite `app/schemas/` to Pydantic (all 10 resources).
4. Adapt `app/models/` base to `DeclarativeBase`; verify no Flask-SQLAlchemy imports.
5. Migrate `app/services/` signatures to accept `db: Session`.
6. Write `app/routers/` one resource at a time (start with `users`, `roles`, `balances`, `transactions`, then the 6 new ones).
7. Write `app/main.py` registering all routers + CORS.
8. Adapt `database_filler.py`.
9. Delete `app/__init__.py` factory, `app/extensions.py`, `app/decorators.py`, `app/errors.py` (Flask-specific); keep `app.py` replaced by `main.py`.
10. Update `Dockerfile`, `docker-compose.yml`, `README.md`, `requirements.txt`.
11. Verify importability: `python -c "import app.main"`; alembic check.

## 16. Sign-off criteria

- [ ] All 10 resources have routers mounted under `/v1/`.
- [ ] No `flask`, `flask_sqlalchemy`, `marshmallow`, `flask_jwt_extended` imports remain in `app/`.
- [ ] `uvicorn main:app` starts and responds on `/docs` and `/openapi.json`.
- [ ] All existing service business logic (cost calc, atomic billing, RBAC, soft-delete) preserved.
- [ ] `database_filler.py` runs and seeds successfully.
- [ ] `requirements.txt` installs cleanly in the Dockerfile build.
