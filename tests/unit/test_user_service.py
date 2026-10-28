"""Unit tests for users service with mocked repository."""

from datetime import date
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.models import Users, Roles
from app.repositories import UserRepository
from app.services.users import (
    get_user_by_id_srv,
    get_user_by_email_srv,
    register_user_srv,
    authenticate_user_srv,
    update_user_srv,
    disable_user_srv,
)
from app.errors import UserNotFound, EmailAlreadyExists, AuthError


def _make_user(user_id: UUID = None, email: str = "test@example.com") -> Users:
    return Users(
        id=user_id or uuid4(),
        uuid=user_id or uuid4(),
        email=email,
        first_name="Test",
        last_name="User",
        phone_number="+1234567890",
        password="hashed_password",
        created_at=date.today(),
        status=True,
    )


class TestGetUserByIdSrv:
    def test_found(self):
        db = MagicMock()
        user = _make_user(UUID("11111111-1111-1111-1111-111111111111"))
        with patch.object(UserRepository, "get_by_id", return_value=user):
            result = get_user_by_id_srv(db=db, user_id=user.uuid)
        assert result == user

    def test_not_found(self):
        db = MagicMock()
        with patch.object(UserRepository, "get_by_id", return_value=None):
            with pytest.raises(UserNotFound):
                get_user_by_id_srv(db=db, user_id=uuid4())


def test_get_user_by_email_srv():
    db = MagicMock()
    user = _make_user(email="test@example.com")
    with patch.object(UserRepository, "get_by_email", return_value=user):
        result = get_user_by_email_srv(db=db, email="test@example.com")
    assert result == user


def test_register_user_srv():
    db = MagicMock()
    data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "+1234567890",
        "email": "jane@example.com",
        "password": "password123",
    }
    created_user = Users(
        id=1,
        uuid=uuid4(),
        email="jane@example.com",
        first_name="Jane",
        last_name="Doe",
        phone_number="+1234567890",
        password="hashed",
        created_at=date.today(),
        status=True,
    )
    with patch.object(UserRepository, "add", return_value=created_user):
        with patch("app.services.users.get_role_by_name_srv", return_value=Roles(id=1, name="User")):
            result = register_user_srv(db=db, data=data)
    assert result.email == "jane@example.com"
    assert result.first_name == "Jane"


def test_authenticate_user_srv_success():
    db = MagicMock()
    user = _make_user(email="test@example.com")
    with patch.object(UserRepository, "get_by_email", return_value=user):
        with patch("app.services.users.verify_password", return_value=True):
            result = authenticate_user_srv(db=db, email="test@example.com", password="password123")
    assert result == user


def test_authenticate_user_srv_wrong_password():
    db = MagicMock()
    user = _make_user(email="test@example.com")
    with patch.object(UserRepository, "get_by_email", return_value=user):
        with patch("app.services.users.verify_password", return_value=False):
            with pytest.raises(AuthError):
                authenticate_user_srv(db=db, email="test@example.com", password="wrong")


def test_update_user_srv():
    db = MagicMock()
    user = _make_user(UUID("11111111-1111-1111-1111-111111111111"))
    data = {"first_name": "Updated"}
    with patch.object(UserRepository, "get_by_id", return_value=user):
        with patch.object(UserRepository, "update", return_value=user):
            result = update_user_srv(db=db, user_id=user.uuid, data=data)
    assert result == user


def test_disable_user_srv():
    db = MagicMock()
    user = _make_user(UUID("11111111-1111-1111-1111-111111111111"))
    with patch.object(UserRepository, "get_by_id", return_value=user):
        with patch.object(UserRepository, "update", return_value=user):
            result = disable_user_srv(db=db, user_id=user.uuid)
    assert result.status is False
    assert result.disabled_at is not None
