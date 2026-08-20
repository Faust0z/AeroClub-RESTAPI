from marshmallow import fields
from .base import BaseSchema


class PlaneStatusSchema(BaseSchema):
    state = fields.Str(required=True)


class PlaneStatusUpdateSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    state = fields.Str(required=True)