# Architecture

## Layering (Controller to Service to Model)

The code follows a Controller to Service to Model architecture with a Marshmallow Schema layer for validation and serialization. There is no separate Repository abstraction; service functions issue SQLAlchemy queries directly.

| Layer | Directory | Responsibility |
| :--- | :--- | :--- |
| Controller | `app/controllers/` | HTTP routing (Flask Blueprints), decorator-based auth/RBAC, request parsing, response shaping. |
| Service | `app/services/` | Business logic, ORM queries, domain rules (e.g., cost calculation, atomic billing). |
| Schema | `app/schemas/` | Marshmallow validation on input and serialization of output. |
| Model | `app/models/` | SQLAlchemy ORM models and association tables. |
| Config | `app/config/settings.py` | Environment-driven configuration. |
| Errors | `app/errors.py` | Domain exceptions and global error handlers. |
| Decorators | `app/decorators.py` | Shared authorization decorators. |

### Application Factory

`app/__init__.py` exposes `create_app()`, which:

1. Builds the Flask app and applies configuration.
2. Initializes `JWTManager`, SQLAlchemy (`db`), and CORS.
3. Runs `db.create_all()` inside an app context at startup.
4. Wires Flask-Migrate (`Migrate`).
5. Registers Blueprints, all namespaced under `/v1/`.

## Request Lifecycle

1. An HTTP request reaches a controller route under `/v1/<resource>/...`.
2. If the route is protected, `@jwt_required()` validates the bearer token; the controller or decorator reads claims via `get_jwt()`.
3. Authorization decorators enforce role and account status before the handler runs.
4. For write operations, the request body is validated against a Marshmallow schema; a `ValidationError` yields `400`.
5. The controller delegates to a service for business logic.
6. The service returns ORM objects; the controller serializes them through a schema into the `{ "data": ... }` envelope.
7. Any thrown domain/HTTP exception is caught by the global error handlers.

## Response and Error Envelopes

Success responses use a uniform wrapper:

```json
{ "data": ... }
```

Errors use a consistent shape defined in `app/errors.py` (`register_error_handlers`):

```json
{
  "error": "NotFound",
  "message": "Plane not found",
  "status": 404,
  "path": "/v1/planes/FOO",
  "timestamp": "2026-01-01T00:00:00+00:00"
}
```

Three handler families are registered:

| Handler | Applies to | HTTP Status |
| :--- | :--- | :--- |
| `HTTPException` | Werkzeug/HTTP errors (404, 401, 403, 409, ...) | Matches the exception code |
| `MarshmallowValidationError` | Schema validation failures | 400 |
| Generic `Exception` | Any unhandled error | 500 |

## Module Map

```
app/
├── __init__.py            create_app() factory, Blueprint registration
├── config/settings.py     .env config (DB_URI, SECRET_KEY, CORS_ORIGINS, DEBUG)
├── errors.py              domain exceptions and global handlers
├── extensions.py          shared db = SQLAlchemy()
├── decorators.py          shared auth/RBAC decorators
├── controllers/           Blueprints (users, transactions, roles, balances)
├── services/              business logic per resource
├── schemas/               Marshmallow schemas per resource
└── models/                ORM models and association tables
```

## Design Notes

- Monetary values are stored as `NUMERIC(10, 2)` and computed with `decimal.Decimal` during cost arithmetic to avoid floating-point drift.
- Users are soft-deleted (`status=False` + `disabled_at`); there is no hard delete path.
- Every account is seeded with at least the `User` role and a zeroed `Balances` row at registration time.
- The `User` role cannot be revoked; this is enforced at the service and documented in the route handler.
