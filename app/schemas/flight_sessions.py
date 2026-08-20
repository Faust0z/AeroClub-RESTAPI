from marshmallow import fields
from .base import BaseSchema


class FlightSessionsSchema(BaseSchema):
    issued_date = fields.Date(dump_only=True)
    observations = fields.Str(allow_none=True)
    flight_session_identifier = fields.Int(dump_only=True)
    itineraries = fields.Nested("ItinerariesSchema", many=True)


class FlightSessionsCreateSchema(BaseSchema):
    user_email = fields.Email(required=True)
    instructor_email = fields.Email(allow_none=True)
    issued_date = fields.Date(required=True)
    observations = fields.Str(allow_none=True)
    itineraries = fields.Nested("ItinerariesCreateSchema", many=True, required=True)