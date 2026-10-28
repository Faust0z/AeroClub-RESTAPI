"""Unit tests for planes service with mocked repository."""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.models import Planes, PlaneStatus
from app.repositories import PlaneRepository, PlaneStatusRepository
from app.schemas import PlanesCreate, PlanesOut, PlanesUpdate
from app.services.planes import (
    get_planes_srv,
    get_plane_by_registration_srv,
    create_plane_srv,
    update_plane_srv,
    update_plane_status_srv,
)
from app.errors import PlaneNotFound, PlaneRegistrationAlreadyExists, PlaneStatusNotFound


def _make_plane(plane_id: UUID = None, registration: str = "LV-ABC") -> Planes:
    return Planes(id=plane_id or uuid4(), brand="Cessna", model="172 Skyhawk", registration=registration, category="Single Engine Piston", acquisition_date=date(2020, 1, 1), consumption_per_hour=36, fare=180.0, description="Trainer", plane_status_id=uuid4())


def _make_plane_status(status_id: UUID = None, state: str = "Active") -> PlaneStatus:
    return PlaneStatus(id=status_id or uuid4(), state=state)


class TestGetPlanesSrv:
    def test_list(self):
        db = MagicMock()
        planes = [_make_plane(UUID("11111111-1111-1111-1111-111111111111"), "LV-ABC"), _make_plane(UUID("22222222-2222-2222-2222-222222222222"), "LV-XYZ")]
        db.execute.return_value.unique.return_value.scalars.return_value.all.return_value = planes
        result = get_planes_srv(db=db)
        assert len(result) == 2
        assert result[0].registration == "LV-ABC"


class TestGetPlaneByRegistrationSrv:
    def test_found(self):
        db = MagicMock()
        plane = _make_plane(registration="LV-ABC")
        with patch.object(PlaneRepository, "get_by_registration", return_value=plane):
            result = get_plane_by_registration_srv(db=db, registration="LV-ABC")
        assert result == plane

    def test_not_found(self):
        db = MagicMock()
        with patch.object(PlaneRepository, "get_by_registration", return_value=None):
            with pytest.raises(PlaneNotFound):
                get_plane_by_registration_srv(db=db, registration="LV-NONE")


class TestCreatePlaneSrv:
    def test_create(self):
        db = MagicMock()
        plane_data = PlanesCreate(
            brand="Cessna",
            model="172 Skyhawk",
            registration="LV-NEW",
            category="Single Engine Piston",
            acquisition_date=date(2020, 1, 1),
            consumption_per_hour=36,
            fare=Decimal("180.0"),
            description="Trainer",
            plane_status_id=uuid4(),
        )
        created_plane = _make_plane(registration="LV-NEW")
        with patch.object(PlaneStatusRepository, "get_by_state", return_value=_make_plane_status(state="Active")):
            with patch.object(PlaneRepository, "add", return_value=created_plane):
                result = create_plane_srv(db=db, data=plane_data)
        assert result.registration == "LV-NEW"
        assert result.brand == "Cessna"


class TestUpdatePlaneSrv:
    def test_update(self):
        db = MagicMock()
        plane = _make_plane(registration="LV-ABC")
        with patch.object(PlaneRepository, "get_by_registration", return_value=plane):
            with patch.object(PlaneRepository, "update", return_value=plane):
                result = update_plane_srv(db=db, registration="LV-ABC", data=PlanesUpdate(fare=Decimal("200.0")))
        assert result.registration == "LV-ABC"


class TestUpdatePlaneStatusSrv:
    def test_update(self):
        db = MagicMock()
        plane = _make_plane(registration="LV-ABC")
        new_status = _make_plane_status(uuid4(), "Under maintenance")
        plane.plane_status_id = new_status.id
        with patch.object(PlaneRepository, "get_by_registration", return_value=plane):
            with patch.object(PlaneStatusRepository, "get_by_state", return_value=new_status):
                with patch.object(PlaneRepository, "update", return_value=plane):
                    result = update_plane_status_srv(db=db, registration="LV-ABC", plane_status_name="Under maintenance")
        assert result.plane_status_id == new_status.id
