from datetime import datetime, timezone


class AppError(Exception):
    status_code: int = 500
    detail: str = "An unexpected error occurred"


class AirportCodeAlreadyExists(AppError):
    status_code = 409
    detail = "Airport code already exists"


class AirportCodeNotFound(AppError):
    status_code = 404
    detail = "Airport code not found"


class AuthError(AppError):
    status_code = 401
    detail = "Authentication credentials were not provided or are invalid"


class BadAuthRequest(AppError):
    status_code = 400
    detail = "Email and password are required"


class BadTimeInput(AppError):
    status_code = 400
    detail = "Arrival time is earlier than departure time"


class BalanceNotFound(AppError):
    status_code = 404
    detail = "Balance not found for this user"


class EmailAlreadyExists(AppError):
    status_code = 409
    detail = "The email given is already registered"


class FareTypeAlreadyExists(AppError):
    status_code = 409
    detail = "Fare type already exists"


class FareTypeNotFound(AppError):
    status_code = 404
    detail = "Fare type not found"


class FlightSessionNotFound(AppError):
    status_code = 404
    detail = "Flight session not found"


class ItineraryTypeAlreadyExists(AppError):
    status_code = 409
    detail = "Itinerary type already exists"


class ItineraryTypeNotFound(AppError):
    status_code = 404
    detail = "Itinerary type not found"


class PaymentTypeNotFound(AppError):
    status_code = 404
    detail = "Payment type not found"


class PermissionDenied(AppError):
    status_code = 403
    detail = "You do not have permission to access this resource"


class PermissionDeniedDisabledUser(AppError):
    status_code = 403
    detail = "User account is disabled"


class PlaneNotFound(AppError):
    status_code = 404
    detail = "Plane not found"


class PlaneStatusNotFound(AppError):
    status_code = 404
    detail = "Plane status not found"


class PaymentTypeAlreadyExists(AppError):
    status_code = 409
    detail = "Payment type already exists"


class PlaneFareNotFound(AppError):
    status_code = 404
    detail = "Plane fare not found"


class PlaneStatusAlreadyExists(AppError):
    status_code = 409
    detail = "Plane Status already exists"


class PlaneRegistrationAlreadyExists(AppError):
    status_code = 409
    detail = "Plane's registration already exists"


class ResourceAlreadyExists(AppError):
    status_code = 409
    detail = "Resource already exists"


class UserNotFound(AppError):
    status_code = 404
    detail = "No user found with the given email"


class RoleNotFound(AppError):
    status_code = 404
    detail = "Role not found"
