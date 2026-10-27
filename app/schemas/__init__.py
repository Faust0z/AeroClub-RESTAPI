from .airport_codes import AirportCodesCreate, AirportCodesOut, AirportCodesUpdate
from .balances import BalancesOut, BalancesUpdate
from .flight_sessions import FlightSessionsCreate, FlightSessionsOut
from .itineraries import ItinerariesCreate, ItinerariesOut
from .itinerary_types import ItineraryTypesCreate, ItineraryTypesOut, ItineraryTypesUpdate
from .payment_types import PaymentTypesCreate, PaymentTypesOut, PaymentTypesUpdate
from .plane_status import PlaneStatusCreate, PlaneStatusOut, PlaneStatusUpdate
from .planes import PlanesCreate, PlanesOut, PlanesUpdate
from .roles import RolesCreate, RolesOut, RolesUpdate
from .transactions import TransactionsAdminOut, TransactionsCreate, TransactionsPublicOut
from .users import (
    UsersAdminOut,
    UsersAdminUpdate,
    UsersInstructorOut,
    UsersOut,
    UsersRegister,
    UsersUpdate,
)

# Rebuild Pydantic models with forward references (e.g. UsersOut -> RolesOut)
UsersOut.model_rebuild()
UsersInstructorOut.model_rebuild()
UsersAdminOut.model_rebuild()

__all__ = [
    "AirportCodesCreate",
    "AirportCodesOut",
    "AirportCodesUpdate",
    "BalancesOut",
    "BalancesUpdate",
    "FlightSessionsCreate",
    "FlightSessionsOut",
    "ItinerariesCreate",
    "ItinerariesOut",
    "ItineraryTypesCreate",
    "ItineraryTypesOut",
    "ItineraryTypesUpdate",
    "PaymentTypesCreate",
    "PaymentTypesOut",
    "PaymentTypesUpdate",
    "PlaneStatusCreate",
    "PlaneStatusOut",
    "PlaneStatusUpdate",
    "PlanesCreate",
    "PlanesOut",
    "PlanesUpdate",
    "RolesCreate",
    "RolesOut",
    "RolesUpdate",
    "TransactionsAdminOut",
    "TransactionsCreate",
    "TransactionsPublicOut",
    "UsersAdminOut",
    "UsersAdminUpdate",
    "UsersInstructorOut",
    "UsersOut",
    "UsersRegister",
    "UsersUpdate",
]
