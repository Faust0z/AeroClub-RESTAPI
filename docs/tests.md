<!-- Load when: Adding or editing tests -->

# Tests — pytest + TestClient

All tests live under `app/tests/`. Integration tests in `tests/integration/`, unit tests in `tests/unit/`.

## Pattern

```python
from fastapi.testclient import TestClient


def test_register_user(client: TestClient, db):
    resp = client.post(
        "/v1/users/register",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "phone_number": "+1234567892",
            "email": "reg_test@example.com",
            "password": "password123",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "reg_test@example.com"
```

Key rules:
- `client` fixture: `TestClient(app)` with dependency override for `get_db`
- `db` fixture: SQLAlchemy session, drops/recreates all tables per test, seeds roles
- `auth_headers` fixture: registers a user, logs in, returns `{"Authorization": "Bearer <token>"}, user_uuid`
- `admin_headers` fixture: creates admin user directly, logs in, returns headers
- Use unique emails per test (e.g. `_unique_email()`) to avoid conflicts across test runs
- Assert status codes and response JSON fields

## Fixture — conftest.py

See `tests/conftest.py`:
- `client`: `TestClient(app)` with `override_get_db`
- `db`: session with `drop_all`/`create_all`, seeds `User`/`Instructor`/`Admin` roles
- `auth_headers`: register + login a regular user
- `admin_headers`: create admin user directly + login

## Example — Auth flow tests

See `tests/integration/test_auth_flow.py`:
- `test_register_user`, `test_register_duplicate_email`, `test_register_short_password`
- `test_login`, `test_login_wrong_password`
- `test_get_my_info`, `test_get_user_by_id`, `test_update_user`, `test_delete_user`
