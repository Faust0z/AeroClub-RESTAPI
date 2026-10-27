# AeroClub Backend

A RESTful API for managing aviation training center operations. It handles user authentication, role-based access control, financial ledger accounting, and flight session billing. The backend uses a layered Router, Service, Model architecture with Pydantic v2 validation, SQLAlchemy ORM, and stateless PyJWT authentication.

## Executive Summary

The system automates the financial and operational workflows of an aviation training center. It replaces manual paper-based tracking with a transactional ledger that records member balances, deposits, and flight-session debits. The architecture follows a layered Router to Service to Model pattern with centralized error handling and schema-based validation.

## Key Architecture Points

- Role-based access control (RBAC) with three cumulative roles: User, Instructor, Admin.
- FastAPI dependency-based authorization: `require_admin`, `require_instructor`, `require_admin_or_instructor`, `require_active_user`.
- Router-to-Service-to-Model layering; services contain business logic and ORM queries.
- Stateless PyJWT authentication with 24-hour TTL and role/status claims.
- Soft deletion for user accounts via `status=False` and `disabled_at`.
- Financial integrity via single-transaction atomic commits for flight-session billing.
- Decimal-precise cost calculation using `decimal.Decimal` to avoid floating-point drift.
- Automatic OpenAPI documentation at `/docs` and `/openapi.json`.

## Technical Stack

| Layer | Technology |
| :--- | :--- |
| Language/Runtime | Python 3.12+ |
| Web Framework | FastAPI (APIRouter-based controllers) |
| ORM | SQLAlchemy 2.0 |
| Serialization | Pydantic v2 |
| Authentication | PyJWT (stateless JWT) |
| Database | PostgreSQL (production), SQLite (local development) |
| Migrations | Alembic |
| Server | Uvicorn |
| Containerization | Docker, Docker Compose |

## Configuration and Deployment (Quick Start)

### Prerequisites

- Python 3.12+
- PostgreSQL (or SQLite for local development)
- Docker and Docker Compose (optional)

### Environment Variables

Create a `.env` file in the project root:

```properties
DB_URI=postgresql://user:password@localhost:5433/aeroclub
SECRET_KEY=your_supersecure_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
CORS_ORIGINS=http://localhost:3000,http://localhost:4200
DEBUG=True
```

`DB_URI` and `SECRET_KEY` are required. `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_HOURS`, `CORS_ORIGINS`, and `DEBUG` are optional.

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
# or: python app.py
```

The API listens on `http://localhost:8000` by default. Interactive docs at `http://localhost:8000/docs`.

### Docker

```bash
# Start PostgreSQL
docker compose up db

# Start the full stack (API behind the "prod" profile)
docker compose --profile prod up --build
```

## Domain Logic and Security

### RBAC Model

Permissions are cumulative. Higher roles inherit all permissions of lower roles.

| Role | Scope |
| :--- | :--- |
| User | Own profile, balance, transactions, and flight sessions. Read-only access to lookup data (planes, airport codes, payment types, etc.). |
| Instructor | Inherits User. Read access to other users. |
| Admin | Inherits User. Full CRUD on users, planes, roles, transactions, and flight sessions. |

Authorization is enforced through FastAPI dependency injection applied at the route level. Protected endpoints require a valid JWT and specific role claims.

### Flight Session Billing

When a flight session is created, the system:

1. Builds the `FlightSessions` record and associated `Itineraries`.
2. Calculates each itinerary cost using `0.1h` (6-minute) billing blocks rounded up.
3. Creates a debit `Transaction` bound to the student's balance.
4. Commits the session and transaction in a single database operation.

If any step fails, the entire operation rolls back. This guarantees that no flight session exists without a corresponding ledger entry.

### User Lifecycle

- Registration creates a `User` role and a zeroed `Balances` row.
- The `User` role cannot be revoked.
- Accounts are soft-deactivated by setting `status=False` and populating `disabled_at`.
- Disabled accounts are blocked by the `require_active_user` dependency reading the `status` claim from the JWT.

### Cost Calculation

Flight hours are billed in 6-minute increments matching aviation logbook conventions:

```python
blocks = ceil(elapsed_seconds / (3600 * 0.1))
billed_hours = blocks * 0.1
itinerary_cost = billed_hours * plane.fare
```

Costs are computed with `decimal.Decimal` and quantized to two decimal places using `ROUND_HALF_UP`.

## Architecture Decisions and Limitations (Trade-offs)

### Stateless JWT

The API uses stateless JWTs with embedded role and status claims. This eliminates the need for a server-side session store and simplifies horizontal scaling. The trade-off is delayed revocation: a user disabled after login retains access for up to 24 hours, until the token expires. There is no token blacklist or revocation store.

### Dependency-Level Authorization

Authorization checks are centralized in FastAPI dependencies rather than duplicated inline in each route. This reduces drift and makes the permission model easier to audit. The `require_admin_or_instructor` dependency handles endpoints accessible to both Admin and Instructor roles.

### No Balance Limits

The system does not enforce upper or lower balance limits. Overdrafts and excessive credit are managed by administrative policy rather than enforced by the software.

### Soft Delete Only

Users are deactivated, not hard-deleted. There is no endpoint to permanently remove user records.

### Schema Layer

Pydantic v2 schemas handle input validation and output serialization. Separate schemas exist for different roles (e.g., `UsersAdminOut`, `UsersInstructorOut`, `UsersOut`) to enforce field-level access control in the response layer.

### Current Limitations

- No automated test suite or CI pipeline.
- API responses follow FastAPI defaults (no `{"data": ...}` wrapper). Postman collection needs updating for the new response shape.
