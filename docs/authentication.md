# Authentication and Authorization

## Token Issuance

Users authenticate via `POST /v1/users/login` with `email` and `password`. Passwords are hashed with Werkzeug (`generate_password_hash` / `check_password_hash`).

On successful login the API returns a JWT (`access_token`) containing:

- **Identity:** the user's email (`sub` claim).
- **Additional claims:**
  - `roles`: list of role names (defaults to `["User"]`).
  - `status`: account active flag at issuance time.
- **Expiry:** 24 hours from issuance.

```json
{
  "msg": "Login successful",
  "access_token": "<jwt>",
  "user": {
    "first_name": "Jane",
    "last_name": "Doe",
    "roles": ["User", "Instructor"]
  }
}
```

Send the token as:

```
Authorization: Bearer <access_token>
```

## Role Matrix

Permissions are cumulative. `Instructor` inherits everything `User` may do; `Admin` inherits everything both others may do.

| Role | Scope | Access |
| :--- | :--- | :--- |
| User | Member base | Own profile, own balance, own transactions, own roles. Read-only access to lookup data. |
| Instructor | Flight trainers | Inherits User. Read access to other users via `UsersInstructorSchema`. |
| Admin | System managers | Inherits User. Full CRUD on users, roles, balances, transactions, and lookup data. |

### Business Rules

- Every registered account receives the `User` role.
- The `User` role cannot be revoked.
- Accounts are soft-deactivated via `status=False` and `disabled_at`.
- A `Balances` row is created for every new user at registration.

## Authorization Enforcement

Authorization is enforced through shared decorators defined in `app/decorators.py`:

- `@active_account_required`: Requires a valid JWT issued to an active account.
- `@admin_required`: Requires the `Admin` role.
- `@instructor_required`: Requires the `Instructor` role.
- `@admin_or_instructor_required`: Requires either `Admin` or `Instructor`.

Controllers apply these decorators at the route level. The decorators read the decoded JWT claims via `get_jwt()` and raise `PermissionDenied` (403) or `PermissionDeniedDisabledUser` (403) when the check fails.

## Important Caveat: Delayed Revocation

The `status` and `roles` claims are captured at token issuance. Because tokens are stateless and there is no revocation or blacklist store, changes made after a token is issued are only observed once the token expires:

- A user disabled after login can continue acting for up to 24 hours.
- A role assignment change only takes effect on a freshly issued token.

This is a deliberate trade-off documented in `docs/adr/001-rbac-jwt-security.md`.

## Public vs Protected Routes

| Type | Routes |
| :--- | :--- |
| Public (no JWT) | `POST /v1/users/register`, `POST /v1/users/login` |
| Protected | All other routes require a valid JWT and, where applicable, a specific role.
