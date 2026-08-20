# Documentation Hub

## Getting Started

| Document | What it covers |
| :--- | :--- |
| [README](../README.md) | Project overview, quick start, setup, running locally and with Docker. |
| [Postman Guide](postman.md) | How to import and drive the Postman collection. |
| [Postman Collection](postman_collection.json) | Machine-readable API collection with auto-login scripts. |

## Architecture and Design

| Document | What it covers |
| :--- | :--- |
| [architecture.md](architecture.md) | Layering, request lifecycle, response and error envelopes, module map. |
| [authentication.md](authentication.md) | JWT flow, RBAC matrix, disabled-user revocation caveat, shared decorators. |
| [financial-model.md](financial-model.md) | Ledger design, flight-session billing algorithm, precision notes. |
| [database.md](database.md) | Entities, relationships, soft-delete, money handling. |

## Quick Facts

- **Base URL prefix:** all API routes live under `/v1/`.
- **Auth:** stateless JWT (`Authorization: Bearer <token>`), issued at login with a 24h TTL.
- **Response envelope:** `{ "data": ... }` for successes, a consistent `{ "error", "message", "status", "path", "timestamp" }` object for failures.
- **Database:** PostgreSQL for production (SQLite supported for local dev); schema bootstrapped via `db.create_all()` on startup.
- **RBAC:** shared decorators (`@admin_required`, `@instructor_required`, `@admin_or_instructor_required`, `@active_account_required`) enforce permissions at the controller layer.
