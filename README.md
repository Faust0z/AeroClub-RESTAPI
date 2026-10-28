# AeroClub Backend

A RESTful API for managing aviation training center operations. It handles user authentication, role-based access control, financial ledger accounting, and flight session billing.

## Technical Stack

| Layer | Technology |
|-------|------------|
| Language/Runtime | Python 3.12+ |
| Web Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Serialization | Pydantic v2 |
| Authentication | PyJWT (stateless JWT, bcrypt password hashing) |
| Database | PostgreSQL (production), SQLite (development) |
| Migrations | Alembic |
| Server | Uvicorn |
| Tests | pytest |

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL (or SQLite for local development)
- Docker and Docker Compose (optional)

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed required data (roles, payment types, airport codes, plane status, demo users)
python database_filler.py

# Run the application
uvicorn app.main:app --reload
```

The API listens on `http://localhost:8000`. Interactive API docs are at `http://localhost:8000/docs`.

### Docker

```bash
# Start PostgreSQL
docker compose up db

# Start the full stack (API behind the "prod" profile)
docker compose --profile prod up --build
```

## Domain Logic

- **Authentication**: Stateless JWT with email/password login. Tokens contain roles and account status claims.
- **RBAC**: Three cumulative roles: User → Instructor → Admin. Each higher role inherits permissions from lower ones.
- **Billing**: Flight sessions are billed in 6-minute increments. Costs are computed with `decimal.Decimal` to avoid floating-point drift.
- **Soft delete**: Users are deactivated (`status=False`) rather than hard-deleted.
- **Atomic billing**: Flight session creation and ledger transaction commit atomically.

## Documentation

Detailed documentation is organized in `/docs`:

| Document | What it covers |
|----------|----------------|
| `architecture.md` | High-level system architecture |
| `entities.md` | SQLAlchemy model patterns and conventions |
| `schemas.md` | Pydantic v2 schema patterns |
| `routers.md` | FastAPI route patterns and auth dependencies |
| `services.md` | Service layer business logic |
| `repositories.md` | Repository pattern and data access patterns |
| `auth.md` | JWT authentication and RBAC patterns |
| `errors.md` | Error handling patterns |
| `tests.md` | Testing patterns |
| `openapi.md` | OpenAPI documentation configuration |

Each doc file starts with a header explaining when to read it, making it easy to find relevant information quickly.

## Contributing

See `AGENTS.md` for AI agent guidelines and project conventions.
