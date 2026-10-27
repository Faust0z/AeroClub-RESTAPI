# Steps to Create the Flask → FastAPI Specs Plan

This document lists the ordered steps used to produce the detailed migration specification (`SPECS_PLAN.md`). It is a meta-plan: a checklist of what must be analyzed, decided, and written before any code is edited.

## Step 1 — Repository inventory (completed)
- List all Python files, their roles, and line counts.
- Identify which modules exist vs. which are referenced but missing (6 controller blueprints registered in `app/__init__.py` but with no implementation file).
- Parse `requirements.txt` (UTF-16 LE encoded) to capture exact library versions.
- Read `app.py`, `app/__init__.py`, `app/extensions.py`, `app/config/settings.py`, `app/errors.py`, `app/decorators.py`.
- Read representative controllers, services, schemas, models.
- Read `docs/architecture.md`, `docs/authentication.md`, `docs/database.md`, `README.md`, `docker-compose.yml`, `Dockerfile`.

## Step 2 — Capture user migration decisions (completed)
Record the user's explicit choices so the spec encodes them, not assumptions:
1. Auth: PyJWT (no `fastapi-jwt-auth`), stateless JWT, keep `sub`=email + `roles`/`status` claims, 24h TTL.
2. DB: sync SQLAlchemy 2.0, keep psycopg2-binary, no async/asyncpg.
3. Scope: implement all resources, including the 6 currently-missing controllers (`planes`, `flight_sessions`, `airport_codes`, `payment_types`, `itinerary_types`, `plane_status`).
4. Responses/errors: FastAPI defaults (no `{"data": ...}` wrapper, no custom error envelope). Postman contract break is acceptable.
5. Password hashing: FastAPI default (`passlib[bcrypt]` via `fastapi security` utilities or `bcrypt` directly), drop werkzeug hashing.

## Step 3 — Define the target architecture
- App: single `FastAPI()` instance, no app factory needed (or a thin `create_app()` for parity).
- Routing: one `APIRouter(prefix="/v1")` per resource, registered via `app.include_router()`.
- Config: `pydantic-settings` `BaseSettings` reading `.env` via `python-dotenv`.
- DB: SQLAlchemy 2.0 sync `Engine` + `sessionmaker`, dependency `get_db()` yielding a session via `Depends`.
- Migrations: alembic directly (drop Flask-Migrate), keep `db/migrations/` and `V1__init.sql`.
- Models: keep SQLAlchemy 2.0 declarative models as-is (they are framework-agnostic), drop `flask_sqlalchemy` `db.Model` base if used.
- Schemas: replace Marshmallow with Pydantic v2 models (input + output per resource/role).
- Auth: PyJWT encode/decode, `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/users/login")`, `Depends(get_current_user)` returning user + claims, role/status checks as dependencies or inline.
- Errors: raise `fastapi.HTTPException` with `status_code` + `detail`; add exception handlers only if non-default shape is desired.
- CORS: `CORSMiddleware` with `CORS_ORIGINS`.
- Entry: `uvicorn main:app` (replace `python app.py`).
- Seed: `database_filler.py` adapted to use the new session factory outside a Flask app context.

## Step 4 — Map every existing module to its FastAPI equivalent
For each file under `app/`, decide: keep, rewrite, or delete.
- `app.py` → `main.py` (uvicorn entry)
- `app/__init__.py` (`create_app`) → `app/main.py` FastAPI instance + router registration
- `app/extensions.py` (`db = SQLAlchemy()`) → `app/database.py` (engine, sessionmaker, Base, get_db)
- `app/config/settings.py` → `app/config/settings.py` (Pydantic Settings)
- `app/errors.py` → domain exception classes stay; HTTPException raised at call sites
- `app/decorators.py` → `app/auth/dependencies.py` (`get_current_user`, `require_role`, `require_active`)
- `app/controllers/*.py` → `app/routers/*.py` (`APIRouter`, `@router.get`, etc.)
- `app/services/*.py` → keep logic, inject `db: Session = Depends(get_db)` or accept session as arg
- `app/schemas/*.py` → Pydantic v2 models (rewrite all)
- `app/models/*.py` → keep SQLAlchemy models, verify imports don't rely on Flask-SQLAlchemy `db.Model`
- `database_filler.py` → adapt to new session factory
- `requirements.txt` → swap Flask stack for FastAPI stack
- `Dockerfile`, `docker-compose.yml` → port 5000 → 8000, uvicorn command

## Step 5 — Define the per-endpoint specification
For each of the 10 resources, list:
- Path, method, summary
- Request: path params, query params, Pydantic input body (or None)
- Response: status code, Pydantic output model (or None)
- Auth dependency: none / `get_current_user` / role requirement
- Service function called
- Errors raised (404, 400, 401, 403, 409)

Existing implemented endpoints (4 resources): users, transactions, roles, balances.
Missing-but-referenced endpoints (6 resources): planes, flight_sessions, airport_codes, payment_types, itinerary_types, plane_status — derive from schemas/services/models.

## Step 6 — Define data model changes
- Confirm SQLAlchemy 2.0 models need no structural change (they use `db.Model` from Flask-SQLAlchemy; switch to standalone `DeclarativeBase`).
- Check association tables (`users_have_roles`, etc.) use standalone `Table` not `db.Table`.
- Confirm `NUMERIC(10,2)` + `decimal.Decimal` cost math preserved.
- Confirm soft-delete fields (`status`, `disabled_at`) preserved.

## Step 7 — Define dependency injection & session lifecycle
- `get_db()` generator: `SessionLocal()`, `yield`, `finally: close()`.
- Routers declare `db: Session = Depends(get_db)`.
- Services receive `db: Session` as an explicit argument (no global `db.session`).
- Transaction boundaries: service commits/rolls back; router does not touch session.

## Step 8 — Define auth specification
- `SECRET_KEY` + algorithm (`HS256`) from settings.
- `create_access_token(data, expires_delta=timedelta(hours=24))` using PyJWT.
- `OAuth2PasswordBearer(tokenUrl="/v1/users/login")`.
- `get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db))` → decodes JWT, fetches user, raises `HTTPException(401)` on failure, `HTTPException(403)` if `status` is False.
- Role dependencies: `require_role("Admin")`, `require_role("Instructor")`, `require_role(["Admin","Instructor"])`.
- Login endpoint returns FastAPI default shape (token in body).
- Password: `bcrypt`/`passlib` hash at registration, verify at login.

## Step 9 — Define error specification
- Use `fastapi.HTTPException(status_code=..., detail=...)` everywhere.
- No global `{"error", "message", "status", "path", "timestamp"` envelope (FastAPI default).
- Domain exceptions (`UserNotFound`, `EmailAlreadyExists`, etc.) either kept as plain exceptions raised in services and converted to `HTTPException` in routers, or subclass `HTTPException`.
- Marshmallow `ValidationError` replaced by Pydantic automatic 422 validation (FastAPI default).

## Step 10 — Define CORS & middleware
- `CORSMiddleware(allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])`.

## Step 11 — Define requirements.txt target
Remove: Flask, flask-cors, Flask-JWT-Extended, Flask-Migrate, Flask-SQLAlchemy, marshmallow, marshmallow-sqlalchemy, werkzeug (hashing), blinker, itsdangerous (unless needed).
Add: fastapi, uvicorn[standard], pydantic, pydantic-settings, python-jose[cryptography] or pyjwt, passlib[bcrypt], python-multipart, sqlalchemy (keep), alembic (keep), psycopg2-binary (keep), python-dotenv (keep), faker (keep for seed).

## Step 12 — Define Docker / entrypoint changes
- `Dockerfile`: `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`, expose 8000.
- `docker-compose.yml`: api port `8000:8000`.

## Step 13 — Define migration sequence (incremental, reversible per resource)
1. Add FastAPI deps, new `app/database.py`, `app/config/settings.py` (Pydantic), `app/main.py`.
2. Implement auth module (`app/auth/`).
3. Migrate one resource at a time: write Pydantic schemas, write router, keep Flask running in parallel or switch wholesale.
4. Adapt `database_filler.py`.
5. Remove Flask blueprints and `app/__init__.py` factory once all routers ported.
6. Update `requirements.txt`, `Dockerfile`, `docker-compose.yml`, `README.md`.

## Step 14 — Review and sign-off criteria
- All 10 resources have routers under `/v1/`.
- All existing service business logic preserved (cost calc, atomic billing, RBAC).
- No Flask imports remain in `app/`.
- `requirements.txt` builds cleanly in the Dockerfile.
- Spec reviewed against `docs/` for consistency.
