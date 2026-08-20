from marshmallow import fields
from .base import BaseSchema


class AirportCodesSchema(BaseSchema):
    code = fields.Str(required=True)


class AirportCodesCreateSchema(BaseSchema):
    code = fields.Str(required=True)


class AirportCodesUpdateSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    code = fields.Str(required=True)
    itineraries = fields.Nested("ItinerariesSchema", many=True, dump_only=True)


class AirportCodesWithItinerariesSchema(AirportCodesSchema):
    itineraries = fields.Nested("ItinerariesSchema", many=True, exclude=("airport_codes",))