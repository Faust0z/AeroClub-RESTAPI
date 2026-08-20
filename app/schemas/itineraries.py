from marshmallow import fields, validates_schema, ValidationError
from .base import BaseSchema

class ItinerariesSchema(BaseSchema):
    departure_time = fields.DateTime(required=True)
    arrival_time = fields.DateTime(required=True)
    landings_amount = fields.Int(required=True)
    observations = fields.Str(allow_none=True)
    itinerary_type = fields.Nested("ItineraryTypesSchema")
    airport_codes = fields.Nested("AirportCodesSchema", many=True)

class ItinerariesCreateSchema(BaseSchema):
    departure_time = fields.DateTime(required=True)
    arrival_time = fields.DateTime(required=True)
    landings_amount = fields.Int(required=True)
    observations = fields.Str(allow_none=True)
    itinerary_type = fields.Str(required=True)
    plane_registration = fields.Str(required=True)
    airport_codes = fields.Nested("AirportCodesCreateSchema", many=True, required=True)

    @validates_schema
    def validate_time_range(self, data, **kwargs):
        if data.get("departure_time") and data.get("arrival_time"):
            if data["departure_time"] >= data["arrival_time"]:
                raise ValidationError(
                    {"arrival_time": "Arrival time must be later than departure time."}
                )
