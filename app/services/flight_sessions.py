import uuid
from datetime import date, datetime, timezone
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal
from typing import Optional

from sqlalchemy import and_, select, func
from sqlalchemy.orm import Session, joinedload

from app.models import FlightSessions, Itineraries, Planes, Transactions, Users
from app.repositories import FlightSessionRepository
from app.schemas import FlightSessionsOut
from .airport_codes import get_airport_code_by_code_srv
from .itinerary_types import get_itinerary_type_by_type_srv
from .payment_types import get_payment_type_by_name_srv
from .planes import get_plane_by_registration_srv
from .transactions import sub_user_transaction_srv
from .users import get_user_by_id_srv, get_user_by_email_srv
from ..errors import BadTimeInput, FlightSessionNotFound, UserNotFound


def get_flight_sessions_srv(
    db: Session,
    flight_session_identifier: Optional[int] = None,
    plane_registration: Optional[str] = None,
    admin_email: Optional[str] = None,
    user_first_name: Optional[str] = None,
    user_last_name: Optional[str] = None,
    observations: Optional[str] = None,
    starting_date: Optional[date] = None,
    limit_date: Optional[date] = None,
):
    repo = FlightSessionRepository(db)
    return repo.get_all(
        flight_session_identifier=flight_session_identifier,
        plane_registration=plane_registration,
        admin_email=admin_email,
        user_first_name=user_first_name,
        user_last_name=user_last_name,
        observations=observations,
        starting_date=starting_date,
        limit_date=limit_date,
    )


def get_flight_session_by_identifier_srv(db: Session, flight_session_identifier: int) -> FlightSessions:
    repo = FlightSessionRepository(db)
    session = repo.get_by_identifier(flight_session_identifier=flight_session_identifier)
    if not session:
        raise FlightSessionNotFound
    return session


def get_user_flight_sessions_srv(db: Session, user_id: uuid.UUID) -> list[FlightSessions]:
    repo = FlightSessionRepository(db)
    return repo.get_by_user_id(user_id=user_id)


def create_flight_session_srv(
    db: Session,
    flight_session_data: dict,
    admin_user_id: uuid.UUID,
) -> FlightSessions:
    last_identifier = db.execute(
        select(func.max(FlightSessions.flight_session_identifier))
    ).scalar()
    next_identifier = (last_identifier or 0) + 1
    new_flight_session = FlightSessions(
        flight_session_identifier=next_identifier,
        issued_date=flight_session_data["issued_date"],
        observations=flight_session_data.get("observations"),
    )

    admin = get_user_by_id_srv(db=db, user_id=admin_user_id)
    user = get_user_by_id_srv(db=db, user_id=flight_session_data["user_id"])
    if flight_session_data.get("instructor_email"):
        instructor = get_user_by_email_srv(db=db, email=flight_session_data["instructor_email"])
        new_flight_session.users.append(instructor)
    new_flight_session.users.append(user)
    new_flight_session.users.append(admin)

    total_session_cost = Decimal("0")
    for itinerary_data in flight_session_data["itineraries"]:
        new_itinerary, itinerary_cost = __build_itinerary(db=db, itinerary_data=itinerary_data)
        new_flight_session.itineraries.append(new_itinerary)
        total_session_cost += itinerary_cost

    try:
        new_transaction = sub_user_transaction_srv(
            db=db,
            user_id=user.uuid,
            transaction=Transactions(
                amount=total_session_cost,
                issued_date=datetime.now(timezone.utc),
                description="Transaction automatically created by flight session",
                payment_type=get_payment_type_by_name_srv(db=db, name="Flight Session"),
                balance_id=user.balance.id,
            ),
        )

        new_flight_session.transaction_id = new_transaction.id
        db.add(new_flight_session)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return new_flight_session


def __build_itinerary(db: Session, itinerary_data: dict):
    from app.models import Itineraries

    plane = get_plane_by_registration_srv(db=db, registration=itinerary_data["plane_registration"])
    itinerary_type = get_itinerary_type_by_type_srv(db=db, type=itinerary_data["itinerary_type"])

    new_itinerary = Itineraries(
        departure_time=itinerary_data["departure_time"],
        arrival_time=itinerary_data["arrival_time"],
        landings_amount=itinerary_data["landings_amount"],
        observations=itinerary_data.get("observations"),
        itinerary_type=itinerary_type,
        plane=plane,
    )

    db.add(new_itinerary)

    for airport in itinerary_data.get("airport_codes", []):
        new_itinerary.airport_codes.append(get_airport_code_by_code_srv(db=db, code=airport["code"]))

    return new_itinerary, __calculate_itinerary_cost(
        departure_time=itinerary_data["departure_time"],
        arrival_time=itinerary_data["arrival_time"],
        plane=plane,
    )


def __calculate_itinerary_cost(departure_time: datetime, arrival_time: datetime, plane: Planes) -> Decimal:
    if departure_time >= arrival_time:
        raise BadTimeInput

    delta = arrival_time - departure_time
    elapsed_seconds = Decimal(delta.days * 86400 + delta.seconds) + Decimal(delta.microseconds) / Decimal(1_000_000)

    blocks = (elapsed_seconds / Decimal(3600) / Decimal("0.1")).to_integral_value(rounding=ROUND_CEILING)
    billed_hours = blocks * Decimal("0.1")

    cost = billed_hours * Decimal(plane.fare)
    return cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
