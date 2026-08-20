# ADR 001: Stateless JWT Authentication and Role-Based Access Control (RBAC)

**Status:** Accepted
**Date:** See git history
**Area:** Authentication and Authorization

## Context and Problem Statement

The Aero Club system requires strict separation between regular club members, flight instructors, and system administrators. We needed an authentication mechanism that minimizes database lookup overhead while enforcing domain permissions across API endpoints, and that scales cleanly across containers.

## Decision

We implemented a stateless JWT authentication layer using `Flask-JWT-Extended`. Tokens are issued with a 24-hour expiry and embed the caller's context directly in the payload as additional claims:

- `roles`: the list of role names the user currently holds
- `status`: whether the account is active at the moment of token issuance

Authorization is enforced at the controller (route) layer through shared decorators defined in `app/decorators.py`:

- `@active_account_required`: validates the JWT and checks the `status` claim.
- `@admin_required`: validates the JWT and requires the `Admin` role.
- `@instructor_required`: validates the JWT and requires the `Instructor` role.
- `@admin_or_instructor_required`: validates the JWT and requires either `Admin` or `Instructor`.

These decorators wrap the route handler and raise `PermissionDenied` (403) or `PermissionDeniedDisabledUser` (403) when the check fails.

## Consequences

**Pros**

- No server-side session store; simplifies horizontal scaling and containerization.
- Roles are encoded inside the JWT payload, enabling instant route-level authorization without a per-request role lookup.
- Centralized decorators reduce duplication and drift across controllers.

**Cons / Trade-offs**

- **Delayed revocation.** The `status` claim is captured at issuance time, so a user disabled after receiving a token can continue making requests for up to 24 hours (until the token expires). There is no token-blacklist or revocation store today.
- Because permissions are read from the token rather than the database, a role change (e.g., promoting a user to `Instructor`) only takes effect once a fresh token is issued.
- Decorator ordering matters: `@jwt_required()` must be outermost for Flask-JWT-Extended to process the token before custom role checks run.
