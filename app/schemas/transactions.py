from marshmallow import fields
from .base import BaseSchema
from ..services.payment_types import get_payment_type_by_name_srv


class TransactionsBaseSchema(BaseSchema):
    amount = fields.Decimal(required=True, as_string=True)
    issued_date = fields.Date(required=True)
    description = fields.Str(allow_none=True)


class TransactionsAdminSchema(TransactionsBaseSchema):
    id = fields.Int(dump_only=True)
    payment_type = fields.Nested("PaymentTypesSchema")


class TransactionsPublicSchema(TransactionsBaseSchema):
    payment_type = fields.Method(serialize="get_payment_type_name", deserialize="load_payment_type")

    def load_payment_type(self, value):
        return get_payment_type_by_name_srv(name=value)

    def get_payment_type_name(self, obj):
        return obj.payment_type.type if obj.payment_type else None