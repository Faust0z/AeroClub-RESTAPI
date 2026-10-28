"""Unit tests for flight_sessions service with mocked repository."""

from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.models import FlightSessions, Users, Planes
from app.repositories import FlightSessionRepository
from app.services.flight_sessions import (
    get_flight_sessions_srv,
    get_flight_session_by_identifier_srv,
    create_flight_session_srv,
    __calculate_itinerary_cost as calc_cost,
)
from app.errors import BadTimeInput, FlightSessionNotFound


def _make_flight_session(fs_id: UUID = None, fs_identifier: int = 1) -> FlightSessions:
    return FlightSessions(
        id=fs_id or uuid4(),
        flight_session_identifier=fs_identifier,
        issued_date=date(2024, 1, 1),
        observations=None,
        transaction_id=None,
    )


def _make_plane(registration: str = "LV-ABC") -> Planes:
    return Planes(
        id=uuid4(),
        brand="Cessna",
        model="172 Skyhawk",
        registration=registration,
        category="Single Engine Piston",
        acquisition_date=date(2020, 1, 1),
        consumption_per_hour=36,
        fare=180.0,
        description="Trainer",
        plane_status_id=1,
    )


class TestCalculateItineraryCost:
    def test_normal(self):
        plane = _make_plane()
        departure = datetime(2024, 1, 1, 10, 0, 0)
        arrival = datetime(2024, 1, 1, 10, 30, 0)
        cost = calc_cost(departure, arrival, plane)
        assert cost == Decimal("90.00")

    def test_bad_time(self):
        plane = _make_plane()
        departure = datetime(2024, 1, 1, 10, 0, 0)
        arrival = datetime(2024, 1, 1, 9, 0, 0)
        with pytest.raises(BadTimeInput):
            calc_cost(departure, arrival, plane)


class TestGetFlightSessionByIdentifierSrv:
    def test_found(self):
        db = MagicMock()
        session = _make_flight_session(fs_identifier=1)
        with patch.object(FlightSessionRepository, "get_by_identifier", return_value=session):
            result = get_flight_session_by_identifier_srv(db=db, flight_session_identifier=1)
        assert result == session

    def test_not_found(self):
        db = MagicMock()
        with patch.object(FlightSessionRepository, "get_by_identifier", return_value=None):
            with pytest.raises(FlightSessionNotFound):
                get_flight_session_by_identifier_srv(db=db, flight_session_identifier=999)
