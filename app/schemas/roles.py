from marshmallow import fields
from .base import BaseSchema


class RolesSchema(BaseSchema):
    name = fields.Str(required=True, dump_only=True)


class RolesUserUpdateSchema(BaseSchema):
    name = fields.Str(required=False, dump_only=True)


class RolesUpdateSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=False)