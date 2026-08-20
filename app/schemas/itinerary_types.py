from marshmallow import fields
from .base import BaseSchema


class ItineraryTypesSchema(BaseSchema):
    type = fields.Str(required=True)


class ItineraryTypesUpdateSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    type = fields.Str(required=True)