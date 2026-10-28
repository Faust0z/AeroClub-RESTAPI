"""Unit tests for roles service with mocked repository."""

from datetime import date
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.models import Roles, Users
from app.repositories import RoleRepository, UserRepository
from app.services.roles import (
    get_roles_srv,
    get_role_by_name_srv,
    get_user_roles_srv,
    add_user_role_srv,
    del_user_role_srv,
)
from app.errors import RoleNotFound, UserNotFound


def _make_role(name: str = "User") -> Roles:
    return Roles(name=name)


def _make_user(user_id: UUID = None, roles: list = None) -> Users:
    return Users(
        uuid=user_id or uuid4(),
        email="test@example.com",
        first_name="Test",
        last_name="User",
        phone_number="+1234567890",
        password="hashed",
        created_at=date.today(),
        status=True,
        roles=roles or [],
    )


class TestGetRolesSrv:
    def test_list(self):
        db = MagicMock()
        roles = [_make_role("User"), _make_role("Admin")]
        with patch.object(RoleRepository, "get_all", return_value=roles):
            db.execute.return_value.unique.return_value.scalars.return_value.all.return_value = roles
            result = get_roles_srv(db=db)
        assert len(result) == 2
        assert roles[0].name == "User"
        assert roles[1].name == "Admin"


class TestGetRoleByNameSrv:
    def test_found(self):
        db = MagicMock()
        role = _make_role("User")
        with patch.object(RoleRepository, "get_by_name", return_value=role):
            result = get_role_by_name_srv(db=db, name="User")
        assert result == role

    def test_not_found(self):
        db = MagicMock()
        with patch.object(RoleRepository, "get_by_name", return_value=None):
            with pytest.raises(RoleNotFound):
                get_role_by_name_srv(db=db, name="Nonexistent")


class TestGetUserRolesSrv:
    def test_found(self):
        db = MagicMock()
        user = _make_user(UUID("11111111-1111-1111-1111-111111111111"), [_make_role("User")])
        with patch.object(UserRepository, "get_by_id", return_value=user):
            result = get_user_roles_srv(db=db, user_id=user.uuid)
        assert len(result) == 1
        assert result[0].name == "User"


class TestAddUserRoleSrv:
    def test_add_new_role(self):
        db = MagicMock()
        user_role = _make_role("User")
        admin_role = _make_role("Admin")
        user = _make_user(UUID("11111111-1111-1111-1111-111111111111"), [user_role])
        with patch.object(UserRepository, "get_by_id", return_value=user):
            with patch.object(RoleRepository, "get_by_name", return_value=admin_role):
                with patch.object(UserRepository, "update", return_value=user):
                    result = add_user_role_srv(db=db, user_id=user.uuid, role_name="Admin")
        assert len(result) == 2


class TestDelUserRoleSrv:
    def test_remove_role(self):
        db = MagicMock()
        user_role = _make_role("User")
        admin_role = _make_role("Admin")
        user = _make_user(UUID("11111111-1111-1111-1111-111111111111"), [user_role, admin_role])
        with patch.object(UserRepository, "get_by_id", return_value=user):
            with patch.object(RoleRepository, "get_by_name", return_value=admin_role):
                with patch.object(UserRepository, "update", return_value=user):
                    result = del_user_role_srv(db=db, user_id=user.uuid, role_name="Admin")
        assert len(result) == 1
        assert result[0].name == "User"
