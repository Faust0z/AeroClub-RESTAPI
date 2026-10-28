from sqlalchemy import Column, ForeignKey, Integer, Table
import uuid

from ..database import Base

itinerary_has_airport_codes = Table(
    "itinerary_has_airport_codes",
    Base.metadata,
    Column("itinerary_id", ForeignKey("itineraries.id"), primary_key=True),
    Column("aeroport_codes_id", ForeignKey("airport_codes.id"), primary_key=True),
)

users_have_roles = Table(
    "users_have_roles",
    Base.metadata,
    Column("users_id", ForeignKey("users.id"), primary_key=True),
    Column("roles_id", ForeignKey("roles.id"), primary_key=True),
)

users_have_flight_sessions = Table(
    "users_have_flight_sessions",
    Base.metadata,
    Column("users_id", ForeignKey("users.id"), primary_key=True),
    Column("flight_sessions", ForeignKey("flight_sessions.id"), primary_key=True),
)
