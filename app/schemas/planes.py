from marshmallow import fields
from .base import BaseSchema


class PlanesSchema(BaseSchema):
    brand = fields.Str(required=True)
    model = fields.Str(required=True)
    registration = fields.Str(required=True)
    category = fields.Str(required=True)
    acquisition_date = fields.Date(allow_none=True)
    fare = fields.Decimal(required=True, as_string=True)
    consumption_per_hour = fields.Int(required=True)
    description = fields.Str(allow_none=True)
    plane_status = fields.Nested("PlaneStatusSchema")


class PlanesUpdateSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    brand = fields.Str(required=False)
    model = fields.Str(required=False)
    registration = fields.Str(required=False)
    category = fields.Str(required=False)
    acquisition_date = fields.Date(allow_none=True)
    fare = fields.Decimal(required=False, as_string=True)
    consumption_per_hour = fields.Int(required=False)
    description = fields.Str(allow_none=True)
    plane_status = fields.Nested("PlaneStatusSchema")