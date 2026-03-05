from datetime import datetime, timezone

from flask import Flask, request
from marshmallow import ValidationError as MarshmallowValidationError
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, Forbidden, Conflict, HTTPException


class AirportCodeAlreadyExists(Conflict):
    description = "Airport code already exists"


class AirportCodeNotFound(NotFound):
    description = "Airport code not found"


class AuthError(Unauthorized):
    description = "Authentication credentials were not provided or are invalid"


class BadAuthRequest(BadRequest):
    description = "Email and password are required"


class BadTimeInput(BadRequest):
    description = "Arrival time is earlier than departure time"


class BalanceNotFound(NotFound):
    description = "Balance not found for this user"


class EmailAlreadyExists(Conflict):
    description = "The email given is already registered"


class FareTypeAlreadyExists(Conflict):
    description = "Fare type already exists"


class FareTypeNotFound(NotFound):
    description = "Fare type not found"


class FlightSessionNotFound(NotFound):
    description = "Flight session not found"


class ItineraryTypeAlreadyExists(Conflict):
    description = "Itinerary type already exists"


class ItineraryTypeNotFound(NotFound):
    description = "Itinerary type not found"


class PaymentTypeNotFound(NotFound):
    description = "Payment type not found"


class PermissionDenied(Forbidden):
    description = "You do not have permission to access this resource"


class PermissionDeniedDisabledUser(Forbidden):
    description = "User account is disabled"


class PlaneNotFound(NotFound):
    description = "Plane not found"


class PlaneStatusNotFound(NotFound):
    description = "Plane status not found"


class PaymentTypeAlreadyExists(Conflict):
    description = "Payment type already exists"


class PlaneFareNotFound(NotFound):
    description = "Plane fare not found"


class PlaneStatusAlreadyExists(Conflict):
    description = "Plane Status already exists"


class PlaneRegistrationAlreadyExists(Conflict):
    description = "Plane's registration already exists"


class ResourceAlreadyExists(Conflict):
    description = "Resource already exists"


class UserNotFound(NotFound):
    description = "No user found with the given email"


class RoleNotFound(NotFound):
    description = "Role not found"


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException) -> tuple[dict, int]:
        response: dict = {
            "error": e.__class__.__name__,
            "message": e.description,
            "status": e.code,
            "path": request.path,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return response, e.code

    @app.errorhandler(Exception)  # catches any unhandled exception
    def handle_generic_error(e: Exception) -> tuple[dict, int]:
        response: dict = {
            "error": "InternalServerError",
            "message": str(e) or "An unexpected error occurred",
            "status": 500,
            "path": request.path,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return response, 500

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_error(e: MarshmallowValidationError) -> tuple[dict, int]:
        response: dict = {
            "error": "ValidationError",
            "message": e.messages,
            "status": 400,
            "path": request.path,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return response, 400
