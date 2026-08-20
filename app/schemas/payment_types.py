from marshmallow import fields
from .base import BaseSchema


class PaymentTypesSchema(BaseSchema):
    type = fields.Str(required=True)
    details = fields.Str(allow_none=True)


class PaymentTypesUpdateSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    type = fields.Str(required=False)
    details = fields.Str(allow_none=True)