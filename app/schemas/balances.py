from marshmallow import fields
from .base import BaseSchema


class BalancesSchema(BaseSchema):
    balance = fields.Decimal(required=True, dump_only=True, as_string=True)
    user = fields.Nested("UsersInstructorSchema")


class BalancesUpdateSchema(BalancesSchema):
    id = fields.Int(dump_only=True)
    balance = fields.Decimal(required=False, as_string=True)