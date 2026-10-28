from fastapi.testclient import TestClient


def test_register_user(client: TestClient, db):
    """Test user registration."""
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
    assert resp.status_code == 201, f"Register failed: {resp.text}"
    data = resp.json()
    assert data["email"] == "reg_test@example.com"
    assert data["first_name"] == "Jane"
    assert "uuid" in data


def test_register_duplicate_email(client: TestClient, auth_headers):
    """Test that registering with duplicate email fails."""
    _, user_uuid = auth_headers
    resp = client.post(
        "/v1/users/register",
        json={
            "first_name": "Dup",
            "last_name": "User",
            "phone_number": "+1234567893",
            "email": "auth_test@example.com",
            "password": "password123",
        },
    )
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"


def test_register_short_password(client: TestClient):
    """Test that short password is rejected."""
    resp = client.post(
        "/v1/users/register",
        json={
            "first_name": "Short",
            "last_name": "Pass",
            "phone_number": "+1234567894",
            "email": "short_test@example.com",
            "password": "short",
        },
    )
    assert resp.status_code == 422, f"Expected 422 for short password, got {resp.status_code}"


def test_login(client: TestClient, auth_headers):
    """Test successful login."""
    headers, _ = auth_headers
    assert headers is not None


def test_login_wrong_password(client: TestClient):
    """Test login with wrong password."""
    resp = client.post(
        "/v1/users/login",
        json={"email": "nonexistent@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_get_my_info(client: TestClient, auth_headers):
    """Test getting own profile."""
    headers, user_uuid = auth_headers
    resp = client.get("/v1/users/me", headers=headers)
    assert resp.status_code == 200, f"Get me failed: {resp.text}"
    data = resp.json()
    assert data["uuid"] == str(user_uuid)


def test_get_user_by_id(client: TestClient, auth_headers, admin_headers):
    """Test getting user by UUID (Admin)."""
    headers, user_uuid = auth_headers
    admin_headers_dict, _ = admin_headers
    resp = client.get(f"/v1/users/{user_uuid}", headers=admin_headers_dict)
    assert resp.status_code == 200, f"Get user by ID failed: {resp.text}"
    data = resp.json()
    assert data["uuid"] == str(user_uuid)


def test_update_user(client: TestClient, auth_headers):
    """Test updating own profile."""
    headers, user_uuid = auth_headers
    resp = client.patch(
        f"/v1/users/{user_uuid}",
        json={"first_name": "Updated"},
        headers=headers,
    )
    assert resp.status_code == 200, f"Update failed: {resp.text}"
    data = resp.json()
    assert data["first_name"] == "Updated"


def test_delete_user(client: TestClient, admin_headers):
    """Test deleting (soft-deleting) a user."""
    # First register a user to delete
    resp = client.post(
        "/v1/users/register",
        json={
            "first_name": "ToDelete",
            "last_name": "User",
            "phone_number": "+1234567895",
            "email": "delete_test@example.com",
            "password": "password123",
        },
    )
    assert resp.status_code == 201, f"Register to-delete user failed: {resp.text}"
    user_uuid = resp.json()["uuid"]

    # Login as the user to get a token, then use admin to delete
    login_resp = client.post(
        "/v1/users/login",
        json={"email": "delete_test@example.com", "password": "password123"},
    )
    assert login_resp.status_code == 200

    admin_headers_dict, _ = admin_headers
    resp = client.delete(f"/v1/users/{user_uuid}", headers=admin_headers_dict)
    assert resp.status_code == 200, f"Delete failed: {resp.text}"
