import math
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import joinedload

from app.models import FlightSessions, Itineraries, Planes, Users, Transactions
from .airport_codes import get_airport_code_by_code_srv
from .itinerary_types import get_itinerary_type_by_type_srv
from .payment_types import get_payment_type_by_name_srv
from .planes import get_plane_by_registration_srv
from .transactions import sub_user_transaction_srv
from .users import get_user_by_email_srv
from ..errors import UserNotFound, BadTimeInput, FlightSessionNotFound
from ..extensions import db


def get_flight_sessions_srv(flight_session_identifier: Optional[int] = None, plane_registration: Optional[str] = None,
                            admin_email: Optional[str] = None, user_first_name: Optional[str] = None, user_last_name: Optional[str] = None,
                            observations: Optional[str] = None,
                            starting_date: Optional[date] = None, limit_date: Optional[date] = None) -> list[FlightSessions]:
    stmt = db.select(FlightSessions)

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
        stmt = stmt.where(db.and_(FlightSessions.issued_date >= starting_date, FlightSessions.issued_date <= limit_date))
    elif starting_date:
        stmt = stmt.where(FlightSessions.issued_date >= starting_date)
    elif limit_date:
        stmt = stmt.where(FlightSessions.issued_date <= limit_date)
    if observations:
        stmt = stmt.where(FlightSessions.observations.ilike(f"%{observations}%"))

    return db.session.execute(stmt).unique().scalars().all()


# This method does not use the get_user_by_email_srv method as the rest in order to eager load the flight_sessions
def get_user_flight_sessions_srv(email: str) -> list[FlightSessions]:
    user = db.session.execute(
        db.select(Users)
        .options(
            joinedload(Users.flight_sessions).joinedload(FlightSessions.itineraries).joinedload(Itineraries.plane),
            joinedload(Users.flight_sessions).joinedload(FlightSessions.itineraries).joinedload(Itineraries.airport_codes),
            joinedload(Users.flight_sessions).joinedload(FlightSessions.users)
        )
        .where(Users.email == email)
    ).unique().scalar_one_or_none()
    if not user:
        raise UserNotFound
    return user.flight_sessions


# This method does not use the get_user_by_email_srv method as the rest in order to eager load the flight_sessions
def get_flight_session_by_identifier_srv(flight_session_identifier: int) -> FlightSessions:
    flight_session = db.session.execute(
        db.select(FlightSessions)
        .options(
            joinedload(FlightSessions.itineraries).joinedload(Itineraries.plane),
            joinedload(FlightSessions.itineraries).joinedload(Itineraries.airport_codes),
            joinedload(FlightSessions.users)
        )
        .where(FlightSessions.flight_session_identifier == flight_session_identifier)
    ).unique().scalar_one_or_none()
    if not flight_session:
        raise FlightSessionNotFound
    return flight_session


def create_flight_session_srv(flight_session_data: dict, admin_email: str) -> FlightSessions:
    last_identifier = db.session.query(db.func.max(FlightSessions.flight_session_identifier)).scalar()
    next_identifier = (last_identifier or 0) + 1
    # Creates a local instance to make sure that all the data is in a single session
    new_flight_session = FlightSessions(
        flight_session_identifier=next_identifier,
        issued_date=flight_session_data["issued_date"],
        observations=flight_session_data.get("observations"),
    )

    admin = get_user_by_email_srv(email=admin_email)
    user = get_user_by_email_srv(email=flight_session_data["user_email"])
    if flight_session_data.get("instructor_email"):
        instructor = get_user_by_email_srv(email=flight_session_data["instructor_email"])
        new_flight_session.users.append(instructor)
    new_flight_session.users.append(user)
    new_flight_session.users.append(admin)

    total_session_cost = 0
    for itinerary_data in flight_session_data["itineraries"]:
        new_itinerary, itinerary_cost = __build_itinerary(itinerary_data)
        new_flight_session.itineraries.append(new_itinerary)
        total_session_cost += itinerary_cost

    try:
        new_transaction = sub_user_transaction_srv(
            email=user.email,
            transaction=Transactions(
                amount=total_session_cost,
                issued_date=datetime.now(timezone.utc),
                description="Transaction automatically created by flight session",
                payment_type=get_payment_type_by_name_srv("Flight Session"),
                balance_id=user.balance.id
            )
        )

        new_flight_session.transaction_id = new_transaction.id
        db.session.add(new_flight_session)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return new_flight_session


def __build_itinerary(itinerary_data: dict) -> tuple[Itineraries, float]:
    plane = get_plane_by_registration_srv(registration=itinerary_data["plane_registration"])
    itinerary_type = get_itinerary_type_by_type_srv(type=itinerary_data["itinerary_type"])

    new_itinerary = Itineraries(
        departure_time=itinerary_data["departure_time"],
        arrival_time=itinerary_data["arrival_time"],
        landings_amount=itinerary_data["landings_amount"],
        observations=itinerary_data.get("observations"),
        itinerary_type=itinerary_type,
        plane=plane
    )

    db.session.add(new_itinerary)

    for airport in itinerary_data.get("airport_codes", []):
        new_itinerary.airport_codes.append(get_airport_code_by_code_srv(code=airport["code"]))

    return new_itinerary, __calculate_itinerary_cost(
        departure_time=itinerary_data["departure_time"],
        arrival_time=itinerary_data["arrival_time"],
        plane=plane
    )


def __calculate_itinerary_cost(departure_time: datetime, arrival_time: datetime, plane: Planes) -> float:
    if departure_time >= arrival_time:
        raise BadTimeInput

    diff_hours = (arrival_time - departure_time).total_seconds() / 3600
    minutes_fraction, whole_hours = math.modf(diff_hours)
    cost = whole_hours

    # Business rule: every 6 minutes → 0.1h
    cost += min(math.ceil((minutes_fraction * 60) / 6) * 0.1, 1.0)
    return cost * plane.fare
