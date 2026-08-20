# API Reference

All routes are prefixed with `/v1`. Authentication is via `Authorization: Bearer <token>` (see [authentication.md](authentication.md)). Successful responses use a `{ "data": ... }` envelope; errors use a consistent `{ "error", "message", "status", "path", "timestamp" }` shape.

**Role legend:** **Any** = any authenticated user; **User** = any authenticated user seeing only their own data; **Instructor** = requires the `Instructor` role (inherits User); **Admin** = requires the `Admin` role.

## Users

| Method and Path | Role | Description |
| :--- | :--- | :--- |
| `POST /v1/users/register` | Public | Self-service signup (creates `User` role + zeroed balance). |
| `POST /v1/users/login` | Public | Authenticates, returns 24h JWT. |
| `GET /v1/users/` | Admin / Instructor | List users; filters: `email`, `first_name`, `last_name`, `role_name`. |
| `GET /v1/users/me` | User | Own profile. |
| `GET /v1/users/<email>` | Admin / Instructor | A user's data (role-scoped schema). |
| `PATCH /v1/users/<email>` | Admin, or self | Update user (admin may update email and roles). |
| `DELETE /v1/users/<email>` | Admin | Soft-delete (sets `status=False`, `disabled_at`). |

## Roles

| Method and Path | Role | Description |
| :--- | :--- | :--- |
| `GET /v1/roles/` | Admin | List all roles. |
| `GET /v1/roles/me` | User | Own roles. |
| `GET /v1/roles/<email>` | Admin | A user's roles. |
| `POST /v1/roles/<email>/<role>` | Admin | Grant a role to a user. |
| `DELETE /v1/roles/<email>/<role>` | Admin | Revoke a role (the `User` role is protected from revocation). |

## Balances

| Method and Path | Role | Description |
| :--- | :--- | :--- |
| `GET /v1/balances/` | Admin | All balances; filters: `min_balance`, `max_balance`. |
| `GET /v1/balances/me` | User | Own balance. |
| `GET /v1/balances/<email>` | Admin | A user's balance. |

## Transactions

| Method and Path | Role | Description |
| :--- | :--- | :--- |
| `GET /v1/transactions/` | Admin | All transactions; filters: `email`, `first_name`, `last_name`, `payment_type`, `starting_date`, `limit_date`. |
| `GET /v1/transactions/me` | User | Own transaction history. |
| `GET /v1/transactions/<email>` | Admin | A user's transactions. |
| `POST /v1/transactions/<email>` | Admin | Add funds (credit) to a user's balance. |
