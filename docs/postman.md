# Postman Collection Guide

A ready-to-use Postman collection ships with the repo:

- **Repo root:** `Postman Collection Guide.json`
- **Copy here (docs):** [`postman_collection.json`](postman_collection.json)

It contains requests across the implemented resources (users, balances, transactions, roles) with pre-request scripts that automatically log in and attach the correct JWT per role.

## Setup

1. **Seed the database** (mandatory lookup rows + demo users):

    ```bash
    python database_filler.py
    ```

    This creates the three roles, payment types, airport codes, plane statuses, itinerary types, sample aircraft, and three **Postman-ready users**:

    | Role | Email | Password |
    | :--- | :--- | :--- |
    | User | `postman_user@email.com` | `postman_password` |
    | Instructor | `postman_instructor@email.com` | `postman_password` |
    | Admin | `postman_admin@email.com` | `postman_password` |

2. **Import the collection** into Postman (`File -> Import`).

3. **Set collection variables:**

    - `base_url` -> e.g. `http://localhost:5000/v1`
    - `current_role` -> `User`, `Instructor`, or `Admin` (the role you want to act as).
    - `jwt` -> leave blank; the pre-request scripts populate it automatically.

4. **Run a request.** The collection logs in as the selected role and attaches the JWT for you. Clear or delete the `jwt` variable to switch users or roles.

## Notes

- Some demo users are generated with the **Faker** library, so emails may vary if you regenerate with different seeds; the three fixed `postman_*` accounts above are always created.
- To try an **Admin-only** action (e.g., create a transaction), set `current_role = Admin`.
- The collection assumes the API runs on the default port `5000`; adjust `base_url` for your actual host and port (including the `/v1` prefix).
