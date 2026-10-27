from datetime import date, datetime, timezone
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from app.models import FlightSessions, Itineraries, Planes, Transactions, Users
from .airport_codes import get_airport_code_by_code_srv
from .itinerary_types import get_itinerary_type_by_type_srv
from .payment_types import get_payment_type_by_name_srv
from .planes import get_plane_by_registration_srv
from .transactions import sub_user_transaction_srv
from .users import get_user_by_email_srv
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
) -> list[FlightSessions]:
    stmt = select(FlightSessions)

    if flight_session_identifier:
        stmt = stmt.where(FlightSessions.flight_session_identifier == flight_session_identifier)
    if admin_email or user_first_name or user_last_name:
        stmt = stmt.join(FlightSessions.users)
        if admin_email:
            stmt = stmt.where(Users.email.ilike(f"%{admin_email}%"))
        if user_first_name:
            stmt = stmt.where(Users.first_name.ilike(f"%{user_first_name}%"))
        if user_last_name:
            stmt = stmt.where(Users.last_name.ilike(f"%{user_last_name}%"))
    if plane_registration:
        stmt = stmt.join(FlightSessions.itineraries).join(Itineraries.plane)
        stmt = stmt.where(Planes.registration.ilike(f"%{plane_registration}%"))
    if starting_date and limit_date:
        stmt = stmt.where(and_(FlightSessions.issued_date >= starting_date, FlightSessions.issued_date <= limit_date))
    elif starting_date:
        stmt = stmt.where(FlightSessions.issued_date >= starting_date)
    elif limit_date:
        stmt = stmt.where(FlightSessions.issued_date <= limit_date)
    if observations:
        stmt = stmt.where(FlightSessions.observations.ilike(f"%{observations}%"))

    return db.execute(stmt).unique().scalars().all()


def get_user_flight_sessions_srv(db: Session, email: str) -> list[FlightSessions]:
    user = db.execute(
        select(Users)
        .options(
            joinedload(Users.flight_sessions).joinedload(FlightSessions.itineraries).joinedload(Itineraries.plane),
            joinedload(Users.flight_sessions).joinedload(FlightSessions.itineraries).joinedload(Itineraries.airport_codes),
            joinedload(Users.flight_sessions).joinedload(FlightSessions.users),
        )
        .where(Users.email == email)
    ).unique().scalar_one_or_none()
    if not user:
        raise UserNotFound
    return user.flight_sessions


def get_flight_session_by_identifier_srv(db: Session, flight_session_identifier: int) -> FlightSessions:
    flight_session = db.execute(
        select(FlightSessions)
        .options(
            joinedload(FlightSessions.itineraries).joinedload(Itineraries.plane),
            joinedload(FlightSessions.itineraries).joinedload(Itineraries.airport_codes),
            joinedload(FlightSessions.users),
        )
        .where(FlightSessions.flight_session_identifier == flight_session_identifier)
    ).unique().scalar_one_or_none()
    if not flight_session:
        raise FlightSessionNotFound
    return flight_session


def create_flight_session_srv(db: Session, flight_session_data: dict, admin_email: str) -> FlightSessions:
    last_identifier = db.execute(select(db.func.max(FlightSessions.flight_session_identifier))).scalar()
    next_identifier = (last_identifier or 0) + 1
    new_flight_session = FlightSessions(
        flight_session_identifier=next_identifier,
        issued_date=flight_session_data["issued_date"],
        observations=flight_session_data.get("observations"),
    )

    admin = get_user_by_email_srv(db=db, email=admin_email)
    user = get_user_by_email_srv(db=db, email=flight_session_data["user_email"])
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
            email=user.email,
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
