import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Import all models to register them with Base.metadata
from app.models import Users, Roles, Balances, Transactions, Users  # noqa: F401
from app.models import Planes, FlightSessions, AirportCodes  # noqa: F401
from app.models import PaymentTypes, ItineraryTypes, PlaneStatus  # noqa: F401

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db():
    db = TestingSessionLocal()
    # Drop and recreate all tables for test isolation
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # Seed roles
    from app.models import Roles
    for role_name in ["User", "Instructor", "Admin"]:
        db.add(Roles(name=role_name))
    db.commit()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_headers(client: TestClient, db):
    """Register a user, log in, and return auth headers + user UUID."""
    register_data = {
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1234567890",
        "email": "auth_test@example.com",
        "password": "password123",
    }
    resp = client.post("/v1/users/register", json=register_data)
    assert resp.status_code == 201, f"Register failed: {resp.text}"
    user_uuid = resp.json()["uuid"]

    login_resp = client.post(
        "/v1/users/login",
        json={"email": "auth_test@example.com", "password": "password123"},
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}, user_uuid


@pytest.fixture
def admin_headers(client: TestClient, db):
    """Register an admin user and return auth headers."""
    from app.models import Roles, Users
    from app.auth.dependencies import get_password_hash
    from datetime import date

    admin_role = db.query(Roles).filter(Roles.name == "Admin").first()
    user_role = db.query(Roles).filter(Roles.name == "User").first()

    existing_admin = db.query(Users).filter(Users.email == "admin@example.com").first()
    if not existing_admin:
        admin = Users(
            first_name="Admin",
            last_name="User",
            phone_number="+1234567891",
            email="admin@example.com",
            password=get_password_hash("admin123"),
            roles=[admin_role, user_role],
            status=True,
            created_at=date.today(),
        )
        db.add(admin)
        db.commit()

    login_resp = client.post(
        "/v1/users/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
