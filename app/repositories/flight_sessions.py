import uuid
from datetime import date
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from ..models import FlightSessions, Itineraries, Planes, Users


class FlightSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        flight_session_identifier: Optional[int] = None,
        plane_registration: Optional[str] = None,
        admin_email: Optional[str] = None,
        user_first_name: Optional[str] = None,
        user_last_name: Optional[str] = None,
        observations: Optional[str] = None,
        starting_date: Optional[date] = None,
        limit_date: Optional[date] = None,
    ):
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

        return stmt

    def get_by_user_id(self, user_id: uuid.UUID):
        return self.db.execute(
            select(Users)
            .options(
                joinedload(Users.flight_sessions).joinedload(FlightSessions.itineraries).joinedload(Itineraries.plane),
                joinedload(Users.flight_sessions).joinedload(FlightSessions.itineraries).joinedload(Itineraries.airport_codes),
                joinedload(Users.flight_sessions).joinedload(FlightSessions.users),
            )
            .where(Users.uuid == user_id)
        ).unique().scalar_one_or_none().flight_sessions

    def get_by_identifier(self, flight_session_identifier: int) -> Optional[FlightSessions]:
        return self.db.execute(
            select(FlightSessions)
            .options(
                joinedload(FlightSessions.itineraries).joinedload(Itineraries.plane),
                joinedload(FlightSessions.itineraries).joinedload(Itineraries.airport_codes),
                joinedload(FlightSessions.users),
            )
            .where(FlightSessions.flight_session_identifier == flight_session_identifier)
        ).unique().scalar_one_or_none()

    def add(self, session: FlightSessions) -> FlightSessions:
        self.db.add(session)
        self.db.commit()
        return session

    def flush(self) -> None:
        self.db.flush()
